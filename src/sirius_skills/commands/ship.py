#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple


COMMAND_DIR = Path(__file__).resolve().parent
GUIDE_PLANNING_SCRIPT = COMMAND_DIR / "manage_planning.py"
GUIDE_EXECUTION_SCRIPT = COMMAND_DIR / "manage_execution.py"
SUBFEATURES_SCRIPT = COMMAND_DIR / "manage_subfeatures.py"
ARTIFACT_INVENTORY_SCRIPT = COMMAND_DIR / "artifact_inventory.py"
SHIP_SLICE_SCRIPT = COMMAND_DIR / "ship_slice.py"
ARCHIVE_DATA_SCRIPT = COMMAND_DIR / "archive_data.py"
AUTOMATABLE_OWNERS = {"brief", "blueprint", "implementation"}
SUPPORTED_PREFLIGHT_MODES = {"off", "local_only"}
MUTATION_CAPABLE_PREFLIGHT_OPERATIONS = {
    "bootstrap_next",
    "delegate_resume",
    "finalize",
}
PREFLIGHT_BLOCKING_REASONS = {"approval_required", "commit_checkpoint"}
EXECUTION_RECONCILIATION_START = "<!-- execution-reconciliation:start -->"
EXECUTION_RECONCILIATION_END = "<!-- execution-reconciliation:end -->"


from sirius_skills.lib.workflow_runtime import (  # noqa: E402
    HandoffPayload,
    build_accelerator_readiness,
    dedupe_reason_codes,
    evaluate_planning_approval_gate,
    normalize_stop_reason,
    write_planning_approval_record,
)
from sirius_skills.lib.workflow_state import sync_completed_owners  # noqa: E402
from sirius_skills.lib.workflow_state import markdown_repository  # noqa: E402


@dataclass
class PlannedSliceBacklogEntry:
    planned_slice_id: str
    story_id: str
    title: str
    validation_hint: str
    increment_ids: List[str]
    depends_on: List[str]
    execution_slice_ids: List[str]
    closed_execution_slice_ids: List[str]
    state: str


@dataclass
class BacklogResolution:
    target_type: str
    target_id: str
    target_path: str
    planning_status: str
    increment_order: List[str]
    current_increment: Optional[str]
    completed_increments: List[str]
    ready_next: List[str]
    active_execution_slices: List[str]
    entries: List[PlannedSliceBacklogEntry]
    active_slice_handoff: Optional[Dict[str, object]]
    approval_gate: Dict[str, object]
    preflight_mode: str
    delegate_to_ship_slice: bool

    def to_dict(self) -> Dict[str, object]:
        return {
            "target_type": self.target_type,
            "target_id": self.target_id,
            "target_path": self.target_path,
            "planning_status": self.planning_status,
            "increment_order": list(self.increment_order),
            "current_increment": self.current_increment,
            "completed_increments": list(self.completed_increments),
            "ready_next": list(self.ready_next),
            "active_execution_slices": list(self.active_execution_slices),
            "entries": [asdict(entry) for entry in self.entries],
            "active_slice_handoff": dict(self.active_slice_handoff)
            if self.active_slice_handoff is not None
            else None,
            "approval_gate": dict(self.approval_gate),
            "readiness": build_backlog_readiness(self),
        }


@dataclass
class BootstrapResult:
    backlog: BacklogResolution
    bootstrapped_slice_id: Optional[str]
    bootstrapped_slice_path: Optional[str]
    slice_status: Optional[str]
    checkpoint_slice_id: Optional[str]
    dirty_worktree_paths: List[str]
    next_owner: Optional[str]
    completed: bool
    action: str
    requested_command: str
    delegate_result: Optional[Dict[str, object]] = None
    finalization: Optional[Dict[str, object]] = None
    archive_result: Optional[Dict[str, object]] = None

    def to_dict(self) -> Dict[str, object]:
        payload = self.backlog.to_dict()
        payload["bootstrapped_slice_id"] = self.bootstrapped_slice_id
        payload["bootstrapped_slice_path"] = self.bootstrapped_slice_path
        payload["slice_status"] = self.slice_status
        payload["checkpoint_slice_id"] = self.checkpoint_slice_id
        payload["dirty_worktree_paths"] = list(self.dirty_worktree_paths)
        payload["next_owner"] = self.next_owner
        payload["completed"] = self.completed
        payload["action"] = self.action
        payload["delegate_result"] = (
            dict(self.delegate_result) if self.delegate_result is not None else None
        )
        payload["finalization"] = (
            dict(self.finalization) if self.finalization is not None else None
        )
        payload["archive_result"] = (
            dict(self.archive_result) if self.archive_result is not None else None
        )
        payload["handoff_payload"] = (
            dict(self.backlog.active_slice_handoff["handoff_payload"])
            if self.backlog.active_slice_handoff is not None
            and "handoff_payload" in self.backlog.active_slice_handoff
            else None
        )
        payload["readiness"] = build_bootstrap_readiness(self)
        return payload


def _derive_next_owner(backlog: BacklogResolution) -> Optional[str]:
    if backlog.active_slice_handoff is not None:
        raw_owner = backlog.active_slice_handoff.get("next_owner")
        if isinstance(raw_owner, str) and raw_owner.strip():
            return raw_owner
    if backlog.ready_next:
        return "brief"
    if all(entry.state == "completed" for entry in backlog.entries):
        return "none"
    return "guide-execution"


def _approval_gate_state(backlog: BacklogResolution) -> Dict[str, object]:
    gate = backlog.approval_gate if isinstance(backlog.approval_gate, dict) else {}
    required = bool(gate.get("required"))
    return {
        "required": required,
        "state": str(gate.get("decision") or ("not_required" if not required else "unknown")),
        "reason": gate.get("reason"),
        "approval_path": gate.get("approval_path"),
    }


def _extract_delegate_readiness(
    delegate_result: Optional[Dict[str, object]]
) -> Optional[Dict[str, object]]:
    if not isinstance(delegate_result, dict):
        return None
    readiness = delegate_result.get("readiness")
    return readiness if isinstance(readiness, dict) else None


def _extract_delegate_policy_metadata(
    readiness: Optional[Dict[str, object]],
) -> Tuple[Optional[str], Optional[str]]:
    if not isinstance(readiness, dict):
        return None, None
    policy_action: Optional[str] = None
    raw_action = readiness.get("policy_action")
    if isinstance(raw_action, str):
        normalized_action = raw_action.strip().lower().replace("-", "_")
        if normalized_action in {"stop", "continue"}:
            policy_action = normalized_action
    policy_source: Optional[str] = None
    raw_source = readiness.get("policy_source")
    if isinstance(raw_source, str):
        normalized_source = raw_source.strip().lower().replace("-", "_")
        if normalized_source in {"default", "config"}:
            policy_source = normalized_source
    return policy_action, policy_source


def normalize_preflight_mode(ship_config: Dict[str, object]) -> str:
    raw_preflight = ship_config.get("preflight")
    if raw_preflight is None:
        return "off"
    if not isinstance(raw_preflight, dict):
        raise RuntimeError(
            "Invalid ship preflight config: accelerators.ship.preflight must be an object."
        )
    raw_mode = raw_preflight.get("mode")
    if raw_mode is None:
        return "off"
    normalized_mode = str(raw_mode).strip().lower().replace("-", "_")
    if normalized_mode not in SUPPORTED_PREFLIGHT_MODES:
        raise RuntimeError(
            "Invalid ship preflight mode "
            f"'{raw_mode}'. Supported values: {sorted(SUPPORTED_PREFLIGHT_MODES)}"
        )
    return normalized_mode


def classify_preflight_operation_for_backlog() -> str:
    return "backlog_report"


def classify_preflight_operation_for_result(result: BootstrapResult) -> str:
    if result.requested_command == "finalize":
        return "finalize"
    if result.completed or result.action == "complete":
        return "complete"
    if result.action == "blocked":
        return "blocked"
    if result.requested_command == "bootstrap_next":
        return "bootstrap_next"
    if result.action == "bootstrap_next_slice":
        return "bootstrap_next"
    if result.action == "commit_checkpoint_required":
        if not result.backlog.active_execution_slices:
            return "bootstrap_next"
        return "delegate_resume" if result.backlog.delegate_to_ship_slice else "resume_route"
    if result.backlog.delegate_to_ship_slice and (
        result.action in {"delegated_to_ship_slice", "approval_required"}
        or result.backlog.active_slice_handoff is not None
    ):
        return "delegate_resume"
    if result.backlog.active_slice_handoff is not None:
        return "resume_route"
    return "blocked"


def build_preflight_summary(
    *, mode: str, operation: str, blocked_by: Sequence[object]
) -> Dict[str, object]:
    normalized_blockers = dedupe_reason_codes(blocked_by)
    blocking_checks = [
        blocker for blocker in normalized_blockers if blocker in PREFLIGHT_BLOCKING_REASONS
    ]
    if mode == "off":
        status = "disabled"
        blocking_checks = []
    elif operation not in MUTATION_CAPABLE_PREFLIGHT_OPERATIONS:
        status = "skipped"
        blocking_checks = []
    elif blocking_checks:
        status = "blocked"
    else:
        status = "passed"
    return {
        "mode": mode,
        "operation": operation,
        "status": status,
        "blocking_checks": blocking_checks,
    }


def build_preflight_stop_reason(
    *, mode: str, operation: str, preflight_summary: Dict[str, object], stop_reason: object
) -> Optional[Dict[str, object]]:
    if normalize_stop_reason(stop_reason) is not None:
        return normalize_stop_reason(stop_reason)
    if mode != "local_only" or operation not in MUTATION_CAPABLE_PREFLIGHT_OPERATIONS:
        return None
    if str(preflight_summary.get("status")) != "blocked":
        return None
    blocking_checks = preflight_summary.get("blocking_checks")
    if not isinstance(blocking_checks, list) or not blocking_checks:
        return None
    return {"kind": str(blocking_checks[0]), "phase": "preflight"}


def build_backlog_readiness(backlog: BacklogResolution) -> Dict[str, object]:
    next_owner = _derive_next_owner(backlog)
    blocked_by: List[str] = []
    approval_gate = _approval_gate_state(backlog)

    if next_owner == "approval":
        blocked_by.append("approval_required")
    elif next_owner == "commit":
        blocked_by.append("commit_checkpoint")
    elif next_owner == "none":
        blocked_by.append("completed")
    elif next_owner == "guide-execution":
        if backlog.active_slice_handoff is None and not backlog.ready_next:
            blocked_by.append("dependency_blocked")
        else:
            blocked_by.append("execution_resolution_required")

    readiness = build_accelerator_readiness(
        next_owner=next_owner,
        automatable_owners=AUTOMATABLE_OWNERS,
        blocked_by=blocked_by,
        stop_reason=None,
        approval_gate=approval_gate,
        commit_checkpoint={
            "required": next_owner == "commit",
            "state": "waiting_commit" if next_owner == "commit" else "not_required",
            "slice_id": None,
        },
    )
    readiness["policy_action"] = None
    readiness["policy_source"] = None
    readiness["preflight"] = build_preflight_summary(
        mode=backlog.preflight_mode,
        operation=classify_preflight_operation_for_backlog(),
        blocked_by=readiness["blocked_by"],
    )
    return readiness


def build_bootstrap_readiness(result: BootstrapResult) -> Dict[str, object]:
    next_owner = result.next_owner or _derive_next_owner(result.backlog)
    blocked_by: List[str] = []
    approval_gate = _approval_gate_state(result.backlog)

    delegate_readiness = _extract_delegate_readiness(result.delegate_result)
    stop_reason = None
    policy_action: Optional[str] = None
    policy_source: Optional[str] = None
    if delegate_readiness is not None:
        delegate_blocked = delegate_readiness.get("blocked_by")
        if isinstance(delegate_blocked, list):
            for item in delegate_blocked:
                if isinstance(item, str):
                    blocked_by.append(item)
        delegate_stop = delegate_readiness.get("stop_reason")
        stop_reason = normalize_stop_reason(delegate_stop)
        policy_action, policy_source = _extract_delegate_policy_metadata(delegate_readiness)

    if result.action == "approval_required":
        blocked_by.append("approval_required")
    elif result.action == "reconciliation_required":
        blocked_by.append("feature_reconciliation_required")
        if stop_reason is None:
            stop_reason = {
                "kind": "feature_reconciliation_required",
                "phase": "finalization",
            }
    elif result.action == "commit_checkpoint_required":
        blocked_by.append("commit_checkpoint")
    elif result.action == "blocked":
        blocked_by.append("dependency_blocked")
    elif result.completed or result.action == "complete":
        blocked_by.append("completed")

    if next_owner == "approval":
        blocked_by.append("approval_required")
    elif next_owner == "commit":
        blocked_by.append("commit_checkpoint")
    elif next_owner == "none":
        blocked_by.append("completed")

    normalized_blocked_by = dedupe_reason_codes(blocked_by)
    operation = classify_preflight_operation_for_result(result)
    preflight = build_preflight_summary(
        mode=result.backlog.preflight_mode,
        operation=operation,
        blocked_by=normalized_blocked_by,
    )
    stop_reason = build_preflight_stop_reason(
        mode=result.backlog.preflight_mode,
        operation=operation,
        preflight_summary=preflight,
        stop_reason=stop_reason,
    )

    commit_required = result.action == "commit_checkpoint_required" or next_owner == "commit"
    readiness = build_accelerator_readiness(
        next_owner=next_owner,
        automatable_owners=AUTOMATABLE_OWNERS,
        blocked_by=normalized_blocked_by,
        stop_reason=stop_reason,
        approval_gate=approval_gate,
        commit_checkpoint={
            "required": commit_required,
            "state": "waiting_commit" if commit_required else "not_required",
            "slice_id": result.checkpoint_slice_id,
        },
    )
    readiness["policy_action"] = policy_action
    readiness["policy_source"] = policy_source
    readiness["preflight"] = preflight
    return readiness


def load_module(script_path: Path, name: str):
    if script_path.name == "manage_planning.py":
        from sirius_skills.commands import manage_planning
        return manage_planning
    elif script_path.name == "manage_execution.py":
        from sirius_skills.commands import manage_execution
        return manage_execution
    elif script_path.name == "manage_subfeatures.py":
        from sirius_skills.commands import manage_subfeatures
        return manage_subfeatures
    elif script_path.name == "artifact_inventory.py":
        from sirius_skills.commands import artifact_inventory
        return artifact_inventory
    elif script_path.name == "archive_data.py":
        from sirius_skills.commands import archive_data
        return archive_data
    raise RuntimeError(f"Unknown script path: {script_path}")


def record_approval_decision(
    selector: str,
    *,
    explicit_scope: Optional[str] = None,
    approval_note: Optional[str] = None,
) -> Dict[str, object]:
    planning_module = load_module(GUIDE_PLANNING_SCRIPT, "manage_planning")
    feature, feature_dir, metadata, _, _ = resolve_target(
        planning_module,
        selector,
        explicit_scope=explicit_scope,
    )
    if str(metadata["status"]) != "planning_reviewed":
        raise RuntimeError(
            "Approval can be recorded only when planning status is "
            f"'planning_reviewed'. Current status: '{metadata['status']}'."
        )

    target_dir = Path(feature_dir)
    return write_planning_approval_record(
        target_id=str(feature["feature"]),
        target_path=str(feature["path"]),
        target_dir=target_dir,
        planning_metadata=metadata,
        approval_note=approval_note,
    )


def _split_table_row(line: str) -> List[str]:
    return markdown_repository.split_table_row(line)


def _normalize_table_header(value: str) -> str:
    return markdown_repository.normalize_table_header(value)


def _split_cell_values(value: str) -> List[str]:
    return markdown_repository.split_cell_values(value)


def _find_markdown_table(lines: Sequence[str], required_headers: Sequence[str]) -> Tuple[Dict[str, int], int]:
    return markdown_repository.find_markdown_table(lines, required_headers)


def parse_planned_slices(slice_planning_path: Path) -> List[Dict[str, object]]:
    return markdown_repository.parse_planned_slices(slice_planning_path)


def parse_increment_plan(
    slice_planning_path: Path,
) -> Tuple[List[str], Dict[str, List[str]]]:
    return markdown_repository.parse_increment_plan(slice_planning_path)


def parse_traceability_table(
    traceability_path: Path,
) -> Tuple[List[str], int, Dict[str, int], List[List[str]]]:
    return markdown_repository.parse_traceability_table(traceability_path)


def collect_increment_metadata(
    slice_planning_path: Path, traceability_records
) -> Tuple[List[str], Dict[str, List[str]]]:
    increment_order, increment_ids_by_planned_slice = parse_increment_plan(slice_planning_path)
    for record in traceability_records:
        increment_ids = _split_cell_values(record.increments)
        for increment_id in increment_ids:
            if increment_id not in increment_order:
                increment_order.append(increment_id)
        for planned_slice_id in record.planned_slice_ids:
            bucket = increment_ids_by_planned_slice.setdefault(planned_slice_id, [])
            for increment_id in increment_ids:
                if increment_id not in bucket:
                    bucket.append(increment_id)
    return increment_order, increment_ids_by_planned_slice


def record_execution_slice_id(
    traceability_path: Path, planned_slice_id: str, execution_slice_id: str
) -> None:
    markdown_repository.record_execution_slice_id(traceability_path, planned_slice_id, execution_slice_id)


def resolve_target(planning_module, selector: str, explicit_scope: Optional[str]):
    rows, feature, scope_context = planning_module.resolve_feature_lookup(
        selector, explicit_scope=explicit_scope
    )
    if feature is None:
        raise RuntimeError(f"Planning target not found: {selector}")
    feature_dir = planning_module.feature_dir_for_row(feature, scope_context=scope_context)
    metadata = planning_module.read_metadata(feature_dir)
    status = str(metadata["status"])
    if status not in {"planning_reviewed", "slice_ready", "implemented"}:
        raise RuntimeError(
            f"Planning target '{feature['feature']}' must be in 'planning_reviewed', "
            f"'slice_ready', or 'implemented'. Current status: '{status}'."
        )
    target_type = "subfeature" if "/subfeatures/" in str(feature["path"]) else "feature"
    return feature, feature_dir, metadata, scope_context, target_type


def parse_dependency_selector(dependency: str) -> Optional[Tuple[str, str]]:
    parts = dependency.rsplit(" ", 1)
    if len(parts) != 2:
        return None
    selector, status = (part.strip() for part in parts)
    if not selector or not status:
        return None
    return selector, status


def dependency_is_satisfied(
    dependency: str,
    completed_planned_slices: set,
    planning_module,
    planning_rows: List[Dict[str, object]],
    scope_context: object,
    target_type: str,
    target_dir: Path,
    sibling_subfeature_rows: Optional[List[Dict[str, object]]] = None,
    subfeature_module=None,
) -> bool:
    if dependency in completed_planned_slices:
        return True

    parsed_dependency = parse_dependency_selector(dependency)
    if parsed_dependency is None:
        return False
    selector, required_status = parsed_dependency

    if (
        target_type == "subfeature"
        and sibling_subfeature_rows is not None
        and subfeature_module is not None
    ):
        try:
            required_subfeature_status = subfeature_module.normalize_status(required_status)
        except ValueError:
            required_subfeature_status = None
        if required_subfeature_status is not None:
            sibling_subfeature = subfeature_module.find_subfeature(
                sibling_subfeature_rows, selector
            )
            if sibling_subfeature is not None:
                sibling_metadata = subfeature_module.read_metadata(
                    subfeature_module.subfeature_dir_for_row(
                        sibling_subfeature, scope_context
                    )
                )
                actual_status = str(sibling_metadata["status"])
                return subfeature_module.STATUS_SEQUENCE.index(
                    actual_status
                ) >= subfeature_module.STATUS_SEQUENCE.index(required_subfeature_status)

    try:
        required_planning_status = planning_module.normalize_status(required_status)
    except ValueError:
        return False

    dependency_target = planning_module.find_feature(
        planning_rows, selector, scope_context=scope_context
    )
    if dependency_target is None:
        return False

    dependency_metadata = planning_module.read_metadata(
        planning_module.feature_dir_for_row(dependency_target, scope_context=scope_context)
    )
    actual_planning_status = str(dependency_metadata["status"])
    return planning_module.STATUS_SEQUENCE.index(
        actual_planning_status
    ) >= planning_module.STATUS_SEQUENCE.index(required_planning_status)


def resolve_backlog(selector: str, explicit_scope: Optional[str] = None) -> BacklogResolution:
    planning_module = load_module(GUIDE_PLANNING_SCRIPT, "manage_planning")
    execution_module = load_module(GUIDE_EXECUTION_SCRIPT, "manage_execution")
    subfeature_module = load_module(SUBFEATURES_SCRIPT, "manage_subfeatures")
    artifact_inventory = load_module(ARTIFACT_INVENTORY_SCRIPT, "artifact_inventory")

    feature, target_dir, metadata, scope_context, target_type = resolve_target(
        planning_module, selector, explicit_scope
    )
    target_dir_path = Path(target_dir)

    slice_planning_path = Path(target_dir) / "slice-planning.md"
    traceability_path = Path(target_dir) / "slice-traceability.md"
    if not slice_planning_path.exists():
        raise RuntimeError(f"Missing planning file: {slice_planning_path}")
    if not traceability_path.exists():
        raise RuntimeError(f"Missing traceability file: {traceability_path}")

    planned_slices = parse_planned_slices(slice_planning_path)
    traceability_records = artifact_inventory.parse_traceability_records(
        traceability_path,
        target_type,
        str(feature["feature"]),
        str(feature["path"]),
    )
    increment_order, increment_ids_by_planned_slice = collect_increment_metadata(
        slice_planning_path, traceability_records
    )
    execution_rows = execution_module.parse_registry(scope_context=scope_context)
    execution_status_by_id = {str(row["id"]): str(row["status"]) for row in execution_rows}
    planning_rows = planning_module.parse_registry(scope_context=scope_context)
    ship_config = ship_accelerator_config(scope_context, execution_module)
    preflight_mode = normalize_preflight_mode(ship_config)
    sibling_subfeature_rows: Optional[List[Dict[str, object]]] = None
    if target_type == "subfeature":
        sibling_subfeature_rows = subfeature_module.load_registry(
            str(target_dir_path.parent.parent)
        )

    execution_ids_by_planned_slice: Dict[str, List[str]] = {}
    for record in traceability_records:
        if not record.execution_slice_ids:
            continue
        if len(record.planned_slice_ids) == 1:
            bucket = execution_ids_by_planned_slice.setdefault(
                record.planned_slice_ids[0], []
            )
            for execution_slice_id in record.execution_slice_ids:
                if execution_slice_id not in bucket:
                    bucket.append(execution_slice_id)
            continue
        if len(record.planned_slice_ids) == len(record.execution_slice_ids):
            for planned_slice_id, execution_slice_id in zip(
                record.planned_slice_ids, record.execution_slice_ids
            ):
                bucket = execution_ids_by_planned_slice.setdefault(planned_slice_id, [])
                if execution_slice_id not in bucket:
                    bucket.append(execution_slice_id)

    completed_planned_slices = set()
    active_execution_slices: List[str] = []
    entries: List[PlannedSliceBacklogEntry] = []

    for planned_slice in planned_slices:
        planned_slice_id = str(planned_slice["planned_slice_id"])
        execution_slice_ids = execution_ids_by_planned_slice.get(planned_slice_id, [])
        closed_execution_slice_ids = [
            slice_id
            for slice_id in execution_slice_ids
            if execution_status_by_id.get(slice_id) == "closed"
        ]
        non_closed_execution_slice_ids = [
            slice_id
            for slice_id in execution_slice_ids
            if execution_status_by_id.get(slice_id) not in {None, "closed"}
        ]
        if closed_execution_slice_ids:
            completed_planned_slices.add(planned_slice_id)
        active_execution_slices.extend(
            slice_id for slice_id in non_closed_execution_slice_ids if slice_id not in active_execution_slices
        )
        entries.append(
            PlannedSliceBacklogEntry(
                planned_slice_id=planned_slice_id,
                story_id=str(planned_slice["story_id"]),
                title=str(planned_slice["title"]),
                validation_hint=str(planned_slice.get("validation_hint", "")),
                increment_ids=list(increment_ids_by_planned_slice.get(planned_slice_id, [])),
                depends_on=list(planned_slice["depends_on"]),
                execution_slice_ids=list(execution_slice_ids),
                closed_execution_slice_ids=list(closed_execution_slice_ids),
                state="pending",
            )
        )

    dependency_ready_next: List[str] = []
    for entry in entries:
        if entry.closed_execution_slice_ids:
            entry.state = "completed"
            continue
        if any(slice_id in active_execution_slices for slice_id in entry.execution_slice_ids):
            entry.state = "active"
            continue
        if all(
            dependency_is_satisfied(
                dep,
                completed_planned_slices,
                planning_module,
                planning_rows,
                scope_context,
                target_type,
                target_dir_path,
                sibling_subfeature_rows=sibling_subfeature_rows,
                subfeature_module=subfeature_module,
            )
            for dep in entry.depends_on
        ):
            entry.state = "ready"
            dependency_ready_next.append(entry.planned_slice_id)
        else:
            entry.state = "blocked"

    active_increment_ids: List[str] = []
    for entry in entries:
        if entry.state != "active":
            continue
        for increment_id in entry.increment_ids:
            if increment_id not in active_increment_ids:
                active_increment_ids.append(increment_id)

    current_increment: Optional[str] = None
    if active_increment_ids:
        current_increment = active_increment_ids[0]
    else:
        for increment_id in increment_order:
            if any(
                increment_id in entry.increment_ids and entry.state != "completed"
                for entry in entries
            ):
                current_increment = increment_id
                break

    ready_next: List[str] = []
    for entry in entries:
        if entry.state != "ready":
            continue
        if current_increment is None or current_increment in entry.increment_ids:
            ready_next.append(entry.planned_slice_id)
            continue
        entry.state = "deferred"

    completed_increments: List[str] = []
    for increment_id in increment_order:
        increment_entries = [
            entry for entry in entries if increment_id in entry.increment_ids
        ]
        if increment_entries and all(entry.state == "completed" for entry in increment_entries):
            completed_increments.append(increment_id)

    active_slice_handoff: Optional[Dict[str, object]] = None
    if len(active_execution_slices) == 1:
        active_slice_id = active_execution_slices[0]
        active_slice = execution_module.resolve_slice(execution_rows, active_slice_id)
        if active_slice is not None:
            active_entry = next(
                (
                    entry
                    for entry in entries
                    if active_slice_id == entry.planned_slice_id
                    or active_slice_id in entry.execution_slice_ids
                ),
                None,
            )
            active_slice_handoff = build_active_slice_handoff(
                target_type,
                str(feature["feature"]),
                active_slice,
                active_entry,
                execution_module=execution_module,
                scope_context=scope_context,
            )

    approval_gate = evaluate_planning_approval_gate(
        target_id=str(feature["feature"]),
        target_path=str(feature["path"]),
        target_dir=target_dir_path,
        planning_metadata=metadata,
    )

    return BacklogResolution(
        target_type=target_type,
        target_id=str(feature["feature"]),
        target_path=str(feature["path"]),
        planning_status=str(metadata["status"]),
        increment_order=increment_order,
        current_increment=current_increment,
        completed_increments=completed_increments,
        ready_next=ready_next,
        active_execution_slices=active_execution_slices,
        entries=entries,
        active_slice_handoff=active_slice_handoff,
        approval_gate=approval_gate,
        preflight_mode=preflight_mode,
        delegate_to_ship_slice=bool(ship_config.get("delegate_to_ship_slice", False)),
    )


def inspect_slice_artifacts(slice_row: Dict[str, object], execution_module, scope_context) -> Dict[str, bool]:
    slice_path = Path(execution_module.slice_path_for_row(slice_row, scope_context=scope_context))
    return {
        "brief_exists": (slice_path / "brief.md").is_file(),
        "requirements_exists": (slice_path / "checklists" / "requirements.md").is_file(),
        "blueprint_exists": (slice_path / "blueprint.md").is_file(),
        "metadata_exists": (slice_path / ".slice-meta.json").is_file(),
    }


def build_active_slice_handoff(
    target_type: str,
    target_id: str,
    slice_row: Dict[str, object],
    backlog_entry: Optional[PlannedSliceBacklogEntry],
    *,
    execution_module,
    scope_context,
) -> Dict[str, object]:
    status = str(slice_row["status"])
    checks = inspect_slice_artifacts(slice_row, execution_module, scope_context)
    config = execution_module.load_config(required=True, scope_context=scope_context)
    validation_hint = backlog_entry.validation_hint if backlog_entry is not None else ""
    missing_artifacts: List[str] = []
    downstream_owners: List[str]

    if not checks["brief_exists"]:
        missing_artifacts.append("brief.md")
    if not checks["requirements_exists"]:
        missing_artifacts.append("checklists/requirements.md")
    if status in {"blueprint_ready", "execution_ready", "closed"} and not checks["blueprint_exists"]:
        missing_artifacts.append("blueprint.md")

    if status == "draft":
        next_owner = "brief"
        next_action = "create_or_update_brief"
        downstream_owners = [
            "blueprint",
            "implementation",
            "review-execution",
            "close-slice",
            "commit",
        ]
    elif status == "brief_ready":
        next_owner = "blueprint"
        next_action = "create_or_update_blueprint"
        downstream_owners = [
            "implementation",
            "review-execution",
            "close-slice",
            "commit",
        ]
    elif status == "blueprint_ready" and not bool(config["auto_start_implementation"]):
        next_owner = "guide-execution"
        next_action = "promote_blueprint_to_execution_ready"
        downstream_owners = [
            "implementation",
            "review-execution",
            "close-slice",
            "commit",
        ]
    elif status in {"blueprint_ready", "execution_ready"}:
        next_owner = "implementation"
        next_action = "implement_validate_review_and_close"
        downstream_owners = ["review-execution", "close-slice", "commit"]
    elif status == "closed":
        next_owner = "commit"
        next_action = "commit_completed_slice"
        downstream_owners = []
    else:
        next_owner = "guide-execution"
        next_action = "resolve_active_slice"
        downstream_owners = ["implementation", "review-execution", "close-slice", "commit"]

    handoff_payload = HandoffPayload(
        target_type=target_type,
        target_id=target_id,
        planned_slice_id=(
            backlog_entry.planned_slice_id if backlog_entry is not None else str(slice_row["id"])
        ),
        execution_slice_id=str(slice_row["id"]),
        execution_slice_path=str(slice_row["path"]),
        slice_status=status,
        next_owner=next_owner,
        action="resume_active_slice",
    ).to_dict()

    return {
        "slice_id": str(slice_row["id"]),
        "slice_path": str(slice_row["path"]),
        "slice_status": status,
        "next_owner": next_owner,
        "next_action": next_action,
        "validation_hint": validation_hint,
        "missing_artifacts": missing_artifacts,
        "downstream_owners": downstream_owners,
        "handoff_payload": handoff_payload,
    }


def bootstrap_next_slice(
    selector: str, explicit_scope: Optional[str] = None
) -> BootstrapResult:
    backlog = resolve_backlog(selector, explicit_scope=explicit_scope)
    if backlog.active_execution_slices:
        raise RuntimeError(
            "Cannot bootstrap the next planned slice while another mapped execution "
            "slice is still active: "
            + ", ".join(backlog.active_execution_slices)
        )

    if not backlog.ready_next:
        completed = all(entry.state == "completed" for entry in backlog.entries)
        return BootstrapResult(
            backlog=backlog,
            bootstrapped_slice_id=None,
            bootstrapped_slice_path=None,
            slice_status=None,
            checkpoint_slice_id=None,
            dirty_worktree_paths=[],
            next_owner=None,
            completed=completed,
            action="complete" if completed else "blocked",
            requested_command="bootstrap_next",
            delegate_result=None,
        )

    planning_module = load_module(GUIDE_PLANNING_SCRIPT, "manage_planning")
    execution_module = load_module(GUIDE_EXECUTION_SCRIPT, "manage_execution")
    _, target_dir, _, scope_context, _ = resolve_target(
        planning_module, selector, explicit_scope
    )
    checkpoint_required = require_commit_checkpoint(
        backlog, str(scope_context.repo_root), requested_command="bootstrap_next"
    )
    if checkpoint_required is not None:
        return checkpoint_required

    next_planned_slice_id = backlog.ready_next[0]
    entry = next(
        item for item in backlog.entries if item.planned_slice_id == next_planned_slice_id
    )
    _, created = execution_module.create_slice(
        next_planned_slice_id,
        entry.title,
        scope_context=scope_context,
    )
    execution_rows = execution_module.parse_registry(scope_context=scope_context)
    slice_row = execution_module.resolve_slice(execution_rows, next_planned_slice_id)
    if slice_row is None:
        raise RuntimeError(
            f"Bootstrapped slice could not be resolved: {next_planned_slice_id}"
        )
    if not created and str(slice_row["status"]) != "closed":
        raise RuntimeError(
            f"Execution slice '{next_planned_slice_id}' already exists with status "
            f"'{slice_row['status']}'."
        )

    record_execution_slice_id(
        Path(target_dir) / "slice-traceability.md",
        next_planned_slice_id,
        next_planned_slice_id,
    )
    refreshed_backlog = resolve_backlog(selector, explicit_scope=explicit_scope)
    approval_required = require_approval_checkpoint(
        refreshed_backlog,
        scope_context=scope_context,
        execution_module=execution_module,
        requested_command="bootstrap_next",
    )
    if approval_required is not None:
        return approval_required
    delegate_result = maybe_delegate_to_ship_slice(
        refreshed_backlog,
        scope_context=scope_context,
        execution_module=execution_module,
    )
    return BootstrapResult(
        backlog=refreshed_backlog,
        bootstrapped_slice_id=next_planned_slice_id,
        bootstrapped_slice_path=str(slice_row["path"]),
        slice_status=str(slice_row["status"]),
        checkpoint_slice_id=None,
        dirty_worktree_paths=[],
        next_owner=(
            str(delegate_result["next_owner"])
            if delegate_result is not None and "next_owner" in delegate_result
            else (
                str(refreshed_backlog.active_slice_handoff["next_owner"])
                if refreshed_backlog.active_slice_handoff is not None
                else "guide-execution"
            )
        ),
        completed=False,
        action="delegated_to_ship_slice" if delegate_result is not None else "bootstrap_next_slice",
        requested_command="bootstrap_next",
        delegate_result=delegate_result,
    )


def resume_execution(
    selector: str, explicit_scope: Optional[str] = None
) -> BootstrapResult:
    backlog = resolve_backlog(selector, explicit_scope=explicit_scope)
    if len(backlog.active_execution_slices) > 1:
        raise RuntimeError(
            "Cannot resume while multiple mapped execution slices are active: "
            + ", ".join(backlog.active_execution_slices)
        )

    planning_module = load_module(GUIDE_PLANNING_SCRIPT, "manage_planning")
    execution_module = load_module(GUIDE_EXECUTION_SCRIPT, "manage_execution")
    _, _, _, scope_context, _ = resolve_target(
        planning_module, selector, explicit_scope
    )

    if backlog.active_execution_slices:
        active_slice_id = backlog.active_execution_slices[0]
        execution_rows = execution_module.parse_registry(scope_context=scope_context)
        slice_row = execution_module.resolve_slice(execution_rows, active_slice_id)
        if slice_row is None:
            raise RuntimeError(
                f"Mapped active execution slice could not be resolved: {active_slice_id}"
            )
        approval_required = require_approval_checkpoint(
            backlog,
            scope_context=scope_context,
            execution_module=execution_module,
            requested_command="resume",
        )
        if approval_required is not None:
            return approval_required
        delegate_result = maybe_delegate_to_ship_slice(
            backlog,
            scope_context=scope_context,
            execution_module=execution_module,
        )
        return BootstrapResult(
            backlog=backlog,
            bootstrapped_slice_id=active_slice_id,
            bootstrapped_slice_path=str(slice_row["path"]),
            slice_status=str(slice_row["status"]),
            checkpoint_slice_id=None,
            dirty_worktree_paths=[],
            next_owner=(
                str(delegate_result["next_owner"])
                if delegate_result is not None and "next_owner" in delegate_result
                else (
                    str(backlog.active_slice_handoff["next_owner"])
                    if backlog.active_slice_handoff is not None
                    else "guide-execution"
                )
            ),
            completed=False,
            action="delegated_to_ship_slice" if delegate_result is not None else "resume_active_slice",
            requested_command="resume",
            delegate_result=delegate_result,
        )

    checkpoint_required = require_commit_checkpoint(
        backlog, str(scope_context.repo_root), requested_command="resume"
    )
    if checkpoint_required is not None:
        return checkpoint_required

    if backlog.ready_next:
        return bootstrap_next_slice(selector, explicit_scope=explicit_scope)

    completed = all(entry.state == "completed" for entry in backlog.entries)
    if completed:
        return BootstrapResult(
            backlog=backlog,
            bootstrapped_slice_id=None,
            bootstrapped_slice_path=None,
            slice_status=None,
            checkpoint_slice_id=None,
            dirty_worktree_paths=[],
            next_owner=None,
            completed=True,
            action="complete",
            requested_command="resume",
            delegate_result=None,
        )

    blocked = [
        entry.planned_slice_id for entry in backlog.entries if entry.state == "blocked"
    ]
    raise RuntimeError(
        "No ready planned slice remains while unfinished slices are blocked: "
        + ", ".join(blocked)
    )


def read_dirty_worktree_paths(repo_root: str) -> List[str]:
    result = subprocess.run(
        ["git", "-C", repo_root, "status", "--short", "--untracked-files=no"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError("Unable to inspect git worktree state for commit checkpoint.")
    return [line.rstrip() for line in result.stdout.splitlines() if line.strip()]


def require_commit_checkpoint(
    backlog: BacklogResolution, repo_root: str, *, requested_command: str
) -> Optional[BootstrapResult]:
    completed_entries = [entry for entry in backlog.entries if entry.state == "completed"]
    if not completed_entries:
        return None
    dirty_worktree_paths = read_dirty_worktree_paths(repo_root)
    if not dirty_worktree_paths:
        return None
    return BootstrapResult(
        backlog=backlog,
        bootstrapped_slice_id=None,
        bootstrapped_slice_path=None,
        slice_status=None,
        checkpoint_slice_id=completed_entries[-1].planned_slice_id,
        dirty_worktree_paths=dirty_worktree_paths,
        next_owner="commit",
        completed=False,
        action="commit_checkpoint_required",
        requested_command=requested_command,
        delegate_result=None,
    )


def require_approval_checkpoint(
    backlog: BacklogResolution,
    *,
    scope_context,
    execution_module,
    requested_command: str,
) -> Optional[BootstrapResult]:
    if backlog.active_slice_handoff is None:
        return None
    ship_config = ship_accelerator_config(scope_context, execution_module)
    if not bool(ship_config.get("delegate_to_ship_slice", False)):
        return None

    gate = backlog.approval_gate
    if not bool(gate.get("required")):
        return None
    if str(gate.get("decision")) == "approved":
        return None

    return BootstrapResult(
        backlog=backlog,
        bootstrapped_slice_id=None,
        bootstrapped_slice_path=None,
        slice_status=None,
        checkpoint_slice_id=None,
        dirty_worktree_paths=[],
        next_owner="approval",
        completed=False,
        action="approval_required",
        requested_command=requested_command,
        delegate_result=None,
    )


def ship_accelerator_config(scope_context, execution_module) -> Dict[str, object]:
    raw_config = execution_module.load_raw_config(required=False, scope_context=scope_context)
    accelerators = raw_config.get("accelerators", {})
    if not isinstance(accelerators, dict):
        return {}
    ship_config = accelerators.get("ship", {})
    return ship_config if isinstance(ship_config, dict) else {}



def _relative_display_path(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def _extract_execution_reconciliation_block(markdown: str) -> Optional[str]:
    return markdown_repository.extract_execution_reconciliation_block(markdown)


def _parse_execution_reconciliation_fields(block_text: str) -> Dict[str, str]:
    return markdown_repository.parse_execution_reconciliation_fields(block_text)


def inspect_execution_reconciliation(
    target_dir: Path, backlog: BacklogResolution
) -> Dict[str, object]:
    design_path = target_dir / "system-design.md"
    expected_planned_slice_ids = [entry.planned_slice_id for entry in backlog.entries]
    summary: Dict[str, object] = {
        "required": True,
        "owner": "reconcile-execution",
        "path": _relative_display_path(design_path),
        "expected_planned_slice_ids": expected_planned_slice_ids,
        "reviewed_planned_slice_ids": [],
        "missing_planned_slice_ids": list(expected_planned_slice_ids),
        "unexpected_planned_slice_ids": [],
        "status": "missing_design",
        "archivable": False,
        "reason": "Missing system-design.md for execution reconciliation.",
    }
    if not design_path.exists():
        return summary

    summary["status"] = "missing_block"
    summary["reason"] = (
        "Missing execution reconciliation block in system-design.md."
    )
    markdown = design_path.read_text(encoding="utf-8")
    block_text = _extract_execution_reconciliation_block(markdown)
    if block_text is None:
        return summary

    fields = _parse_execution_reconciliation_fields(block_text)
    raw_status = fields.get("status", "")
    normalized_status = raw_status.strip().lower().replace("-", "_")
    reviewed_planned_slice_ids = _split_cell_values(
        fields.get("reviewed planned slice ids", "")
    )
    expected_set = set(expected_planned_slice_ids)
    reviewed_set = set(reviewed_planned_slice_ids)
    missing_planned_slice_ids = [
        slice_id for slice_id in expected_planned_slice_ids if slice_id not in reviewed_set
    ]
    unexpected_planned_slice_ids = [
        slice_id for slice_id in reviewed_planned_slice_ids if slice_id not in expected_set
    ]
    summary.update(
        {
            "reviewed_planned_slice_ids": reviewed_planned_slice_ids,
            "missing_planned_slice_ids": missing_planned_slice_ids,
            "unexpected_planned_slice_ids": unexpected_planned_slice_ids,
        }
    )
    if normalized_status != "aligned":
        summary["status"] = "invalid_status"
        summary["reason"] = (
            "Execution reconciliation must declare 'Status: aligned' before archive."
        )
        return summary
    if missing_planned_slice_ids or unexpected_planned_slice_ids:
        summary["status"] = "coverage_mismatch"
        summary["reason"] = (
            "Execution reconciliation coverage does not match the completed planned slice IDs."
        )
        return summary

    summary["status"] = "aligned"
    summary["archivable"] = True
    summary["reason"] = "Execution reconciliation is aligned and covers all planned slices."
    return summary


def finalize_target(
    selector: str, explicit_scope: Optional[str] = None
) -> BootstrapResult:
    backlog = resolve_backlog(selector, explicit_scope=explicit_scope)
    if backlog.active_execution_slices:
        raise RuntimeError(
            "Cannot finalize while mapped execution slices are still active: "
            + ", ".join(backlog.active_execution_slices)
        )
    if not backlog.entries or not all(entry.state == "completed" for entry in backlog.entries):
        raise RuntimeError(
            "Cannot finalize while planned slices remain unfinished."
        )

    sync_results = sync_completed_owners(
        owner_type=backlog.target_type, owner_id=backlog.target_id
    )
    if sync_results:
        backlog = resolve_backlog(selector, explicit_scope=explicit_scope)

    if backlog.planning_status != "implemented":
        raise RuntimeError(
            f"Planning target '{backlog.target_id}' must be in 'implemented' status before finalization. "
            f"Current status: '{backlog.planning_status}'."
        )

    planning_module = load_module(GUIDE_PLANNING_SCRIPT, "manage_planning")
    _, target_dir, _, scope_context, _ = resolve_target(
        planning_module, selector, explicit_scope
    )
    checkpoint_required = require_commit_checkpoint(
        backlog, str(scope_context.repo_root), requested_command="finalize"
    )
    if checkpoint_required is not None:
        return checkpoint_required

    reconciliation = inspect_execution_reconciliation(Path(target_dir), backlog)
    if not bool(reconciliation.get("archivable")):
        return BootstrapResult(
            backlog=backlog,
            bootstrapped_slice_id=None,
            bootstrapped_slice_path=None,
            slice_status=None,
            checkpoint_slice_id=None,
            dirty_worktree_paths=[],
            next_owner="reconcile-execution",
            completed=False,
            action="reconciliation_required",
            requested_command="finalize",
            delegate_result=None,
            finalization=reconciliation,
            archive_result=None,
        )

    archive_module = load_module(ARCHIVE_DATA_SCRIPT, "archive_data")
    try:
        archive_result = archive_module.build_archive_result(
            backlog.target_type, backlog.target_id, True
        )
    except archive_module.ArchiveUsageError as exc:
        raise RuntimeError(str(exc))

    refreshed_backlog = resolve_backlog(selector, explicit_scope=explicit_scope)
    refreshed_reconciliation = inspect_execution_reconciliation(
        Path(target_dir), refreshed_backlog
    )
    return BootstrapResult(
        backlog=refreshed_backlog,
        bootstrapped_slice_id=None,
        bootstrapped_slice_path=None,
        slice_status=None,
        checkpoint_slice_id=None,
        dirty_worktree_paths=[],
        next_owner="none",
        completed=True,
        action="archived",
        requested_command="finalize",
        delegate_result=None,
        finalization=refreshed_reconciliation,
        archive_result=archive_result,
    )


def maybe_delegate_to_ship_slice(
    backlog: BacklogResolution,
    *,
    scope_context,
    execution_module,
) -> Optional[Dict[str, object]]:
    if backlog.active_slice_handoff is None or not SHIP_SLICE_SCRIPT.is_file():
        return None
    ship_config = ship_accelerator_config(scope_context, execution_module)
    if not bool(ship_config.get("delegate_to_ship_slice", False)):
        return None

    handoff_payload = backlog.active_slice_handoff.get("handoff_payload")
    if not isinstance(handoff_payload, dict):
        return None

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".json",
        prefix="ship-handoff-",
        delete=False,
    ) as handle:
        json.dump(handoff_payload, handle, indent=2)
        handle.write("\n")
        handoff_path = Path(handle.name)

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "sirius_skills.cli",
                "ship-slice",
                "--handoff",
                str(handoff_path),
                "--json",
            ],
            cwd=str(scope_context.repo_root),
            check=False,
            capture_output=True,
            text=True,
        )
    finally:
        handoff_path.unlink(missing_ok=True)

    if result.returncode != 0:
        raise RuntimeError(
            "ship-slice delegation failed: "
            + (result.stderr.strip() or result.stdout.strip() or "unknown error")
        )
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        raise RuntimeError("ship-slice delegation did not return a JSON object.")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Resolve one reviewed feature or subfeature into remaining planned slices "
            "using planning traceability and execution closure state."
        )
    )
    parser.add_argument("target", help="Feature slug, subfeature slug, or planning packet path.")
    parser.add_argument(
        "--scope",
        help="Optional planning scope path when the target is outside the active scope.",
    )
    parser.add_argument(
        "--bootstrap-next",
        action="store_true",
        help="Bootstrap the next ready execution slice and record its traceability mapping.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume an active mapped slice or bootstrap the next ready slice.",
    )
    parser.add_argument(
        "--finalize",
        action="store_true",
        help=(
            "Require a durable execution reconciliation record for a completed implemented "
            "target, then archive its closed slices."
        ),
    )
    parser.add_argument(
        "--approve",
        action="store_true",
        help=(
            "Record durable approval for a planning_reviewed target so delegated "
            "execution autopilot can proceed."
        ),
    )
    parser.add_argument(
        "--approval-note",
        help="Optional note recorded with the approval decision.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable output.")
    return parser


def render_text(result: BacklogResolution) -> str:
    gate = result.approval_gate
    lines = [
        f"Target: {result.target_type} {result.target_id}",
        f"Planning status: {result.planning_status}",
        f"Approval gate: {gate.get('decision')}",
        f"Path: {result.target_path}",
        f"Increment order: {', '.join(result.increment_order) if result.increment_order else '-'}",
        f"Current increment: {result.current_increment or '-'}",
        f"Completed increments: {', '.join(result.completed_increments) if result.completed_increments else '-'}",
        f"Ready next: {', '.join(result.ready_next) if result.ready_next else '-'}",
        f"Active execution slices: {', '.join(result.active_execution_slices) if result.active_execution_slices else '-'}",
        "",
        "Planned slices:",
    ]
    gate_reason = str(gate.get("reason") or "").strip()
    if gate_reason:
        lines.insert(3, f"Approval reason: {gate_reason}")
    for entry in result.entries:
        suffix = ""
        if entry.depends_on:
            suffix = f" (depends on: {', '.join(entry.depends_on)})"
        increment_suffix = (
            f" [increments: {', '.join(entry.increment_ids)}]"
            if entry.increment_ids
            else ""
        )
        lines.append(f"- {entry.planned_slice_id}{increment_suffix}: {entry.state}{suffix}")
    if result.active_slice_handoff is not None:
        lines.extend(render_active_slice_handoff_lines(result.active_slice_handoff))
    return "\n".join(lines)


def render_active_slice_handoff_lines(handoff: Dict[str, object]) -> List[str]:
    downstream_owners = handoff.get("downstream_owners", [])
    missing_artifacts = handoff.get("missing_artifacts", [])
    lines = [
        "",
        "Active slice handoff:",
        f"- Slice: {handoff['slice_id']}",
        f"- Slice path: {handoff['slice_path']}",
        f"- Slice status: {handoff['slice_status']}",
        f"- Next owner: {handoff['next_owner']}",
        f"- Next action: {handoff['next_action']}",
    ]
    validation_hint = str(handoff.get("validation_hint") or "").strip()
    if validation_hint:
        lines.append(f"- Validation hint: {validation_hint}")
    if missing_artifacts:
        lines.append(f"- Missing artifacts: {', '.join(str(item) for item in missing_artifacts)}")
    if downstream_owners:
        lines.append(
            "- Downstream owners after this step: "
            + ", ".join(str(owner) for owner in downstream_owners)
        )
    return lines


def render_bootstrap_text(result: BootstrapResult) -> str:
    lines = [render_text(result.backlog)]
    if result.action == "resume_active_slice" and result.bootstrapped_slice_id:
        lines.extend(
            [
                "",
                f"Resume slice: {result.bootstrapped_slice_id}",
                f"Slice path: {result.bootstrapped_slice_path}",
                f"Slice status: {result.slice_status}",
                f"Next owner: {result.next_owner}",
            ]
        )
    elif result.action == "bootstrap_next_slice" and result.bootstrapped_slice_id:
        lines.extend(
            [
                "",
                f"Bootstrapped slice: {result.bootstrapped_slice_id}",
                f"Slice path: {result.bootstrapped_slice_path}",
                f"Slice status: {result.slice_status}",
                f"Next owner: {result.next_owner}",
            ]
        )
    elif result.action == "commit_checkpoint_required":
        lines.extend(
            [
                "",
                f"Commit checkpoint required for: {result.checkpoint_slice_id}",
                f"Next owner: {result.next_owner}",
                "Dirty worktree paths:",
                *[f"- {path}" for path in result.dirty_worktree_paths],
            ]
        )
    elif result.action == "approval_required":
        lines.extend(
            [
                "",
                "Approval checkpoint required before delegated execution starts.",
                f"Next owner: {result.next_owner}",
            ]
        )
    elif result.action == "reconciliation_required":
        finalization = result.finalization or {}
        lines.extend(
            [
                "",
                "Execution reconciliation is required before archive.",
                f"Next owner: {result.next_owner}",
                f"Reconciliation status: {finalization.get('status', 'unknown')}",
                f"Reconciliation path: {finalization.get('path', '-')}",
                f"Reason: {finalization.get('reason', '-')}",
            ]
        )
        missing_ids = finalization.get("missing_planned_slice_ids")
        if isinstance(missing_ids, list) and missing_ids:
            lines.append(
                "Missing planned slice coverage: " + ", ".join(str(item) for item in missing_ids)
            )
        unexpected_ids = finalization.get("unexpected_planned_slice_ids")
        if isinstance(unexpected_ids, list) and unexpected_ids:
            lines.append(
                "Unexpected planned slice coverage: "
                + ", ".join(str(item) for item in unexpected_ids)
            )
    elif result.action == "archived":
        archive_result = result.archive_result or {}
        applied = archive_result.get("applied") if isinstance(archive_result, dict) else None
        message = applied.get("message") if isinstance(applied, dict) else None
        lines.extend(
            [
                "",
                "Finalization complete.",
                str(message or "Archived completed target after reconciliation."),
            ]
        )
    elif result.completed:
        lines.extend(["", "All planned slices are already completed."])
    else:
        lines.extend(["", "No ready slice was bootstrapped."])
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    selected_actions = sum(
        1 for flag in (args.bootstrap_next, args.resume, args.finalize) if flag
    )
    if selected_actions > 1:
        print(
            "Choose at most one of --bootstrap-next, --resume, or --finalize.",
            file=sys.stderr,
        )
        return 2
    approval_record: Optional[Dict[str, object]] = None
    try:
        if args.approve:
            approval_record = record_approval_decision(
                args.target,
                explicit_scope=args.scope,
                approval_note=args.approval_note,
            )
        if args.resume:
            result = resume_execution(args.target, explicit_scope=args.scope)
        elif args.finalize:
            result = finalize_target(args.target, explicit_scope=args.scope)
        elif args.bootstrap_next:
            result = bootstrap_next_slice(args.target, explicit_scope=args.scope)
        else:
            result = resolve_backlog(args.target, explicit_scope=args.scope)
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.json:
        payload = result.to_dict() if hasattr(result, "to_dict") else result
        if approval_record is not None and isinstance(payload, dict):
            payload["approval_recorded"] = approval_record
        print(json.dumps(payload, indent=2))
    else:
        if approval_record is not None:
            print(
                "Recorded approval at "
                f"{approval_record['approval_path']} ({approval_record['approved_at']})."
            )
        if isinstance(result, BootstrapResult):
            print(render_bootstrap_text(result))
        else:
            print(render_text(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
