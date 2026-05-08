#!/usr/bin/env python3

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple


SCRIPT_DIR = Path(__file__).resolve().parent
IMPORT_PATH_CANDIDATES = (
    SCRIPT_DIR.parent / "lib",
    SCRIPT_DIR.parents[2] / "lib",
    SCRIPT_DIR.parents[1] / "lib",
)

for candidate in reversed(IMPORT_PATH_CANDIDATES):
    if candidate.is_dir() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from workflow_state import (  # noqa: E402
    SemanticPreviewRecord,
    build_semantic_preview,
    load_inventory,
    normalize_dir_relpath,
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
    planning = inventory.context.planning
    scope_context = planning.SCOPE_RUNTIME.resolve_scope_context()
    rows: List[Dict[str, object]] = []
    planning_dir = str(inventory.context.planning_root)
    for feature_dir in planning.discover_feature_dirs(planning_dir):
        feature_path = Path(feature_dir)
        metadata, skipped_artifact = _safe_read_metadata(
            planning.read_metadata, "feature", feature_path.name, feature_path
        )
        if skipped_artifact is not None:
            skipped.append(skipped_artifact)
            continue
        rows.append(planning.build_registry_row(feature_dir, metadata, scope_context))
    return sorted(rows, key=lambda row: (str(row["path"]), str(row.get("updated_at") or "")))


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

    deduped_skipped = _dedupe_skipped(skipped)
    semantic_preview = build_semantic_preview(inventory, sorted(selected))
    suggestions = [record.to_dict() for record in semantic_preview]

    return {
        "ok": True,
        "apply": apply,
        "summary": {
            "planned_actions": sum(1 for action in actions if action.changed),
            "applied_actions": sum(1 for action in actions if action.applied),
            "skipped_artifacts": len(deduped_skipped),
            "semantic_preview_count": len(semantic_preview),
            "suggested_repairs": len(semantic_preview),
        },
        "actions": [action.to_dict() for action in actions],
        "semantic_preview": suggestions,
        "suggestions": suggestions,
        "skipped": [artifact.to_dict() for artifact in deduped_skipped],
    }
