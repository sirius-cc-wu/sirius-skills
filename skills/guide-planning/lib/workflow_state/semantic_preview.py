from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

from workflow_state.inventory import normalize_dir_relpath, parse_traceability_records
from workflow_state.models import Inventory, SemanticPreviewRecord


VALID_ARTIFACT_TYPES = {"proposal", "feature", "subfeature", "slice"}


def _selected_types(raw_types: Sequence[str]) -> Set[str]:
    selected = {artifact_type for artifact_type in raw_types if artifact_type in VALID_ARTIFACT_TYPES}
    return selected or set(VALID_ARTIFACT_TYPES)


def _safe_read_metadata(reader, artifact_type: str, artifact_id: str, path: Path):
    try:
        return reader(str(path)), None
    except RuntimeError:
        return None, SemanticPreviewRecord(
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            path=normalize_dir_relpath(path),
            code="metadata_read_error",
            message="",
        )


def _dedupe_preview_records(
    preview_records: Sequence[SemanticPreviewRecord],
) -> List[SemanticPreviewRecord]:
    seen = set()
    result: List[SemanticPreviewRecord] = []
    for item in preview_records:
        key = (item.artifact_type, item.artifact_id, item.path, item.code, item.message)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _canonical_feature_slugs(
    inventory: Inventory,
) -> Tuple[Set[str], Dict[str, Dict[str, object]], Dict[str, str]]:
    slugs: Set[str] = set()
    metadata_by_slug: Dict[str, Dict[str, object]] = {}
    path_by_slug: Dict[str, str] = {}
    for feature_dir in inventory.feature_dirs:
        metadata, preview_record = _safe_read_metadata(
            inventory.context.planning.read_metadata,
            "feature",
            feature_dir.name,
            feature_dir,
        )
        if preview_record is not None or metadata is None:
            continue
        feature_slug = str(metadata.get("feature_slug") or feature_dir.name)
        slugs.add(feature_slug)
        metadata_by_slug[feature_slug] = metadata
        path_by_slug[feature_slug] = normalize_dir_relpath(feature_dir)
    return slugs, metadata_by_slug, path_by_slug


def _proposal_link_preview(
    inventory: Inventory,
    selected: Set[str],
    canonical_feature_slugs: Sequence[str],
) -> List[SemanticPreviewRecord]:
    if "proposal" not in selected:
        return []
    preview_records: List[SemanticPreviewRecord] = []
    candidate_suffix = (
        f" Candidate canonical features: {', '.join(canonical_feature_slugs)}."
        if canonical_feature_slugs
        else " No canonical features are currently available."
    )
    for proposal_dir in inventory.proposal_dirs:
        metadata, preview_record = _safe_read_metadata(
            inventory.context.propose.read_metadata,
            "proposal",
            proposal_dir.name,
            proposal_dir,
        )
        if preview_record is not None or metadata is None:
            continue
        proposal_path = normalize_dir_relpath(proposal_dir)
        for field_name, code in (
            ("target_feature", "repair_target_feature_link"),
            ("promoted_feature", "repair_promoted_feature_link"),
        ):
            value = metadata.get(field_name)
            if not isinstance(value, str) or not value.strip():
                continue
            if value in canonical_feature_slugs:
                continue
            preview_records.append(
                SemanticPreviewRecord(
                    artifact_type="proposal",
                    artifact_id=proposal_dir.name,
                    path=proposal_path,
                    code=code,
                    message=(
                        f"Preview only: update .proposal-meta.json field '{field_name}' "
                        f"from '{value}' to a valid canonical feature slug."
                        f"{candidate_suffix}"
                    ),
                )
            )
    return preview_records


def _planning_status_preview(
    inventory: Inventory,
    selected: Set[str],
    feature_metadata_by_slug: Dict[str, Dict[str, object]],
    feature_paths_by_slug: Dict[str, str],
) -> List[SemanticPreviewRecord]:
    if "feature" not in selected:
        return []
    preview_records: List[SemanticPreviewRecord] = []
    slice_rows_by_feature: Dict[str, List[Dict[str, object]]] = {}
    for row in inventory.slice_rows:
        feature_slug = str(row.get("feature") or "").strip()
        if feature_slug:
            slice_rows_by_feature.setdefault(feature_slug, []).append(dict(row))

    for feature_slug, rows in slice_rows_by_feature.items():
        metadata = feature_metadata_by_slug.get(feature_slug)
        if metadata is None:
            continue
        current_status = str(metadata.get("status") or "")
        if current_status in {"slice_ready", "implemented"}:
            continue
        suggested_status = (
            "implemented"
            if rows and all(str(row.get("status")) == "closed" for row in rows)
            else "slice_ready"
        )
        slice_ids = ", ".join(sorted(str(row["id"]) for row in rows))
        preview_records.append(
            SemanticPreviewRecord(
                artifact_type="feature",
                artifact_id=feature_slug,
                path=feature_paths_by_slug[feature_slug],
                code="repair_planning_status_handoff",
                message=(
                    "Preview only: update .planning-meta.json status "
                    f"from '{current_status}' to '{suggested_status}' to match "
                    f"existing execution slices: {slice_ids}."
                ),
            )
        )
    return preview_records


def _traceability_preview(
    inventory: Inventory,
    selected: Set[str],
) -> List[SemanticPreviewRecord]:
    preview_records: List[SemanticPreviewRecord] = []
    slice_ids_by_feature: Dict[str, Set[str]] = {}
    for row in inventory.slice_rows:
        feature_slug = str(row.get("feature") or "").strip()
        slice_id = str(row.get("id") or "").strip()
        if feature_slug and slice_id:
            slice_ids_by_feature.setdefault(feature_slug, set()).add(slice_id)

    owner_specs: List[Tuple[str, str, Path, str]] = []
    if "feature" in selected:
        for feature_dir in inventory.feature_dirs:
            owner_specs.append(
                (
                    "feature",
                    feature_dir.name,
                    feature_dir / "slice-traceability.md",
                    normalize_dir_relpath(feature_dir),
                )
            )
    if "subfeature" in selected:
        for feature_dir in inventory.feature_dirs:
            for subfeature_dir in inventory.subfeature_dirs_by_feature.get(feature_dir.name, []):
                owner_specs.append(
                    (
                        "subfeature",
                        subfeature_dir.name,
                        subfeature_dir / "slice-traceability.md",
                        normalize_dir_relpath(subfeature_dir),
                    )
                )

    for owner_type, owner_id, traceability_path, owner_path in owner_specs:
        records = parse_traceability_records(traceability_path, owner_type, owner_id, owner_path)
        actual_slice_ids = slice_ids_by_feature.get(owner_id, set())
        if not actual_slice_ids:
            continue
        for record in records:
            if record.execution_slice_ids:
                continue
            matching_ids = [
                slice_id for slice_id in record.planned_slice_ids if slice_id in actual_slice_ids
            ]
            if not matching_ids:
                continue
            preview_records.append(
                SemanticPreviewRecord(
                    artifact_type=owner_type,
                    artifact_id=owner_id,
                    path=owner_path,
                    code="repair_traceability_execution_ids",
                    message=(
                        "Preview only: backfill 'Execution Slice IDs' in "
                        f"slice-traceability.md for story '{record.story_id}' with "
                        f"{', '.join(matching_ids)}."
                    ),
                )
            )
    return preview_records


def build_semantic_preview(
    inventory: Inventory,
    artifact_types: Optional[Sequence[str]] = None,
) -> List[SemanticPreviewRecord]:
    selected = _selected_types(artifact_types or [])
    canonical_feature_slugs, feature_metadata_by_slug, feature_paths_by_slug = _canonical_feature_slugs(
        inventory
    )
    preview_records = _proposal_link_preview(
        inventory,
        selected,
        sorted(canonical_feature_slugs),
    )
    preview_records.extend(
        _planning_status_preview(
            inventory,
            selected,
            feature_metadata_by_slug,
            feature_paths_by_slug,
        )
    )
    preview_records.extend(_traceability_preview(inventory, selected))
    return _dedupe_preview_records(preview_records)
