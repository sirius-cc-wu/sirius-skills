from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

from sirius_skills.lib.workflow_state.inventory import iter_traceability_records, load_inventory
from sirius_skills.lib.workflow_state.models import Inventory, SemanticPreviewRecord, TransitionCheckResult
from sirius_skills.lib.workflow_state.semantic_preview import build_semantic_preview


OK_OUTCOME = "ok"
WARNING_OUTCOME = "warning"
BLOCK_OUTCOME = "block"
PREVIEW_PREFIX = "Preview only:"


def _rewrite_message(message: str, severity: str) -> str:
    stripped = message.strip()
    if stripped.startswith(PREVIEW_PREFIX):
        stripped = stripped[len(PREVIEW_PREFIX) :].strip()
    label = "Transition warning" if severity == WARNING_OUTCOME else "Transition block"
    return f"{label}: {stripped}"


def _clone_record(record: SemanticPreviewRecord, severity: str) -> SemanticPreviewRecord:
    return SemanticPreviewRecord(
        artifact_type=record.artifact_type,
        artifact_id=record.artifact_id,
        path=record.path,
        code=record.code,
        message=_rewrite_message(record.message, severity),
        apply_supported=record.apply_supported,
    )


def _dedupe(records: Sequence[SemanticPreviewRecord]) -> List[SemanticPreviewRecord]:
    seen: Set[Tuple[str, str, str, str, str]] = set()
    result: List[SemanticPreviewRecord] = []
    for item in records:
        key = (item.artifact_type, item.artifact_id, item.path, item.code, item.message)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _subfeature_dirs_by_id(inventory: Inventory) -> Dict[str, Path]:
    result: Dict[str, Path] = {}
    for paths in inventory.subfeature_dirs_by_feature.values():
        for subfeature_dir in paths:
            result[subfeature_dir.name] = subfeature_dir
    return result


def _preview_records_by_owner(
    inventory: Inventory, artifact_types: Optional[Sequence[str]] = None
) -> Dict[Tuple[str, str], List[SemanticPreviewRecord]]:
    records = build_semantic_preview(inventory, artifact_types)
    by_owner: Dict[Tuple[str, str], List[SemanticPreviewRecord]] = {}
    for record in records:
        by_owner.setdefault((record.artifact_type, record.artifact_id), []).append(record)
    return by_owner


def _records_for_related_slice_owners(
    inventory: Inventory, slice_id: str
) -> List[SemanticPreviewRecord]:
    preview_by_owner = _preview_records_by_owner(inventory, ("feature", "subfeature"))
    findings: List[SemanticPreviewRecord] = []
    for record in iter_traceability_records(inventory):
        if slice_id not in record.planned_slice_ids and slice_id not in record.execution_slice_ids:
            continue
        findings.extend(
            _clone_record(item, WARNING_OUTCOME)
            for item in preview_by_owner.get((record.owner_type, record.owner_id), [])
        )
    return _dedupe(findings)


def _subfeature_blockers_for_slice_close(
    inventory: Inventory, slice_id: str
) -> List[SemanticPreviewRecord]:
    subfeature_dirs = _subfeature_dirs_by_id(inventory)
    findings: List[SemanticPreviewRecord] = []
    for record in iter_traceability_records(inventory):
        if record.owner_type != "subfeature":
            continue
        if slice_id not in record.planned_slice_ids and slice_id not in record.execution_slice_ids:
            continue
        subfeature_dir = subfeature_dirs.get(record.owner_id)
        if subfeature_dir is None:
            continue
        metadata = inventory.context.subfeatures.read_metadata(str(subfeature_dir))
        current_status = str(metadata.get("status") or "")
        if current_status in {"reviewed", "finalized"}:
            continue
        findings.append(
            SemanticPreviewRecord(
                artifact_type="subfeature",
                artifact_id=record.owner_id,
                path=record.owner_path,
                code="transition_subfeature_review_required",
                message=(
                    f"Transition block: closing slice '{slice_id}' would leave linked "
                    f"subfeature '{record.owner_id}' in status '{current_status}'. "
                    "Advance the subfeature to at least 'reviewed' before closing linked slices "
                    "or rerun with --force."
                ),
            )
        )
    return _dedupe(findings)


def _open_slice_warnings_for_subfeature(
    inventory: Inventory, subfeature_id: str
) -> List[SemanticPreviewRecord]:
    slice_rows_by_id = {row.id: row for row in inventory.slice_registry if row.id}
    findings: List[SemanticPreviewRecord] = []
    for record in iter_traceability_records(inventory):
        if record.owner_type != "subfeature" or record.owner_id != subfeature_id:
            continue
        linked_rows = [
            slice_rows_by_id[slice_id]
            for slice_id in record.planned_slice_ids
            if slice_id in slice_rows_by_id
        ]
        open_slice_ids = sorted(row.id for row in linked_rows if row.status != "closed")
        if not open_slice_ids:
            continue
        findings.append(
            SemanticPreviewRecord(
                artifact_type="subfeature",
                artifact_id=subfeature_id,
                path=record.owner_path,
                code="transition_open_execution_slices",
                message=(
                    f"Transition warning: subfeature '{subfeature_id}' is being finalized "
                    "while linked execution slices remain open: "
                    + ", ".join(open_slice_ids)
                    + "."
                ),
            )
        )
    return _dedupe(findings)


def _result(
    block_findings: Sequence[SemanticPreviewRecord],
    warning_findings: Sequence[SemanticPreviewRecord],
    override_flag: Optional[str] = None,
) -> TransitionCheckResult:
    if block_findings:
        return TransitionCheckResult(
            outcome=BLOCK_OUTCOME,
            findings=_dedupe(block_findings),
            override_flag=override_flag,
        )
    if warning_findings:
        return TransitionCheckResult(
            outcome=WARNING_OUTCOME,
            findings=_dedupe(warning_findings),
            override_flag=override_flag,
        )
    return TransitionCheckResult(outcome=OK_OUTCOME, findings=[], override_flag=override_flag)


def _load_inventory_if_available() -> Optional[Inventory]:
    try:
        return load_inventory()
    except (RuntimeError, ValueError):
        return None


def evaluate_feature_transition(feature_id: str, target_status: str) -> TransitionCheckResult:
    if target_status not in {"slice_ready", "implemented"}:
        return TransitionCheckResult(outcome=OK_OUTCOME, findings=[])
    inventory = _load_inventory_if_available()
    if inventory is None:
        return TransitionCheckResult(outcome=OK_OUTCOME, findings=[])
    preview_by_owner = _preview_records_by_owner(inventory, ("feature",))
    warnings = [
        _clone_record(item, WARNING_OUTCOME)
        for item in preview_by_owner.get(("feature", feature_id), [])
    ]
    return _result([], warnings)


def evaluate_subfeature_transition(
    subfeature_id: str, target_status: str
) -> TransitionCheckResult:
    if target_status != "finalized":
        return TransitionCheckResult(outcome=OK_OUTCOME, findings=[])
    inventory = _load_inventory_if_available()
    if inventory is None:
        return TransitionCheckResult(outcome=OK_OUTCOME, findings=[])
    warnings: List[SemanticPreviewRecord] = []
    warnings.extend(_open_slice_warnings_for_subfeature(inventory, subfeature_id))
    preview_by_owner = _preview_records_by_owner(inventory, ("subfeature",))
    warnings.extend(
        _clone_record(item, WARNING_OUTCOME)
        for item in preview_by_owner.get(("subfeature", subfeature_id), [])
    )
    return _result([], warnings)


def evaluate_slice_transition(slice_id: str, target_status: str) -> TransitionCheckResult:
    if target_status != "closed":
        return TransitionCheckResult(outcome=OK_OUTCOME, findings=[])
    inventory = _load_inventory_if_available()
    if inventory is None:
        return TransitionCheckResult(outcome=OK_OUTCOME, findings=[], override_flag="--force")
    blockers = _subfeature_blockers_for_slice_close(inventory, slice_id)
    warnings = _records_for_related_slice_owners(inventory, slice_id)
    return _result(blockers, warnings, override_flag="--force")


def format_transition_message(base_message: str, result: TransitionCheckResult) -> str:
    if not result.findings:
        return base_message
    details = "\n".join(f"- {item.code}: {item.message}" for item in result.findings)
    return f"{base_message}\nTransition findings:\n{details}"
