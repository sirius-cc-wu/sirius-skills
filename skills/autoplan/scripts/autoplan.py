#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shlex
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
ADD_SUBFEATURE_SCRIPT = SKILLS_DIR / "add-subfeature" / "scripts" / "manage_subfeatures.py"

if REPO_LIB_DIR.is_dir() and str(REPO_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(REPO_LIB_DIR))
if SKILL_LIB_DIR.is_dir() and str(SKILL_LIB_DIR) not in sys.path:
    sys.path.append(str(SKILL_LIB_DIR))

from workflow_runtime import (  # noqa: E402
    CheckpointRecord,
    RequestHandoffRecord,
    append_event,
    build_accelerator_readiness,
    classify_stop_reason_from_message,
    evaluate_planning_approval_gate,
    load_checkpoint,
    mark_checkpoint_stale,
    normalize_stop_reason,
    query_learnings,
    record_failure,
    record_failure_for_stop_reason,
    render_failure_summary,
    write_planning_approval_record,
    write_checkpoint,
    write_request_handoff,
)


DEFAULT_RUNTIME_DIR = Path(".skills/runtime")
DEFAULT_LEARNINGS_PATH = Path(".skills/learnings.jsonl")
SUBFEATURE_METADATA_FILE = ".subfeature-meta.json"
DISCOVER_STUB_MARKER = "<!-- add-subfeature:discover-stub -->"


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

SUBFEATURE_STATUS_TO_OWNER = {
    "impact_ready": ("design", "run_design"),
    "design_ready": ("breakdown", "run_breakdown"),
    "breakdown_ready": ("review-planning", "run_review_planning"),
    "reviewed": ("approval", "approval_required"),
    "finalized": ("guide-planning", "resolve_follow_on_delta"),
}

VALID_OWNER_NAMES = (
    {owner for owner, _ in STATUS_TO_OWNER.values()}
    | {owner for owner, _ in SUBFEATURE_STATUS_TO_OWNER.values()}
    | {"assess"}
)
AUTOMATABLE_OWNERS = {"discover", "assess", "design", "breakdown", "review-planning"}


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
        help="Execute the planning owner chain in sequence until a stop boundary.",
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
        help="Optional review note used when advancing into a reviewed planning state.",
    )
    parser.add_argument(
        "--approve",
        action="store_true",
        help="Record or refresh the durable approval record for a reviewed planning target.",
    )
    parser.add_argument(
        "--approval-note",
        default=None,
        help="Optional note recorded with the approval decision.",
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


def runtime_paths(repo_root: Path) -> tuple[Path, Path, Path, Path]:
    runtime_dir = repo_root / DEFAULT_RUNTIME_DIR
    checkpoint_path = runtime_dir / "checkpoints" / "autoplan-active.json"
    event_log_path = runtime_dir / "execution-log.jsonl"
    request_handoff_path = runtime_dir / "request-handoff.json"
    learnings_path = repo_root / DEFAULT_LEARNINGS_PATH
    return checkpoint_path, event_log_path, request_handoff_path, learnings_path


def emit_failure_response(
    *,
    args: argparse.Namespace,
    event_log_path: Path,
    reason_code: str,
    message: str,
    target_id: str = "",
    next_owner: str = "",
    owner: str = "",
    evidence_refs: Sequence[str] | None = None,
) -> int:
    context = record_failure(
        event_log_path,
        skill="autoplan",
        stage="planning",
        reason_code=reason_code,
        message=message,
        target_id=target_id,
        next_owner=next_owner,
        owner=owner,
        evidence_refs=evidence_refs,
    )
    if args.json:
        print(
            json.dumps(
                {
                    "event_log_path": str(event_log_path),
                    "failure_context": context.to_dict(),
                    "ok": False,
                    "skill": "autoplan",
                    "stage": "planning",
                    "target_id": target_id,
                },
                indent=2,
                sort_keys=True,
            )
        )
    print(render_failure_summary(context), file=sys.stderr)
    return 2


def read_dirty_worktree_paths(repo_root: Path, target_path: Path | None = None) -> list[str]:
    command = ["git", "-C", str(repo_root), "status", "--short", "--untracked-files=all"]
    if target_path is not None:
        try:
            relative_target = target_path.resolve().relative_to(repo_root.resolve())
        except ValueError as exc:
            raise RuntimeError(
                "Planning commit checkpoint target must stay inside the git repository root."
            ) from exc
        command.extend(["--", str(relative_target)])
    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError("Unable to inspect git worktree state for planning commit checkpoint.")
    return [line.rstrip() for line in result.stdout.splitlines() if line.strip()]


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
    if status == "implemented":
        return "guide-planning", "resolve_follow_on_delta"
    return STATUS_TO_OWNER.get(status, ("guide-planning", "resolve_planning_state"))


def is_subfeature_target(feature_dir: Path) -> bool:
    return (feature_dir / SUBFEATURE_METADATA_FILE).is_file()


def discover_is_stub(feature_dir: Path) -> bool:
    discover_path = feature_dir / "discover.md"
    if not discover_path.is_file():
        return True
    return DISCOVER_STUB_MARKER in discover_path.read_text(encoding="utf-8")


def read_subfeature_state(feature_dir: Path, subfeature_module) -> dict[str, Any]:
    raw_metadata = subfeature_module.read_metadata(str(feature_dir))
    return {
        "raw_metadata": raw_metadata,
        "raw_status": str(raw_metadata["status"]),
        "approval_status": str(raw_metadata.get("approval_status") or "pending"),
        "ready_slice_ids": list(raw_metadata.get("ready_slice_ids") or []),
        "discover_is_stub": discover_is_stub(feature_dir),
    }


def owner_for_subfeature_state(subfeature_state: dict[str, Any]) -> tuple[str, str]:
    raw_status = str(subfeature_state["raw_status"])
    if raw_status == "draft":
        if subfeature_state["discover_is_stub"]:
            return "discover", "run_discover"
        return "assess", "run_assess"
    if raw_status == "reviewed":
        if (
            str(subfeature_state["approval_status"]) == "approved"
            and subfeature_state["ready_slice_ids"]
        ):
            return "guide-planning", "resolve_planning_state"
    owner = SUBFEATURE_STATUS_TO_OWNER.get(raw_status)
    if owner is None:
        raise RuntimeError(f"Unsupported subfeature status for autoplan: '{raw_status}'.")
    return owner


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


def extract_missing_required_files(message: str) -> list[str]:
    if not message:
        return []
    return sorted({match for match in re.findall(r"Missing required file '([^']+)'", message)})


def bootstrap_specs_for_owner(
    *,
    owner: str,
    target_path: str,
    missing_files: Sequence[str],
) -> list[tuple[list[str], str]]:
    specs: list[tuple[list[str], str]] = []
    missing = set(missing_files)
    if owner == "breakdown":
        required = {"slice-planning.md", "slice-traceability.md"}
        if required.issubset(missing):
            display = (
                "python3 skills/breakdown/scripts/scaffold_breakdown.py "
                f"{shlex.quote(target_path)}"
            )
            specs.append(
                (
                    [
                        "python3",
                        str(SKILLS_DIR / "breakdown" / "scripts" / "scaffold_breakdown.py"),
                        target_path,
                    ],
                    display,
                )
            )
    if owner == "design" and "system-design.md" in missing:
        display = (
            "python3 skills/design/scripts/scaffold_design.py "
            f"{shlex.quote(target_path)}"
        )
        specs.append(
            (
                [
                    "python3",
                    str(SKILLS_DIR / "design" / "scripts" / "scaffold_design.py"),
                    target_path,
                ],
                display,
            )
        )
    return specs


def execute_safe_bootstrap(
    *,
    owner: str,
    target_path: str,
    missing_files: Sequence[str],
    repo_root: Path,
) -> list[str]:
    executed_commands: list[str] = []
    for argv, display in bootstrap_specs_for_owner(
        owner=owner, target_path=target_path, missing_files=missing_files
    ):
        result = subprocess.run(
            argv,
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()
            stdout = result.stdout.strip()
            detail = stderr or stdout or "bootstrap command failed"
            raise RuntimeError(
                f"Safe bootstrap for owner '{owner}' failed while running '{display}': {detail}"
            )
        executed_commands.append(display)
    return executed_commands


def execute_feature_owner_chain(
    rows: list[dict[str, object]],
    feature: dict[str, object],
    *,
    planning_module,
    repo_root: Path,
    scope_context,
    stop_on_owner: list[str],
    review_note: Optional[str],
) -> tuple[str, list[dict[str, Any]], Optional[dict[str, Any]]]:
    steps: list[dict[str, Any]] = []
    feature_dir = planning_module.feature_dir_for_row(feature, scope_context=scope_context)
    target_path = str(feature["path"])

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
            missing_files = extract_missing_required_files(message)
            executed_bootstrap_commands = execute_safe_bootstrap(
                owner=owner,
                target_path=target_path,
                missing_files=missing_files,
                repo_root=repo_root,
            )
            if executed_bootstrap_commands:
                return (
                    next_status,
                    steps,
                    {
                        "kind": "bootstrap_applied",
                        "owner": owner,
                        "status": next_status,
                        "target_status": target_status,
                        "message": (
                            f"Applied safe bootstrap commands for '{owner}'. "
                            "Continue with the owner workflow."
                        ),
                        "missing_files": missing_files,
                        "bootstrap_commands_executed": executed_bootstrap_commands,
                    },
                )
            return (
                next_status,
                steps,
                {
                    "kind": classify_stop_reason_from_message(
                        message, stage="planning"
                    ),
                    "owner": owner,
                    "status": next_status,
                    "target_status": target_status,
                    "message": message,
                    "missing_files": missing_files,
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


def execute_subfeature_owner_chain(
    feature_dir: Path,
    *,
    planning_module,
    repo_root: Path,
    subfeature_module,
    target_path: str,
    stop_on_owner: list[str],
    review_note: Optional[str],
) -> tuple[str, list[dict[str, Any]], Optional[dict[str, Any]]]:
    steps: list[dict[str, Any]] = []
    subfeature_state = read_subfeature_state(feature_dir, subfeature_module)
    raw_metadata = subfeature_state["raw_metadata"]
    parent_feature_dir, _, subfeature_scope_context = subfeature_module.resolve_parent_feature(
        planning_module, str(raw_metadata["parent_feature_slug"])
    )
    subfeature_rows = subfeature_module.load_registry(parent_feature_dir)
    subfeature_row = subfeature_module.find_subfeature(
        subfeature_rows, str(raw_metadata["subfeature_id"])
    )
    if subfeature_row is None:
        raise RuntimeError(
            f"Subfeature '{raw_metadata['subfeature_id']}' is missing from the parent registry."
        )

    for _ in range(len(SUBFEATURE_STATUS_TO_OWNER) + 2):
        subfeature_state = read_subfeature_state(feature_dir, subfeature_module)
        raw_status = str(subfeature_state["raw_status"])

        if raw_status == "reviewed":
            return (
                raw_status,
                steps,
                {
                    "kind": "approval_boundary",
                    "owner": "approval",
                    "status": raw_status,
                    "target_status": raw_status,
                    "message": "Reached reviewed approval boundary for subfeature planning.",
                },
            )
        if raw_status == "finalized":
            return raw_status, steps, None
        if raw_status == "draft" and subfeature_state["discover_is_stub"]:
            return (
                raw_status,
                steps,
                {
                    "kind": "artifact_stub",
                    "owner": "discover",
                    "status": raw_status,
                    "target_status": raw_status,
                    "message": (
                        "Subfeature discovery is still the add-subfeature bootstrap stub; "
                        "run discover to author the real discovery packet."
                    ),
                },
            )

        if raw_status == "draft":
            owner, target_status = "assess", "impact_ready"
        elif raw_status == "impact_ready":
            owner, target_status = "design", "design_ready"
        elif raw_status == "design_ready":
            owner, target_status = "breakdown", "breakdown_ready"
        elif raw_status == "breakdown_ready":
            owner, target_status = "review-planning", "reviewed"
        else:
            raise RuntimeError(f"Unsupported subfeature status for owner-chain: '{raw_status}'.")

        if owner in stop_on_owner:
            return (
                raw_status,
                steps,
                {
                    "kind": "owner_stop",
                    "owner": owner,
                    "status": raw_status,
                    "target_status": target_status,
                    "message": (
                        f"Stopped before '{owner}' because it is configured in stop_on_owner."
                    ),
                },
            )

        transition_review_note = review_note if target_status == "reviewed" else None
        success, message = subfeature_module.update_subfeature_status(
            planning_module,
            parent_feature_dir,
            subfeature_row,
            target_status,
            subfeature_scope_context,
            force=False,
            review_note=transition_review_note,
        )
        next_raw_status = str(subfeature_module.read_metadata(str(feature_dir))["status"])
        advanced = next_raw_status != raw_status
        steps.append(
            {
                "owner": owner,
                "from_status": raw_status,
                "target_status": target_status,
                "success": bool(success),
                "advanced": advanced,
                "result_status": next_raw_status,
                "message": message,
            }
        )

        if not success or not advanced:
            missing_files = extract_missing_required_files(message)
            executed_bootstrap_commands = execute_safe_bootstrap(
                owner=owner,
                target_path=target_path,
                missing_files=missing_files,
                repo_root=repo_root,
            )
            if executed_bootstrap_commands:
                return (
                    next_raw_status,
                    steps,
                    {
                        "kind": "bootstrap_applied",
                        "owner": owner,
                        "status": next_raw_status,
                        "target_status": target_status,
                        "message": (
                            f"Applied safe bootstrap commands for '{owner}'. "
                            "Continue with the owner workflow."
                        ),
                        "missing_files": missing_files,
                        "bootstrap_commands_executed": executed_bootstrap_commands,
                    },
                )
            return (
                next_raw_status,
                steps,
                {
                    "kind": classify_stop_reason_from_message(message, stage="planning"),
                    "owner": owner,
                    "status": next_raw_status,
                    "target_status": target_status,
                    "message": message,
                    "missing_files": missing_files,
                },
            )

        if next_raw_status == "reviewed":
            return (
                next_raw_status,
                steps,
                {
                    "kind": "approval_boundary",
                    "owner": "approval",
                    "status": next_raw_status,
                    "target_status": next_raw_status,
                    "message": "Reached reviewed approval boundary for subfeature planning.",
                },
            )

    current_status = str(subfeature_module.read_metadata(str(feature_dir))["status"])
    return current_status, steps, {
        "kind": "safety_stop",
        "owner": "guide-planning",
        "status": current_status,
        "target_status": current_status,
        "message": "Stopped owner-chain due to unexpected subfeature loop safety boundary.",
    }


def evaluate_subfeature_approval_gate(
    *,
    feature_dir: Path,
    subfeature_state: dict[str, Any],
) -> dict[str, Any]:
    raw_metadata = dict(subfeature_state["raw_metadata"])
    raw_status = str(subfeature_state["raw_status"])
    approval_status = str(subfeature_state["approval_status"])
    gate_payload: dict[str, Any] = {
        "required": raw_status == "reviewed",
        "decision": "not_required",
        "reason": None,
        "planning_status": "planning_reviewed" if raw_status == "reviewed" else raw_status,
        "planning_updated_at": str(raw_metadata.get("updated_at") or ""),
        "approval_path": str(feature_dir / SUBFEATURE_METADATA_FILE),
    }
    if raw_status != "reviewed":
        return gate_payload

    gate_payload["approved_at"] = raw_metadata.get("approved_at")
    gate_payload["approval_note"] = raw_metadata.get("approval_note")
    if approval_status == "approved":
        gate_payload["decision"] = "approved"
        gate_payload["reason"] = "approval_valid"
    else:
        gate_payload["decision"] = "waiting_approval"
        gate_payload["reason"] = "approval_not_recorded"
    return gate_payload


def build_readiness_payload(
    *,
    next_owner: str,
    approval_gate: dict[str, Any],
    dirty_worktree_paths: list[str],
    owner_chain: Optional[dict[str, Any]],
) -> dict[str, Any]:
    blocked_by: list[str] = []
    approval_required = next_owner == "approval"
    commit_required = next_owner == "commit"
    approval_state = str(approval_gate.get("decision") or "").strip()

    if approval_required:
        blocked_by.append("approval_required")
        stop_reason = {
            "kind": "approval_required",
            "reason": approval_gate.get("reason"),
            "approval_path": approval_gate.get("approval_path"),
        }
    elif commit_required:
        blocked_by.append("commit_checkpoint")
        stop_reason = {
            "kind": "commit_checkpoint",
            "dirty_worktree_paths": dirty_worktree_paths,
        }
    else:
        stop_reason = normalize_stop_reason(
            owner_chain.get("stop_reason") if isinstance(owner_chain, dict) else None
        )
        if isinstance(stop_reason, dict) and str(stop_reason.get("kind") or "") == "bootstrap_applied":
            stop_reason = None
    if next_owner == "guide-planning":
        blocked_by.append("planning_resolution_required")

    return build_accelerator_readiness(
        next_owner=next_owner,
        automatable_owners=AUTOMATABLE_OWNERS,
        blocked_by=blocked_by,
        stop_reason=stop_reason,
        approval_gate={
            "required": bool(approval_gate.get("required", False)),
            "state": approval_state or ("waiting_approval" if approval_required else "not_required"),
            "reason": approval_gate.get("reason"),
            "approval_path": approval_gate.get("approval_path"),
        },
        commit_checkpoint={
            "required": commit_required,
            "state": "waiting_commit" if commit_required else "not_required",
        },
    )


def build_owner_handoff(
    *,
    target_id: str,
    target_path: str,
    next_owner: str,
    execute_owner_chain_enabled: bool,
    owner_chain: Optional[dict[str, Any]],
) -> Optional[dict[str, Any]]:
    if not execute_owner_chain_enabled or next_owner not in AUTOMATABLE_OWNERS:
        return None
    if not isinstance(owner_chain, dict) or not owner_chain.get("enabled"):
        return None

    stop_reason = normalize_stop_reason(owner_chain.get("stop_reason"))
    if stop_reason is None:
        return None

    reason_kind = str(stop_reason.get("kind") or "").strip()
    reason_owner = str(stop_reason.get("owner") or "").strip()
    if reason_kind in {"approval_boundary", "owner_stop"}:
        return None
    if reason_owner and reason_owner != next_owner:
        return None

    message = str(stop_reason.get("message") or "").strip()
    raw_missing_files = stop_reason.get("missing_files")
    if isinstance(raw_missing_files, list):
        missing_files = [
            item.strip()
            for item in raw_missing_files
            if isinstance(item, str) and item.strip()
        ]
    else:
        missing_files = extract_missing_required_files(message)
    bootstrap_commands = [
        display
        for _, display in bootstrap_specs_for_owner(
            owner=next_owner,
            target_path=target_path,
            missing_files=missing_files,
        )
    ]
    raw_executed_commands = stop_reason.get("bootstrap_commands_executed")
    bootstrap_commands_executed = (
        [
            item.strip()
            for item in raw_executed_commands
            if isinstance(item, str) and item.strip()
        ]
        if isinstance(raw_executed_commands, list)
        else []
    )
    if bootstrap_commands_executed:
        bootstrap_commands = []

    return {
        "should_invoke_skill": True,
        "owner": next_owner,
        "target_id": target_id,
        "target_path": target_path,
        "stop_reason": stop_reason,
        "missing_files": missing_files,
        "bootstrap_commands": bootstrap_commands,
        "bootstrap_commands_executed": bootstrap_commands_executed,
    }


def build_request_handoff_record(
    *,
    target_id: str,
    target_path: str,
    planning_status: str,
    next_owner: str,
    action: str,
    approval_gate: dict[str, Any],
    owner_chain: Optional[dict[str, Any]],
    owner_handoff: Optional[dict[str, Any]],
) -> RequestHandoffRecord:
    stop_reason = normalize_stop_reason(
        owner_chain.get("stop_reason") if isinstance(owner_chain, dict) else None
    )
    stop_reason_payload = stop_reason if isinstance(stop_reason, dict) else {}
    evidence_refs: list[str] = []
    if isinstance(owner_handoff, dict):
        missing_files = owner_handoff.get("missing_files")
        if isinstance(missing_files, list):
            evidence_refs.extend(
                item.strip()
                for item in missing_files
                if isinstance(item, str) and item.strip()
            )

    classification = "request_route"
    route_decision = "continue_planning"
    summary = None
    reason = None
    open_questions: list[str] = []

    if planning_status == "implemented":
        classification = "follow_on_delta"
        route_decision = "open_or_continue_subfeature"
        summary = (
            "Parent feature is already implemented. New requests on this feature should "
            "open or continue a subfeature instead of mutating the old packet in place."
        )
        reason = (
            "Implemented planning state is terminal for the parent packet; route back "
            "through guide-planning so follow-on work can land under add-subfeature."
        )
        open_questions.append("Which subfeature should own this follow-on change?")
    elif next_owner == "approval":
        classification = "approval_boundary"
        route_decision = "record_approval"
        summary = "Planning is review-ready and waiting for explicit approval."
        reason = str(approval_gate.get("reason") or "approval_not_recorded")
    elif next_owner == "commit":
        classification = "commit_checkpoint"
        route_decision = "commit_planning"
        summary = "Approved planning is waiting for a commit checkpoint before execution."
        reason = "dirty_worktree_paths_present"
    elif next_owner == "slice":
        classification = "execution_bootstrap"
        route_decision = "bootstrap_slice"
        summary = "Planning is approved and committed; execution bootstrap is next."
        reason = "planning_ready_for_execution"
    elif isinstance(owner_handoff, dict):
        classification = "owner_handoff"
        route_decision = f"invoke_{next_owner}"
        summary = f"Owner handoff is ready for '{next_owner}'."
        reason = str(stop_reason_payload.get("kind") or "owner_handoff")
    elif next_owner == "guide-planning":
        classification = "planning_resolution"
        route_decision = "resolve_planning_state"
        summary = "Planning state needs manual routing before automation can continue."
        reason = str(stop_reason_payload.get("kind") or "planning_resolution_required")
    else:
        classification = "request_route"
        route_decision = f"invoke_{next_owner}"
        summary = f"Continue with planning owner '{next_owner}'."
        reason = str(stop_reason_payload.get("kind") or action)

    return RequestHandoffRecord(
        request_id=f"autoplan:{target_id}",
        source_skill="autoplan",
        target_id=target_id,
        target_path=target_path,
        route_decision=route_decision,
        next_owner=next_owner,
        action=action,
        updated_at=utc_now(),
        classification=classification,
        planning_status=planning_status,
        summary=summary,
        reason=reason,
        evidence_refs=evidence_refs,
        open_questions=open_questions,
    )


def write_runtime_records(
    checkpoint_path: Path,
    event_log_path: Path,
    request_handoff_path: Path,
    *,
    target_id: str,
    target_path: str,
    planning_status: str,
    next_owner: str,
    action: str,
    learnings: list[dict[str, Any]],
    auto_decision_policy: str,
    approval_gate: dict[str, Any],
    owner_chain: Optional[dict[str, Any]],
    owner_handoff: Optional[dict[str, Any]],
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
    if owner_handoff is not None:
        event["owner_handoff_owner"] = owner_handoff.get("owner")
        event["owner_handoff_kind"] = owner_handoff.get("stop_reason", {}).get("kind")
    append_event(event_log_path, event)

    write_request_handoff(
        request_handoff_path,
        build_request_handoff_record(
            target_id=target_id,
            target_path=target_path,
            planning_status=planning_status,
            next_owner=next_owner,
            action=action,
            approval_gate=approval_gate,
            owner_chain=owner_chain,
            owner_handoff=owner_handoff,
        ),
    )

    checkpoint_payload: dict[str, Any] = {
        "target_id": target_id,
        "planning_status": planning_status,
        "next_owner": next_owner,
        "learning_ids": [item["id"] for item in learnings],
        "auto_decision_policy": auto_decision_policy,
    }
    if owner_chain is not None:
        checkpoint_payload["owner_chain"] = owner_chain
    if owner_handoff is not None:
        checkpoint_payload["owner_handoff"] = owner_handoff

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
    checkpoint_path, event_log_path, request_handoff_path, learnings_path = runtime_paths(
        repo_root
    )

    try:
        rows, feature, scope_context, metadata, prior_checkpoint = resolve_target(
            args, checkpoint_path, planning_module
        )
    except RuntimeError as exc:
        return emit_failure_response(
            args=args,
            event_log_path=event_log_path,
            reason_code="resolution_failed",
            message=str(exc),
            target_id=args.target or "",
        )

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
        return emit_failure_response(
            args=args,
            event_log_path=event_log_path,
            reason_code="invalid_configuration",
            message=str(exc),
            target_id=str(feature["feature"]),
        )

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
        return emit_failure_response(
            args=args,
            event_log_path=event_log_path,
            reason_code="invalid_configuration",
            message=str(exc),
            target_id=str(feature["feature"]),
        )

    target_id = str(feature["feature"])
    try:
        feature_dir = Path(planning_module.feature_dir_for_row(feature, scope_context=scope_context))
        subfeature_module = (
            load_module(ADD_SUBFEATURE_SCRIPT, "manage_subfeatures_for_autoplan")
            if is_subfeature_target(feature_dir)
            else None
        )
        planning_status = str(metadata["status"])
        owner_chain: Optional[dict[str, Any]] = None

        if execute_owner_chain_enabled:
            if subfeature_module is None:
                planning_status, steps, stop_reason = execute_feature_owner_chain(
                    rows,
                    feature,
                    planning_module=planning_module,
                    repo_root=repo_root,
                    scope_context=scope_context,
                    stop_on_owner=stop_on_owner,
                    review_note=review_note,
                )
            else:
                planning_status, steps, stop_reason = execute_subfeature_owner_chain(
                    feature_dir,
                    planning_module=planning_module,
                    repo_root=repo_root,
                    subfeature_module=subfeature_module,
                    target_path=str(feature["path"]),
                    stop_on_owner=stop_on_owner,
                    review_note=review_note,
                )
            owner_chain = {
                "enabled": True,
                "stop_on_owner": stop_on_owner,
                "steps": steps,
                "stop_reason": normalize_stop_reason(stop_reason),
            }

        metadata = planning_module.read_metadata(str(feature_dir))
        planning_status = str(metadata["status"])
        subfeature_state = (
            read_subfeature_state(feature_dir, subfeature_module)
            if subfeature_module is not None
            else None
        )
        approval_recorded = False

        if args.approve:
            approval_recorded = True
            if subfeature_module is None:
                if planning_status != "planning_reviewed":
                    return emit_failure_response(
                        args=args,
                        event_log_path=event_log_path,
                        reason_code="invalid_transition",
                        message=(
                            "Approval can be recorded only when planning status is "
                            f"'planning_reviewed'. Current status: '{planning_status}'."
                        ),
                        target_id=target_id,
                        next_owner="approval",
                    )
                write_planning_approval_record(
                    target_id=target_id,
                    target_path=str(feature["path"]),
                    target_dir=feature_dir,
                    planning_metadata=metadata,
                    approval_note=args.approval_note,
                )
            else:
                assert subfeature_state is not None
                if str(subfeature_state["raw_status"]) != "reviewed":
                    return emit_failure_response(
                        args=args,
                        event_log_path=event_log_path,
                        reason_code="invalid_transition",
                        message=(
                            "Approval can be recorded only when subfeature status is "
                            f"'reviewed'. Current status: '{subfeature_state['raw_status']}'."
                        ),
                        target_id=target_id,
                        next_owner="approval",
                    )
                raw_metadata = subfeature_state["raw_metadata"]
                parent_feature_dir, _, subfeature_scope_context = subfeature_module.resolve_parent_feature(
                    planning_module, str(raw_metadata["parent_feature_slug"])
                )
                subfeature_rows = subfeature_module.load_registry(parent_feature_dir)
                subfeature_row = subfeature_module.find_subfeature(
                    subfeature_rows, str(raw_metadata["subfeature_id"])
                )
                if subfeature_row is None:
                    raise RuntimeError(
                        f"Subfeature '{raw_metadata['subfeature_id']}' is missing from the parent registry."
                    )
                success, message = subfeature_module.update_subfeature_approval(
                    planning_module,
                    parent_feature_dir,
                    subfeature_row,
                    subfeature_scope_context,
                    approval_note=args.approval_note,
                )
                if not success:
                    raise RuntimeError(message)

            metadata = planning_module.read_metadata(str(feature_dir))
            planning_status = str(metadata["status"])
            subfeature_state = (
                read_subfeature_state(feature_dir, subfeature_module)
                if subfeature_module is not None
                else None
            )

        approval_gate = (
            evaluate_planning_approval_gate(
                target_id=target_id,
                target_path=str(feature["path"]),
                target_dir=feature_dir,
                planning_metadata=metadata,
            )
            if subfeature_module is None
            else evaluate_subfeature_approval_gate(
                feature_dir=feature_dir,
                subfeature_state=subfeature_state,
            )
        )
        dirty_worktree_paths = read_dirty_worktree_paths(repo_root, feature_dir)

        if subfeature_state is not None and str(subfeature_state["raw_status"]) == "reviewed":
            if str(approval_gate.get("decision") or "") != "approved":
                next_owner, action = "approval", "approval_required"
            elif dirty_worktree_paths or approval_recorded:
                next_owner, action = "commit", "commit_planning"
            else:
                next_owner, action = "slice", "bootstrap_slice"
        elif planning_status == "planning_reviewed":
            if str(approval_gate.get("decision") or "") != "approved":
                next_owner, action = "approval", "approval_required"
            elif dirty_worktree_paths or approval_recorded:
                next_owner, action = "commit", "commit_planning"
            else:
                next_owner, action = "slice", "bootstrap_slice"
        else:
            next_owner, action = (
                owner_for_subfeature_state(subfeature_state)
                if subfeature_state is not None
                else owner_for_status(planning_status)
            )

        owner_handoff = build_owner_handoff(
            target_id=target_id,
            target_path=str(feature["path"]),
            next_owner=next_owner,
            execute_owner_chain_enabled=execute_owner_chain_enabled,
            owner_chain=owner_chain,
        )
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
            request_handoff_path,
            target_id=target_id,
            target_path=str(feature["path"]),
            planning_status=planning_status,
            next_owner=next_owner,
            action=action,
            learnings=learnings,
            auto_decision_policy=auto_decision_policy,
            approval_gate=approval_gate,
            owner_chain=owner_chain,
            owner_handoff=owner_handoff,
        )

        readiness = build_readiness_payload(
            next_owner=next_owner,
            approval_gate=approval_gate,
            dirty_worktree_paths=dirty_worktree_paths,
            owner_chain=owner_chain,
        )
        failure_context = (
            record_failure_for_stop_reason(
                event_log_path,
                skill="autoplan",
                stage="planning",
                stop_reason=owner_chain.get("stop_reason") if owner_chain is not None else None,
                target_id=target_id,
                next_owner=next_owner,
                evidence_refs=(
                    owner_handoff.get("missing_files")
                    if isinstance(owner_handoff, dict)
                    else None
                ),
            )
            if (
                owner_chain is not None
                and str(
                    (owner_chain.get("stop_reason") or {}).get("kind")
                    if isinstance(owner_chain, dict)
                    else ""
                )
                != "bootstrap_applied"
            )
            else None
        )

        payload = {
            "run_id": "autoplan-active",
            "target_id": target_id,
            "target_path": str(feature["path"]),
            "target_kind": "subfeature" if subfeature_state is not None else "feature",
            "planning_status": planning_status,
            "next_owner": next_owner,
            "action": action,
            "auto_decision_policy": auto_decision_policy,
            "execute_owner_chain": execute_owner_chain_enabled,
            "owner_chain": owner_chain,
            "owner_handoff": owner_handoff,
            "checkpoint_path": str(checkpoint_path),
            "event_log_path": str(event_log_path),
            "request_handoff_path": str(request_handoff_path),
            "failure_context": (
                failure_context.to_dict() if failure_context is not None else None
            ),
            "learnings": learnings,
            "checkpoint_stale_reason": checkpoint_stale_reason,
            "approval_gate": approval_gate,
            "dirty_worktree_paths": dirty_worktree_paths,
            "readiness": readiness,
        }
        if subfeature_state is not None:
            payload["subfeature_status"] = str(subfeature_state["raw_status"])
            payload["subfeature_approval_status"] = str(subfeature_state["approval_status"])
            payload["subfeature_discover_stub"] = bool(subfeature_state["discover_is_stub"])
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(
                "\n".join(
                    item
                    for item in [
                        f"Target: {target_id}",
                        (
                            f"Subfeature status: {subfeature_state['raw_status']}"
                            if subfeature_state is not None
                            else None
                        ),
                        f"Planning status: {planning_status}",
                        f"Next owner: {next_owner}",
                        f"Action: {action}",
                    ]
                    if item is not None
                )
            )
        return 0
    except RuntimeError as exc:
        return emit_failure_response(
            args=args,
            event_log_path=event_log_path,
            reason_code="runtime_error",
            message=str(exc),
            target_id=target_id,
        )


if __name__ == "__main__":
    raise SystemExit(main())
