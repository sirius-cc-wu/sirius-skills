#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
SKILLS_DIR = SKILL_DIR.parent
REPO_LIB_DIR = SKILLS_DIR.parent / "lib"
SKILL_LIB_DIR = SKILL_DIR / "lib"
GUIDE_EXECUTION_SCRIPT = (
    SKILLS_DIR / "guide-execution" / "scripts" / "manage_execution.py"
)

if REPO_LIB_DIR.is_dir() and str(REPO_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(REPO_LIB_DIR))
if SKILL_LIB_DIR.is_dir() and str(SKILL_LIB_DIR) not in sys.path:
    sys.path.append(str(SKILL_LIB_DIR))

from workflow_runtime import (  # noqa: E402
    CheckpointRecord,
    HandoffPayload,
    append_event,
    load_checkpoint,
    mark_checkpoint_stale,
    query_learnings,
    read_handoff_payload,
    write_checkpoint,
)


DEFAULT_RUNTIME_DIR = Path(".skills/runtime")
DEFAULT_LEARNINGS_PATH = Path(".skills/learnings.jsonl")


@dataclass
class SliceRoute:
    slice_id: str
    slice_path: str
    slice_status: str
    next_owner: str
    action: str
    target_type: str
    target_id: str
    handoff_payload: Dict[str, Any]


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
        description="Resume one active execution slice with checkpointed runtime context."
    )
    parser.add_argument(
        "selector",
        nargs="?",
        help="Optional execution slice id or slice path.",
    )
    parser.add_argument(
        "--handoff",
        default=None,
        help="Optional path to a handoff payload JSON file emitted by ship.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from the previously written ship-slice checkpoint.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Render machine-readable output.",
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


def git_dirty_paths(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.rstrip() for line in result.stdout.splitlines() if line.strip()]


def runtime_paths(repo_root: Path) -> tuple[Path, Path, Path]:
    runtime_dir = repo_root / DEFAULT_RUNTIME_DIR
    checkpoint_path = runtime_dir / "checkpoints" / "ship-slice-active.json"
    event_log_path = runtime_dir / "execution-log.jsonl"
    learnings_path = repo_root / DEFAULT_LEARNINGS_PATH
    return checkpoint_path, event_log_path, learnings_path


def inspect_slice_artifacts(slice_row: Dict[str, Any], execution_module, scope_context) -> Dict[str, bool]:
    slice_path = execution_module.slice_path_for_row(slice_row, scope_context=scope_context)
    return execution_module.validate_slice(slice_row, scope_context=scope_context)[2] | {
        "slice_path_exists": slice_path.is_dir()
    }


def build_route(
    slice_row: Dict[str, Any],
    *,
    target_type: str,
    target_id: str,
    repo_root: Path,
) -> SliceRoute:
    status = str(slice_row["status"])
    dirty_paths = git_dirty_paths(repo_root)
    if status == "draft":
        next_owner = "brief"
        action = "create_or_update_brief"
    elif status == "brief_ready":
        next_owner = "blueprint"
        action = "create_or_update_blueprint"
    elif status in {"blueprint_ready", "execution_ready"}:
        next_owner = "implementation"
        action = "implement_validate_review_and_close"
    elif status == "closed" and dirty_paths:
        next_owner = "commit"
        action = "commit_completed_slice"
    elif status == "closed":
        next_owner = "none"
        action = "completed"
    else:
        next_owner = "guide-execution"
        action = "resolve_active_slice"

    handoff_payload = HandoffPayload(
        target_type=target_type,
        target_id=target_id,
        planned_slice_id=str(slice_row["id"]),
        execution_slice_id=str(slice_row["id"]),
        execution_slice_path=str(slice_row["path"]),
        slice_status=status,
        next_owner=next_owner,
        action="resume_active_slice",
    ).to_dict()
    return SliceRoute(
        slice_id=str(slice_row["id"]),
        slice_path=str(slice_row["path"]),
        slice_status=status,
        next_owner=next_owner,
        action=action,
        target_type=target_type,
        target_id=target_id,
        handoff_payload=handoff_payload,
    )


def resolve_input_payload(
    args: argparse.Namespace,
    checkpoint_path: Path,
) -> tuple[Optional[HandoffPayload], Optional[CheckpointRecord]]:
    handoff = read_handoff_payload(Path(args.handoff)) if args.handoff else None
    checkpoint = load_checkpoint(checkpoint_path) if args.resume and checkpoint_path.exists() else None
    return handoff, checkpoint


def resolve_slice(
    args: argparse.Namespace,
    execution_module,
    checkpoint_path: Path,
) -> tuple[Dict[str, Any], str, str, Optional[CheckpointRecord]]:
    scope_context = execution_module.resolve_execution_scope_context()
    rows = execution_module.parse_registry(scope_context=scope_context)
    handoff, checkpoint = resolve_input_payload(args, checkpoint_path)

    selector = args.selector
    target_type = "slice"
    target_id = selector or ""
    if handoff is not None:
        selector = handoff.execution_slice_id
        target_type = handoff.target_type
        target_id = handoff.target_id
    elif checkpoint is not None and not selector:
        payload = dict(checkpoint.payload)
        selector = str(payload.get("slice_id") or payload.get("execution_slice_id") or "")
        target_type = str(payload.get("target_type") or "slice")
        target_id = str(payload.get("target_id") or selector or "")

    if selector:
        row = execution_module.resolve_slice(rows, selector)
    else:
        row = execution_module.find_active_slice(rows)
        if row is not None:
            selector = str(row["id"])
            target_id = selector
    if row is None:
        raise RuntimeError("No active or requested execution slice could be resolved.")
    if not target_id:
        target_id = str(row["id"])
    return row, target_type, target_id, checkpoint


def write_runtime_records(
    *,
    checkpoint_path: Path,
    event_log_path: Path,
    route: SliceRoute,
    dirty_paths: list[str],
    learnings: list[dict[str, Any]],
) -> None:
    event = {
        "timestamp": utc_now(),
        "skill": "ship-slice",
        "slice_id": route.slice_id,
        "slice_status": route.slice_status,
        "next_owner": route.next_owner,
        "action": route.action,
        "target_id": route.target_id,
    }
    append_event(event_log_path, event)
    write_checkpoint(
        checkpoint_path,
        CheckpointRecord(
            run_id="ship-slice-active",
            state=route.action,
            payload={
                "slice_id": route.slice_id,
                "slice_path": route.slice_path,
                "slice_status": route.slice_status,
                "target_type": route.target_type,
                "target_id": route.target_id,
                "next_owner": route.next_owner,
                "dirty_worktree_paths": list(dirty_paths),
                "handoff_payload": dict(route.handoff_payload),
                "learning_ids": [item["id"] for item in learnings],
            },
        ),
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    execution_module = load_module(GUIDE_EXECUTION_SCRIPT, "manage_execution_for_ship_slice")
    repo_root = git_repo_root()
    checkpoint_path, event_log_path, learnings_path = runtime_paths(repo_root)

    try:
        slice_row, target_type, target_id, prior_checkpoint = resolve_slice(
            args,
            execution_module,
            checkpoint_path,
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    route = build_route(
        slice_row,
        target_type=target_type,
        target_id=target_id,
        repo_root=repo_root,
    )

    checkpoint_stale_reason = None
    if prior_checkpoint is not None:
        prior_slice_status = str(prior_checkpoint.payload.get("slice_status") or "")
        if prior_slice_status and prior_slice_status != route.slice_status:
            checkpoint_stale_reason = (
                f"slice status changed from {prior_slice_status} to {route.slice_status}"
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
    dirty_paths = git_dirty_paths(repo_root)
    write_runtime_records(
        checkpoint_path=checkpoint_path,
        event_log_path=event_log_path,
        route=route,
        dirty_paths=dirty_paths,
        learnings=learnings,
    )

    payload = {
        "run_id": "ship-slice-active",
        "slice_id": route.slice_id,
        "slice_path": route.slice_path,
        "slice_status": route.slice_status,
        "next_owner": route.next_owner,
        "action": route.action,
        "target_type": route.target_type,
        "target_id": route.target_id,
        "handoff_payload": route.handoff_payload,
        "checkpoint_path": str(checkpoint_path),
        "event_log_path": str(event_log_path),
        "dirty_worktree_paths": dirty_paths,
        "learnings": learnings,
        "checkpoint_stale_reason": checkpoint_stale_reason,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            "\n".join(
                [
                    f"Slice: {route.slice_id}",
                    f"Status: {route.slice_status}",
                    f"Next owner: {route.next_owner}",
                    f"Action: {route.action}",
                ]
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
