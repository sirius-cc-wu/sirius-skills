#!/usr/bin/env python3

import argparse
import importlib.util
import json
import os
import re
import shutil
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

from workflow_state import evaluate_feature_transition, format_transition_message  # noqa: E402

DEFAULT_PLANNING_DIR = "docs/features"
DEFAULT_PROPOSAL_DIR = "docs/proposals"
DEFAULT_DESIGN_DIAGRAM_MODE = "embedded"
VALID_DESIGN_DIAGRAM_MODES = {"embedded", "linked_svg"}
VALID_CONSOLIDATION_DISPOSITIONS = {
    "additive",
    "narrowing",
    "superseding",
    "replacement",
}
CONFIG_DIR = ".skills"
CONFIG_FILE = os.path.join(CONFIG_DIR, "planning.json")
SCOPE_RUNTIME_PATH = Path(__file__).resolve().with_name("scope_runtime.py")
REGISTRY_JSON_FILE = "registry.json"
REGISTRY_HEADER = (
    "# Planning Registry\n\n"
    "| Feature | Status | Updated | Path |\n"
    "|---|---|---|---|\n"
)
METADATA_FILE = ".planning-meta.json"
SUBFEATURE_METADATA_FILE = ".subfeature-meta.json"
FEATURE_SLUG_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
STATUS_SEQUENCE = [
    "discovery_pending",
    "discovery_ready",
    "design_ready",
    "breakdown_ready",
    "planning_reviewed",
    "slice_ready",
    "implemented",
]
SYNCABLE_MAX_STATUS = "slice_ready"
VALID_STATUSES = set(STATUS_SEQUENCE)
STATUS_ALIASES = {
    "discovery_pending": "discovery_pending",
    "discovering": "discovery_pending",
    "discovery_ready": "discovery_ready",
    "discover_ready": "discovery_ready",
    "design_ready": "design_ready",
    "breakdown_ready": "breakdown_ready",
    "review_ready": "planning_reviewed",
    "planning_reviewed": "planning_reviewed",
    "reviewed": "planning_reviewed",
    "slice_ready": "slice_ready",
    "implemented": "implemented",
}
SUBFEATURE_STATUS_TO_PLANNING_STATUS = {
    "draft": "discovery_pending",
    "impact_ready": "discovery_ready",
    "design_ready": "design_ready",
    "breakdown_ready": "breakdown_ready",
    "reviewed": "planning_reviewed",
    "finalized": "implemented",
}


def now_timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def load_scope_runtime_module():
    spec = importlib.util.spec_from_file_location("scope_runtime", SCOPE_RUNTIME_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


SCOPE_RUNTIME = load_scope_runtime_module()


def normalize_planning_dir(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("Planning directory cannot be empty.")
    if normalized in {".", "./"}:
        raise ValueError("Planning directory cannot be the repository root.")
    normalized = normalized.rstrip("/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def normalize_design_diagram_mode(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in VALID_DESIGN_DIAGRAM_MODES:
        raise ValueError(
            "Planning config field 'design_diagram_mode' must be one of "
            f"{sorted(VALID_DESIGN_DIAGRAM_MODES)}."
        )
    return normalized


def validate_feature_slug(value: str) -> str:
    feature_slug = value.strip()
    if not feature_slug:
        raise ValueError("Feature slug cannot be empty.")
    if "/" in feature_slug or "\\" in feature_slug:
        raise ValueError("Feature slug must not contain path separators.")
    if not FEATURE_SLUG_PATTERN.fullmatch(feature_slug):
        raise ValueError(
            "Invalid feature slug. Use only letters, numbers, dot, underscore, and hyphen."
        )
    return feature_slug


def normalize_status(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in STATUS_ALIASES:
        raise ValueError(
            f"Invalid status '{value}'. Valid canonical states: {sorted(VALID_STATUSES)}"
        )
    return STATUS_ALIASES[normalized]


def normalize_optional_timestamp(value: object) -> Optional[str]:
    if value is None or value == "" or value == "-":
        return None
    if not isinstance(value, str):
        raise RuntimeError("Timestamp fields must be strings when present.")
    return value


def normalize_feature_path(path: str) -> str:
    normalized = path.rstrip("/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized + "/"


def relative_path_from_scope_root(path: str, scope_context: object) -> str:
    resolved = Path(path).resolve()
    try:
        relative = resolved.relative_to(Path(scope_context.scope_root).resolve())
    except ValueError as exc:
        raise RuntimeError(
            f"Feature path '{path}' must stay inside scope '{scope_context.scope_root}'."
        ) from exc
    return normalize_feature_path(str(relative))


def normalize_review_note(value: object) -> Optional[str]:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise RuntimeError("Review note must be a string when present.")
    cleaned = re.sub(r"\s+", " ", value.strip())
    return cleaned or None


def normalize_slice_ids(value: object) -> List[str]:
    if value is None or value == "":
        return []
    if not isinstance(value, list):
        raise RuntimeError("Ready slice IDs must be stored as a list.")
    normalized: List[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise RuntimeError("Ready slice IDs must contain non-empty strings.")
        normalized.append(item.strip())
    return list(dict.fromkeys(normalized))


def normalize_story_ids(value: object) -> List[str]:
    if value is None or value == "":
        return []
    if not isinstance(value, list):
        raise RuntimeError("Related story IDs must be stored as a list.")
    normalized: List[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise RuntimeError("Related story IDs must contain non-empty strings.")
        normalized.append(item.strip())
    return list(dict.fromkeys(normalized))


def normalize_string_list_field(value: object, field_name: str) -> List[str]:
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


def normalize_required_string_field(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"{field_name} must be a non-empty string.")
    return value.strip()


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
                "kind": normalize_required_string_field(
                    item.get("kind"), "Consolidation target kind"
                ),
                "ref": normalize_required_string_field(
                    item.get("ref"), "Consolidation target ref"
                ),
                "change": normalize_required_string_field(
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
        "historical_artifacts": normalize_string_list_field(
            value.get("historical_artifacts"), "Historical artifacts"
        ),
        "surface_simplifications": normalize_string_list_field(
            value.get("surface_simplifications"), "Surface simplifications"
        ),
        "justification": normalize_review_note(value.get("justification")),
    }


def parse_consolidation_json_arg(value: Optional[str]) -> Optional[Dict[str, object]]:
    if value is None:
        return None
    try:
        payload = json.loads(value)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Consolidation summary must be valid JSON.") from exc
    return normalize_consolidation_summary(payload)


def load_raw_config(
    required: bool = False, scope_context: Optional[object] = None
) -> Dict[str, object]:
    if scope_context is None:
        scope_context = SCOPE_RUNTIME.resolve_scope_context()
    config = SCOPE_RUNTIME.load_merged_config(scope_context, "planning")
    if not config:
        config_file = str(scope_context.planning_config_path)
        if required:
            raise RuntimeError(
                f"Planning config not found at '{config_file}'. "
                "Ask the user where planning docs should be created, then run "
                "`manage_planning.py init <planning-dir>`."
            )
        return {}
    return config


def load_config(
    required: bool = False, scope_context: Optional[object] = None
) -> Dict[str, str]:
    config = load_raw_config(required=required, scope_context=scope_context)

    planning_dir = config.get("planning_dir", DEFAULT_PLANNING_DIR)
    if not isinstance(planning_dir, str):
        raise RuntimeError("Planning config field 'planning_dir' must be a string.")

    proposal_dir = config.get("proposal_dir", DEFAULT_PROPOSAL_DIR)
    if not isinstance(proposal_dir, str):
        raise RuntimeError("Planning config field 'proposal_dir' must be a string.")

    design_diagram_mode = config.get(
        "design_diagram_mode", DEFAULT_DESIGN_DIAGRAM_MODE
    )
    if not isinstance(design_diagram_mode, str):
        raise RuntimeError(
            "Planning config field 'design_diagram_mode' must be a string."
        )

    return {
        "planning_dir": normalize_planning_dir(planning_dir),
        "proposal_dir": normalize_planning_dir(proposal_dir),
        "design_diagram_mode": normalize_design_diagram_mode(design_diagram_mode),
    }


def write_config(
    planning_dir: str,
    proposal_dir: str,
    design_diagram_mode: str,
    existing: Optional[Dict[str, object]] = None,
) -> None:
    config_file = SCOPE_RUNTIME.resolve_scope_context().planning_config_path
    os.makedirs(config_file.parent, exist_ok=True)
    updated: Dict[str, object] = dict(existing or {})
    updated["planning_dir"] = normalize_planning_dir(planning_dir)
    updated["proposal_dir"] = normalize_planning_dir(proposal_dir)
    updated["design_diagram_mode"] = normalize_design_diagram_mode(
        design_diagram_mode
    )
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(updated, f, indent=2)
        f.write("\n")


def get_registry_paths(
    required_config: bool = False, scope_context: Optional[object] = None
) -> Tuple[str, str, str]:
    if scope_context is None:
        scope_context = SCOPE_RUNTIME.resolve_scope_context()
    config = load_config(required=required_config, scope_context=scope_context)
    planning_dir = SCOPE_RUNTIME.resolve_scope_path(
        scope_context.scope_root,
        normalize_planning_dir(config["planning_dir"]),
    )
    return (
        planning_dir,
        os.path.join(planning_dir, "README.md"),
        os.path.join(planning_dir, REGISTRY_JSON_FILE),
    )


def ensure_registry(planning_dir: str) -> None:
    normalized_planning_dir = normalize_planning_dir(planning_dir)
    index_file = os.path.join(normalized_planning_dir, "README.md")
    registry_json_file = os.path.join(normalized_planning_dir, REGISTRY_JSON_FILE)
    os.makedirs(normalized_planning_dir, exist_ok=True)
    if not os.path.exists(index_file):
        with open(index_file, "w", encoding="utf-8") as f:
            f.write(REGISTRY_HEADER)
    if not os.path.exists(registry_json_file):
        with open(registry_json_file, "w", encoding="utf-8") as f:
            json.dump({"features": []}, f, indent=2)
            f.write("\n")


def normalize_registry_row(row: Dict[str, object]) -> Dict[str, object]:
    feature_value = row.get("feature")
    path_value = row.get("path")
    if not isinstance(feature_value, str):
        raise RuntimeError("Registry row field 'feature' must be a string.")
    if not isinstance(path_value, str):
        raise RuntimeError("Registry row field 'path' must be a string.")

    return {
        "feature": validate_feature_slug(feature_value),
        "status": normalize_status(str(row.get("status", ""))),
        "updated_at": normalize_optional_timestamp(row.get("updated_at")),
        "path": normalize_feature_path(path_value),
    }


def parse_registry_markdown(index_file: str) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    if not os.path.exists(index_file):
        return rows

    with open(index_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("|"):
                continue
            if line.startswith("| Feature |") or line.startswith("|---"):
                continue
            cols = [c.strip() for c in line.strip("|").split("|")]
            if len(cols) != 4:
                continue
            rows.append(
                normalize_registry_row(
                    {
                        "feature": cols[0],
                        "status": cols[1],
                        "updated_at": cols[2],
                        "path": cols[3],
                    }
                )
            )
    return rows


def load_registry_json(registry_json_file: str) -> List[Dict[str, object]]:
    try:
        with open(registry_json_file, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Planning registry JSON is not valid JSON.") from exc

    if isinstance(payload, list):
        raw_rows = payload
    elif isinstance(payload, dict):
        raw_rows = payload.get("features")
    else:
        raise RuntimeError("Planning registry JSON must be a JSON object or list.")

    if raw_rows is None:
        raw_rows = []
    if not isinstance(raw_rows, list):
        raise RuntimeError("Planning registry field 'features' must be a list.")
    return [normalize_registry_row(row) for row in raw_rows]


def write_registry(rows: List[Dict[str, object]], scope_context: Optional[object] = None) -> None:
    planning_dir, index_file, registry_json_file = get_registry_paths(
        required_config=False, scope_context=scope_context
    )
    ensure_registry(planning_dir)

    sorted_rows = sorted(rows, key=lambda row: (str(row["path"]), row.get("updated_at") or ""))
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(REGISTRY_HEADER)
        for row in sorted_rows:
            updated = row.get("updated_at") or "-"
            f.write(
                f"| {row['feature']} | {row['status']} | {updated} | {row['path']} |\n"
            )

    payload = {"features": sorted_rows}
    with open(registry_json_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")


def parse_registry(scope_context: Optional[object] = None) -> List[Dict[str, object]]:
    planning_dir, index_file, registry_json_file = get_registry_paths(
        required_config=False, scope_context=scope_context
    )
    ensure_registry(planning_dir)
    if os.path.exists(registry_json_file):
        rows = load_registry_json(registry_json_file)
    else:
        rows = parse_registry_markdown(index_file)
    return sync_registry(rows, scope_context=scope_context)


def build_registry_row(
    feature_dir: str, metadata: Dict[str, object], scope_context: object
) -> Dict[str, object]:
    return {
        "feature": validate_feature_slug(str(metadata["feature_slug"])),
        "status": normalize_status(str(metadata["status"])),
        "updated_at": normalize_optional_timestamp(metadata.get("updated_at")),
        "path": relative_path_from_scope_root(feature_dir, scope_context),
    }


def discover_feature_dirs(planning_dir: str) -> List[str]:
    root = Path(planning_dir)
    if not root.exists():
        return []
    discovered_paths = {
        str(metadata_path.parent)
        for metadata_path in root.rglob(METADATA_FILE)
        if metadata_path.is_file()
    }
    discovered_paths.update(
        str(metadata_path.parent)
        for metadata_path in root.rglob(SUBFEATURE_METADATA_FILE)
        if metadata_path.is_file()
    )
    return sorted(discovered_paths)


def sync_registry(
    seed_rows: Optional[List[Dict[str, object]]] = None, scope_context: Optional[object] = None
) -> List[Dict[str, object]]:
    if scope_context is None:
        scope_context = SCOPE_RUNTIME.resolve_scope_context()
    planning_dir, _, _ = get_registry_paths(required_config=False, scope_context=scope_context)
    ensure_registry(planning_dir)

    by_path: Dict[str, Dict[str, object]] = {}
    for row in seed_rows or []:
        by_path[str(row["path"])] = dict(row)

    discovered_paths = set()
    for feature_dir in discover_feature_dirs(planning_dir):
        metadata = read_metadata(feature_dir)
        row = build_registry_row(feature_dir, metadata, scope_context)
        discovered_paths.add(str(row["path"]))
        by_path[str(row["path"])] = row

    rows = [row for path, row in by_path.items() if path in discovered_paths]
    write_registry(rows, scope_context=scope_context)
    return rows


def metadata_path_for(feature_dir: str) -> str:
    return os.path.join(feature_dir, METADATA_FILE)


def subfeature_metadata_path_for(feature_dir: str) -> str:
    return os.path.join(feature_dir, SUBFEATURE_METADATA_FILE)


def _derived_subfeature_metadata(feature_dir: str) -> Optional[Dict[str, object]]:
    path = subfeature_metadata_path_for(feature_dir)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Subfeature metadata is not valid JSON.") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("Subfeature metadata must be a JSON object.")
    subfeature_id = payload.get("subfeature_id")
    if not isinstance(subfeature_id, str):
        raise RuntimeError("Subfeature metadata field 'subfeature_id' must be a string.")
    raw_status = payload.get("status")
    if not isinstance(raw_status, str):
        raise RuntimeError("Subfeature metadata field 'status' must be a string.")
    planning_status = SUBFEATURE_STATUS_TO_PLANNING_STATUS.get(raw_status.strip().lower())
    if planning_status is None:
        raise RuntimeError(
            f"Subfeature status '{raw_status}' cannot be mapped into planning metadata."
        )
    return {
        "feature_slug": validate_feature_slug(subfeature_id),
        "status": planning_status,
        "created_at": normalize_optional_timestamp(payload.get("created_at"))
        or now_timestamp(),
        "updated_at": normalize_optional_timestamp(payload.get("updated_at"))
        or now_timestamp(),
        "requires_ui_flow": False,
        "review_note": normalize_review_note(payload.get("review_note")),
        "ready_slice_ids": [],
        "related_story_ids": [],
        "consolidation": normalize_consolidation_summary(payload.get("consolidation")),
    }


def build_metadata(feature_slug: str, requires_ui_flow: bool = False) -> Dict[str, object]:
    timestamp = now_timestamp()
    return {
        "feature_slug": validate_feature_slug(feature_slug),
        "status": "discovery_pending",
        "created_at": timestamp,
        "updated_at": timestamp,
        "requires_ui_flow": requires_ui_flow,
        "review_note": None,
        "ready_slice_ids": [],
        "related_story_ids": [],
        "consolidation": None,
    }


def normalize_metadata(payload: object) -> Dict[str, object]:
    if not isinstance(payload, dict):
        raise RuntimeError("Planning metadata must be a JSON object.")

    feature_slug = payload.get("feature_slug")
    if not isinstance(feature_slug, str):
        raise RuntimeError("Planning metadata field 'feature_slug' must be a string.")

    requires_ui_flow = payload.get("requires_ui_flow", False)
    if not isinstance(requires_ui_flow, bool):
        raise RuntimeError("Planning metadata field 'requires_ui_flow' must be a boolean.")

    return {
        "feature_slug": validate_feature_slug(feature_slug),
        "status": normalize_status(str(payload.get("status", ""))),
        "created_at": normalize_optional_timestamp(payload.get("created_at")) or now_timestamp(),
        "updated_at": normalize_optional_timestamp(payload.get("updated_at")) or now_timestamp(),
        "requires_ui_flow": requires_ui_flow,
        "review_note": normalize_review_note(payload.get("review_note")),
        "ready_slice_ids": normalize_slice_ids(
            payload.get("ready_slice_ids", payload.get("ready_task_ids"))
        ),
        "related_story_ids": normalize_story_ids(payload.get("related_story_ids")),
        "consolidation": normalize_consolidation_summary(payload.get("consolidation")),
    }


def read_metadata(feature_dir: str) -> Dict[str, object]:
    derived_subfeature_metadata = _derived_subfeature_metadata(feature_dir)
    if derived_subfeature_metadata is not None:
        return derived_subfeature_metadata
    path = metadata_path_for(feature_dir)
    if not os.path.exists(path):
        raise RuntimeError(f"Planning metadata not found at '{path}'.")
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Planning metadata is not valid JSON.") from exc
    return normalize_metadata(payload)


def write_metadata(feature_dir: str, metadata: Dict[str, object]) -> None:
    if os.path.exists(subfeature_metadata_path_for(feature_dir)):
        raise RuntimeError(
            "Subfeature planning state is derived from '.subfeature-meta.json'; "
            "use add-subfeature to update subfeatures."
        )
    os.makedirs(feature_dir, exist_ok=True)
    with open(metadata_path_for(feature_dir), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        f.write("\n")


def feature_dir_for_row(
    row: Dict[str, object], scope_context: Optional[object] = None
) -> str:
    if scope_context is None:
        scope_context = SCOPE_RUNTIME.resolve_scope_context()
    return SCOPE_RUNTIME.resolve_scope_path(
        scope_context.scope_root,
        str(row["path"]).rstrip("/"),
    )


def find_feature(
    rows: List[Dict[str, object]],
    selector: str,
    scope_context: Optional[object] = None,
) -> Optional[Dict[str, object]]:
    normalized_selector = selector.rstrip("/")
    if normalized_selector.startswith("./"):
        normalized_selector = normalized_selector[2:]

    for row in rows:
        if row["feature"] == normalized_selector:
            return row
        path_value = str(row["path"]).rstrip("/")
        if path_value == normalized_selector:
            return row
        absolute_path = feature_dir_for_row(row, scope_context=scope_context).rstrip("/")
        if absolute_path == normalized_selector:
            return row
        if os.path.basename(path_value) == normalized_selector:
            return row
        if os.path.basename(absolute_path) == normalized_selector:
            return row
    return None


def is_slug_selector(selector: str) -> bool:
    normalized_selector = selector.strip()
    if not normalized_selector:
        return False
    if os.path.isabs(normalized_selector):
        return False
    if normalized_selector.startswith("./"):
        return False
    return "/" not in normalized_selector and "\\" not in normalized_selector


def scope_label(scope_root: str, repo_root: str) -> str:
    scope_path = Path(scope_root).resolve()
    repo_path = Path(repo_root).resolve()
    try:
        relative = scope_path.relative_to(repo_path)
    except ValueError:
        return str(scope_path)
    return "." if str(relative) == "." else str(relative)


def list_plausible_scope_contexts(scope_context: object) -> List[object]:
    contexts = [scope_context]
    for nested_scope_root in SCOPE_RUNTIME.list_nested_scope_roots(scope_context.scope_root):
        contexts.append(
            SCOPE_RUNTIME.resolve_scope_context(
                start_path=scope_context.start_dir, explicit_scope=nested_scope_root
            )
        )
    return contexts


def resolve_feature_lookup(
    selector: str, explicit_scope: Optional[str] = None
) -> Tuple[List[Dict[str, object]], Optional[Dict[str, object]], object]:
    scope_context = SCOPE_RUNTIME.resolve_scope_context(explicit_scope=explicit_scope)
    rows = parse_registry(scope_context=scope_context)

    if explicit_scope is not None or not is_slug_selector(selector):
        return rows, find_feature(rows, selector, scope_context=scope_context), scope_context

    matches: List[Tuple[object, List[Dict[str, object]], Dict[str, object]]] = []
    for candidate_scope_context in list_plausible_scope_contexts(scope_context):
        candidate_rows = parse_registry(scope_context=candidate_scope_context)
        feature = find_feature(
            candidate_rows, selector, scope_context=candidate_scope_context
        )
        if feature:
            matches.append((candidate_scope_context, candidate_rows, feature))

    if not matches:
        return rows, None, scope_context

    if len(matches) == 1:
        candidate_scope_context, candidate_rows, feature = matches[0]
        if candidate_scope_context.scope_root != scope_context.scope_root:
            raise RuntimeError(
                f"Planning feature not found in active scope "
                f"'{scope_label(scope_context.scope_root, scope_context.repo_root)}'. "
                f"Found matching feature in scope "
                f"'{scope_label(candidate_scope_context.scope_root, scope_context.repo_root)}'. "
                "Re-run with --scope <path>."
            )
        return candidate_rows, feature, candidate_scope_context

    candidate_labels = sorted(
        {
            scope_label(
                candidate_scope_context.scope_root, candidate_scope_context.repo_root
            )
            for candidate_scope_context, _, _ in matches
        }
    )
    raise RuntimeError(
        f"Ambiguous planning feature selector '{selector}'. Matching scopes: "
        f"{', '.join(candidate_labels)}. Re-run with --scope <path>."
    )


def find_active_feature(rows: List[Dict[str, object]]) -> Optional[Dict[str, object]]:
    if not rows:
        return None
    open_rows = [row for row in rows if row["status"] not in {"slice_ready", "implemented"}]
    candidates = open_rows or rows
    return max(candidates, key=lambda row: (row.get("updated_at") or "", row["feature"]))


def validate_required_file(feature_dir: str, filename: str) -> Tuple[bool, str]:
    path = os.path.join(feature_dir, filename)
    if not os.path.exists(path):
        return False, f"Missing required file '{filename}'."
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    if not content:
        return False, f"Required file '{filename}' is empty."
    return True, f"Found '{filename}'."


def validate_feature_state(feature_dir: str, metadata: Dict[str, object]) -> Tuple[bool, List[str], List[Dict[str, object]]]:
    checks: List[Dict[str, object]] = []
    issues: List[str] = []
    status = str(metadata["status"])
    status_index = STATUS_SEQUENCE.index(status)

    def record_check(name: str, ok: bool, detail: str) -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})
        if not ok:
            issues.append(detail)

    exists = os.path.isdir(feature_dir)
    record_check("feature_dir", exists, "Feature planning directory exists." if exists else "Feature planning directory does not exist.")
    if not exists:
        return False, issues, checks

    if status_index >= STATUS_SEQUENCE.index("discovery_ready"):
        ok, detail = validate_required_file(feature_dir, "discover.md")
        record_check("discover", ok, detail)

    if status_index >= STATUS_SEQUENCE.index("design_ready"):
        ok, detail = validate_required_file(feature_dir, "system-design.md")
        record_check("system_design", ok, detail)
        if bool(metadata.get("requires_ui_flow")):
            ok, detail = validate_required_file(feature_dir, "ui-design.md")
            record_check("ui_design", ok, detail)

    if status_index >= STATUS_SEQUENCE.index("breakdown_ready"):
        ok, detail = validate_required_file(feature_dir, "slice-planning.md")
        record_check("slice_planning", ok, detail)
        ok, detail = validate_required_file(feature_dir, "slice-traceability.md")
        record_check("slice_traceability", ok, detail)

    if status_index >= STATUS_SEQUENCE.index("planning_reviewed"):
        review_note = metadata.get("review_note")
        ok = isinstance(review_note, str) and bool(review_note.strip())
        record_check(
            "review_note",
            ok,
            "Planning review note recorded." if ok else "Planning review requires a non-empty review note.",
        )

    if status == "slice_ready":
        slice_ids = metadata.get("ready_slice_ids")
        ok = isinstance(slice_ids, list) and len(slice_ids) > 0
        record_check(
            "ready_slice_ids",
            ok,
            "Ready slice IDs recorded for slice bootstrap."
            if ok
            else "Slice readiness requires at least one ready slice ID.",
        )

    return not issues, issues, checks


def create_feature(
    feature_slug: str,
    requires_ui_flow: bool = False,
    scope_context: Optional[object] = None,
) -> Tuple[str, bool]:
    if scope_context is None:
        scope_context = SCOPE_RUNTIME.resolve_scope_context()
    planning_dir, _, _ = get_registry_paths(
        required_config=False, scope_context=scope_context
    )
    feature_dir = os.path.join(planning_dir, validate_feature_slug(feature_slug))
    return create_feature_at_path(
        feature_dir,
        feature_slug,
        requires_ui_flow=requires_ui_flow,
        scope_context=scope_context,
    )


def create_feature_at_path(
    feature_dir: str,
    feature_slug: str,
    requires_ui_flow: bool = False,
    scope_context: Optional[object] = None,
) -> Tuple[str, bool]:
    if scope_context is None:
        scope_context = SCOPE_RUNTIME.resolve_scope_context()
    rows = parse_registry(scope_context=scope_context)
    normalized_feature_dir = os.path.normpath(feature_dir)
    for row in rows:
        if os.path.normpath(feature_dir_for_row(row, scope_context=scope_context)) == normalized_feature_dir:
            return normalized_feature_dir, False
    existing = find_feature(rows, feature_slug, scope_context=scope_context)
    if existing:
        return feature_dir_for_row(existing, scope_context=scope_context), False

    planning_dir, _, _ = get_registry_paths(
        required_config=False, scope_context=scope_context
    )
    ensure_registry(planning_dir)
    metadata = build_metadata(feature_slug, requires_ui_flow=requires_ui_flow)
    write_metadata(normalized_feature_dir, metadata)
    sync_registry(rows, scope_context=scope_context)
    return normalized_feature_dir, True


def can_transition(current: str, target: str) -> bool:
    if current == target:
        return True
    return STATUS_SEQUENCE.index(target) - STATUS_SEQUENCE.index(current) == 1


def next_status(current: str) -> Optional[str]:
    current_index = STATUS_SEQUENCE.index(current)
    if current_index >= len(STATUS_SEQUENCE) - 1:
        return None
    return STATUS_SEQUENCE[current_index + 1]


def apply_metadata_overrides(
    metadata: Dict[str, object],
    review_note: Optional[str] = None,
    slice_ids: Optional[List[str]] = None,
    requires_ui_flow: Optional[bool] = None,
    consolidation: Optional[Dict[str, object]] = None,
) -> Dict[str, object]:
    updated_metadata = dict(metadata)
    if review_note is not None:
        updated_metadata["review_note"] = normalize_review_note(review_note)
    if slice_ids is not None:
        updated_metadata["ready_slice_ids"] = normalize_slice_ids(slice_ids)
    if requires_ui_flow is not None:
        updated_metadata["requires_ui_flow"] = requires_ui_flow
    if consolidation is not None:
        updated_metadata["consolidation"] = normalize_consolidation_summary(consolidation)
    return updated_metadata


def update_feature_status(
    rows: List[Dict[str, object]],
    feature: Dict[str, object],
    status: str,
    force: bool = False,
    review_note: Optional[str] = None,
    slice_ids: Optional[List[str]] = None,
    requires_ui_flow: Optional[bool] = None,
    consolidation: Optional[Dict[str, object]] = None,
    scope_context: Optional[object] = None,
) -> Tuple[bool, str]:
    feature_dir = feature_dir_for_row(feature, scope_context=scope_context)
    if os.path.exists(subfeature_metadata_path_for(feature_dir)):
        return (
            False,
            "Subfeature planning state is derived from '.subfeature-meta.json'; "
            "use add-subfeature set-status instead.",
        )
    metadata = read_metadata(feature_dir)
    current_status = str(metadata["status"])

    if not force and not can_transition(current_status, status):
        return (
            False,
            f"Invalid status transition from '{current_status}' to '{status}'. "
            f"Allowed states: {STATUS_SEQUENCE}",
        )

    updated_metadata = dict(metadata)
    updated_metadata["status"] = status
    updated_metadata["updated_at"] = now_timestamp()
    if review_note is not None:
        updated_metadata["review_note"] = normalize_review_note(review_note)
    if slice_ids is not None:
        updated_metadata["ready_slice_ids"] = normalize_slice_ids(slice_ids)
    elif status == "implemented":
        updated_metadata["ready_slice_ids"] = []
    if requires_ui_flow is not None:
        updated_metadata["requires_ui_flow"] = requires_ui_flow
    if consolidation is not None:
        updated_metadata["consolidation"] = normalize_consolidation_summary(consolidation)

    ok, issues, _ = validate_feature_state(feature_dir, updated_metadata)
    if not force and not ok:
        return False, "Cannot set status: " + "; ".join(issues)

    write_metadata(feature_dir, updated_metadata)
    feature["status"] = status
    feature["updated_at"] = updated_metadata["updated_at"]
    write_registry(rows, scope_context=scope_context)
    message = f"Updated {feature['feature']} to status '{status}'"
    transition_result = evaluate_feature_transition(str(feature["feature"]), status)
    return True, format_transition_message(message, transition_result)


def sync_feature_status(
    rows: List[Dict[str, object]],
    feature: Dict[str, object],
    through: Optional[str] = None,
    review_note: Optional[str] = None,
    slice_ids: Optional[List[str]] = None,
    requires_ui_flow: Optional[bool] = None,
    consolidation: Optional[Dict[str, object]] = None,
    scope_context: Optional[object] = None,
) -> Tuple[bool, str]:
    feature_dir = feature_dir_for_row(feature, scope_context=scope_context)
    if os.path.exists(subfeature_metadata_path_for(feature_dir)):
        return (
            False,
            "Subfeature planning state is derived from '.subfeature-meta.json'; "
            "use add-subfeature set-status instead.",
        )
    metadata = read_metadata(feature_dir)
    current_status = str(metadata["status"])

    if through is None:
        target_status = SYNCABLE_MAX_STATUS
    else:
        target_status = through

    if STATUS_SEQUENCE.index(target_status) > STATUS_SEQUENCE.index(SYNCABLE_MAX_STATUS):
        return (
            False,
            f"sync-status supports transitions only through '{SYNCABLE_MAX_STATUS}', "
            f"not '{target_status}'. Use set-status for terminal execution states.",
        )
    if STATUS_SEQUENCE.index(target_status) < STATUS_SEQUENCE.index(current_status):
        return (
            False,
            f"Cannot sync planning feature '{feature['feature']}' backward from "
            f"'{current_status}' to '{target_status}'.",
        )

    updated_metadata = apply_metadata_overrides(
        metadata,
        review_note=review_note,
        slice_ids=slice_ids,
        requires_ui_flow=requires_ui_flow,
        consolidation=consolidation,
    )
    current_ok, current_issues, _ = validate_feature_state(feature_dir, updated_metadata)
    if not current_ok:
        return (
            False,
            f"Cannot sync planning feature '{feature['feature']}' because current status "
            f"'{current_status}' is inconsistent: {'; '.join(current_issues)}",
        )

    working_metadata = dict(updated_metadata)
    advanced_statuses: List[str] = []
    blocked_status: Optional[str] = None
    blocked_issues: List[str] = []

    while True:
        current_working_status = str(working_metadata["status"])
        candidate_status = next_status(current_working_status)
        if candidate_status is None:
            break
        if STATUS_SEQUENCE.index(candidate_status) > STATUS_SEQUENCE.index(target_status):
            break

        candidate_metadata = dict(working_metadata)
        candidate_metadata["status"] = candidate_status
        ok, issues, _ = validate_feature_state(feature_dir, candidate_metadata)
        if not ok:
            blocked_status = candidate_status
            blocked_issues = issues
            break

        working_metadata["status"] = candidate_status
        advanced_statuses.append(candidate_status)

    metadata_changed = working_metadata != metadata
    final_status = str(working_metadata["status"])

    if metadata_changed:
        working_metadata["updated_at"] = now_timestamp()
        write_metadata(feature_dir, working_metadata)
        feature["status"] = final_status
        feature["updated_at"] = working_metadata["updated_at"]
        write_registry(rows, scope_context=scope_context)

    if advanced_statuses:
        message = (
            f"Synced {feature['feature']} from '{current_status}' to '{final_status}' "
            f"(advanced through: {', '.join(advanced_statuses)})."
        )
        transition_result = evaluate_feature_transition(str(feature["feature"]), final_status)
        message = format_transition_message(message, transition_result)
    elif metadata_changed:
        message = (
            f"Updated planning metadata for {feature['feature']} at status "
            f"'{current_status}'."
        )
    else:
        message = (
            f"Planning feature '{feature['feature']}' is already aligned at status "
            f"'{current_status}'."
        )

    if blocked_status is not None:
        message += (
            f" Next blocked status '{blocked_status}': {'; '.join(blocked_issues)}"
        )

    return True, message


def validate_feature(
    feature: Dict[str, object], scope_context: Optional[object] = None
) -> Tuple[bool, List[str], List[Dict[str, object]]]:
    feature_dir = feature_dir_for_row(feature, scope_context=scope_context)
    metadata = read_metadata(feature_dir)
    return validate_feature_state(feature_dir, metadata)


def load_manage_proposals_module():
    script_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "propose",
        "scripts",
        "manage_proposals.py",
    )
    spec = importlib.util.spec_from_file_location("manage_proposals", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load proposal management helpers.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def promote_proposal_to_feature(
    proposal_selector: str,
    feature_slug: Optional[str],
    require_ui_flow: bool = False,
    force: bool = False,
    scope: Optional[str] = None,
    target_scope: Optional[str] = None,
) -> Tuple[bool, str]:
    manage_proposals = load_manage_proposals_module()
    try:
        proposal_rows, proposal, proposal_scope_context = (
            manage_proposals.resolve_proposal_lookup(
                proposal_selector, explicit_scope=scope
            )
        )
    except RuntimeError as exc:
        return False, str(exc)
    if not proposal:
        return False, f"Proposal not found: {proposal_selector}"

    proposal_dir = manage_proposals.proposal_dir_for_row(
        proposal, scope_context=proposal_scope_context
    )
    proposal_metadata = manage_proposals.read_metadata(proposal_dir)
    current_status = str(proposal_metadata["status"])
    if current_status != "accepted" and not force:
        return False, "Only accepted proposals can be promoted."

    target_feature = (
        feature_slug or proposal_metadata.get("target_feature") or proposal["proposal"]
    )
    target_scope_context = proposal_scope_context
    if target_scope is not None:
        try:
            target_scope_context = SCOPE_RUNTIME.resolve_scope_context(
                start_path=proposal_scope_context.start_dir,
                explicit_scope=target_scope,
            )
        except ValueError as exc:
            return False, str(exc)
    try:
        normalized_feature = validate_feature_slug(str(target_feature))
        feature_dir, created = create_feature(
            normalized_feature,
            requires_ui_flow=require_ui_flow,
            scope_context=target_scope_context,
        )
    except (RuntimeError, ValueError) as exc:
        return False, str(exc)

    if not created and not force:
        return False, f"Canonical feature planning folder already exists: {feature_dir}"

    copied_files: List[str] = []

    user_stories_source = os.path.join(proposal_dir, manage_proposals.USER_STORIES_FILE)
    user_stories_target = os.path.join(feature_dir, manage_proposals.USER_STORIES_FILE)
    if os.path.exists(user_stories_source) and not os.path.exists(user_stories_target):
        shutil.copyfile(user_stories_source, user_stories_target)
        copied_files.append(manage_proposals.USER_STORIES_FILE)

    timestamp = now_timestamp()
    updated_metadata = dict(proposal_metadata)
    updated_metadata["status"] = "promoted"
    updated_metadata["updated_at"] = timestamp
    updated_metadata["target_feature"] = normalized_feature
    updated_metadata["promoted_feature"] = normalized_feature
    updated_metadata["promoted_at"] = timestamp
    manage_proposals.write_metadata(proposal_dir, updated_metadata)

    proposal["status"] = "promoted"
    proposal["updated_at"] = timestamp
    manage_proposals.write_registry(proposal_rows, scope_context=proposal_scope_context)

    copied_text = ", ".join(copied_files) if copied_files else "no proposal docs copied"
    return (
        True,
        f"Promoted proposal '{proposal['proposal']}' to feature '{normalized_feature}' "
        f"({copied_text}).",
    )


def cmd_init(args: argparse.Namespace) -> int:
    raw_config = load_raw_config(required=False)
    config = load_config(required=False)
    scope_context = SCOPE_RUNTIME.resolve_scope_context()
    planning_dir = (
        normalize_planning_dir(args.planning_dir) if args.planning_dir else config["planning_dir"]
    )
    write_config(
        planning_dir,
        config["proposal_dir"],
        config["design_diagram_mode"],
        existing=raw_config,
    )
    ensure_registry(SCOPE_RUNTIME.resolve_scope_path(scope_context.scope_root, planning_dir))
    print(f"Initialized planning registry and config in '{planning_dir}/'.")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    try:
        feature_slug = validate_feature_slug(args.feature_slug)
        feature_dir, created = create_feature(
            feature_slug, requires_ui_flow=args.require_ui_flow
        )
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not created:
        print(f"Feature planning folder already exists: {feature_dir}")
        return 0

    print(f"Created planning feature: {feature_dir}")
    return 0


def cmd_set_status(args: argparse.Namespace) -> int:
    try:
        status = normalize_status(args.status)
        rows, feature, scope_context = resolve_feature_lookup(
            args.feature, explicit_scope=args.scope
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not feature:
        print(f"Planning feature not found: {args.feature}", file=sys.stderr)
        return 2

    requires_ui_flow: Optional[bool]
    if args.require_ui_flow:
        requires_ui_flow = True
    elif args.clear_ui_flow:
        requires_ui_flow = False
    else:
        requires_ui_flow = None

    success, message = update_feature_status(
        rows,
        feature,
        status,
        force=args.force,
        review_note=args.review_note,
        slice_ids=args.slice_id if args.slice_id else None,
        requires_ui_flow=requires_ui_flow,
        consolidation=parse_consolidation_json_arg(args.consolidation_json),
        scope_context=scope_context,
    )
    stream = sys.stdout if success else sys.stderr
    print(message, file=stream)
    return 0 if success else 2


def cmd_get_active(_: argparse.Namespace) -> int:
    rows = parse_registry()
    feature = find_active_feature(rows)
    if not feature:
        print("No planning features found.", file=sys.stderr)
        return 1
    print(json.dumps(feature, indent=2))
    return 0


def cmd_validate_feature(args: argparse.Namespace) -> int:
    try:
        _, feature, scope_context = resolve_feature_lookup(
            args.feature, explicit_scope=args.scope
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if not feature:
        print(f"Planning feature not found: {args.feature}", file=sys.stderr)
        return 2

    ok, issues, checks = validate_feature(feature, scope_context=scope_context)
    result = {"feature": feature, "ok": ok, "checks": checks, "issues": issues}
    print(json.dumps(result, indent=2))
    return 0 if ok else 3


def cmd_sync_status(args: argparse.Namespace) -> int:
    try:
        rows, feature, scope_context = resolve_feature_lookup(
            args.feature, explicit_scope=args.scope
        )
        through = normalize_status(args.through) if args.through else None
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not feature:
        print(f"Planning feature not found: {args.feature}", file=sys.stderr)
        return 2

    requires_ui_flow: Optional[bool]
    if args.require_ui_flow:
        requires_ui_flow = True
    elif args.clear_ui_flow:
        requires_ui_flow = False
    else:
        requires_ui_flow = None

    success, message = sync_feature_status(
        rows,
        feature,
        through=through,
        review_note=args.review_note,
        slice_ids=args.slice_id if args.slice_id else None,
        requires_ui_flow=requires_ui_flow,
        consolidation=parse_consolidation_json_arg(args.consolidation_json),
        scope_context=scope_context,
    )
    stream = sys.stdout if success else sys.stderr
    print(message, file=stream)
    return 0 if success else 2


def cmd_promote_proposal(args: argparse.Namespace) -> int:
    success, message = promote_proposal_to_feature(
        args.proposal,
        feature_slug=args.feature_slug,
        require_ui_flow=args.require_ui_flow,
        force=args.force,
        scope=args.scope,
        target_scope=args.target_scope,
    )
    stream = sys.stdout if success else sys.stderr
    print(message, file=stream)
    return 0 if success else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_p = subparsers.add_parser(
        "init", help="Initialize the planning registry and planning config"
    )
    init_p.add_argument(
        "planning_dir",
        nargs="?",
        help="Planning directory path (defaults to configured path or 'docs/features')",
    )

    add_p = subparsers.add_parser(
        "add", help="Create a feature planning folder and metadata"
    )
    add_p.add_argument("feature_slug", help="Feature slug")
    add_p.add_argument(
        "--require-ui-flow",
        action="store_true",
        help="Require ui-design.md before design can be marked ready.",
    )

    set_p = subparsers.add_parser("set-status", help="Update a planning feature status")
    set_p.add_argument("feature", help="Feature slug, folder name, or path")
    set_p.add_argument("status", help="New status")
    set_p.add_argument(
        "--review-note",
        help="Readiness note to persist when planning review is complete.",
    )
    set_p.add_argument(
        "--slice-id",
        action="append",
        default=[],
        help="Ready slice ID for slice bootstrap. Repeatable.",
    )
    set_p.add_argument(
        "--consolidation-json",
        help="Normalized consolidation summary as a JSON object.",
    )
    ui_group = set_p.add_mutually_exclusive_group()
    ui_group.add_argument(
        "--require-ui-flow",
        action="store_true",
        help="Mark UI flow as required for this feature.",
    )
    ui_group.add_argument(
        "--clear-ui-flow",
        action="store_true",
        help="Clear the UI flow requirement for this feature.",
    )
    set_p.add_argument(
        "--force",
        action="store_true",
        help="Override transition and validation safeguards during manual repair.",
    )
    set_p.add_argument(
        "--scope",
        help="Explicit scope path to use for feature lookup.",
    )

    subparsers.add_parser("get-active", help="Return the active planning feature as JSON")

    validate_p = subparsers.add_parser(
        "validate-feature", help="Validate planning feature/file consistency"
    )
    validate_p.add_argument("feature", help="Feature slug, folder name, or path")
    validate_p.add_argument(
        "--scope",
        help="Explicit scope path to use for feature lookup.",
    )

    sync_p = subparsers.add_parser(
        "sync-status",
        help="Advance planning metadata as far as current artifacts safely allow",
    )
    sync_p.add_argument("feature", help="Feature slug, folder name, or path")
    sync_p.add_argument(
        "--through",
        help=(
            "Optional maximum status to reach. Defaults to the highest syncable "
            "planning state."
        ),
    )
    sync_p.add_argument(
        "--review-note",
        help="Review readiness note to persist before attempting planning_reviewed.",
    )
    sync_p.add_argument(
        "--slice-id",
        action="append",
        default=[],
        help="Ready slice ID to persist before attempting slice_ready. Repeatable.",
    )
    sync_p.add_argument(
        "--consolidation-json",
        help="Normalized consolidation summary as a JSON object.",
    )
    sync_ui_group = sync_p.add_mutually_exclusive_group()
    sync_ui_group.add_argument(
        "--require-ui-flow",
        action="store_true",
        help="Mark UI flow as required for this feature before syncing.",
    )
    sync_ui_group.add_argument(
        "--clear-ui-flow",
        action="store_true",
        help="Clear the UI flow requirement for this feature before syncing.",
    )
    sync_p.add_argument(
        "--scope",
        help="Explicit scope path to use for feature lookup.",
    )

    promote_p = subparsers.add_parser(
        "promote-proposal",
        help="Promote an accepted proposal into canonical feature planning",
    )
    promote_p.add_argument("proposal", help="Proposal slug, folder name, or path")
    promote_p.add_argument(
        "--feature-slug",
        help="Canonical feature slug to create. Defaults to target_feature or proposal slug.",
    )
    promote_p.add_argument(
        "--require-ui-flow",
        action="store_true",
        help="Mark UI flow as required when the canonical feature is created.",
    )
    promote_p.add_argument(
        "--force",
        action="store_true",
        help="Override promotion safeguards during manual repair.",
    )
    promote_p.add_argument(
        "--scope",
        help="Explicit scope path to use for proposal lookup.",
    )
    promote_p.add_argument(
        "--target-scope",
        help="Explicit scope path to use for canonical feature creation.",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "init":
            return cmd_init(args)
        if args.command == "add":
            return cmd_add(args)
        if args.command == "set-status":
            return cmd_set_status(args)
        if args.command == "get-active":
            return cmd_get_active(args)
        if args.command == "validate-feature":
            return cmd_validate_feature(args)
        if args.command == "sync-status":
            return cmd_sync_status(args)
        if args.command == "promote-proposal":
            return cmd_promote_proposal(args)
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
