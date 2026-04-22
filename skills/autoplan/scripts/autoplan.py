#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
SKILLS_DIR = SKILL_DIR.parent
REPO_LIB_DIR = SKILLS_DIR.parent / "lib"
SKILL_LIB_DIR = SKILL_DIR / "lib"
GUIDE_PLANNING_SCRIPT = SKILLS_DIR / "guide-planning" / "scripts" / "manage_planning.py"

if REPO_LIB_DIR.is_dir() and str(REPO_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(REPO_LIB_DIR))
if SKILL_LIB_DIR.is_dir() and str(SKILL_LIB_DIR) not in sys.path:
    sys.path.append(str(SKILL_LIB_DIR))

from workflow_runtime import CheckpointRecord, append_event, load_checkpoint, mark_checkpoint_stale, query_learnings, write_checkpoint  # noqa: E402


DEFAULT_RUNTIME_DIR = Path(".skills/runtime")
DEFAULT_LEARNINGS_PATH = Path(".skills/learnings.jsonl")


STATUS_TO_OWNER = {
    "discovery_pending": ("discover", "run_discover"),
    "discovery_ready": ("design", "run_design"),
    "design_ready": ("breakdown", "run_breakdown"),
    "breakdown_ready": ("review-planning", "run_review_planning"),
    "planning_reviewed": ("approval", "approval_required"),
}

OWNER_TRANSITIONS = {
    "discovery_pending": ("discover", "discovery_ready"),
    "discovery_ready": ("design", "design_ready"),
    "design_ready": ("breakdown", "breakdown_ready"),
    "breakdown_ready": ("review-planning", "planning_reviewed"),
}

VALID_OWNER_NAMES = {owner for owner, _ in STATUS_TO_OWNER.values()}


def load_module(script_path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resume one planning target with checkpointed planning context."
    )
    parser.add_argument("target", nargs="?", help="Feature slug or planning packet path.")
    parser.add_argument("--scope", default=None, help="Optional planning scope path.")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint.")
    parser.add_argument("--json", action="store_true", help="Render machine-readable output.")
    parser.set_defaults(execute_owner_chain=None)
    parser.add_argument(
        "--execute-owner-chain",
        dest="execute_owner_chain",
        action="store_true",
        help="Execute discover/design/breakdown/review-planning in sequence until a stop boundary.",
    )
    parser.add_argument(
        "--no-execute-owner-chain",
        dest="execute_owner_chain",
        action="store_false",
        help="Disable owner-chain execution even if enabled in planning config.",
    )
    parser.add_argument(
        "--stop-on-owner",
        action="append",
        default=None,
        help="Owner boundary to stop before executing (repeatable).",
    )
    parser.add_argument(
        "--review-note",
        default=None,
        help="Optional review note used when advancing into planning_reviewed.",
    )
    return parser.parse_args(argv)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def git_repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=True,
        capture_output=True,
        text=True,
    )
    return Path(result.stdout.strip())


def runtime_paths(repo_root: Path) -> tuple[Path, Path, Path]:
    runtime_dir = repo_root / DEFAULT_RUNTIME_DIR
    checkpoint_path = runtime_dir / "checkpoints" / "autoplan-active.json"
    event_log_path = runtime_dir / "execution-log.jsonl"
    learnings_path = repo_root / DEFAULT_LEARNINGS_PATH
    return checkpoint_path, event_log_path, learnings_path


def resolve_target(args: argparse.Namespace, checkpoint_path: Path, planning_module):
    checkpoint = load_checkpoint(checkpoint_path) if args.resume and checkpoint_path.exists() else None
    selector = args.target or (str(checkpoint.payload.get("target_id")) if checkpoint is not None else None)
    if not selector:
        raise RuntimeError("No planning target was provided and no autoplan checkpoint exists.")
    rows, feature, scope_context = planning_module.resolve_feature_lookup(
        selector, explicit_scope=args.scope
    )
    if feature is None:
        raise RuntimeError(f"Planning target not found: {selector}")
    feature_dir = planning_module.feature_dir_for_row(feature, scope_context=scope_context)
    metadata = planning_module.read_metadata(feature_dir)
    return rows, feature, scope_context, metadata, checkpoint


def owner_for_status(status: str) -> tuple[str, str]:
    return STATUS_TO_OWNER.get(status, ("guide-planning", "resolve_planning_state"))


def normalize_owner_name(raw_owner: str) -> str:
    return raw_owner.strip().lower().replace("_", "-")


def parse_stop_on_owners(raw_value: object) -> list[str]:
    if raw_value is None:
        return []
    if isinstance(raw_value, str):
        candidates: list[str] = [raw_value]
    elif isinstance(raw_value, list):
        candidates = []
        for item in raw_value:
            if not isinstance(item, str):
                raise RuntimeError("autoplan stop_on_owner entries must be strings.")
            candidates.append(item)
    else:
        raise RuntimeError("autoplan stop_on_owner must be a string or list of strings.")

    normalized: list[str] = []
    for candidate in candidates:
        owner = normalize_owner_name(candidate)
        if not owner:
            continue
        if owner not in VALID_OWNER_NAMES:
            raise RuntimeError(
                "Invalid autoplan stop_on_owner value "
                f"'{candidate}'. Valid owners: {sorted(VALID_OWNER_NAMES)}"
            )
        if owner not in normalized:
            normalized.append(owner)
    return normalized


def parse_optional_review_note(raw_value: object) -> Optional[str]:
    if raw_value is None:
        return None
    if not isinstance(raw_value, str):
        raise RuntimeError("autoplan review_note must be a string when present.")
    cleaned = raw_value.strip()
    return cleaned or None


def classify_owner_chain_stop_kind(message: str) -> str:
    lowered = message.lower()
    if "missing required file" in lowered or "requires a non-empty review note" in lowered:
        return "missing_required_input"
    if "ambiguous" in lowered:
        return "ambiguity"
    if "invalid status transition" in lowered:
        return "invalid_transition"
    return "validation_failed"


def execute_owner_chain(
    rows: list[dict[str, object]],
    feature: dict[str, object],
    *,
    planning_module,
    scope_context,
    stop_on_owner: list[str],
    review_note: Optional[str],
) -> tuple[str, list[dict[str, Any]], Optional[dict[str, Any]]]:
    steps: list[dict[str, Any]] = []
    feature_dir = planning_module.feature_dir_for_row(feature, scope_context=scope_context)

    for _ in range(len(OWNER_TRANSITIONS) + 1):
        metadata = planning_module.read_metadata(feature_dir)
        current_status = str(metadata["status"])
        transition = OWNER_TRANSITIONS.get(current_status)
        if transition is None:
            if current_status == "planning_reviewed":
                return (
                    current_status,
                    steps,
                    {
                        "kind": "approval_boundary",
                        "owner": "approval",
                        "status": current_status,
                        "target_status": current_status,
                        "message": "Reached planning_reviewed approval boundary.",
                    },
                )
            return current_status, steps, None

        owner, target_status = transition
        if owner in stop_on_owner:
            return (
                current_status,
                steps,
                {
                    "kind": "owner_stop",
                    "owner": owner,
                    "status": current_status,
                    "target_status": target_status,
                    "message": (
                        f"Stopped before '{owner}' because it is configured in stop_on_owner."
                    ),
                },
            )

        sync_review_note = review_note if target_status == "planning_reviewed" else None
        success, message = planning_module.sync_feature_status(
            rows,
            feature,
            through=target_status,
            review_note=sync_review_note,
            scope_context=scope_context,
        )

        next_status = str(planning_module.read_metadata(feature_dir)["status"])
        advanced = next_status != current_status
        step = {
            "owner": owner,
            "from_status": current_status,
            "target_status": target_status,
            "success": bool(success),
            "advanced": advanced,
            "result_status": next_status,
            "message": message,
        }
        steps.append(step)

        if not success or not advanced:
            return (
                next_status,
                steps,
                {
                    "kind": classify_owner_chain_stop_kind(message),
                    "owner": owner,
                    "status": next_status,
                    "target_status": target_status,
                    "message": message,
                },
            )

        if next_status == "planning_reviewed":
            return (
                next_status,
                steps,
                {
                    "kind": "approval_boundary",
                    "owner": "approval",
                    "status": next_status,
                    "target_status": next_status,
                    "message": "Reached planning_reviewed approval boundary.",
                },
            )

    metadata = planning_module.read_metadata(feature_dir)
    return str(metadata["status"]), steps, {
        "kind": "safety_stop",
        "owner": "guide-planning",
        "status": str(metadata["status"]),
        "target_status": str(metadata["status"]),
        "message": "Stopped owner-chain due to unexpected loop safety boundary.",
    }


def write_runtime_records(
    checkpoint_path: Path,
    event_log_path: Path,
    *,
    target_id: str,
    planning_status: str,
    next_owner: str,
    action: str,
    learnings: list[dict[str, Any]],
    auto_decision_policy: str,
    owner_chain: Optional[dict[str, Any]],
) -> None:
    event: dict[str, Any] = {
        "timestamp": utc_now(),
        "skill": "autoplan",
        "target_id": target_id,
        "planning_status": planning_status,
        "next_owner": next_owner,
        "action": action,
    }
    if owner_chain is not None:
        event["owner_chain_enabled"] = bool(owner_chain.get("enabled", False))
        stop_reason = owner_chain.get("stop_reason")
        if isinstance(stop_reason, dict):
            event["owner_chain_stop_kind"] = stop_reason.get("kind")
            event["owner_chain_stop_owner"] = stop_reason.get("owner")
    append_event(event_log_path, event)

    checkpoint_payload: dict[str, Any] = {
        "target_id": target_id,
        "planning_status": planning_status,
        "next_owner": next_owner,
        "learning_ids": [item["id"] for item in learnings],
        "auto_decision_policy": auto_decision_policy,
    }
    if owner_chain is not None:
        checkpoint_payload["owner_chain"] = owner_chain

    write_checkpoint(
        checkpoint_path,
        CheckpointRecord(
            run_id="autoplan-active",
            state=action,
            payload=checkpoint_payload,
        ),
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    planning_module = load_module(GUIDE_PLANNING_SCRIPT, "manage_planning_for_autoplan")
    repo_root = git_repo_root()
    checkpoint_path, event_log_path, learnings_path = runtime_paths(repo_root)

    try:
        rows, feature, scope_context, metadata, prior_checkpoint = resolve_target(
            args, checkpoint_path, planning_module
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    raw_config = planning_module.load_raw_config(required=False, scope_context=scope_context)
    accelerators = raw_config.get("accelerators", {}) if isinstance(raw_config, dict) else {}
    autoplan_config = accelerators.get("autoplan", {}) if isinstance(accelerators, dict) else {}
    auto_decision_policy = (
        str(autoplan_config.get("auto_decision_policy", "conservative"))
        if isinstance(autoplan_config, dict)
        else "conservative"
    )

    try:
        config_execute_owner_chain = bool(autoplan_config.get("execute_owner_chain", False)) if isinstance(autoplan_config, dict) else False
        config_stop_on_owner = parse_stop_on_owners(
            autoplan_config.get("stop_on_owner") if isinstance(autoplan_config, dict) else None
        )
        config_review_note = parse_optional_review_note(
            autoplan_config.get("review_note") if isinstance(autoplan_config, dict) else None
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    execute_owner_chain_enabled = (
        config_execute_owner_chain
        if args.execute_owner_chain is None
        else bool(args.execute_owner_chain)
    )
    try:
        stop_on_owner = (
            config_stop_on_owner
            if args.stop_on_owner is None
            else parse_stop_on_owners(args.stop_on_owner)
        )
        review_note = (
            config_review_note
            if args.review_note is None
            else parse_optional_review_note(args.review_note)
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    target_id = str(feature["feature"])
    planning_status = str(metadata["status"])
    owner_chain: Optional[dict[str, Any]] = None

    if execute_owner_chain_enabled:
        planning_status, steps, stop_reason = execute_owner_chain(
            rows,
            feature,
            planning_module=planning_module,
            scope_context=scope_context,
            stop_on_owner=stop_on_owner,
            review_note=review_note,
        )
        owner_chain = {
            "enabled": True,
            "stop_on_owner": stop_on_owner,
            "steps": steps,
            "stop_reason": stop_reason,
        }

    next_owner, action = owner_for_status(planning_status)
    checkpoint_stale_reason: Optional[str] = None
    if prior_checkpoint is not None:
        prior_status = str(prior_checkpoint.payload.get("planning_status") or "")
        if prior_status and prior_status != planning_status:
            checkpoint_stale_reason = (
                f"planning status changed from {prior_status} to {planning_status}"
            )
            mark_checkpoint_stale(checkpoint_path, checkpoint_stale_reason)

    learnings = [
        record.to_dict()
        for record in query_learnings(
            learnings_path,
            scope=target_id,
            states=("active", "candidate"),
        )
    ]
    write_runtime_records(
        checkpoint_path,
        event_log_path,
        target_id=target_id,
        planning_status=planning_status,
        next_owner=next_owner,
        action=action,
        learnings=learnings,
        auto_decision_policy=auto_decision_policy,
        owner_chain=owner_chain,
    )

    payload = {
        "run_id": "autoplan-active",
        "target_id": target_id,
        "target_path": str(feature["path"]),
        "planning_status": planning_status,
        "next_owner": next_owner,
        "action": action,
        "auto_decision_policy": auto_decision_policy,
        "execute_owner_chain": execute_owner_chain_enabled,
        "owner_chain": owner_chain,
        "checkpoint_path": str(checkpoint_path),
        "event_log_path": str(event_log_path),
        "learnings": learnings,
        "checkpoint_stale_reason": checkpoint_stale_reason,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            "\n".join(
                [
                    f"Target: {target_id}",
                    f"Planning status: {planning_status}",
                    f"Next owner: {next_owner}",
                    f"Action: {action}",
                ]
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
