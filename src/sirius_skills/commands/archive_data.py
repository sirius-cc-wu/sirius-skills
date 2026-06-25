#!/usr/bin/env python3

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from sirius_skills.commands.artifact_inventory import (  # noqa: E402
    iter_subfeature_dirs,
    load_inventory,
    normalize_dir_relpath,
)
from sirius_skills.lib.workflow_state import markdown_repository


VALID_ARTIFACT_TYPES = ("proposal", "feature", "subfeature", "slice")
PROPOSAL_CANDIDATE_STATUSES = {"rejected", "superseded", "promoted"}
ARCHIVE_SUMMARIES_START = markdown_repository.ARCHIVE_SUMMARIES_START
ARCHIVE_SUMMARIES_END = markdown_repository.ARCHIVE_SUMMARIES_END
SLICE_SUMMARY_START_TEMPLATE = markdown_repository.SLICE_SUMMARY_START_TEMPLATE
SLICE_SUMMARY_END_TEMPLATE = markdown_repository.SLICE_SUMMARY_END_TEMPLATE
PLANTUML_BLOCK_PATTERN = markdown_repository.PLANTUML_BLOCK_PATTERN
SLICE_BLOCK_PATTERN = markdown_repository.SLICE_SUMMARY_BLOCK_PATTERN

PreparedSliceSummary = markdown_repository.PreparedSliceSummary


@dataclass
class ArchiveCandidate:
    artifact_type: str
    artifact_id: str
    status: str
    path: str
    reason: str
    archivable: bool
    consolidation: Optional[Dict[str, object]] = None

    def to_dict(self) -> Dict[str, object]:
        payload: Dict[str, object] = {
            "artifact_type": self.artifact_type,
            "artifact_id": self.artifact_id,
            "status": self.status,
            "path": self.path,
            "reason": self.reason,
            "archivable": self.archivable,
        }
        if self.consolidation is not None:
            payload["consolidation"] = self.consolidation
        return payload


@dataclass
class ScopeArchiveTarget:
    artifact_type: str
    artifact_id: str
    status: str
    path: str
    planning_dir: Path
    design_path: Path
    closed_slice_rows: List[Dict[str, object]]


class ArchiveUsageError(RuntimeError):
    pass


def _safe_read_metadata(reader, path: Path) -> Optional[Dict[str, object]]:
    try:
        return reader(str(path))
    except (RuntimeError, ValueError):
        return None


def _load_raw_metadata(path: Path) -> Optional[Dict[str, object]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def _normalize_string_list(value: object) -> List[str]:
    if not isinstance(value, list):
        return []
    normalized: List[str] = []
    seen = set()
    for item in value:
        if not isinstance(item, str):
            continue
        candidate = item.strip()
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        normalized.append(candidate)
    return normalized


def _extract_consolidation_summary(metadata: Optional[Dict[str, object]]) -> Optional[Dict[str, object]]:
    if not isinstance(metadata, dict):
        return None
    raw = metadata.get("consolidation")
    if not isinstance(raw, dict):
        return None
    disposition = raw.get("disposition")
    if not isinstance(disposition, str) or not disposition.strip():
        return None
    targets: List[Dict[str, str]] = []
    for item in raw.get("targets", []):
        if not isinstance(item, dict):
            continue
        kind = item.get("kind")
        ref = item.get("ref")
        change = item.get("change")
        if not all(isinstance(field, str) and field.strip() for field in (kind, ref, change)):
            continue
        targets.append(
            {
                "kind": kind.strip(),
                "ref": ref.strip(),
                "change": change.strip(),
            }
        )
    justification = raw.get("justification")
    return {
        "disposition": disposition.strip().lower(),
        "targets": targets,
        "historical_artifacts": _normalize_string_list(raw.get("historical_artifacts")),
        "surface_simplifications": _normalize_string_list(raw.get("surface_simplifications")),
        "justification": justification.strip() if isinstance(justification, str) and justification.strip() else None,
    }


def _parse_markdown_row(line: str) -> List[str]:
    return markdown_repository.split_table_row(line)


def _dedupe_preserve_order(values: List[str]) -> List[str]:
    return markdown_repository._dedupe_preserve_order(values)


def _dedupe_text_blocks(values: List[str]) -> List[str]:
    return markdown_repository._dedupe_text_blocks(values)


def _extract_slice_ids_from_planning_text(markdown: str) -> List[str]:
    return markdown_repository.extract_slice_ids_from_planning_text(markdown)


def _slice_planning_ids(planning_dir: Path) -> List[str]:
    planning_path = planning_dir / "slice-planning.md"
    if not planning_path.exists():
        return []
    return markdown_repository.extract_slice_ids_from_planning_text(
        planning_path.read_text(encoding="utf-8")
    )


def _load_slice_metadata(inventory, row: Dict[str, object]) -> Dict[str, object]:
    return inventory.context.execution.load_slice_metadata(
        inventory.context.execution.slice_path_for_row(row)
    )


def _is_slice_archived(inventory, row: Dict[str, object]) -> bool:
    metadata = _load_slice_metadata(inventory, row)
    if isinstance(metadata.get("archived_at"), str):
        return True
    archive_dir = inventory.context.execution.default_archive_dir()
    return str(row["path"]).startswith(f"{archive_dir.rstrip('/')}/")


def _is_closed_unarchived_slice(inventory, row: Dict[str, object]) -> bool:
    return str(row.get("status", "")) == "closed" and not _is_slice_archived(inventory, row)


def _closed_slice_rows_for_ids(inventory, slice_ids: List[str]) -> List[Dict[str, object]]:
    rows_by_id = {str(row["id"]): row for row in inventory.slice_rows}
    closed_rows: List[Dict[str, object]] = []
    for slice_id in slice_ids:
        row = rows_by_id.get(slice_id)
        if row is None:
            continue
        if _is_closed_unarchived_slice(inventory, row):
            closed_rows.append(row)
    return closed_rows


def _feature_candidate(inventory, feature_dir: Path) -> Optional[ArchiveCandidate]:
    metadata = _safe_read_metadata(inventory.context.planning.read_metadata, feature_dir)
    if metadata is None:
        return None
    closed_rows = _closed_slice_rows_for_ids(inventory, _slice_planning_ids(feature_dir))
    if not closed_rows:
        return None
    consolidation = _extract_consolidation_summary(metadata)
    consolidation_suffix = ""
    if consolidation is not None:
        consolidation_suffix = (
            f" Consolidation '{consolidation['disposition']}' names "
            f"{len(consolidation['historical_artifacts'])} historical artifact(s)."
        )
    return ArchiveCandidate(
        artifact_type="feature",
        artifact_id=feature_dir.name,
        status=str(metadata.get("status", "unknown")),
        path=normalize_dir_relpath(feature_dir),
        reason=(
            f"{len(closed_rows)} closed planned slice(s) can be summarized into "
            f"system-design.md and archived.{consolidation_suffix}"
        ),
        archivable=True,
        consolidation=consolidation,
    )


def _subfeature_candidate(inventory, subfeature_dir: Path) -> Optional[ArchiveCandidate]:
    metadata = _safe_read_metadata(inventory.context.subfeatures.read_metadata, subfeature_dir)
    if metadata is None:
        metadata = _load_raw_metadata(subfeature_dir / ".subfeature-meta.json")
    if metadata is None:
        return None
    closed_rows = _closed_slice_rows_for_ids(inventory, _slice_planning_ids(subfeature_dir))
    if not closed_rows:
        return None
    consolidation = _extract_consolidation_summary(metadata)
    consolidation_suffix = ""
    if consolidation is not None:
        consolidation_suffix = (
            f" Consolidation '{consolidation['disposition']}' names "
            f"{len(consolidation['historical_artifacts'])} historical artifact(s)."
        )
    return ArchiveCandidate(
        artifact_type="subfeature",
        artifact_id=subfeature_dir.name,
        status=str(metadata.get("status", "unknown")),
        path=normalize_dir_relpath(subfeature_dir),
        reason=(
            f"{len(closed_rows)} closed planned slice(s) can be summarized into "
            f"system-design.md and archived.{consolidation_suffix}"
        ),
        archivable=True,
        consolidation=consolidation,
    )


def discover_candidates(artifact_type: Optional[str] = None) -> List[ArchiveCandidate]:
    inventory = load_inventory()
    candidates: List[ArchiveCandidate] = []
    selected = {artifact_type} if artifact_type else set(VALID_ARTIFACT_TYPES)

    if "proposal" in selected:
        for proposal_dir in inventory.proposal_dirs:
            metadata = _safe_read_metadata(inventory.context.propose.read_metadata, proposal_dir)
            if metadata is None:
                continue
            status = str(metadata.get("status", ""))
            if status not in PROPOSAL_CANDIDATE_STATUSES:
                continue
            candidates.append(
                ArchiveCandidate(
                    artifact_type="proposal",
                    artifact_id=proposal_dir.name,
                    status=status,
                    path=normalize_dir_relpath(proposal_dir),
                    reason=f"Proposal status '{status}' is archive-eligible.",
                    archivable=False,
                )
            )

    if "feature" in selected:
        for feature_dir in inventory.feature_dirs:
            candidate = _feature_candidate(inventory, feature_dir)
            if candidate is not None:
                candidates.append(candidate)

    if "subfeature" in selected:
        for subfeature_dir in iter_subfeature_dirs(inventory):
            candidate = _subfeature_candidate(inventory, subfeature_dir)
            if candidate is not None:
                candidates.append(candidate)

    if "slice" in selected:
        for row in inventory.slice_rows:
            if not _is_closed_unarchived_slice(inventory, row):
                continue
            candidates.append(
                ArchiveCandidate(
                    artifact_type="slice",
                    artifact_id=str(row["id"]),
                    status=str(row.get("status", "unknown")),
                    path=str(row["path"]),
                    reason="Closed slice can be archived through the execution owner helper.",
                    archivable=True,
                )
            )

    return sorted(candidates, key=lambda item: (item.artifact_type, item.artifact_id))


def _candidate_matches(candidate: ArchiveCandidate, artifact_id: str) -> bool:
    normalized = artifact_id.rstrip("/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return candidate.artifact_id == normalized or candidate.path.rstrip("/") == normalized


def _select_candidate(
    candidates: List[ArchiveCandidate], artifact_type: str, artifact_id: str
) -> ArchiveCandidate:
    matches = [
        candidate
        for candidate in candidates
        if candidate.artifact_type == artifact_type and _candidate_matches(candidate, artifact_id)
    ]
    if not matches:
        raise ArchiveUsageError(f"Archivable {artifact_type} not found: {artifact_id}")
    unique_paths = {candidate.path for candidate in matches}
    if len(unique_paths) > 1:
        raise ArchiveUsageError(
            f"Ambiguous {artifact_type} selector '{artifact_id}'. Use the artifact path."
        )
    return matches[0]


def _resolve_scope_target(
    inventory,
    artifact_type: str,
    artifact_id: str,
) -> ScopeArchiveTarget:
    candidates = discover_candidates(artifact_type)
    candidate = _select_candidate(candidates, artifact_type, artifact_id)
    planning_dir = Path.cwd() / candidate.path.rstrip("/")
    closed_rows = _closed_slice_rows_for_ids(inventory, _slice_planning_ids(planning_dir))
    if not closed_rows:
        raise ArchiveUsageError(f"No closed slices are ready to archive for {artifact_type}:{artifact_id}")
    design_path = planning_dir / "system-design.md"
    if not design_path.exists():
        raise ArchiveUsageError(
            f"Cannot archive {artifact_type}:{artifact_id} because system-design.md is missing."
        )
    return ScopeArchiveTarget(
        artifact_type=artifact_type,
        artifact_id=candidate.artifact_id,
        status=candidate.status,
        path=candidate.path,
        planning_dir=planning_dir,
        design_path=design_path,
        closed_slice_rows=closed_rows,
    )


def _extract_heading_title(text: str, default: str) -> str:
    return markdown_repository.extract_heading_title(text, default)


def _extract_section_body(text: str, heading: str) -> Optional[str]:
    return markdown_repository.extract_section_body(text, heading)


def _extract_brief_items(brief_text: str) -> List[str]:
    return markdown_repository.extract_brief_items(brief_text)


def _extract_blueprint_summary(blueprint_text: str) -> Optional[str]:
    return markdown_repository.extract_blueprint_summary(blueprint_text)


def _extract_blueprint_figures(blueprint_text: str) -> List[str]:
    return markdown_repository.extract_blueprint_figures(blueprint_text)


def _is_structural_plantuml(block: str) -> bool:
    return markdown_repository.is_structural_plantuml(block)


def _extract_structural_figures(text: str) -> List[str]:
    return markdown_repository.extract_structural_figures(text)


def _prepare_slice_summary(inventory, row: Dict[str, object]) -> PreparedSliceSummary:
    slice_dir = inventory.context.execution.slice_path_for_row(row)
    brief_path = Path(slice_dir) / "brief.md"
    blueprint_path = Path(slice_dir) / "blueprint.md"
    brief_text = brief_path.read_text(encoding="utf-8") if brief_path.exists() else ""
    blueprint_text = blueprint_path.read_text(encoding="utf-8") if blueprint_path.exists() else ""
    return PreparedSliceSummary(
        slice_id=str(row["id"]),
        title=markdown_repository.extract_heading_title(brief_text, str(row["id"])),
        brief_items=markdown_repository.extract_brief_items(brief_text),
        design_summary=markdown_repository.extract_blueprint_summary(blueprint_text),
        blueprint_text=blueprint_text,
    )


def _render_slice_summary_block(summary: PreparedSliceSummary) -> str:
    return markdown_repository.render_slice_summary_block(summary)


def _load_existing_summary_blocks(design_text: str) -> Dict[str, str]:
    return markdown_repository.load_existing_summary_blocks(design_text)


def _write_summary_appendix(
    design_path: Path,
    blocks: Dict[str, str],
    structural_figures: Optional[List[str]] = None,
) -> None:
    markdown_repository.write_summary_appendix(design_path, blocks, structural_figures)


def _apply_scope_archive(
    inventory,
    artifact_type: str,
    artifact_id: str,
    include_structural_diagrams: bool = False,
) -> Dict[str, object]:
    target = _resolve_scope_target(inventory, artifact_type, artifact_id)
    prepared_summaries = [
        _prepare_slice_summary(inventory, row)
        for row in sorted(target.closed_slice_rows, key=lambda row: str(row["id"]))
    ]
    preserved_structural_figures: List[str] = []
    if include_structural_diagrams:
        for summary in prepared_summaries:
            preserved_structural_figures.extend(
                _extract_structural_figures(summary.blueprint_text)
            )
        preserved_structural_figures.extend(
            _extract_structural_figures(target.design_path.read_text(encoding="utf-8"))
        )
        preserved_structural_figures = _dedupe_text_blocks(preserved_structural_figures)

    rows = inventory.context.execution.load_registry_json(inventory.context.slice_registry)
    archived_slice_ids: List[str] = []
    for row in sorted(target.closed_slice_rows, key=lambda item: str(item["id"])):
        current_row = inventory.context.execution.resolve_slice(rows, str(row["id"]))
        if current_row is None:
            raise ArchiveUsageError(f"Slice not found: {row['id']}")
        ok, message, updated_slice = inventory.context.execution.archive_slice(rows, current_row)
        if not ok:
            raise ArchiveUsageError(message)
        archived_slice_ids.append(str(updated_slice["id"]))
        rows = inventory.context.execution.load_registry_json(inventory.context.slice_registry)

    rendered_blocks = {
        summary.slice_id: _render_slice_summary_block(summary)
        for summary in prepared_summaries
    }
    _write_summary_appendix(
        target.design_path,
        rendered_blocks,
        structural_figures=preserved_structural_figures,
    )

    applied = {
        "artifact_type": artifact_type,
        "artifact_id": target.artifact_id,
        "path": target.path,
        "archived_slice_ids": archived_slice_ids,
        "updated_design_path": normalize_dir_relpath(target.design_path),
        "message": (
            f"Summarized and archived {len(archived_slice_ids)} closed slice(s) for "
            f"{artifact_type}:{target.artifact_id}"
        ),
    }
    if include_structural_diagrams:
        applied["structural_diagrams_included"] = len(preserved_structural_figures)
    return applied


def build_archive_result(
    artifact_type: Optional[str] = None,
    artifact_id: Optional[str] = None,
    apply: bool = False,
    include_structural_diagrams: bool = False,
) -> Dict[str, object]:
    if artifact_id and not artifact_type:
        raise ArchiveUsageError("Use --artifact-type with --artifact-id.")

    candidates = discover_candidates(artifact_type)
    if artifact_type and artifact_id:
        candidates = [
            candidate
            for candidate in candidates
            if candidate.artifact_type == artifact_type
            and _candidate_matches(candidate, artifact_id)
        ]

    applied = None
    if apply:
        if artifact_type not in {"slice", "feature", "subfeature"} or not artifact_id:
            raise ArchiveUsageError(
                "Apply mode requires --artifact-type slice, feature, or subfeature plus --artifact-id."
            )
        inventory = load_inventory()
        if artifact_type == "slice":
            target = _select_candidate(discover_candidates("slice"), "slice", artifact_id)
            _, _, slice_registry = inventory.context.execution.get_registry_paths(required_config=False)
            rows = inventory.context.execution.load_registry_json(slice_registry)
            slice_row = inventory.context.execution.resolve_slice(rows, target.artifact_id)
            if slice_row is None:
                raise ArchiveUsageError(f"Slice not found: {artifact_id}")
            ok, message, updated_slice = inventory.context.execution.archive_slice(rows, slice_row)
            if not ok:
                raise ArchiveUsageError(message)
            applied = {
                "artifact_type": "slice",
                "artifact_id": str(updated_slice["id"]),
                "path": str(updated_slice["path"]),
                "message": message,
            }
        else:
            applied = _apply_scope_archive(
                inventory,
                artifact_type,
                artifact_id,
                include_structural_diagrams=include_structural_diagrams,
            )

    return {
        "ok": True,
        "apply": apply,
        "summary": {
            "candidate_count": len(candidates),
            "archivable_count": sum(1 for candidate in candidates if candidate.archivable),
        },
        "candidates": [candidate.to_dict() for candidate in candidates],
        "applied": applied,
    }
