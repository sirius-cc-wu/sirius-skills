#!/usr/bin/env python3

import argparse
import importlib.util
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_LIB_DIR = SCRIPT_DIR.parent / "lib"
REPO_LIB_DIR = next(
    (
        candidate / "lib"
        for candidate in SCRIPT_DIR.parents
        if (candidate / "lib" / "workflow_state").is_dir()
    ),
    None,
)

if REPO_LIB_DIR is not None and str(REPO_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(REPO_LIB_DIR))
if SKILL_LIB_DIR.is_dir() and str(SKILL_LIB_DIR) not in sys.path:
    sys.path.append(str(SKILL_LIB_DIR))

from workflow_state import evaluate_subfeature_transition, format_transition_message  # noqa: E402


DEFAULT_PLANNING_DIR = "docs/features"
PLANNING_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "guide-planning"
    / "scripts"
    / "manage_planning.py"
)
SUBFEATURES_DIR_NAME = "subfeatures"
REGISTRY_JSON_FILE = "registry.json"
REGISTRY_HEADER = (
    "# Subfeature Registry\n\n"
    "| Subfeature | Status | Type | Updated | Path |\n"
    "|---|---|---|---|---|\n"
)
METADATA_FILE = ".subfeature-meta.json"
DISCOVER_FILE = "discover.md"
IMPACT_FILE = "impact-analysis.md"
DESIGN_FILE = "system-design.md"
SLICE_PLANNING_FILE = "slice-planning.md"
SLICE_TRACEABILITY_FILE = "slice-traceability.md"
DISCOVER_STUB_MARKER = "<!-- add-subfeature:discover-stub -->"
SLUG_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
STATUS_SEQUENCE = [
    "draft",
    "impact_ready",
    "design_ready",
    "breakdown_ready",
    "reviewed",
    "finalized",
]
VALID_STATUSES = set(STATUS_SEQUENCE)
STATUS_ALIASES = {
    "draft": "draft",
    "impact_ready": "impact_ready",
    "impact-ready": "impact_ready",
    "design_ready": "design_ready",
    "design-ready": "design_ready",
    "breakdown_ready": "breakdown_ready",
    "breakdown-ready": "breakdown_ready",
    "reviewed": "reviewed",
    "review_ready": "reviewed",
    "review-ready": "reviewed",
    "finalized": "finalized",
}
APPROVAL_STATUSES = {"pending", "approved"}
APPROVAL_STATUS_ALIASES = {
    "pending": "pending",
    "approved": "approved",
}
SUBFEATURE_TYPES = {"additive", "narrowing", "superseding", "replacement"}
SUBFEATURE_TYPE_ALIASES = {
    "additive": "additive",
    "narrowing": "narrowing",
    "superseding": "superseding",
    "replacement": "replacement",
}
VALID_CONSOLIDATION_DISPOSITIONS = {
    "additive",
    "narrowing",
    "superseding",
    "replacement",
}
def now_timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def load_manage_planning_module():
    spec = importlib.util.spec_from_file_location("manage_planning", PLANNING_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def validate_slug(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} cannot be empty.")
    if "/" in normalized or "\\" in normalized:
        raise ValueError(f"{field_name} must not contain path separators.")
    if not SLUG_PATTERN.fullmatch(normalized):
        raise ValueError(
            f"Invalid {field_name.lower()}. Use only letters, numbers, dot, underscore, and hyphen."
        )
    return normalized


def normalize_status(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in STATUS_ALIASES:
        raise ValueError(
            f"Invalid status '{value}'. Valid canonical states: {sorted(VALID_STATUSES)}"
        )
    return STATUS_ALIASES[normalized]


def normalize_subfeature_type(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in SUBFEATURE_TYPE_ALIASES:
        raise ValueError(
            f"Invalid subfeature type '{value}'. Valid types: {sorted(SUBFEATURE_TYPES)}"
        )
    return SUBFEATURE_TYPE_ALIASES[normalized]


def normalize_approval_status(value: object, status: Optional[str] = None) -> str:
    if value in {None, ""}:
        return "approved" if status == "finalized" else "pending"
    if not isinstance(value, str):
        raise RuntimeError("Approval status must be a string when present.")
    normalized = value.strip().lower()
    if normalized not in APPROVAL_STATUS_ALIASES:
        raise RuntimeError(
            f"Invalid approval status '{value}'. Valid statuses: {sorted(APPROVAL_STATUSES)}"
        )
    return APPROVAL_STATUS_ALIASES[normalized]


def normalize_optional_timestamp(value: object) -> Optional[str]:
    if value is None or value == "" or value == "-":
        return None
    if not isinstance(value, str):
        raise RuntimeError("Timestamp fields must be strings when present.")
    return value


def normalize_optional_string(value: object, field_name: str) -> Optional[str]:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise RuntimeError(f"{field_name} must be a string when present.")
    cleaned = re.sub(r"\s+", " ", value.strip())
    return cleaned or None


def normalize_string_list(value: object, field_name: str) -> List[str]:
    if value is None or value == "":
        return []
    if not isinstance(value, list):
        raise RuntimeError(f"{field_name} must be stored as a list.")
    normalized: List[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise RuntimeError(f"{field_name} must contain non-empty strings.")
        normalized.append(item.strip())
    return list(dict.fromkeys(normalized))


def merge_string_lists(existing: List[str], updates: List[str]) -> List[str]:
    return list(dict.fromkeys([*existing, *updates]))


def normalize_consolidation_disposition(value: object) -> str:
    if not isinstance(value, str):
        raise RuntimeError("Consolidation disposition must be a string.")
    normalized = value.strip().lower()
    if normalized not in VALID_CONSOLIDATION_DISPOSITIONS:
        raise RuntimeError(
            "Consolidation disposition must be one of "
            f"{sorted(VALID_CONSOLIDATION_DISPOSITIONS)}."
        )
    return normalized


def normalize_required_string(value: object, field_name: str) -> str:
    normalized = normalize_optional_string(value, field_name)
    if not normalized:
        raise RuntimeError(f"{field_name} must be a non-empty string.")
    return normalized


def normalize_consolidation_targets(value: object) -> List[Dict[str, str]]:
    if value is None or value == "":
        return []
    if not isinstance(value, list):
        raise RuntimeError("Consolidation targets must be stored as a list.")
    normalized: List[Dict[str, str]] = []
    for item in value:
        if not isinstance(item, dict):
            raise RuntimeError("Each consolidation target must be a JSON object.")
        normalized.append(
            {
                "kind": normalize_required_string(
                    item.get("kind"), "Consolidation target kind"
                ),
                "ref": normalize_required_string(
                    item.get("ref"), "Consolidation target ref"
                ),
                "change": normalize_required_string(
                    item.get("change"), "Consolidation target change"
                ),
            }
        )
    deduped: List[Dict[str, str]] = []
    seen = set()
    for item in normalized:
        key = (item["kind"], item["ref"], item["change"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def normalize_consolidation_summary(value: object) -> Optional[Dict[str, object]]:
    if value is None or value == "":
        return None
    if not isinstance(value, dict):
        raise RuntimeError("Consolidation summary must be a JSON object.")
    return {
        "disposition": normalize_consolidation_disposition(value.get("disposition")),
        "targets": normalize_consolidation_targets(value.get("targets")),
        "historical_artifacts": normalize_string_list(
            value.get("historical_artifacts"), "Historical artifacts"
        ),
        "surface_simplifications": normalize_string_list(
            value.get("surface_simplifications"), "Surface simplifications"
        ),
        "justification": normalize_optional_string(
            value.get("justification"), "Consolidation justification"
        ),
    }


def parse_consolidation_json_arg(value: Optional[str]) -> Optional[Dict[str, object]]:
    if value is None:
        return None
    try:
        payload = json.loads(value)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Consolidation summary must be valid JSON.") from exc
    return normalize_consolidation_summary(payload)


def normalize_path(path: str) -> str:
    normalized = path.rstrip("/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized + "/"


def resolve_parent_feature(
    manage_planning, selector: str
) -> Tuple[str, str, object]:
    rows, feature, scope_context = manage_planning.resolve_feature_lookup(selector)
    if not feature:
        raise RuntimeError(f"Canonical feature not found: {selector}")
    feature_dir = manage_planning.feature_dir_for_row(feature, scope_context=scope_context)
    return feature_dir, str(feature["feature"]), scope_context


def subfeature_registry_paths(feature_dir: str) -> Tuple[str, str, str]:
    subfeatures_dir = os.path.join(feature_dir, SUBFEATURES_DIR_NAME)
    return (
        subfeatures_dir,
        os.path.join(subfeatures_dir, "README.md"),
        os.path.join(subfeatures_dir, REGISTRY_JSON_FILE),
    )


def ensure_subfeature_registry(feature_dir: str) -> None:
    subfeatures_dir, readme_path, registry_json_path = subfeature_registry_paths(feature_dir)
    os.makedirs(subfeatures_dir, exist_ok=True)
    if not os.path.exists(readme_path):
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(REGISTRY_HEADER)
    if not os.path.exists(registry_json_path):
        with open(registry_json_path, "w", encoding="utf-8") as f:
            json.dump({"subfeatures": []}, f, indent=2)
            f.write("\n")


def normalize_registry_row(row: Dict[str, object]) -> Dict[str, object]:
    subfeature_id = row.get("subfeature_id")
    path_value = row.get("path")
    if not isinstance(subfeature_id, str):
        raise RuntimeError("Registry row field 'subfeature_id' must be a string.")
    if not isinstance(path_value, str):
        raise RuntimeError("Registry row field 'path' must be a string.")

    return {
        "subfeature_id": validate_slug(subfeature_id, "Subfeature ID"),
        "status": normalize_status(str(row.get("status", ""))),
        "subfeature_type": normalize_subfeature_type(
            str(row.get("subfeature_type", "additive"))
        ),
        "updated_at": normalize_optional_timestamp(row.get("updated_at")),
        "path": normalize_path(path_value),
    }


def load_registry(feature_dir: str) -> List[Dict[str, object]]:
    ensure_subfeature_registry(feature_dir)
    _, _, registry_json_path = subfeature_registry_paths(feature_dir)
    try:
        with open(registry_json_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Subfeature registry JSON is not valid JSON.") from exc

    if isinstance(payload, list):
        raw_rows = payload
    elif isinstance(payload, dict):
        raw_rows = payload.get("subfeatures")
    else:
        raise RuntimeError("Subfeature registry JSON must be a JSON object or list.")

    if raw_rows is None:
        raw_rows = []
    if not isinstance(raw_rows, list):
        raise RuntimeError("Subfeature registry field 'subfeatures' must be a list.")
    return [normalize_registry_row(row) for row in raw_rows]


def write_registry(feature_dir: str, rows: List[Dict[str, object]]) -> None:
    ensure_subfeature_registry(feature_dir)
    _, readme_path, registry_json_path = subfeature_registry_paths(feature_dir)
    sorted_rows = sorted(
        rows, key=lambda row: (str(row["path"]), row.get("updated_at") or "")
    )
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(REGISTRY_HEADER)
        for row in sorted_rows:
            updated = row.get("updated_at") or "-"
            f.write(
                f"| {row['subfeature_id']} | {row['status']} | {row['subfeature_type']} | {updated} | {row['path']} |\n"
            )

    with open(registry_json_path, "w", encoding="utf-8") as f:
        json.dump({"subfeatures": sorted_rows}, f, indent=2)
        f.write("\n")


def metadata_path_for(subfeature_dir: str) -> str:
    return os.path.join(subfeature_dir, METADATA_FILE)


def build_metadata(
    parent_feature_slug: str,
    subfeature_id: str,
    subfeature_type: str = "additive",
    summary: Optional[str] = None,
) -> Dict[str, object]:
    timestamp = now_timestamp()
    return {
        "subfeature_id": validate_slug(subfeature_id, "Subfeature ID"),
        "parent_feature_slug": validate_slug(parent_feature_slug, "Parent feature slug"),
        "status": "draft",
        "approval_status": "pending",
        "created_at": timestamp,
        "updated_at": timestamp,
        "subfeature_type": normalize_subfeature_type(subfeature_type),
        "summary": normalize_optional_string(summary, "Summary"),
        "affected_artifacts": [],
        "affected_story_ids": [],
        "affected_slice_ids": [],
        "ready_slice_ids": [],
        "consolidation": None,
        "review_note": None,
        "approved_at": None,
        "approved_by": None,
        "approval_note": None,
        "finalized_at": None,
    }


def normalize_metadata(payload: object) -> Dict[str, object]:
    if not isinstance(payload, dict):
        raise RuntimeError("Subfeature metadata must be a JSON object.")

    subfeature_id = payload.get("subfeature_id")
    parent_feature_slug = payload.get("parent_feature_slug")
    if not isinstance(subfeature_id, str):
        raise RuntimeError("Subfeature metadata field 'subfeature_id' must be a string.")
    if not isinstance(parent_feature_slug, str):
        raise RuntimeError(
            "Subfeature metadata field 'parent_feature_slug' must be a string."
        )

    status = normalize_status(str(payload.get("status", "")))
    approval_status = normalize_approval_status(payload.get("approval_status"), status=status)
    finalized_at = normalize_optional_timestamp(payload.get("finalized_at"))
    updated_at = normalize_optional_timestamp(payload.get("updated_at")) or now_timestamp()
    approved_at = normalize_optional_timestamp(payload.get("approved_at"))
    if approval_status == "approved" and approved_at is None:
        approved_at = finalized_at or updated_at

    return {
        "subfeature_id": validate_slug(subfeature_id, "Subfeature ID"),
        "parent_feature_slug": validate_slug(
            parent_feature_slug, "Parent feature slug"
        ),
        "status": status,
        "approval_status": approval_status,
        "created_at": normalize_optional_timestamp(payload.get("created_at"))
        or now_timestamp(),
        "updated_at": updated_at,
        "subfeature_type": normalize_subfeature_type(
            str(payload.get("subfeature_type", "additive"))
        ),
        "summary": normalize_optional_string(payload.get("summary"), "Summary"),
        "affected_artifacts": normalize_string_list(
            payload.get("affected_artifacts"), "Affected artifacts"
        ),
        "affected_story_ids": normalize_string_list(
            payload.get("affected_story_ids"), "Affected story IDs"
        ),
        "affected_slice_ids": normalize_string_list(
            payload.get("affected_slice_ids"), "Affected slice IDs"
        ),
        "ready_slice_ids": normalize_string_list(
            payload.get("ready_slice_ids"), "Ready slice IDs"
        ),
        "consolidation": normalize_consolidation_summary(payload.get("consolidation")),
        "review_note": normalize_optional_string(payload.get("review_note"), "Review note"),
        "approved_at": approved_at,
        "approved_by": normalize_optional_string(payload.get("approved_by"), "Approved by"),
        "approval_note": normalize_optional_string(
            payload.get("approval_note"), "Approval note"
        ),
        "finalized_at": finalized_at,
    }


def read_metadata(subfeature_dir: str) -> Dict[str, object]:
    path = metadata_path_for(subfeature_dir)
    if not os.path.exists(path):
        raise RuntimeError(f"Subfeature metadata not found at '{path}'.")
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Subfeature metadata is not valid JSON.") from exc
    return normalize_metadata(payload)


def write_metadata(subfeature_dir: str, metadata: Dict[str, object]) -> None:
    os.makedirs(subfeature_dir, exist_ok=True)
    with open(metadata_path_for(subfeature_dir), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        f.write("\n")


def subfeature_dir_for_row(row: Dict[str, object], scope_context: object) -> str:
    return str(
        Path(scope_context.scope_root) / str(row["path"]).rstrip("/")
    )


def find_subfeature(rows: List[Dict[str, object]], selector: str) -> Optional[Dict[str, object]]:
    normalized_selector = selector.rstrip("/")
    if normalized_selector.startswith("./"):
        normalized_selector = normalized_selector[2:]

    for row in rows:
        if row["subfeature_id"] == normalized_selector:
            return row
        path_value = str(row["path"]).rstrip("/")
        if path_value == normalized_selector:
            return row
        if os.path.basename(path_value) == normalized_selector:
            return row
    return None


def write_discover_stub(
    subfeature_dir: str,
    parent_feature_slug: str,
    subfeature_id: str,
    subfeature_type: str,
    summary: Optional[str],
) -> None:
    discover_path = os.path.join(subfeature_dir, DISCOVER_FILE)
    if os.path.exists(discover_path):
        return

    title = subfeature_id.replace("-", " ").strip().title()
    summary_line = summary or "Describe why this existing feature needs a durable subfeature."
    content = (
        f"{DISCOVER_STUB_MARKER}\n"
        f"# Discover: {title}\n\n"
        "> Bootstrap stub created by `add-subfeature`.\n"
        "> Replace this scaffold with the real discovery packet via the `discover` skill.\n\n"
        "## Parent Feature\n\n"
        f"- Feature: `{parent_feature_slug}`\n"
        f"- Subfeature ID: `{subfeature_id}`\n"
        f"- Subfeature Type: `{subfeature_type}`\n\n"
        "## Problem\n\n"
        f"{summary_line}\n\n"
        "## Requested Subfeature\n\n"
        "- Describe the durable child capability this feature now needs.\n"
        "- Note whether this is additive, narrowing, superseding, or replacement work.\n\n"
        "## Consolidation Expectations\n\n"
        "- If this subfeature narrows, supersedes, or replaces existing workflow surface, name the affected capability, artifact, command path, or validation path.\n"
        "- Describe what should become active, historical, retired, or archival-eligible as a result.\n"
        "- Explain the intended user-facing simplification, or state why no valid consolidation target exists.\n\n"
        "## Baseline Artifacts To Assess\n\n"
        "- `discover.md`\n"
        "- `system-design.md`\n"
        "- `user-stories.md`\n\n"
        "## Subfeature Execution Planning\n\n"
        "- Add or update `slice-planning.md` and `slice-traceability.md` inside this subfeature folder for any new execution work.\n"
        "- Treat the parent feature docs as baseline context unless impact analysis explicitly narrows or supersedes them.\n\n"
        "## Risks and Open Questions\n\n"
        "- What existing stories, slices, or validation paths might this subfeature affect?\n"
    )
    with open(discover_path, "w", encoding="utf-8") as f:
        f.write(content)


def validate_required_file(subfeature_dir: str, filename: str) -> Tuple[bool, str]:
    path = os.path.join(subfeature_dir, filename)
    if not os.path.exists(path):
        return False, f"Missing required file '{filename}'."
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    if not content:
        return False, f"Required file '{filename}' is empty."
    return True, f"Found '{filename}'."


def validate_subfeature_state(
    subfeature_dir: str, metadata: Dict[str, object]
) -> Tuple[bool, List[str], List[Dict[str, object]]]:
    checks: List[Dict[str, object]] = []
    issues: List[str] = []
    status = str(metadata["status"])
    status_index = STATUS_SEQUENCE.index(status)

    def record_check(name: str, ok: bool, detail: str) -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})
        if not ok:
            issues.append(detail)

    exists = os.path.isdir(subfeature_dir)
    record_check(
        "subfeature_dir",
        exists,
        "Subfeature directory exists." if exists else "Subfeature directory does not exist.",
    )
    if not exists:
        return False, issues, checks

    ok, detail = validate_required_file(subfeature_dir, DISCOVER_FILE)
    record_check("discover", ok, detail)

    if status_index >= STATUS_SEQUENCE.index("impact_ready"):
        ok, detail = validate_required_file(subfeature_dir, IMPACT_FILE)
        record_check("impact_analysis", ok, detail)

    if status_index >= STATUS_SEQUENCE.index("design_ready"):
        ok, detail = validate_required_file(subfeature_dir, DESIGN_FILE)
        record_check("system_design", ok, detail)

    if status_index >= STATUS_SEQUENCE.index("breakdown_ready"):
        ok, detail = validate_required_file(subfeature_dir, SLICE_PLANNING_FILE)
        record_check("slice_planning", ok, detail)
        ok, detail = validate_required_file(subfeature_dir, SLICE_TRACEABILITY_FILE)
        record_check("slice_traceability", ok, detail)

    if status_index >= STATUS_SEQUENCE.index("reviewed"):
        review_note = metadata.get("review_note")
        ok = isinstance(review_note, str) and bool(review_note.strip())
        record_check(
            "review_note",
            ok,
            "Planning review note recorded."
            if ok
            else "Reviewed state requires a non-empty review note.",
        )

    approval_status = str(metadata.get("approval_status") or "pending")
    approved_at = metadata.get("approved_at")
    approved_by = metadata.get("approved_by")
    approval_note = metadata.get("approval_note")
    ready_slice_ids = metadata.get("ready_slice_ids")

    approval_allowed = status_index >= STATUS_SEQUENCE.index("reviewed")
    if approval_status == "approved":
        record_check(
            "approval_state",
            approval_allowed,
            "Approval recorded after planning review."
            if approval_allowed
            else "Approval cannot be recorded before the subfeature reaches 'reviewed'.",
        )
        record_check(
            "approved_at",
            isinstance(approved_at, str) and bool(approved_at.strip()),
            "Approval timestamp recorded."
            if isinstance(approved_at, str) and bool(approved_at.strip())
            else "Approved subfeatures require a non-empty approved_at timestamp.",
        )
    else:
        record_check(
            "pending_approval_timestamp",
            approved_at is None,
            "Pending approval has no approval timestamp."
            if approved_at is None
            else "Pending approval must not keep an approved_at timestamp.",
        )
        record_check(
            "pending_approval_actor",
            approved_by is None,
            "Pending approval has no approver recorded."
            if approved_by is None
            else "Pending approval must not keep an approved_by value.",
        )
        record_check(
            "pending_approval_note",
            approval_note is None,
            "Pending approval has no approval note."
            if approval_note is None
            else "Pending approval must not keep an approval_note value.",
        )

    has_ready_slice_ids = isinstance(ready_slice_ids, list) and len(ready_slice_ids) > 0
    if has_ready_slice_ids:
        record_check(
            "ready_slice_ids",
            approval_status == "approved" and approval_allowed,
            "Ready slice IDs recorded for approved execution handoff."
            if approval_status == "approved" and approval_allowed
            else "Ready slice IDs require an approved reviewed subfeature.",
        )

    return not issues, issues, checks


def can_transition(current: str, target: str) -> bool:
    if current == target:
        return True
    return STATUS_SEQUENCE.index(target) - STATUS_SEQUENCE.index(current) == 1


def create_subfeature(
    manage_planning,
    feature_dir: str,
    parent_feature_slug: str,
    subfeature_id: str,
    subfeature_type: str,
    summary: Optional[str],
    scope_context: object,
) -> Tuple[str, bool]:
    rows = load_registry(feature_dir)
    existing = find_subfeature(rows, subfeature_id)
    if existing:
        return subfeature_dir_for_row(existing, scope_context), False

    subfeature_dir = os.path.join(feature_dir, SUBFEATURES_DIR_NAME, subfeature_id)
    os.makedirs(subfeature_dir, exist_ok=True)
    metadata = build_metadata(
        parent_feature_slug,
        subfeature_id,
        subfeature_type=subfeature_type,
        summary=summary,
    )
    write_metadata(subfeature_dir, metadata)
    write_discover_stub(
        subfeature_dir,
        parent_feature_slug,
        subfeature_id,
        metadata["subfeature_type"],
        summary,
    )

    rows.append(
        {
            "subfeature_id": subfeature_id,
            "status": metadata["status"],
            "subfeature_type": metadata["subfeature_type"],
            "updated_at": metadata["updated_at"],
            "path": manage_planning.relative_path_from_scope_root(
                subfeature_dir, scope_context
            ),
        }
    )
    write_registry(feature_dir, rows)
    manage_planning.sync_registry(scope_context=scope_context)
    return subfeature_dir, True


def update_subfeature_status(
    manage_planning,
    feature_dir: str,
    subfeature: Dict[str, object],
    status: str,
    scope_context: object,
    force: bool = False,
    subfeature_type: Optional[str] = None,
    summary: Optional[str] = None,
    review_note: Optional[str] = None,
    affected_artifacts: Optional[List[str]] = None,
    affected_story_ids: Optional[List[str]] = None,
    affected_slice_ids: Optional[List[str]] = None,
    consolidation: Optional[Dict[str, object]] = None,
) -> Tuple[bool, str]:
    rows = load_registry(feature_dir)
    selected = find_subfeature(rows, str(subfeature["subfeature_id"]))
    if not selected:
        return False, f"Subfeature disappeared from registry: {subfeature['subfeature_id']}"

    subfeature_dir = subfeature_dir_for_row(selected, scope_context)
    metadata = read_metadata(subfeature_dir)
    current_status = str(metadata["status"])

    if not force and not can_transition(current_status, status):
        return (
            False,
            f"Invalid status transition from '{current_status}' to '{status}'. Allowed states: {STATUS_SEQUENCE}",
        )

    updated_metadata = dict(metadata)
    timestamp = now_timestamp()
    updated_metadata["status"] = status
    updated_metadata["updated_at"] = timestamp
    if subfeature_type is not None:
        updated_metadata["subfeature_type"] = normalize_subfeature_type(subfeature_type)
    if summary is not None:
        updated_metadata["summary"] = normalize_optional_string(summary, "Summary")
    if review_note is not None:
        updated_metadata["review_note"] = normalize_optional_string(review_note, "Review note")
    if affected_artifacts is not None:
        updated_metadata["affected_artifacts"] = normalize_string_list(
            affected_artifacts, "Affected artifacts"
        )
    if affected_story_ids is not None:
        updated_metadata["affected_story_ids"] = normalize_string_list(
            affected_story_ids, "Affected story IDs"
        )
    if affected_slice_ids is not None:
        updated_metadata["affected_slice_ids"] = normalize_string_list(
            affected_slice_ids, "Affected slice IDs"
        )
    if consolidation is not None:
        updated_metadata["consolidation"] = normalize_consolidation_summary(consolidation)
    if status == "reviewed" and current_status != "reviewed":
        updated_metadata["approval_status"] = "pending"
        updated_metadata["approved_at"] = None
        updated_metadata["approved_by"] = None
        updated_metadata["approval_note"] = None
        updated_metadata["ready_slice_ids"] = []
    if status == "finalized":
        if str(updated_metadata.get("approval_status") or "pending") != "approved":
            updated_metadata["approval_status"] = "approved"
            updated_metadata["approved_at"] = timestamp
        updated_metadata["finalized_at"] = timestamp

    ok, issues, _ = validate_subfeature_state(subfeature_dir, updated_metadata)
    if not force and not ok:
        return False, "Cannot set status: " + "; ".join(issues)

    write_metadata(subfeature_dir, updated_metadata)
    legacy_planning_meta_path = Path(subfeature_dir) / ".planning-meta.json"
    if legacy_planning_meta_path.exists():
        legacy_planning_meta_path.unlink()
    selected["status"] = status
    selected["subfeature_type"] = updated_metadata["subfeature_type"]
    selected["updated_at"] = timestamp
    write_registry(feature_dir, rows)
    manage_planning.sync_registry(scope_context=scope_context)
    message = f"Updated {selected['subfeature_id']} to status '{status}'"
    transition_result = evaluate_subfeature_transition(str(selected["subfeature_id"]), status)
    return True, format_transition_message(message, transition_result)


def update_subfeature_approval(
    manage_planning,
    feature_dir: str,
    subfeature: Dict[str, object],
    scope_context: object,
    ready_slice_ids: Optional[List[str]] = None,
    approval_note: Optional[str] = None,
    approved_by: Optional[str] = None,
    require_existing_approval: bool = False,
) -> Tuple[bool, str]:
    rows = load_registry(feature_dir)
    selected = find_subfeature(rows, str(subfeature["subfeature_id"]))
    if not selected:
        return False, f"Subfeature disappeared from registry: {subfeature['subfeature_id']}"

    subfeature_dir = subfeature_dir_for_row(selected, scope_context)
    metadata = read_metadata(subfeature_dir)
    current_status = str(metadata["status"])
    if current_status not in {"reviewed", "finalized"}:
        return (
            False,
            "Human approval can be recorded only after the subfeature reaches 'reviewed'.",
        )

    current_approval_status = str(metadata.get("approval_status") or "pending")
    if require_existing_approval and current_approval_status != "approved":
        return (
            False,
            f"Subfeature '{selected['subfeature_id']}' must record explicit human approval before slice bootstrap.",
        )

    updated_metadata = dict(metadata)
    updated_metadata["approval_status"] = "approved"
    if updated_metadata.get("approved_at") is None:
        updated_metadata["approved_at"] = now_timestamp()
    if approved_by is not None:
        updated_metadata["approved_by"] = normalize_optional_string(approved_by, "Approved by")
    if approval_note is not None:
        updated_metadata["approval_note"] = normalize_optional_string(
            approval_note, "Approval note"
        )
    if ready_slice_ids is not None:
        updated_metadata["ready_slice_ids"] = merge_string_lists(
            list(updated_metadata.get("ready_slice_ids") or []),
            normalize_string_list(ready_slice_ids, "Ready slice IDs"),
        )
    if current_status == "finalized" and updated_metadata.get("finalized_at") is None:
        updated_metadata["finalized_at"] = updated_metadata["approved_at"]
    updated_metadata["updated_at"] = now_timestamp()

    ok, issues, _ = validate_subfeature_state(subfeature_dir, updated_metadata)
    if not ok:
        return False, "Cannot record approval: " + "; ".join(issues)

    write_metadata(subfeature_dir, updated_metadata)
    selected["updated_at"] = updated_metadata["updated_at"]
    write_registry(feature_dir, rows)
    manage_planning.sync_registry(scope_context=scope_context)

    ready_slice_summary = list(updated_metadata.get("ready_slice_ids") or [])
    if ready_slice_summary:
        return (
            True,
            f"Recorded approval for {selected['subfeature_id']} with ready slices: "
            + ", ".join(ready_slice_summary),
        )
    return True, f"Recorded approval for {selected['subfeature_id']}"


def cmd_init_feature(args: argparse.Namespace) -> int:
    manage_planning = load_manage_planning_module()
    try:
        feature_dir, _, _ = resolve_parent_feature(manage_planning, args.feature)
        ensure_subfeature_registry(feature_dir)
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(
        f"Initialized subfeature registry: {os.path.join(feature_dir, SUBFEATURES_DIR_NAME)}"
    )
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    manage_planning = load_manage_planning_module()
    try:
        feature_dir, parent_feature_slug, scope_context = resolve_parent_feature(
            manage_planning, args.feature
        )
        ensure_subfeature_registry(feature_dir)
        subfeature_id = validate_slug(args.subfeature_id, "Subfeature ID")
        subfeature_dir, created = create_subfeature(
            manage_planning,
            feature_dir,
            parent_feature_slug,
            subfeature_id,
            normalize_subfeature_type(args.type),
            args.summary,
            scope_context,
        )
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not created:
        print(f"Subfeature already exists: {subfeature_dir}")
        return 0

    print(f"Created subfeature: {subfeature_dir}")
    return 0


def cmd_set_status(args: argparse.Namespace) -> int:
    manage_planning = load_manage_planning_module()
    try:
        feature_dir, _, scope_context = resolve_parent_feature(manage_planning, args.feature)
        rows = load_registry(feature_dir)
        subfeature = find_subfeature(rows, args.subfeature)
        if not subfeature:
            print(f"Subfeature not found: {args.subfeature}", file=sys.stderr)
            return 2
        status = normalize_status(args.status)
        success, message = update_subfeature_status(
            manage_planning,
            feature_dir,
            subfeature,
            status,
            scope_context,
            force=args.force,
            subfeature_type=args.type,
            summary=args.summary,
            review_note=args.review_note,
            affected_artifacts=args.affected_artifact if args.affected_artifact else None,
            affected_story_ids=args.story_id if args.story_id else None,
            affected_slice_ids=args.slice_id if args.slice_id else None,
            consolidation=parse_consolidation_json_arg(args.consolidation_json),
        )
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    stream = sys.stdout if success else sys.stderr
    print(message, file=stream)
    return 0 if success else 2


def cmd_approve(args: argparse.Namespace) -> int:
    manage_planning = load_manage_planning_module()
    try:
        feature_dir, _, scope_context = resolve_parent_feature(manage_planning, args.feature)
        rows = load_registry(feature_dir)
        subfeature = find_subfeature(rows, args.subfeature)
        if not subfeature:
            print(f"Subfeature not found: {args.subfeature}", file=sys.stderr)
            return 2
        success, message = update_subfeature_approval(
            manage_planning,
            feature_dir,
            subfeature,
            scope_context,
            ready_slice_ids=args.slice_id if args.slice_id else None,
            approval_note=args.approval_note,
            approved_by=args.approved_by,
        )
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    stream = sys.stdout if success else sys.stderr
    print(message, file=stream)
    return 0 if success else 2


def cmd_validate(args: argparse.Namespace) -> int:
    manage_planning = load_manage_planning_module()
    try:
        feature_dir, _, scope_context = resolve_parent_feature(manage_planning, args.feature)
        rows = load_registry(feature_dir)
        subfeature = find_subfeature(rows, args.subfeature)
        if not subfeature:
            print(f"Subfeature not found: {args.subfeature}", file=sys.stderr)
            return 2
        subfeature_dir = subfeature_dir_for_row(subfeature, scope_context)
        metadata = read_metadata(subfeature_dir)
        ok, issues, checks = validate_subfeature_state(subfeature_dir, metadata)
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    result = {
        "feature": os.path.basename(feature_dir.rstrip("/")),
        "subfeature": subfeature,
        "metadata": metadata,
        "ok": ok,
        "checks": checks,
        "issues": issues,
    }
    print(json.dumps(result, indent=2))
    return 0 if ok else 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_p = subparsers.add_parser(
        "init-feature", help="Initialize feature-local subfeature registry files"
    )
    init_p.add_argument("feature", help="Feature slug, folder name, or path")

    add_p = subparsers.add_parser(
        "add", help="Create a durable subfeature for an existing feature"
    )
    add_p.add_argument("feature", help="Parent feature slug, folder name, or path")
    add_p.add_argument("subfeature_id", help="Subfeature ID or short slug")
    add_p.add_argument(
        "--type",
        default="additive",
        help="Subfeature type: additive, narrowing, superseding, or replacement.",
    )
    add_p.add_argument(
        "--summary", default=None, help="Optional summary of the requested subfeature."
    )

    status_p = subparsers.add_parser(
        "set-status", help="Advance a subfeature status once required artifacts exist"
    )
    status_p.add_argument("feature", help="Parent feature slug, folder name, or path")
    status_p.add_argument("subfeature", help="Subfeature ID, folder name, or path")
    status_p.add_argument("status", help="Target status")
    status_p.add_argument("--type", default=None, help="Override subfeature type")
    status_p.add_argument("--summary", default=None, help="Update summary")
    status_p.add_argument("--review-note", default=None, help="Review note text")
    status_p.add_argument(
        "--affected-artifact",
        action="append",
        default=[],
        help="Affected artifact path. Repeatable.",
    )
    status_p.add_argument(
        "--story-id", action="append", default=[], help="Affected story ID. Repeatable."
    )
    status_p.add_argument(
        "--slice-id", action="append", default=[], help="Affected slice ID. Repeatable."
    )
    status_p.add_argument(
        "--consolidation-json",
        default=None,
        help="Normalized consolidation summary as a JSON object.",
    )
    status_p.add_argument(
        "--force",
        action="store_true",
        help="Allow deliberate repair when the subfeature is not in the normal state.",
    )

    approve_p = subparsers.add_parser(
        "approve",
        help="Record explicit human approval and optional ready slice IDs for a reviewed subfeature",
    )
    approve_p.add_argument("feature", help="Parent feature slug, folder name, or path")
    approve_p.add_argument("subfeature", help="Subfeature ID, folder name, or path")
    approve_p.add_argument(
        "--approved-by",
        default=None,
        help="Optional approver identity or handle for the approval record.",
    )
    approve_p.add_argument(
        "--approval-note",
        default=None,
        help="Optional approval note describing the approval outcome.",
    )
    approve_p.add_argument(
        "--slice-id",
        action="append",
        default=[],
        help="Ready slice ID to record as part of the approved execution handoff. Repeatable.",
    )

    validate_p = subparsers.add_parser(
        "validate", help="Validate one subfeature registry row and metadata packet"
    )
    validate_p.add_argument("feature", help="Parent feature slug, folder name, or path")
    validate_p.add_argument("subfeature", help="Subfeature ID, folder name, or path")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init-feature":
        return cmd_init_feature(args)
    if args.command == "add":
        return cmd_add(args)
    if args.command == "set-status":
        return cmd_set_status(args)
    if args.command == "approve":
        return cmd_approve(args)
    if args.command == "validate":
        return cmd_validate(args)

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
