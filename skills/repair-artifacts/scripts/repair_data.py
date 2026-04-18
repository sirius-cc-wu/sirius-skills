#!/usr/bin/env python3

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parents[1]
REPO_ROOT = SCRIPT_DIR.parents[2]
REPO_LIB_DIR = REPO_ROOT / "lib"
SKILL_LIB_DIR = SKILL_ROOT / "lib"

if REPO_LIB_DIR.is_dir() and str(REPO_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(REPO_LIB_DIR))
if SKILL_LIB_DIR.is_dir() and str(SKILL_LIB_DIR) not in sys.path:
    sys.path.append(str(SKILL_LIB_DIR))

from workflow_state.inventory import (  # noqa: E402
    load_inventory,
    normalize_dir_relpath,
    parse_traceability_records,
)


VALID_ARTIFACT_TYPES = ("proposal", "feature", "subfeature", "slice")


@dataclass
class RepairAction:
    artifact_type: str
    owner_id: Optional[str]
    registry_path: str
    readme_path: str
    current_count: int
    rebuilt_count: int
    changed: bool
    applied: bool

    def to_dict(self) -> Dict[str, object]:
        return {
            "artifact_type": self.artifact_type,
            "owner_id": self.owner_id,
            "registry_path": self.registry_path,
            "readme_path": self.readme_path,
            "current_count": self.current_count,
            "rebuilt_count": self.rebuilt_count,
            "changed": self.changed,
            "applied": self.applied,
        }


@dataclass
class SkippedArtifact:
    artifact_type: str
    artifact_id: str
    path: str
    message: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "artifact_type": self.artifact_type,
            "artifact_id": self.artifact_id,
            "path": self.path,
            "message": self.message,
        }


@dataclass
class RepairSuggestion:
    artifact_type: str
    artifact_id: str
    path: str
    code: str
    message: str
    apply_supported: bool = False

    def to_dict(self) -> Dict[str, object]:
        return {
            "artifact_type": self.artifact_type,
            "artifact_id": self.artifact_id,
            "path": self.path,
            "code": self.code,
            "message": self.message,
            "apply_supported": self.apply_supported,
        }


def selected_types(raw_types: Sequence[str]) -> Set[str]:
    return set(raw_types) if raw_types else set(VALID_ARTIFACT_TYPES)


def normalize_file_relpath(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(resolved)


def _rows_equal(left: List[Dict[str, object]], right: List[Dict[str, object]]) -> bool:
    return left == right


def _safe_read_metadata(reader, artifact_type: str, artifact_id: str, path: Path):
    try:
        return reader(str(path)), None
    except RuntimeError as exc:
        return None, SkippedArtifact(
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            path=normalize_dir_relpath(path),
            message=str(exc),
        )


def _rebuild_proposal_rows(inventory, skipped: List[SkippedArtifact]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for proposal_dir in inventory.proposal_dirs:
        metadata, skipped_artifact = _safe_read_metadata(
            inventory.context.propose.read_metadata, "proposal", proposal_dir.name, proposal_dir
        )
        if skipped_artifact is not None:
            skipped.append(skipped_artifact)
            continue
        rows.append(
            inventory.context.propose.normalize_registry_row(
                {
                    "proposal": proposal_dir.name,
                    "status": metadata.get("status", "draft"),
                    "updated_at": metadata.get("updated_at"),
                    "path": normalize_dir_relpath(proposal_dir),
                }
            )
        )
    return sorted(rows, key=lambda row: str(row["path"]))


def _rebuild_feature_rows(inventory, skipped: List[SkippedArtifact]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for feature_dir in inventory.feature_dirs:
        metadata, skipped_artifact = _safe_read_metadata(
            inventory.context.planning.read_metadata, "feature", feature_dir.name, feature_dir
        )
        if skipped_artifact is not None:
            skipped.append(skipped_artifact)
            continue
        rows.append(
            inventory.context.planning.normalize_registry_row(
                {
                    "feature": feature_dir.name,
                    "status": metadata.get("status", "discovery_pending"),
                    "updated_at": metadata.get("updated_at"),
                    "path": normalize_dir_relpath(feature_dir),
                }
            )
        )
    return sorted(rows, key=lambda row: str(row["path"]))


def _rebuild_subfeature_rows(inventory, skipped: List[SkippedArtifact]) -> Dict[str, List[Dict[str, object]]]:
    rows_by_feature: Dict[str, List[Dict[str, object]]] = {}
    for feature_dir in inventory.feature_dirs:
        feature_slug = feature_dir.name
        rows: List[Dict[str, object]] = []
        for subfeature_dir in inventory.subfeature_dirs_by_feature.get(feature_slug, []):
            metadata, skipped_artifact = _safe_read_metadata(
                inventory.context.subfeatures.read_metadata,
                "subfeature",
                subfeature_dir.name,
                subfeature_dir,
            )
            if skipped_artifact is not None:
                skipped.append(skipped_artifact)
                continue
            rows.append(
                inventory.context.subfeatures.normalize_registry_row(
                    {
                        "subfeature_id": subfeature_dir.name,
                        "status": metadata.get("status", "draft"),
                        "subfeature_type": metadata.get("subfeature_type", "additive"),
                        "updated_at": metadata.get("updated_at"),
                        "path": normalize_dir_relpath(subfeature_dir),
                    }
                )
            )
        rows_by_feature[feature_slug] = sorted(rows, key=lambda row: str(row["path"]))
    return rows_by_feature


def _rebuild_slice_rows(inventory, skipped: List[SkippedArtifact]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for slice_dir in inventory.slice_dirs:
        metadata, skipped_artifact = _safe_read_metadata(
            inventory.context.execution.load_slice_metadata, "slice", slice_dir.name, slice_dir
        )
        if skipped_artifact is not None:
            skipped.append(skipped_artifact)
            continue
        rows.append(
            inventory.context.execution.normalize_registry_row(
                {
                    "id": metadata.get("slice_id"),
                    "feature": metadata.get("feature"),
                    "status": metadata.get("status", "draft"),
                    "path": normalize_dir_relpath(slice_dir),
                    "updated_at": metadata.get("updated_at"),
                    "closed_at": metadata.get("closed_at"),
                    "archived_at": metadata.get("archived_at"),
                    "relations": metadata.get("relations", []),
                }
            )
        )
    return sorted(rows, key=lambda row: str(row["path"]))


def _dedupe_skipped(skipped: Sequence[SkippedArtifact]) -> List[SkippedArtifact]:
    seen = set()
    result: List[SkippedArtifact] = []
    for item in skipped:
        key = (item.artifact_type, item.artifact_id, item.path, item.message)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _dedupe_suggestions(
    suggestions: Sequence[RepairSuggestion],
) -> List[RepairSuggestion]:
    seen = set()
    result: List[RepairSuggestion] = []
    for item in suggestions:
        key = (item.artifact_type, item.artifact_id, item.path, item.code, item.message)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _canonical_feature_slugs(
    inventory, skipped: List[SkippedArtifact]
) -> Tuple[Set[str], Dict[str, Dict[str, object]], Dict[str, str]]:
    slugs: Set[str] = set()
    metadata_by_slug: Dict[str, Dict[str, object]] = {}
    path_by_slug: Dict[str, str] = {}
    for feature_dir in inventory.feature_dirs:
        metadata, skipped_artifact = _safe_read_metadata(
            inventory.context.planning.read_metadata, "feature", feature_dir.name, feature_dir
        )
        if skipped_artifact is not None:
            skipped.append(skipped_artifact)
            continue
        feature_slug = str(metadata.get("feature_slug") or feature_dir.name)
        slugs.add(feature_slug)
        metadata_by_slug[feature_slug] = metadata
        path_by_slug[feature_slug] = normalize_dir_relpath(feature_dir)
    return slugs, metadata_by_slug, path_by_slug


def _proposal_link_suggestions(
    inventory,
    selected: Set[str],
    skipped: List[SkippedArtifact],
    canonical_feature_slugs: Sequence[str],
) -> List[RepairSuggestion]:
    if "proposal" not in selected:
        return []
    suggestions: List[RepairSuggestion] = []
    candidate_suffix = (
        f" Candidate canonical features: {', '.join(canonical_feature_slugs)}."
        if canonical_feature_slugs
        else " No canonical features are currently available."
    )
    for proposal_dir in inventory.proposal_dirs:
        metadata, skipped_artifact = _safe_read_metadata(
            inventory.context.propose.read_metadata, "proposal", proposal_dir.name, proposal_dir
        )
        if skipped_artifact is not None:
            skipped.append(skipped_artifact)
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
            suggestions.append(
                RepairSuggestion(
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
    return suggestions


def _planning_status_suggestions(
    inventory,
    selected: Set[str],
    feature_metadata_by_slug: Dict[str, Dict[str, object]],
    feature_paths_by_slug: Dict[str, str],
) -> List[RepairSuggestion]:
    if "feature" not in selected:
        return []
    suggestions: List[RepairSuggestion] = []
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
        suggestions.append(
            RepairSuggestion(
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
    return suggestions


def _traceability_suggestions(
    inventory,
    selected: Set[str],
) -> List[RepairSuggestion]:
    suggestions: List[RepairSuggestion] = []
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
                ("feature", feature_dir.name, feature_dir / "slice-traceability.md", normalize_dir_relpath(feature_dir))
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
            matching_ids = [slice_id for slice_id in record.planned_slice_ids if slice_id in actual_slice_ids]
            if not matching_ids:
                continue
            suggestions.append(
                RepairSuggestion(
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
    return suggestions


def build_repair_result(
    artifact_types: Optional[Sequence[str]] = None, apply: bool = False
) -> Dict[str, object]:
    inventory = load_inventory()
    selected = selected_types(artifact_types or [])
    skipped: List[SkippedArtifact] = []
    actions: List[RepairAction] = []

    if "proposal" in selected:
        rebuilt = _rebuild_proposal_rows(inventory, skipped)
        current = sorted(inventory.proposal_rows, key=lambda row: str(row["path"]))
        changed = not _rows_equal(current, rebuilt)
        if apply and changed:
            inventory.context.propose.write_registry(rebuilt)
        actions.append(
            RepairAction(
                artifact_type="proposal",
                owner_id=None,
                registry_path=normalize_file_relpath(inventory.context.proposal_registry),
                readme_path=normalize_file_relpath(inventory.context.proposal_readme),
                current_count=len(current),
                rebuilt_count=len(rebuilt),
                changed=changed,
                applied=apply and changed,
            )
        )

    if "feature" in selected:
        rebuilt = _rebuild_feature_rows(inventory, skipped)
        current = sorted(inventory.planning_rows, key=lambda row: str(row["path"]))
        changed = not _rows_equal(current, rebuilt)
        if apply and changed:
            inventory.context.planning.write_registry(rebuilt)
        actions.append(
            RepairAction(
                artifact_type="feature",
                owner_id=None,
                registry_path=normalize_file_relpath(inventory.context.planning_registry),
                readme_path=normalize_file_relpath(inventory.context.planning_readme),
                current_count=len(current),
                rebuilt_count=len(rebuilt),
                changed=changed,
                applied=apply and changed,
            )
        )

    if "subfeature" in selected:
        rebuilt_by_feature = _rebuild_subfeature_rows(inventory, skipped)
        for feature_dir in inventory.feature_dirs:
            feature_slug = feature_dir.name
            current = sorted(
                inventory.subfeature_registry_rows.get(feature_slug, []),
                key=lambda row: str(row["path"]),
            )
            rebuilt = rebuilt_by_feature.get(feature_slug, [])
            changed = not _rows_equal(current, rebuilt)
            if apply and changed:
                inventory.context.subfeatures.write_registry(str(feature_dir), rebuilt)
            _, readme_path, registry_path = inventory.context.subfeatures.subfeature_registry_paths(
                str(feature_dir)
            )
            actions.append(
                RepairAction(
                    artifact_type="subfeature",
                    owner_id=feature_slug,
                    registry_path=normalize_file_relpath(Path(registry_path)),
                    readme_path=normalize_file_relpath(Path(readme_path)),
                    current_count=len(current),
                    rebuilt_count=len(rebuilt),
                    changed=changed,
                    applied=apply and changed,
                )
            )

    if "slice" in selected:
        rebuilt = _rebuild_slice_rows(inventory, skipped)
        current = sorted(inventory.slice_rows, key=lambda row: str(row["path"]))
        changed = not _rows_equal(current, rebuilt)
        if apply and changed:
            inventory.context.execution.write_registry(rebuilt)
        actions.append(
            RepairAction(
                artifact_type="slice",
                owner_id=None,
                registry_path=normalize_file_relpath(inventory.context.slice_registry),
                readme_path=normalize_file_relpath(inventory.context.slice_readme),
                current_count=len(current),
                rebuilt_count=len(rebuilt),
                changed=changed,
                applied=apply and changed,
                )
            )

    canonical_feature_slugs, feature_metadata_by_slug, feature_paths_by_slug = _canonical_feature_slugs(
        inventory, skipped
    )
    suggestions = _proposal_link_suggestions(
        inventory, selected, skipped, sorted(canonical_feature_slugs)
    )
    suggestions.extend(
        _planning_status_suggestions(
            inventory, selected, feature_metadata_by_slug, feature_paths_by_slug
        )
    )
    suggestions.extend(_traceability_suggestions(inventory, selected))
    deduped_skipped = _dedupe_skipped(skipped)
    deduped_suggestions = _dedupe_suggestions(suggestions)

    return {
        "ok": True,
        "apply": apply,
        "summary": {
            "planned_actions": sum(1 for action in actions if action.changed),
            "applied_actions": sum(1 for action in actions if action.applied),
            "skipped_artifacts": len(deduped_skipped),
            "suggested_repairs": len(deduped_suggestions),
        },
        "actions": [action.to_dict() for action in actions],
        "suggestions": [suggestion.to_dict() for suggestion in deduped_suggestions],
        "skipped": [artifact.to_dict() for artifact in deduped_skipped],
    }
