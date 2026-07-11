#!/usr/bin/env python3

import importlib.util
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


COMMAND_DIR = Path(__file__).resolve().parent
PLANNING_SCRIPT = COMMAND_DIR / "manage_planning.py"
SUBFEATURE_SCRIPT = COMMAND_DIR / "manage_subfeatures.py"
EXECUTION_SCRIPT = COMMAND_DIR / "manage_execution.py"

from sirius_skills.commands.artifact_inventory import normalize_dir_relpath, parse_traceability_records  # noqa: E402
from sirius_skills.commands.metrics_store import STORY_SIZE_WEIGHTS, write_metrics  # noqa: E402


@dataclass
class MeasurementTarget:
    artifact_type: str
    artifact_id: str
    artifact_path: Path
    status: str
    scope_context: object
    parent_feature: Optional[str]
    affected_story_ids: List[str]


def load_module(script_path: Path, name: str):
    if script_path.name == "manage_planning.py":
        from sirius_skills.commands import manage_planning
        return manage_planning
    elif script_path.name == "manage_subfeatures.py":
        from sirius_skills.commands import manage_subfeatures
        return manage_subfeatures
    elif script_path.name == "manage_execution.py":
        from sirius_skills.commands import manage_execution
        return manage_execution
    raise RuntimeError(f"Unknown script path: {script_path}")


def _dedupe(items: List[str]) -> List[str]:
    return list(dict.fromkeys(items))


def _unavailable_churn() -> Dict[str, object]:
    return {
        "added_lines": None,
        "deleted_lines": None,
        "total_changed_lines": None,
        "source_commit_shas": [],
        "confidence": "unavailable",
    }


def resolve_measurement_target(
    selector: str, explicit_scope: Optional[str] = None
) -> MeasurementTarget:
    planning = load_module(PLANNING_SCRIPT, "measure_manage_planning")
    subfeatures = load_module(SUBFEATURE_SCRIPT, "measure_manage_subfeatures")

    rows, feature, scope_context = planning.resolve_feature_lookup(
        selector, explicit_scope=explicit_scope
    )
    if feature is None:
        raise RuntimeError(f"Measurement target not found: {selector}")

    target_dir = Path(planning.feature_dir_for_row(feature, scope_context=scope_context))
    planning_metadata = planning.read_metadata(str(target_dir))
    artifact_type = "subfeature" if "/subfeatures/" in str(feature["path"]) else "feature"

    parent_feature = None
    affected_story_ids: List[str] = []
    if artifact_type == "subfeature":
        subfeature_metadata = subfeatures.read_metadata(str(target_dir))
        parent_feature = str(subfeature_metadata.get("parent_feature_slug") or "").strip() or None
        affected_story_ids = [
            story_id
            for story_id in subfeature_metadata.get(
                "story_ids", subfeature_metadata.get("affected_story_ids", [])
            )
            if isinstance(story_id, str) and story_id.strip()
        ]
        if str(subfeature_metadata.get("status")) != "finalized":
            raise RuntimeError(
                f"Subfeature '{feature['feature']}' must be finalized before measurement. "
                f"Current status: '{subfeature_metadata.get('status')}'."
            )

    if str(planning_metadata.get("status")) != "implemented":
        raise RuntimeError(
            f"Planning target '{feature['feature']}' must be implemented before measurement. "
            f"Current status: '{planning_metadata.get('status')}'."
        )

    return MeasurementTarget(
        artifact_type=artifact_type,
        artifact_id=str(feature["feature"]),
        artifact_path=target_dir,
        status=str(planning_metadata["status"]),
        scope_context=scope_context,
        parent_feature=parent_feature,
        affected_story_ids=affected_story_ids,
    )


def _parse_target_traceability(target: MeasurementTarget):
    return parse_traceability_records(
        target.artifact_path / "slice-traceability.md",
        target.artifact_type,
        target.artifact_id,
        normalize_dir_relpath(target.artifact_path),
    )


def _load_parent_traceability_records(target: MeasurementTarget) -> List[object]:
    if target.artifact_type != "subfeature" or not target.parent_feature:
        return []

    planning = load_module(PLANNING_SCRIPT, "measure_manage_planning_parent")
    rows = planning.parse_registry(scope_context=target.scope_context)
    parent_row = planning.find_feature(
        rows, target.parent_feature, scope_context=target.scope_context
    )
    if parent_row is None:
        return []
    parent_dir = Path(
        planning.feature_dir_for_row(parent_row, scope_context=target.scope_context)
    )
    parent_records = parse_traceability_records(
        parent_dir / "slice-traceability.md",
        "feature",
        target.parent_feature,
        normalize_dir_relpath(parent_dir),
    )
    if not target.affected_story_ids:
        return parent_records
    return [
        record for record in parent_records if record.story_id in set(target.affected_story_ids)
    ]


def _story_size_summary(target: MeasurementTarget, records: List[object]) -> Dict[str, object]:
    effective_records = records
    if not any(record.story_size for record in effective_records):
        effective_records = _load_parent_traceability_records(target)

    sizes_by_story: Dict[str, Optional[str]] = {}
    for record in effective_records:
        if not record.story_id or not record.story_size:
            continue
        existing = sizes_by_story.get(record.story_id)
        if existing is not None and existing != record.story_size:
            raise RuntimeError(
                f"Conflicting story sizes for story '{record.story_id}' in traceability."
            )
        sizes_by_story[record.story_id] = record.story_size

    unsupported_sizes = sorted(
        {
            size
            for size in sizes_by_story.values()
            if size is not None and size not in STORY_SIZE_WEIGHTS
        }
    )
    if unsupported_sizes:
        return {
            "weights": dict(STORY_SIZE_WEIGHTS),
            "sum_points": None,
            "unsupported_sizes": unsupported_sizes,
        }

    if not sizes_by_story:
        return {
            "weights": dict(STORY_SIZE_WEIGHTS),
            "sum_points": None,
            "unsupported_sizes": [],
        }

    return {
        "weights": dict(STORY_SIZE_WEIGHTS),
        "sum_points": sum(STORY_SIZE_WEIGHTS[size] for size in sizes_by_story.values() if size),
        "unsupported_sizes": [],
    }


def _planned_slice_ids(records: List[object]) -> List[str]:
    ordered: List[str] = []
    for record in records:
        for planned_slice_id in record.planned_slice_ids:
            if planned_slice_id not in ordered:
                ordered.append(planned_slice_id)
    return ordered


def _linked_execution_slices(target: MeasurementTarget, records: List[object]) -> List[str]:
    execution = load_module(EXECUTION_SCRIPT, "measure_manage_execution")
    execution_rows = execution.parse_registry(scope_context=target.scope_context)
    existing_ids = {str(row["id"]) for row in execution_rows}
    linked: List[str] = []
    for record in records:
        for slice_id in record.execution_slice_ids:
            if slice_id in existing_ids and slice_id not in linked:
                linked.append(slice_id)
    return linked


def _classify_execution_mode(
    planned_slice_ids: List[str], linked_execution_slice_ids: List[str]
) -> str:
    if not planned_slice_ids:
        return "unknown"
    if not linked_execution_slice_ids:
        return "direct"
    if len(linked_execution_slice_ids) >= len(planned_slice_ids):
        return "guided"
    return "mixed"


def _compute_commit_churn(repo_root: str, commit_shas: Optional[List[str]]) -> Dict[str, object]:
    if not commit_shas:
        return _unavailable_churn()

    added_lines = 0
    deleted_lines = 0
    normalized_shas = _dedupe([sha.strip() for sha in commit_shas if sha.strip()])
    for commit_sha in normalized_shas:
        result = subprocess.run(
            ["git", "-C", repo_root, "--no-pager", "show", "--numstat", "--format=", commit_sha],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Unable to compute churn for commit '{commit_sha}'.")
        for line in result.stdout.splitlines():
            parts = line.split("\t", 2)
            if len(parts) < 2:
                continue
            added, deleted = parts[0], parts[1]
            if added.isdigit():
                added_lines += int(added)
            if deleted.isdigit():
                deleted_lines += int(deleted)

    return {
        "added_lines": added_lines,
        "deleted_lines": deleted_lines,
        "total_changed_lines": added_lines + deleted_lines,
        "source_commit_shas": normalized_shas,
        "confidence": "high",
    }


def build_metrics_for_target(
    target: MeasurementTarget,
    *,
    computed_at: str,
    commit_shas: Optional[List[str]] = None,
) -> Dict[str, object]:
    records = _parse_target_traceability(target)
    planned_slice_ids = _planned_slice_ids(records)
    linked_execution_slice_ids = _linked_execution_slices(target, records)

    return {
        "artifact_type": target.artifact_type,
        "artifact_id": target.artifact_id,
        "computed_at": computed_at,
        "status": target.status,
        "execution_mode": _classify_execution_mode(
            planned_slice_ids, linked_execution_slice_ids
        ),
        "story_size": _story_size_summary(target, records),
        "slices": {
            "planned_count": len(planned_slice_ids) if planned_slice_ids else None,
            "linked_slice_ids": linked_execution_slice_ids,
        },
        "implementation_churn": _compute_commit_churn(
            str(target.scope_context.repo_root), commit_shas
        ),
        "workflow_outcomes": {
            "follow_up_fix_count": None,
            "review_findings_count": None,
            "planning_drift": None,
        },
    }


def build_metrics_record(
    selector: str,
    *,
    explicit_scope: Optional[str] = None,
    computed_at: str,
    commit_shas: Optional[List[str]] = None,
    write: bool = False,
) -> Dict[str, object]:
    target = resolve_measurement_target(selector, explicit_scope=explicit_scope)
    record = build_metrics_for_target(
        target, computed_at=computed_at, commit_shas=commit_shas
    )
    if write:
        write_metrics(target.artifact_path, record)
    return record
