#!/usr/bin/env python3

import json
from pathlib import Path
from typing import Dict, List, Optional


IMPLEMENTATION_METRICS_FILENAME = "implementation-metrics.json"
STORY_SIZE_WEIGHTS = {"S": 1, "M": 3, "L": 5}


def sidecar_path_for(target_path: str | Path) -> Path:
    path = Path(target_path)
    if path.is_file():
        path = path.parent
    return path / IMPLEMENTATION_METRICS_FILENAME


def _normalize_optional_int(value: object, field_name: str) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise RuntimeError(f"{field_name} must be an integer or null.")
    return value


def _normalize_string_list(value: object, field_name: str) -> List[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise RuntimeError(f"{field_name} must be a list.")
    normalized: List[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise RuntimeError(f"{field_name} must contain non-empty strings.")
        normalized.append(item.strip())
    return list(dict.fromkeys(normalized))


def _normalize_optional_scalar(value: object, field_name: str) -> object:
    if value is None:
        return None
    if isinstance(value, (bool, int, str)):
        return value
    raise RuntimeError(f"{field_name} must be a string, integer, boolean, or null.")


def normalize_metrics_record(record: Dict[str, object]) -> Dict[str, object]:
    artifact_type = record.get("artifact_type")
    if artifact_type not in {"feature", "subfeature"}:
        raise RuntimeError("artifact_type must be 'feature' or 'subfeature'.")

    artifact_id = record.get("artifact_id")
    if not isinstance(artifact_id, str) or not artifact_id.strip():
        raise RuntimeError("artifact_id must be a non-empty string.")

    computed_at = record.get("computed_at")
    if not isinstance(computed_at, str) or not computed_at.strip():
        raise RuntimeError("computed_at must be a non-empty string.")

    status = record.get("status")
    if not isinstance(status, str) or not status.strip():
        raise RuntimeError("status must be a non-empty string.")

    story_size_payload = record.get("story_size")
    if story_size_payload is None:
        story_size_payload = {}
    if not isinstance(story_size_payload, dict):
        raise RuntimeError("story_size must be an object.")

    slices_payload = record.get("slices")
    if slices_payload is None:
        slices_payload = {}
    if not isinstance(slices_payload, dict):
        raise RuntimeError("slices must be an object.")

    churn_payload = record.get("implementation_churn")
    if churn_payload is None:
        churn_payload = {}
    if not isinstance(churn_payload, dict):
        raise RuntimeError("implementation_churn must be an object.")

    outcomes_payload = record.get("workflow_outcomes")
    if outcomes_payload is None:
        outcomes_payload = {}
    if not isinstance(outcomes_payload, dict):
        raise RuntimeError("workflow_outcomes must be an object.")

    execution_mode = record.get("execution_mode")
    if execution_mode not in {"guided", "direct", "mixed", "unknown"}:
        raise RuntimeError("execution_mode must be guided, direct, mixed, or unknown.")

    confidence = churn_payload.get("confidence", "unavailable")
    if confidence not in {"high", "partial", "unavailable"}:
        raise RuntimeError(
            "implementation_churn.confidence must be high, partial, or unavailable."
        )

    normalized = {
        "artifact_type": artifact_type,
        "artifact_id": artifact_id.strip(),
        "computed_at": computed_at.strip(),
        "status": status.strip(),
        "execution_mode": execution_mode,
        "story_size": {
            "weights": dict(STORY_SIZE_WEIGHTS),
            "sum_points": _normalize_optional_int(
                story_size_payload.get("sum_points"), "story_size.sum_points"
            ),
            "unsupported_sizes": _normalize_string_list(
                story_size_payload.get("unsupported_sizes"),
                "story_size.unsupported_sizes",
            ),
        },
        "slices": {
            "planned_count": _normalize_optional_int(
                slices_payload.get("planned_count"), "slices.planned_count"
            ),
            "linked_slice_ids": _normalize_string_list(
                slices_payload.get("linked_slice_ids"), "slices.linked_slice_ids"
            ),
        },
        "implementation_churn": {
            "added_lines": _normalize_optional_int(
                churn_payload.get("added_lines"), "implementation_churn.added_lines"
            ),
            "deleted_lines": _normalize_optional_int(
                churn_payload.get("deleted_lines"),
                "implementation_churn.deleted_lines",
            ),
            "total_changed_lines": _normalize_optional_int(
                churn_payload.get("total_changed_lines"),
                "implementation_churn.total_changed_lines",
            ),
            "source_commit_shas": _normalize_string_list(
                churn_payload.get("source_commit_shas"),
                "implementation_churn.source_commit_shas",
            ),
            "confidence": confidence,
        },
        "workflow_outcomes": {
            "follow_up_fix_count": _normalize_optional_int(
                outcomes_payload.get("follow_up_fix_count"),
                "workflow_outcomes.follow_up_fix_count",
            ),
            "review_findings_count": _normalize_optional_int(
                outcomes_payload.get("review_findings_count"),
                "workflow_outcomes.review_findings_count",
            ),
            "planning_drift": _normalize_optional_scalar(
                outcomes_payload.get("planning_drift"),
                "workflow_outcomes.planning_drift",
            ),
        },
    }
    return normalized


def read_metrics(target_path: str | Path) -> Optional[Dict[str, object]]:
    sidecar_path = sidecar_path_for(target_path)
    if not sidecar_path.exists():
        return None
    try:
        payload = json.loads(sidecar_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{sidecar_path} is not valid JSON.") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"{sidecar_path} must contain a JSON object.")
    return normalize_metrics_record(payload)


def write_metrics(target_path: str | Path, record: Dict[str, object]) -> Path:
    sidecar_path = sidecar_path_for(target_path)
    normalized = normalize_metrics_record(record)
    sidecar_path.parent.mkdir(parents=True, exist_ok=True)
    sidecar_path.write_text(json.dumps(normalized, indent=2) + "\n", encoding="utf-8")
    return sidecar_path
