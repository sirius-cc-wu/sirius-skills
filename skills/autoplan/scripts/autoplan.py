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
    metadata = planning_module.read_metadata(str(feature["path"]))
    return rows, feature, scope_context, metadata, checkpoint


def owner_for_status(status: str) -> tuple[str, str]:
    return STATUS_TO_OWNER.get(status, ("guide-planning", "resolve_planning_state"))


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
) -> None:
    append_event(
        event_log_path,
        {
            "timestamp": utc_now(),
            "skill": "autoplan",
            "target_id": target_id,
            "planning_status": planning_status,
            "next_owner": next_owner,
            "action": action,
        },
    )
    write_checkpoint(
        checkpoint_path,
        CheckpointRecord(
            run_id="autoplan-active",
            state=action,
            payload={
                "target_id": target_id,
                "planning_status": planning_status,
                "next_owner": next_owner,
                "learning_ids": [item["id"] for item in learnings],
                "auto_decision_policy": auto_decision_policy,
            },
        ),
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    planning_module = load_module(GUIDE_PLANNING_SCRIPT, "manage_planning_for_autoplan")
    repo_root = git_repo_root()
    checkpoint_path, event_log_path, learnings_path = runtime_paths(repo_root)

    try:
        _, feature, scope_context, metadata, prior_checkpoint = resolve_target(
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

    target_id = str(feature["feature"])
    planning_status = str(metadata["status"])
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
    )

    payload = {
        "run_id": "autoplan-active",
        "target_id": target_id,
        "target_path": str(feature["path"]),
        "planning_status": planning_status,
        "next_owner": next_owner,
        "action": action,
        "auto_decision_policy": auto_decision_policy,
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
