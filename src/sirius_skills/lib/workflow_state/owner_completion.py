from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from sirius_skills.lib.workflow_state.inventory import iter_traceability_records, load_inventory
from sirius_skills.lib.workflow_state.models import Inventory, TraceabilityRecord


OwnerKey = Tuple[str, str, str]


def _safe_load_inventory() -> Optional[Inventory]:
    try:
        return load_inventory()
    except (RuntimeError, ValueError):
        return None


def _execution_ids_by_planned_slice(
    records: Sequence[TraceabilityRecord],
) -> Dict[str, List[str]]:
    mapping: Dict[str, List[str]] = {}
    for record in records:
        planned_slice_ids = list(record.planned_slice_ids)
        execution_slice_ids = list(record.execution_slice_ids)
        if not planned_slice_ids or not execution_slice_ids:
            continue
        if len(planned_slice_ids) == 1:
            bucket = mapping.setdefault(planned_slice_ids[0], [])
            for execution_slice_id in execution_slice_ids:
                if execution_slice_id not in bucket:
                    bucket.append(execution_slice_id)
            continue
        if len(planned_slice_ids) == len(execution_slice_ids):
            for planned_slice_id, execution_slice_id in zip(
                planned_slice_ids, execution_slice_ids
            ):
                bucket = mapping.setdefault(planned_slice_id, [])
                if execution_slice_id not in bucket:
                    bucket.append(execution_slice_id)
    return mapping


def _owner_records_for_scope(
    inventory: Inventory,
    *,
    slice_id: Optional[str] = None,
    owner_type: Optional[str] = None,
    owner_id: Optional[str] = None,
) -> Dict[OwnerKey, List[TraceabilityRecord]]:
    records = iter_traceability_records(inventory)
    owner_keys: set[OwnerKey] = set()
    for record in records:
        if slice_id is not None and (
            slice_id not in record.planned_slice_ids
            and slice_id not in record.execution_slice_ids
        ):
            continue
        if owner_type is not None and record.owner_type != owner_type:
            continue
        if owner_id is not None and record.owner_id != owner_id:
            continue
        owner_keys.add((record.owner_type, record.owner_id, record.owner_path))

    grouped: Dict[OwnerKey, List[TraceabilityRecord]] = {}
    for record in records:
        key = (record.owner_type, record.owner_id, record.owner_path)
        if key not in owner_keys:
            continue
        grouped.setdefault(key, []).append(record)
    return grouped


def _completed_owner_execution_slices(
    records: Sequence[TraceabilityRecord], execution_status_by_id: Dict[str, str]
) -> Optional[List[str]]:
    planned_slice_ids: List[str] = []
    for record in records:
        for planned_slice_id in record.planned_slice_ids:
            if planned_slice_id and planned_slice_id not in planned_slice_ids:
                planned_slice_ids.append(planned_slice_id)
    if not planned_slice_ids:
        return None

    execution_ids_by_planned_slice = _execution_ids_by_planned_slice(records)
    closed_execution_slice_ids: List[str] = []
    for planned_slice_id in planned_slice_ids:
        execution_slice_ids = execution_ids_by_planned_slice.get(planned_slice_id, [])
        closed_ids = [
            execution_slice_id
            for execution_slice_id in execution_slice_ids
            if execution_status_by_id.get(execution_slice_id) == "closed"
        ]
        if not closed_ids:
            return None
        for closed_id in closed_ids:
            if closed_id not in closed_execution_slice_ids:
                closed_execution_slice_ids.append(closed_id)
    return sorted(closed_execution_slice_ids)


def _sync_feature_completion(
    inventory: Inventory, owner_id: str, owner_path: str
) -> Optional[Dict[str, object]]:
    planning = inventory.context.planning
    scope_context = planning.SCOPE_RUNTIME.resolve_scope_context()
    planning.sync_registry(scope_context=scope_context)
    rows, feature, scope_context = planning.resolve_feature_lookup(owner_path)
    if feature is None:
        rows, feature, scope_context = planning.resolve_feature_lookup(owner_id)
    if feature is None:
        raise RuntimeError(
            f"Unable to resolve planning feature '{owner_id}' for completion handoff."
        )

    feature_dir = planning.feature_dir_for_row(feature, scope_context=scope_context)
    metadata = planning.read_metadata(feature_dir)
    if str(metadata.get("status")) == "implemented" and not metadata.get("ready_slice_ids"):
        return None

    force = not planning.can_transition(str(metadata.get("status") or ""), "implemented")
    success, message = planning.update_feature_status(
        rows,
        feature,
        "implemented",
        force=force,
        slice_ids=[],
        scope_context=scope_context,
    )
    if not success:
        raise RuntimeError(message)
    return {
        "owner_type": "feature",
        "owner_id": owner_id,
        "status": "implemented",
        "message": message,
    }


def _ensure_subfeature_registry_row(
    inventory: Inventory,
    feature_dir: str,
    subfeature_dir: str,
    subfeature_id: str,
    scope_context: object,
):
    planning = inventory.context.planning
    subfeatures = inventory.context.subfeatures
    subfeatures.ensure_subfeature_registry(feature_dir)
    rows = subfeatures.load_registry(feature_dir)
    selected = subfeatures.find_subfeature(rows, subfeature_id)
    if selected is not None:
        return selected

    metadata = subfeatures.read_metadata(subfeature_dir)
    rows.append(
        subfeatures.normalize_registry_row(
            {
                "subfeature_id": subfeature_id,
                "status": metadata.get("status", "draft"),
                "subfeature_type": metadata.get("subfeature_type", "additive"),
                "updated_at": metadata.get("updated_at"),
                "path": planning.relative_path_from_scope_root(
                    subfeature_dir, scope_context
                ),
            }
        )
    )
    subfeatures.write_registry(feature_dir, rows)
    refreshed_rows = subfeatures.load_registry(feature_dir)
    selected = subfeatures.find_subfeature(refreshed_rows, subfeature_id)
    if selected is None:
        raise RuntimeError(
            f"Unable to resolve subfeature '{subfeature_id}' after registry refresh."
        )
    return selected


def _sync_subfeature_completion(
    inventory: Inventory,
    owner_id: str,
    owner_path: str,
    closed_execution_slice_ids: List[str],
) -> Optional[Dict[str, object]]:
    planning = inventory.context.planning
    subfeatures = inventory.context.subfeatures
    scope_context = planning.SCOPE_RUNTIME.resolve_scope_context()
    planning.sync_registry(scope_context=scope_context)
    rows, subfeature_feature, scope_context = planning.resolve_feature_lookup(owner_path)
    if subfeature_feature is None:
        rows, subfeature_feature, scope_context = planning.resolve_feature_lookup(owner_id)
    if subfeature_feature is None:
        raise RuntimeError(
            f"Unable to resolve planning subfeature '{owner_id}' for completion handoff."
        )

    subfeature_dir = planning.feature_dir_for_row(
        subfeature_feature, scope_context=scope_context
    )
    metadata = subfeatures.read_metadata(subfeature_dir)
    if str(metadata.get("status")) == "finalized":
        return None

    parent_feature_dir = str(Path(subfeature_dir).parent.parent)
    selected = _ensure_subfeature_registry_row(
        inventory,
        parent_feature_dir,
        subfeature_dir,
        owner_id,
        scope_context,
    )
    force = not subfeatures.can_transition(str(metadata.get("status") or ""), "finalized")
    success, message = subfeatures.update_subfeature_status(
        planning,
        parent_feature_dir,
        selected,
        "finalized",
        scope_context,
        force=force,
        affected_slice_ids=closed_execution_slice_ids,
    )
    if not success:
        raise RuntimeError(message)
    return {
        "owner_type": "subfeature",
        "owner_id": owner_id,
        "status": "finalized",
        "message": message,
    }


def sync_completed_owners(
    *,
    slice_id: Optional[str] = None,
    owner_type: Optional[str] = None,
    owner_id: Optional[str] = None,
) -> List[Dict[str, object]]:
    """Promote completed planning owners from traced closed execution slices.

    This is the shared terminal reconciliation hook. It intentionally derives
    completion from traceability plus execution slice closure instead of relying
    on a specific caller such as close-slice.
    """
    inventory = _safe_load_inventory()
    if inventory is None:
        return []

    execution_status_by_id = {
        str(row.get("id") or "").strip(): str(row.get("status") or "").strip()
        for row in inventory.slice_rows
        if str(row.get("id") or "").strip()
    }
    owner_records = _owner_records_for_scope(
        inventory,
        slice_id=slice_id,
        owner_type=owner_type,
        owner_id=owner_id,
    )
    sync_results: List[Dict[str, object]] = []
    for (record_owner_type, record_owner_id, owner_path), records in owner_records.items():
        closed_execution_slice_ids = _completed_owner_execution_slices(
            records, execution_status_by_id
        )
        if not closed_execution_slice_ids:
            continue
        if record_owner_type == "feature":
            result = _sync_feature_completion(inventory, record_owner_id, owner_path)
        elif record_owner_type == "subfeature":
            result = _sync_subfeature_completion(
                inventory, record_owner_id, owner_path, closed_execution_slice_ids
            )
        else:
            result = None
        if result is not None:
            sync_results.append(result)
    return sync_results


def sync_owner_completion(slice_id: str) -> List[Dict[str, object]]:
    return sync_completed_owners(slice_id=slice_id)
