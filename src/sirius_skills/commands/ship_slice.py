#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import shlex
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Sequence


COMMAND_DIR = Path(__file__).resolve().parent
GUIDE_EXECUTION_SCRIPT = COMMAND_DIR / "manage_execution.py"
CLOSE_SLICE_SCRIPT = COMMAND_DIR / "close_slice.py"


from sirius_skills.lib.workflow_runtime import (  # noqa: E402
    CheckpointRecord,
    HandoffPayload,
    append_event,
    build_accelerator_readiness,
    classify_stop_reason_from_message,
    detect_scope_spillover,
    is_failure_reason,
    load_checkpoint,
    mark_checkpoint_stale,
    normalize_stop_reason,
    query_learnings,
    read_handoff_payload,
    record_failure,
    record_failure_for_stop_reason,
    render_failure_summary,
    snapshot_dirty_worktree as runtime_snapshot_dirty_worktree,
    write_checkpoint,
)


DEFAULT_RUNTIME_DIR = Path(".skills/runtime")
DEFAULT_LEARNINGS_PATH = Path(".skills/learnings.jsonl")

CHAIN_TARGET_STATUS_BY_STATE = {
    "draft": "blueprint_ready",
    "brief_ready": "blueprint_ready",
    "blueprint_ready": "execution_ready",
}

VALID_STOP_OWNERS = {
    "brief",
    "blueprint",
    "implementation",
    "review-execution",
    "commit",
    "guide-execution",
    "none",
}
AUTOMATABLE_OWNERS = {"brief", "blueprint", "implementation"}
VALID_CONTINUATION_POLICY_BOUNDARIES = {
    "review_boundary",
    "commit_checkpoint",
}
VALID_CONTINUATION_POLICY_ACTIONS = {"stop", "continue"}
VALID_CONTINUATION_POLICY_SOURCES = {"default", "config"}


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


@dataclass
class WorktreeOwnership:
    baseline_from_checkpoint: bool
    baseline_dirty_paths: list[str]
    current_dirty_paths: list[str]
    owned_dirty_paths: list[str]
    unowned_dirty_paths: list[str]
    owned_file_conflict_paths: list[str]
    baseline_snapshot: Dict[str, str]
    current_snapshot: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TerminalAutomationConfig:
    auto_format: bool = False
    auto_close: bool = False
    auto_commit: bool = False
    format_command: Optional[list[str]] = None


@dataclass
class TerminalAutomationResult:
    enabled: bool = False
    attempted: bool = False
    format_applied: bool = False
    close_applied: bool = False
    commit_applied: bool = False
    formatted_paths: list[str] = field(default_factory=list)
    committed_paths: list[str] = field(default_factory=list)
    commit_message: Optional[str] = None
    stop_reason: Optional[dict[str, Any]] = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContinuationPolicyConfig:
    review_boundary_action: str = "stop"
    review_boundary_source: str = "default"
    commit_checkpoint_action: str = "stop"
    commit_checkpoint_source: str = "default"

    def decision_for(self, boundary: str) -> Dict[str, str]:
        if boundary == "review_boundary":
            return {
                "boundary": "review_boundary",
                "policy_action": self.review_boundary_action,
                "policy_source": self.review_boundary_source,
            }
        if boundary == "commit_checkpoint":
            return {
                "boundary": "commit_checkpoint",
                "policy_action": self.commit_checkpoint_action,
                "policy_source": self.commit_checkpoint_source,
            }
        raise RuntimeError(f"Unsupported continuation-policy boundary: {boundary}")


def load_module(script_path: Path, name: str):
    if script_path.name == "manage_execution.py":
        from sirius_skills.commands import manage_execution
        return manage_execution
    raise RuntimeError(f"Unknown script path: {script_path}")


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
    parser.set_defaults(execute_owner_chain=None)
    parser.add_argument(
        "--execute-owner-chain",
        dest="execute_owner_chain",
        action="store_true",
        help=(
            "Execute one-slice owner chain through brief/blueprint/implementation routing "
            "until a review or checkpoint boundary."
        ),
    )
    parser.add_argument(
        "--no-execute-owner-chain",
        dest="execute_owner_chain",
        action="store_false",
        help="Disable owner-chain execution even when enabled in execution config.",
    )
    parser.add_argument(
        "--stop-on-owner",
        action="append",
        default=None,
        help="Owner boundary to stop before executing (repeatable).",
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


def emit_failure_response(
    *,
    args: argparse.Namespace,
    event_log_path: Path,
    reason_code: str,
    message: str,
    target_id: str = "",
    slice_id: str = "",
    next_owner: str = "",
    owner: str = "",
    evidence_refs: Sequence[str] | None = None,
) -> int:
    context = record_failure(
        event_log_path,
        skill="ship-slice",
        stage="execution",
        reason_code=reason_code,
        message=message,
        target_id=target_id,
        slice_id=slice_id,
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
                    "skill": "ship-slice",
                    "slice_id": slice_id,
                    "stage": "execution",
                    "target_id": target_id,
                },
                indent=2,
                sort_keys=True,
            )
        )
    print(render_failure_summary(context), file=sys.stderr)
    return 2


def snapshot_dirty_worktree(repo_root: Path) -> tuple[list[str], Dict[str, str]]:
    return runtime_snapshot_dirty_worktree(
        repo_root,
        ignored_prefixes=(".skills/runtime/",),
    )


def compute_worktree_ownership_from_baseline(
    repo_root: Path,
    baseline_snapshot: Dict[str, str],
    *,
    baseline_from_checkpoint: bool,
) -> tuple[WorktreeOwnership, list[str]]:
    dirty_lines, current_snapshot = snapshot_dirty_worktree(repo_root)
    current_paths = sorted(current_snapshot)

    owned_dirty_paths: list[str] = []
    unowned_dirty_paths: list[str] = []
    owned_file_conflict_paths: list[str] = []
    for path in current_paths:
        baseline_digest = baseline_snapshot.get(path)
        current_digest = current_snapshot[path]
        if baseline_digest is None:
            owned_dirty_paths.append(path)
        elif baseline_digest == current_digest:
            unowned_dirty_paths.append(path)
        else:
            owned_file_conflict_paths.append(path)

    ownership = WorktreeOwnership(
        baseline_from_checkpoint=baseline_from_checkpoint,
        baseline_dirty_paths=sorted(baseline_snapshot),
        current_dirty_paths=current_paths,
        owned_dirty_paths=owned_dirty_paths,
        unowned_dirty_paths=unowned_dirty_paths,
        owned_file_conflict_paths=owned_file_conflict_paths,
        baseline_snapshot=dict(baseline_snapshot),
        current_snapshot=current_snapshot,
    )
    return ownership, dirty_lines


def compute_worktree_ownership(
    repo_root: Path,
    prior_checkpoint: Optional[CheckpointRecord],
) -> tuple[WorktreeOwnership, list[str]]:
    dirty_lines, current_snapshot = snapshot_dirty_worktree(repo_root)

    baseline_snapshot: Dict[str, str] = {}
    baseline_from_checkpoint = False
    if prior_checkpoint is not None:
        raw_ownership = prior_checkpoint.payload.get("worktree_ownership")
        if isinstance(raw_ownership, dict):
            raw_snapshot = raw_ownership.get("baseline_snapshot")
            if isinstance(raw_snapshot, dict):
                baseline_snapshot = {
                    str(path): str(digest)
                    for path, digest in raw_snapshot.items()
                    if str(path).strip()
                }
                baseline_from_checkpoint = True

    if not baseline_snapshot:
        baseline_snapshot = dict(current_snapshot)

    ownership, _ = compute_worktree_ownership_from_baseline(
        repo_root,
        baseline_snapshot,
        baseline_from_checkpoint=baseline_from_checkpoint,
    )
    ownership.current_snapshot = current_snapshot
    return ownership, dirty_lines


def parse_command_config(raw_value: object, field_name: str) -> Optional[list[str]]:
    if raw_value is None:
        return None
    if isinstance(raw_value, str):
        command = [part for part in shlex.split(raw_value) if part]
    elif isinstance(raw_value, list):
        command = []
        for item in raw_value:
            if not isinstance(item, str) or not item.strip():
                raise RuntimeError(f"ship-slice {field_name} entries must be non-empty strings.")
            command.append(item.strip())
    else:
        raise RuntimeError(f"ship-slice {field_name} must be a string or list of strings.")
    if not command:
        raise RuntimeError(f"ship-slice {field_name} cannot be empty.")
    return command


def parse_terminal_automation_config(raw_config: object) -> TerminalAutomationConfig:
    if not isinstance(raw_config, dict):
        return TerminalAutomationConfig()

    format_command = parse_command_config(raw_config.get("format_command"), "format_command")
    config = TerminalAutomationConfig(
        auto_format=bool(raw_config.get("auto_format", False)),
        auto_close=bool(raw_config.get("auto_close", False)),
        auto_commit=bool(raw_config.get("auto_commit", False)),
        format_command=format_command,
    )
    if config.auto_commit and not config.auto_close:
        raise RuntimeError("ship-slice auto_commit requires auto_close.")
    if config.auto_format and config.format_command is None:
        raise RuntimeError("ship-slice auto_format requires format_command.")
    return config


def parse_continuation_policy_action(raw_value: object, *, boundary: str) -> str:
    if not isinstance(raw_value, str):
        raise RuntimeError(
            "ship-slice continuation_policy values must be strings "
            f"('stop' or 'continue'); got {type(raw_value).__name__} for '{boundary}'."
        )
    normalized = raw_value.strip().lower().replace("-", "_")
    if normalized not in VALID_CONTINUATION_POLICY_ACTIONS:
        raise RuntimeError(
            "Invalid ship-slice continuation_policy value "
            f"'{raw_value}' for '{boundary}'. "
            f"Valid values: {sorted(VALID_CONTINUATION_POLICY_ACTIONS)}"
        )
    return normalized


def parse_continuation_policy_config(raw_config: object) -> ContinuationPolicyConfig:
    if not isinstance(raw_config, dict):
        return ContinuationPolicyConfig()

    raw_policy = raw_config.get("continuation_policy")
    if raw_policy is None:
        return ContinuationPolicyConfig()
    if not isinstance(raw_policy, dict):
        raise RuntimeError("ship-slice continuation_policy must be a JSON object.")

    config = ContinuationPolicyConfig()
    for raw_key, raw_value in raw_policy.items():
        normalized_key = normalize_stop_reason({"kind": raw_key})
        if normalized_key is None:
            raise RuntimeError(
                f"Invalid ship-slice continuation_policy boundary '{raw_key}'."
            )
        boundary = str(normalized_key.get("kind"))
        if boundary not in VALID_CONTINUATION_POLICY_BOUNDARIES:
            raise RuntimeError(
                "Invalid ship-slice continuation_policy boundary "
                f"'{raw_key}'. Valid boundaries: {sorted(VALID_CONTINUATION_POLICY_BOUNDARIES)}"
            )
        action = parse_continuation_policy_action(raw_value, boundary=boundary)
        if boundary == "review_boundary":
            config.review_boundary_action = action
            config.review_boundary_source = "config"
        elif boundary == "commit_checkpoint":
            config.commit_checkpoint_action = action
            config.commit_checkpoint_source = "config"

    return config


def synthesize_commit_message(
    *,
    slice_id: str,
    execution_module,
    scope_context,
) -> str:
    conventions = execution_module.load_conventions_config(
        required=False, scope_context=scope_context
    )
    summary = f"Complete {slice_id}"
    scope = "ship-slice"
    issue_id = execution_module.infer_id_from_branch(conventions) or slice_id
    template = conventions.get("commit_format")
    if template:
        return template.format_map(
            {
                "ID": issue_id,
                "id": issue_id,
                "scope": scope,
                "summary": summary,
            }
        )
    return f"{scope}: {summary}"


def _manual_route_from(
    route: SliceRoute,
    *,
    next_owner: str,
    action: str,
) -> SliceRoute:
    return SliceRoute(
        slice_id=route.slice_id,
        slice_path=route.slice_path,
        slice_status=route.slice_status,
        next_owner=next_owner,
        action=action,
        target_type=route.target_type,
        target_id=route.target_id,
        handoff_payload=dict(route.handoff_payload),
    )


def run_command(
    command: Sequence[str],
    *,
    cwd: Path,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )


def run_formatter(
    *,
    repo_root: Path,
    config: TerminalAutomationConfig,
    ownership: WorktreeOwnership,
) -> tuple[WorktreeOwnership, list[str], Optional[dict[str, Any]], bool]:
    if not config.auto_format or not ownership.owned_dirty_paths:
        return ownership, [f"?? {path}" for path in ownership.current_dirty_paths], None, False

    before_snapshot = dict(ownership.current_snapshot)
    result = run_command(
        [*(config.format_command or []), *ownership.owned_dirty_paths],
        cwd=repo_root,
    )
    updated_ownership, dirty_lines = compute_worktree_ownership_from_baseline(
        repo_root,
        ownership.baseline_snapshot,
        baseline_from_checkpoint=ownership.baseline_from_checkpoint,
    )
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "Formatter command failed.").strip()
        return (
            updated_ownership,
            dirty_lines,
            {"kind": "formatter_failed", "message": message},
            False,
        )

    spillover = detect_scope_spillover(
        before_snapshot,
        updated_ownership.current_snapshot,
        allowed_paths=ownership.owned_dirty_paths,
    )
    if spillover:
        return (
            updated_ownership,
            dirty_lines,
            {"kind": "formatter_spillover", "paths": spillover},
            False,
        )
    return updated_ownership, dirty_lines, None, True


def run_close_slice(
    *,
    repo_root: Path,
    slice_id: str,
) -> tuple[bool, str]:
    result = run_command(
        [
            sys.executable,
            "-m",
            "sirius_skills.cli",
            "close-slice",
            "--slice",
            slice_id,
            "--json",
        ],
        cwd=repo_root,
    )
    message = (result.stdout or result.stderr).strip()
    if result.returncode != 0:
        return False, message or f"Unable to close slice {slice_id}."
    return True, message


def run_owned_commit(
    *,
    repo_root: Path,
    owned_paths: Sequence[str],
    commit_message: str,
) -> tuple[bool, str]:
    if not owned_paths:
        return True, "No owned dirty paths remain to commit."

    stage = run_command(["git", "add", "--all", "--", *owned_paths], cwd=repo_root)
    if stage.returncode != 0:
        return False, (stage.stderr or stage.stdout or "Unable to stage owned files.").strip()

    commit = run_command(["git", "commit", "-m", commit_message], cwd=repo_root)
    if commit.returncode != 0:
        return False, (commit.stderr or commit.stdout or "Owned commit failed.").strip()
    return True, (commit.stdout or commit.stderr).strip()


def apply_terminal_automation(
    *,
    route: SliceRoute,
    rows: list[dict[str, Any]],
    slice_row: Dict[str, Any],
    execution_module,
    scope_context,
    repo_root: Path,
    worktree_ownership: WorktreeOwnership,
    dirty_paths: list[str],
    terminal_config: TerminalAutomationConfig,
    continuation_policy: ContinuationPolicyConfig,
) -> tuple[
    list[dict[str, Any]],
    Dict[str, Any],
    SliceRoute,
    WorktreeOwnership,
    list[str],
    TerminalAutomationResult,
]:
    result = TerminalAutomationResult(
        enabled=bool(
            terminal_config.auto_format
            or terminal_config.auto_close
            or terminal_config.auto_commit
        )
    )
    dirty_lines = [f"?? {path}" for path in worktree_ownership.current_dirty_paths]
    if not result.enabled:
        return rows, slice_row, route, worktree_ownership, dirty_lines, result

    updated_rows = rows
    updated_slice_row = slice_row
    updated_route = route
    updated_ownership = worktree_ownership
    dirty_lines = list(dirty_paths)
    review_policy = continuation_policy.decision_for("review_boundary")
    should_auto_close = (
        route.next_owner == "review-execution"
        and terminal_config.auto_close
        and review_policy["policy_action"] == "continue"
    )
    if (
        route.next_owner == "review-execution"
        and terminal_config.auto_close
        and review_policy["policy_action"] == "stop"
    ):
        result.notes.append(
            "Skipped auto_close because continuation_policy.review_boundary is 'stop'."
        )

    if should_auto_close:
        result.attempted = True
        if terminal_config.auto_format:
            updated_ownership, dirty_lines, stop_reason, format_applied = run_formatter(
                repo_root=repo_root,
                config=terminal_config,
                ownership=updated_ownership,
            )
            if format_applied:
                result.format_applied = True
                result.formatted_paths = list(updated_ownership.owned_dirty_paths)
            if stop_reason is not None:
                result.stop_reason = stop_reason
                updated_route = _manual_route_from(
                    route,
                    next_owner="guide-execution",
                    action="resolve_formatter_scope",
                )
                return (
                    updated_rows,
                    updated_slice_row,
                    updated_route,
                    updated_ownership,
                    dirty_lines,
                    result,
                )

        close_ok, close_message = run_close_slice(repo_root=repo_root, slice_id=route.slice_id)
        result.notes.append(close_message)
        if not close_ok:
            result.stop_reason = {
                "kind": classify_stop_reason_from_message(close_message, stage="execution"),
                "message": close_message,
            }
            updated_route = _manual_route_from(
                route,
                next_owner="close-slice",
                action="close_completed_slice",
            )
            return (
                updated_rows,
                updated_slice_row,
                updated_route,
                updated_ownership,
                dirty_lines,
                result,
            )

        result.close_applied = True
        updated_rows = execution_module.parse_registry(scope_context=scope_context)
        refreshed_slice = execution_module.resolve_slice(updated_rows, route.slice_id)
        if refreshed_slice is None:
            raise RuntimeError(f"Closed slice disappeared from registry: {route.slice_id}")
        updated_slice_row = refreshed_slice
        updated_ownership, dirty_lines = compute_worktree_ownership_from_baseline(
            repo_root,
            updated_ownership.baseline_snapshot,
            baseline_from_checkpoint=updated_ownership.baseline_from_checkpoint,
        )
        updated_route = build_route(
            updated_slice_row,
            target_type=route.target_type,
            target_id=route.target_id,
            repo_root=repo_root,
            worktree_ownership=updated_ownership,
            owner_chain_mode=False,
        )

    if updated_route.next_owner == "commit" and terminal_config.auto_commit:
        commit_policy = continuation_policy.decision_for("commit_checkpoint")
        if commit_policy["policy_action"] != "continue":
            result.notes.append(
                "Skipped auto_commit because continuation_policy.commit_checkpoint is 'stop'."
            )
            return (
                updated_rows,
                updated_slice_row,
                updated_route,
                updated_ownership,
                dirty_lines,
                result,
            )
        result.attempted = True
        commit_message = synthesize_commit_message(
            slice_id=route.slice_id,
            execution_module=execution_module,
            scope_context=scope_context,
        )
        result.commit_message = commit_message
        commit_ok, commit_message_output = run_owned_commit(
            repo_root=repo_root,
            owned_paths=updated_ownership.owned_dirty_paths,
            commit_message=commit_message,
        )
        result.notes.append(commit_message_output)
        if not commit_ok:
            result.stop_reason = {
                "kind": "commit_failed",
                "message": commit_message_output,
            }
            updated_route = _manual_route_from(
                updated_route,
                next_owner="commit",
                action="commit_completed_slice",
            )
            return (
                updated_rows,
                updated_slice_row,
                updated_route,
                updated_ownership,
                dirty_lines,
                result,
            )

        result.commit_applied = True
        result.committed_paths = list(updated_ownership.owned_dirty_paths)
        updated_ownership, dirty_lines = compute_worktree_ownership_from_baseline(
            repo_root,
            updated_ownership.baseline_snapshot,
            baseline_from_checkpoint=updated_ownership.baseline_from_checkpoint,
        )
        updated_route = build_route(
            updated_slice_row,
            target_type=route.target_type,
            target_id=route.target_id,
            repo_root=repo_root,
            worktree_ownership=updated_ownership,
            owner_chain_mode=False,
        )

    return (
        updated_rows,
        updated_slice_row,
        updated_route,
        updated_ownership,
        dirty_lines,
        result,
    )


def runtime_paths(repo_root: Path) -> tuple[Path, Path, Path]:
    runtime_dir = repo_root / DEFAULT_RUNTIME_DIR
    checkpoint_path = runtime_dir / "checkpoints" / "ship-slice-active.json"
    event_log_path = runtime_dir / "execution-log.jsonl"
    learnings_path = repo_root / DEFAULT_LEARNINGS_PATH
    return checkpoint_path, event_log_path, learnings_path


def inspect_slice_artifacts(slice_row: Dict[str, Any], execution_module, scope_context) -> Dict[str, bool]:
    slice_path = Path(execution_module.slice_path_for_row(slice_row, scope_context=scope_context))
    return execution_module.validate_slice(
        slice_row, skip_metadata_status_check=True, scope_context=scope_context
    )[2] | {
        "slice_path_exists": slice_path.is_dir()
    }


def build_route(
    slice_row: Dict[str, Any],
    *,
    target_type: str,
    target_id: str,
    repo_root: Path,
    worktree_ownership: Optional[WorktreeOwnership] = None,
    owner_chain_mode: bool = False,
) -> SliceRoute:
    status = str(slice_row["status"])
    ownership = worktree_ownership or WorktreeOwnership(
        baseline_from_checkpoint=False,
        baseline_dirty_paths=[],
        current_dirty_paths=[],
        owned_dirty_paths=[],
        unowned_dirty_paths=[],
        owned_file_conflict_paths=[],
        baseline_snapshot={},
        current_snapshot={},
    )
    if ownership.owned_file_conflict_paths:
        next_owner = "guide-execution"
        action = "resolve_owned_file_conflict"
    elif status == "draft":
        next_owner = "blueprint"
        action = "create_or_update_blueprint"
    elif status == "brief_ready":
        next_owner = "blueprint"
        action = "create_or_update_blueprint"
    elif status == "blueprint_ready" and owner_chain_mode:
        next_owner = "implementation"
        action = "promote_to_execution_ready"
    elif status in {"blueprint_ready", "execution_ready"} and not owner_chain_mode:
        next_owner = "implementation"
        action = "implement_validate_review_and_close"
    elif status == "execution_ready" and owner_chain_mode:
        next_owner = "review-execution"
        action = "run_review_execution"
    elif (
        status == "closed"
        and not ownership.baseline_from_checkpoint
        and ownership.current_dirty_paths
    ):
        next_owner = "commit"
        action = "commit_completed_slice"
    elif status == "closed" and ownership.owned_dirty_paths:
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


def iter_handoff_scope_contexts(handoff: HandoffPayload, execution_module, fallback_scope):
    handoff_path = Path(handoff.execution_slice_path)
    if not handoff_path.is_absolute():
        handoff_path = fallback_scope.repo_root / handoff_path
    seen = set()
    for candidate in [handoff_path, *handoff_path.parents]:
        if (candidate / ".skills" / "execution.json").exists():
            scope_context = execution_module.resolve_execution_scope_context(
                explicit_scope=candidate
            )
            scope_root = scope_context.scope_root.resolve()
            if scope_root in seen:
                continue
            seen.add(scope_root)
            yield scope_context


def resolve_slice(
    args: argparse.Namespace,
    execution_module,
    checkpoint_path: Path,
) -> tuple[list[dict[str, Any]], Dict[str, Any], str, str, object, Optional[CheckpointRecord]]:
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
        if row is None and handoff is not None:
            for handoff_scope_context in iter_handoff_scope_contexts(
                handoff, execution_module, scope_context
            ):
                scope_context = handoff_scope_context
                rows = execution_module.parse_registry(scope_context=scope_context)
                row = execution_module.resolve_slice(rows, selector)
                if row is not None:
                    break
    else:
        row = execution_module.find_active_slice(rows)
        if row is not None:
            selector = str(row["id"])
            target_id = selector
    if row is None:
        raise RuntimeError("No active or requested execution slice could be resolved.")
    if not target_id:
        target_id = str(row["id"])
    return rows, row, target_type, target_id, scope_context, checkpoint


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
                raise RuntimeError("ship-slice stop_on_owner entries must be strings.")
            candidates.append(item)
    else:
        raise RuntimeError("ship-slice stop_on_owner must be a string or list of strings.")

    normalized: list[str] = []
    for candidate in candidates:
        owner = normalize_owner_name(candidate)
        if not owner:
            continue
        if owner not in VALID_STOP_OWNERS:
            raise RuntimeError(
                "Invalid ship-slice stop_on_owner value "
                f"'{candidate}'. Valid owners: {sorted(VALID_STOP_OWNERS)}"
            )
        if owner not in normalized:
            normalized.append(owner)
    return normalized


def execute_owner_chain(
    rows: list[dict[str, Any]],
    slice_row: Dict[str, Any],
    *,
    execution_module,
    scope_context,
    target_type: str,
    target_id: str,
    repo_root: Path,
    worktree_ownership: WorktreeOwnership,
    stop_on_owner: list[str],
    continuation_policy: ContinuationPolicyConfig,
) -> tuple[SliceRoute, list[dict[str, Any]], Optional[dict[str, Any]]]:
    steps: list[dict[str, Any]] = []

    for _ in range(len(CHAIN_TARGET_STATUS_BY_STATE) + 3):
        route = build_route(
            slice_row,
            target_type=target_type,
            target_id=target_id,
            repo_root=repo_root,
            worktree_ownership=worktree_ownership,
            owner_chain_mode=True,
        )
        current_status = route.slice_status

        if route.next_owner in stop_on_owner:
            return (
                route,
                steps,
                {
                    "kind": "owner_stop",
                    "owner": route.next_owner,
                    "status": current_status,
                    "target_status": CHAIN_TARGET_STATUS_BY_STATE.get(current_status),
                    "message": (
                        f"Stopped before '{route.next_owner}' because it is configured in stop_on_owner."
                    ),
                },
            )

        if route.next_owner == "review-execution":
            decision = continuation_policy.decision_for("review_boundary")
            return (
                route,
                steps,
                {
                    "kind": "review_boundary",
                    "owner": "review-execution",
                    "status": current_status,
                    "target_status": current_status,
                    "policy_action": decision["policy_action"],
                    "policy_source": decision["policy_source"],
                    "message": (
                        "Reached review-execution boundary. "
                        f"Policy action is '{decision['policy_action']}'."
                    ),
                },
            )

        if route.next_owner == "commit":
            decision = continuation_policy.decision_for("commit_checkpoint")
            return (
                route,
                steps,
                {
                    "kind": "commit_checkpoint",
                    "owner": "commit",
                    "status": current_status,
                    "target_status": current_status,
                    "policy_action": decision["policy_action"],
                    "policy_source": decision["policy_source"],
                    "message": (
                        "Closed slice requires commit checkpoint before continuing. "
                        f"Policy action is '{decision['policy_action']}'."
                    ),
                },
            )

        if route.next_owner in {"none", "guide-execution"}:
            return route, steps, None

        target_status = CHAIN_TARGET_STATUS_BY_STATE.get(current_status)
        if target_status is None:
            return route, steps, None

        success, message = execution_module.update_slice_status(
            rows,
            slice_row,
            target_status,
            scope_context=scope_context,
        )
        next_status = str(slice_row["status"])
        advanced = next_status != current_status
        steps.append(
            {
                "owner": route.next_owner,
                "from_status": current_status,
                "target_status": target_status,
                "success": bool(success),
                "advanced": advanced,
                "result_status": next_status,
                "message": message,
            }
        )

        if not success or not advanced:
            failure_route = build_route(
                slice_row,
                target_type=target_type,
                target_id=target_id,
                repo_root=repo_root,
                worktree_ownership=worktree_ownership,
                owner_chain_mode=True,
            )
            return (
                failure_route,
                steps,
                {
                    "kind": classify_stop_reason_from_message(
                        message, stage="execution"
                    ),
                    "owner": route.next_owner,
                    "status": next_status,
                    "target_status": target_status,
                    "message": message,
                },
            )

    safety_route = build_route(
        slice_row,
        target_type=target_type,
        target_id=target_id,
        repo_root=repo_root,
        worktree_ownership=worktree_ownership,
        owner_chain_mode=True,
    )
    return (
        safety_route,
        steps,
        {
            "kind": "safety_stop",
            "owner": safety_route.next_owner,
            "status": safety_route.slice_status,
            "target_status": None,
            "message": "Stopped owner-chain due to unexpected loop safety boundary.",
        },
    )


def build_readiness_payload(
    *,
    route: SliceRoute,
    owner_chain: Optional[dict[str, Any]],
    worktree_ownership: WorktreeOwnership,
    terminal_automation: Optional[TerminalAutomationResult] = None,
) -> dict[str, Any]:
    blocked_by: list[str] = []
    boundary_reason_input = (
        owner_chain.get("stop_reason") if isinstance(owner_chain, dict) else None
    )
    boundary_reason = normalize_stop_reason(boundary_reason_input)
    stop_reason_input = boundary_reason
    if terminal_automation is not None and terminal_automation.stop_reason is not None:
        stop_reason_input = terminal_automation.stop_reason
    if worktree_ownership.owned_file_conflict_paths:
        stop_reason_input = {
            "kind": "owned_file_conflict",
            "paths": list(worktree_ownership.owned_file_conflict_paths),
        }
    stop_reason = normalize_stop_reason(stop_reason_input)
    if boundary_reason is not None and isinstance(boundary_reason.get("kind"), str):
        blocked_by.append(str(boundary_reason["kind"]))

    commit_required = route.next_owner == "commit"
    if commit_required:
        blocked_by.append("commit_checkpoint")
    if route.next_owner == "review-execution":
        blocked_by.append("review_boundary")
    if route.next_owner == "guide-execution" and not worktree_ownership.owned_file_conflict_paths:
        blocked_by.append("execution_resolution_required")
    if route.next_owner == "none":
        blocked_by.append("completed")

    readiness = build_accelerator_readiness(
        next_owner=route.next_owner,
        automatable_owners=AUTOMATABLE_OWNERS,
        blocked_by=blocked_by,
        stop_reason=stop_reason,
        approval_gate={
            "required": False,
            "state": "not_required",
        },
        commit_checkpoint={
            "required": commit_required,
            "state": "waiting_commit" if commit_required else "not_required",
        },
    )
    policy_action: Optional[str] = None
    policy_source: Optional[str] = None
    if boundary_reason is not None:
        raw_action = boundary_reason.get("policy_action")
        if isinstance(raw_action, str):
            normalized_action = raw_action.strip().lower().replace("-", "_")
            if normalized_action in VALID_CONTINUATION_POLICY_ACTIONS:
                policy_action = normalized_action
        raw_source = boundary_reason.get("policy_source")
        if isinstance(raw_source, str):
            normalized_source = raw_source.strip().lower().replace("-", "_")
            if normalized_source in VALID_CONTINUATION_POLICY_SOURCES:
                policy_source = normalized_source
    readiness["policy_action"] = policy_action
    readiness["policy_source"] = policy_source
    return readiness


def write_runtime_records(
    *,
    checkpoint_path: Path,
    event_log_path: Path,
    route: SliceRoute,
    dirty_paths: list[str],
    worktree_ownership: WorktreeOwnership,
    learnings: list[dict[str, Any]],
    owner_chain: Optional[dict[str, Any]],
    terminal_automation: Optional[TerminalAutomationResult],
) -> None:
    event: Dict[str, Any] = {
        "timestamp": utc_now(),
        "skill": "ship-slice",
        "slice_id": route.slice_id,
        "slice_status": route.slice_status,
        "next_owner": route.next_owner,
        "action": route.action,
        "target_id": route.target_id,
        "owned_dirty_paths": list(worktree_ownership.owned_dirty_paths),
        "unowned_dirty_paths": list(worktree_ownership.unowned_dirty_paths),
        "owned_file_conflict_paths": list(worktree_ownership.owned_file_conflict_paths),
    }
    if owner_chain is not None:
        event["owner_chain_enabled"] = bool(owner_chain.get("enabled", False))
        stop_reason = owner_chain.get("stop_reason")
        if isinstance(stop_reason, dict):
            event["owner_chain_stop_kind"] = stop_reason.get("kind")
            event["owner_chain_stop_owner"] = stop_reason.get("owner")
    if terminal_automation is not None:
        event["terminal_automation"] = terminal_automation.to_dict()
    append_event(event_log_path, event)

    checkpoint_payload: Dict[str, Any] = {
        "slice_id": route.slice_id,
        "slice_path": route.slice_path,
        "slice_status": route.slice_status,
        "target_type": route.target_type,
        "target_id": route.target_id,
        "next_owner": route.next_owner,
        "dirty_worktree_paths": list(dirty_paths),
        "worktree_ownership": worktree_ownership.to_dict(),
        "handoff_payload": dict(route.handoff_payload),
        "learning_ids": [item["id"] for item in learnings],
    }
    if owner_chain is not None:
        checkpoint_payload["owner_chain"] = owner_chain
    if terminal_automation is not None:
        checkpoint_payload["terminal_automation"] = terminal_automation.to_dict()

    write_checkpoint(
        checkpoint_path,
        CheckpointRecord(
            run_id="ship-slice-active",
            state=route.action,
            payload=checkpoint_payload,
        ),
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    execution_module = load_module(GUIDE_EXECUTION_SCRIPT, "manage_execution_for_ship_slice")
    repo_root = git_repo_root()
    checkpoint_path, event_log_path, learnings_path = runtime_paths(repo_root)

    try:
        rows, slice_row, target_type, target_id, scope_context, prior_checkpoint = resolve_slice(
            args,
            execution_module,
            checkpoint_path,
        )
    except RuntimeError as exc:
        return emit_failure_response(
            args=args,
            event_log_path=event_log_path,
            reason_code="resolution_failed",
            message=str(exc),
            slice_id=args.selector or "",
        )

    raw_config = execution_module.load_raw_config(required=False, scope_context=scope_context)
    accelerators = raw_config.get("accelerators", {}) if isinstance(raw_config, dict) else {}
    ship_slice_config = accelerators.get("ship_slice", {}) if isinstance(accelerators, dict) else {}

    try:
        config_execute_owner_chain = (
            bool(ship_slice_config.get("execute_owner_chain", False))
            if isinstance(ship_slice_config, dict)
            else False
        )
        config_stop_on_owner = parse_stop_on_owners(
            ship_slice_config.get("stop_on_owner") if isinstance(ship_slice_config, dict) else None
        )
        terminal_config = parse_terminal_automation_config(ship_slice_config)
        continuation_policy = parse_continuation_policy_config(ship_slice_config)
    except RuntimeError as exc:
        return emit_failure_response(
            args=args,
            event_log_path=event_log_path,
            reason_code="invalid_configuration",
            message=str(exc),
            target_id=target_id,
            slice_id=str(slice_row["id"]),
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
    except RuntimeError as exc:
        return emit_failure_response(
            args=args,
            event_log_path=event_log_path,
            reason_code="invalid_configuration",
            message=str(exc),
            target_id=target_id,
            slice_id=str(slice_row["id"]),
        )

    try:
        owner_chain: Optional[dict[str, Any]] = None
        terminal_automation: Optional[TerminalAutomationResult] = None
        worktree_ownership, dirty_paths = compute_worktree_ownership(repo_root, prior_checkpoint)
        if execute_owner_chain_enabled:
            route, steps, stop_reason = execute_owner_chain(
                rows,
                slice_row,
                execution_module=execution_module,
                scope_context=scope_context,
                target_type=target_type,
                target_id=target_id,
                repo_root=repo_root,
                worktree_ownership=worktree_ownership,
                stop_on_owner=stop_on_owner,
                continuation_policy=continuation_policy,
            )
            owner_chain = {
                "enabled": True,
                "stop_on_owner": stop_on_owner,
                "steps": steps,
                "stop_reason": normalize_stop_reason(stop_reason),
            }
        else:
            route = build_route(
                slice_row,
                target_type=target_type,
                target_id=target_id,
                repo_root=repo_root,
                worktree_ownership=worktree_ownership,
                owner_chain_mode=False,
            )

        (
            rows,
            slice_row,
            route,
            worktree_ownership,
            dirty_paths,
            terminal_automation,
        ) = apply_terminal_automation(
            route=route,
            rows=rows,
            slice_row=slice_row,
            execution_module=execution_module,
            scope_context=scope_context,
            repo_root=repo_root,
            worktree_ownership=worktree_ownership,
            dirty_paths=dirty_paths,
            terminal_config=terminal_config,
            continuation_policy=continuation_policy,
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
        write_runtime_records(
            checkpoint_path=checkpoint_path,
            event_log_path=event_log_path,
            route=route,
            dirty_paths=dirty_paths,
            worktree_ownership=worktree_ownership,
            learnings=learnings,
            owner_chain=owner_chain,
            terminal_automation=terminal_automation,
        )

        readiness = build_readiness_payload(
            route=route,
            owner_chain=owner_chain,
            worktree_ownership=worktree_ownership,
            terminal_automation=terminal_automation,
        )
        failure_context = (
            record_failure_for_stop_reason(
                event_log_path,
                skill="ship-slice",
                stage="execution",
                stop_reason=owner_chain.get("stop_reason") if owner_chain is not None else None,
                target_id=target_id,
                slice_id=route.slice_id,
                next_owner=route.next_owner,
            )
            if owner_chain is not None
            else None
        )
        if failure_context is None and terminal_automation is not None:
            failure_context = record_failure_for_stop_reason(
                event_log_path,
                skill="ship-slice",
                stage="execution",
                stop_reason=terminal_automation.stop_reason,
                target_id=target_id,
                slice_id=route.slice_id,
                next_owner=route.next_owner,
            )
        if failure_context is None and is_failure_reason(
            readiness.get("stop_reason", {}).get("kind")
            if isinstance(readiness.get("stop_reason"), dict)
            else None
        ):
            failure_context = record_failure_for_stop_reason(
                event_log_path,
                skill="ship-slice",
                stage="execution",
                stop_reason=readiness.get("stop_reason"),
                target_id=target_id,
                slice_id=route.slice_id,
                next_owner=route.next_owner,
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
            "execute_owner_chain": execute_owner_chain_enabled,
            "owner_chain": owner_chain,
            "checkpoint_path": str(checkpoint_path),
            "event_log_path": str(event_log_path),
            "dirty_worktree_paths": dirty_paths,
            "failure_context": (
                failure_context.to_dict() if failure_context is not None else None
            ),
            "worktree_ownership": worktree_ownership.to_dict(),
            "terminal_automation": (
                terminal_automation.to_dict() if terminal_automation is not None else None
            ),
            "learnings": learnings,
            "checkpoint_stale_reason": checkpoint_stale_reason,
            "readiness": readiness,
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
    except RuntimeError as exc:
        return emit_failure_response(
            args=args,
            event_log_path=event_log_path,
            reason_code="runtime_error",
            message=str(exc),
            target_id=target_id,
            slice_id=str(slice_row["id"]),
        )


if __name__ == "__main__":
    raise SystemExit(main())
