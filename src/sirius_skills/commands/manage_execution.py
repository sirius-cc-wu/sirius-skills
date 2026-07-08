import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


SCRIPT_DIR = Path(__file__).resolve().parent

from sirius_skills.lib.workflow_state import evaluate_slice_transition, format_transition_message  # noqa: E402
from sirius_skills.lib.workflow_state import execution_repository  # noqa: E402

DEFAULT_SLICES_DIR = "slices"
DEFAULT_ARCHIVE_DIRNAME = ".archived"
CONFIG_DIR = ".skills"
CONFIG_FILE = os.path.join(CONFIG_DIR, "execution.json")
CONVENTIONS_CONFIG_DIR = ".skills"
CONVENTIONS_CONFIG_FILE = os.path.join(CONVENTIONS_CONFIG_DIR, "conventions.json")
DEFAULT_PREFERRED_WORKFLOW = "TDD"
DEFAULT_AUTO_START_IMPLEMENTATION = True
REGISTRY_JSON_FILE = "registry.json"
DEFAULT_GENERATED_SLICE_PREFIX = "SPC"
REGISTRY_HEADER = (
    "# Slice Registry\n\n"
    "| ID | Feature | Status | Updated | Closed | Path |\n"
    "|---|---|---|---|---|---|\n"
)
SLICE_METADATA_FILE = ".slice-meta.json"
SLICE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
STATUS_SEQUENCE = [
    "draft",
    "brief_ready",
    "blueprint_ready",
    "execution_ready",
    "closed",
]
VALID_STATUSES = set(STATUS_SEQUENCE)
STATUS_ALIASES = {
    "draft": "draft",
    "brief_ready": "brief_ready",
    "blueprint_ready": "blueprint_ready",
    "execution_ready": "execution_ready",
    "closed": "closed",
}
RELATION_ALIASES = {
    "supersedes": "supersedes",
    "superseded_by": "superseded_by",
    "superseded-by": "superseded_by",
    "invalidates": "invalidates",
    "invalidated_by": "invalidated_by",
    "invalidated-by": "invalidated_by",
    "narrows": "narrows",
    "narrowed_by": "narrowed_by",
    "narrowed-by": "narrowed_by",
    "replaces_partially": "replaces_partially",
    "replaces-partially": "replaces_partially",
    "replaced_partially_by": "replaced_partially_by",
    "replaced-partially-by": "replaced_partially_by",
}
RELATION_INVERSES = {
    "supersedes": "superseded_by",
    "superseded_by": "supersedes",
    "invalidates": "invalidated_by",
    "invalidated_by": "invalidates",
    "narrows": "narrowed_by",
    "narrowed_by": "narrows",
    "replaces_partially": "replaced_partially_by",
    "replaced_partially_by": "replaces_partially",
}


def load_scope_runtime_module():
    from sirius_skills.commands import scope_runtime
    return scope_runtime


SCOPE_RUNTIME = load_scope_runtime_module()


def now_timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "feature"


def normalize_feature_name(value: str) -> str:
    normalized = re.sub(r"\s+", " ", value.strip())
    return normalized.replace("|", "/")


def normalize_slice_dir(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("Slice directory cannot be empty.")
    if normalized in {".", "./"}:
        raise ValueError("Slice directory cannot be the repository root.")
    normalized = normalized.rstrip("/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def validate_slice_id(value: str) -> str:
    slice_id = value.strip()
    if not slice_id:
        raise ValueError("Slice ID cannot be empty.")
    if not SLICE_ID_PATTERN.fullmatch(slice_id):
        raise ValueError(
            "Invalid slice ID. Use only letters, numbers, dot, underscore, and hyphen."
        )
    return slice_id


def normalize_status(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in STATUS_ALIASES:
        raise ValueError(
            f"Invalid status '{value}'. Valid canonical states: {sorted(VALID_STATUSES)}"
        )
    return STATUS_ALIASES[normalized]


def normalize_relation_type(value: str) -> str:
    normalized = value.strip().lower().replace(" ", "_")
    if normalized not in RELATION_ALIASES:
        raise ValueError(
            "Invalid relation type "
            f"'{value}'. Valid relation types: {sorted(set(RELATION_ALIASES.values()))}"
        )
    return RELATION_ALIASES[normalized]


def normalize_optional_timestamp(value: object) -> Optional[str]:
    if value in {None, "", "-"}:
        return None
    if not isinstance(value, str):
        raise RuntimeError("Registry timestamp fields must be strings when present.")
    return value


def format_registry_value(value: object) -> str:
    if value in {None, ""}:
        return "-"
    return str(value)


def normalize_relation_scope(value: object) -> Dict[str, object]:
    if value is None or value == "":
        return {}
    if not isinstance(value, dict):
        raise RuntimeError("Relation scope must be a JSON object when present.")

    normalized: Dict[str, object] = {}

    story_title = value.get("story_title")
    if story_title is not None:
        if not isinstance(story_title, str) or not story_title.strip():
            raise RuntimeError("Relation scope field 'story_title' must be a non-empty string.")
        normalized["story_title"] = re.sub(r"\s+", " ", story_title.strip())

    selector = value.get("selector")
    if selector is not None:
        if not isinstance(selector, str) or not selector.strip():
            raise RuntimeError("Relation scope field 'selector' must be a non-empty string.")
        normalized["selector"] = re.sub(r"\s+", " ", selector.strip())

    requirement_ids = value.get("requirement_ids")
    if requirement_ids is not None:
        if not isinstance(requirement_ids, list):
            raise RuntimeError("Relation scope field 'requirement_ids' must be a list.")
        cleaned_ids: List[str] = []
        for item in requirement_ids:
            if not isinstance(item, str) or not item.strip():
                raise RuntimeError(
                    "Relation scope field 'requirement_ids' must contain non-empty strings."
                )
            cleaned_ids.append(item.strip())
        if cleaned_ids:
            normalized["requirement_ids"] = list(dict.fromkeys(cleaned_ids))

    return normalized


def normalize_relation(relation: object) -> Dict[str, object]:
    if not isinstance(relation, dict):
        raise RuntimeError("Relation entries must be JSON objects.")

    normalized = {
        "type": normalize_relation_type(str(relation.get("type", ""))),
        "target_slice": validate_slice_id(str(relation.get("target_slice", ""))),
    }

    scope = normalize_relation_scope(relation.get("scope"))
    if scope:
        normalized["scope"] = scope

    recorded_at = relation.get("recorded_at")
    if recorded_at is not None:
        normalized["recorded_at"] = normalize_optional_timestamp(recorded_at)

    return normalized


def normalize_relations(value: object) -> List[Dict[str, object]]:
    if value is None or value == "":
        return []
    if not isinstance(value, list):
        raise RuntimeError("Relations must be stored as a list.")
    return [normalize_relation(item) for item in value]


def relation_key(relation: Dict[str, object]) -> Tuple[str, str, str]:
    scope = relation.get("scope", {})
    return (
        str(relation["type"]),
        str(relation["target_slice"]),
        json.dumps(scope, sort_keys=True),
    )


def build_relation(
    relation_type: str,
    target_slice: str,
    story_title: Optional[str] = None,
    requirement_ids: Optional[List[str]] = None,
    selector: Optional[str] = None,
    recorded_at: Optional[str] = None,
) -> Dict[str, object]:
    scope: Dict[str, object] = {}
    if story_title:
        scope["story_title"] = story_title
    if requirement_ids:
        scope["requirement_ids"] = requirement_ids
    if selector:
        scope["selector"] = selector

    relation: Dict[str, object] = {
        "type": normalize_relation_type(relation_type),
        "target_slice": validate_slice_id(target_slice),
        "recorded_at": recorded_at or now_timestamp(),
    }
    if scope:
        relation["scope"] = scope
    return normalize_relation(relation)


def normalize_slice_path(path: str) -> str:
    normalized = path.rstrip("/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized + "/"


def resolve_execution_scope_context(scope_context: Optional[object] = None) -> object:
    return scope_context or SCOPE_RUNTIME.resolve_scope_context()


def execution_config_path(scope_context: Optional[object] = None) -> str:
    resolved_scope = resolve_execution_scope_context(scope_context)
    return str(
        SCOPE_RUNTIME.resolve_scope_path(
            resolved_scope.scope_root,
            SCOPE_RUNTIME.config_relative_path("execution"),
        )
    )


def conventions_config_path(scope_context: Optional[object] = None) -> str:
    resolved_scope = resolve_execution_scope_context(scope_context)
    return str(
        SCOPE_RUNTIME.resolve_scope_path(
            resolved_scope.scope_root,
            SCOPE_RUNTIME.config_relative_path("conventions"),
        )
    )


def slice_path_for_row(row: Dict[str, object], scope_context: Optional[object] = None) -> str:
    resolved_scope = resolve_execution_scope_context(scope_context)
    return str(
        SCOPE_RUNTIME.resolve_scope_path(
            resolved_scope.scope_root,
            str(row["path"]).rstrip("/"),
        )
    )


def default_archive_dir(
    slice_dir: Optional[str] = None, scope_context: Optional[object] = None
) -> str:
    if slice_dir:
        base_dir = normalize_slice_dir(slice_dir)
    else:
        config = load_config(required=True, scope_context=scope_context)
        base_dir = normalize_slice_dir(str(config["slice_dir"]))
    return normalize_slice_dir(os.path.join(base_dir, DEFAULT_ARCHIVE_DIRNAME))


def normalize_registry_row(row: Dict[str, object]) -> Dict[str, object]:
    feature_value = row.get("feature")
    path_value = row.get("path")
    if not isinstance(feature_value, str) or not normalize_feature_name(feature_value):
        raise RuntimeError("Registry row field 'feature' must be a non-empty string.")
    if not isinstance(path_value, str):
        raise RuntimeError("Registry row field 'path' must be a string.")

    normalized = {
        "id": validate_slice_id(str(row.get("id", ""))),
        "feature": normalize_feature_name(feature_value),
        "status": normalize_status(str(row.get("status", ""))),
        "path": normalize_slice_path(path_value),
        "updated_at": normalize_optional_timestamp(row.get("updated_at")),
        "closed_at": normalize_optional_timestamp(row.get("closed_at")),
        "archived_at": normalize_optional_timestamp(row.get("archived_at")),
    }
    if "relations" in row:
        normalized["relations"] = normalize_relations(row.get("relations"))
    return normalized


def load_raw_config(
    required: bool = True, scope_context: Optional[object] = None
) -> Dict[str, object]:
    resolved_scope = resolve_execution_scope_context(scope_context)
    config = SCOPE_RUNTIME.load_merged_config(resolved_scope, "execution")
    if config:
        return config
    config_file = execution_config_path(resolved_scope)

    if not os.path.exists(config_file):
        if required:
            raise RuntimeError(
                "Slice config not found at '.skills/execution.json'. "
                "Ask the user where slices should be created, then run "
                "`manage_execution.py init <slice-dir>`."
            )
        return {
            "slice_dir": DEFAULT_SLICES_DIR,
            "preferred_workflow": DEFAULT_PREFERRED_WORKFLOW,
            "auto_start_implementation": DEFAULT_AUTO_START_IMPLEMENTATION,
        }

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Execution config is not valid JSON.") from exc

    if not isinstance(config, dict):
        raise RuntimeError("Execution config must be a JSON object.")
    return config


def load_config(
    required: bool = True, scope_context: Optional[object] = None
) -> Dict[str, object]:
    config = load_raw_config(required=required, scope_context=scope_context)

    slice_dir = config.get("slice_dir", DEFAULT_SLICES_DIR)
    preferred_workflow = config.get(
        "preferred_workflow", DEFAULT_PREFERRED_WORKFLOW
    )
    auto_start_implementation = config.get(
        "auto_start_implementation", False
    )

    if not isinstance(slice_dir, str):
        raise RuntimeError("Execution config field 'slice_dir' must be a string.")
    if not isinstance(preferred_workflow, str):
        raise RuntimeError(
            "Execution config field 'preferred_workflow' must be a string."
        )
    if not isinstance(auto_start_implementation, bool):
        raise RuntimeError(
            "Execution config field 'auto_start_implementation' must be a boolean."
        )

    return {
        "slice_dir": normalize_slice_dir(slice_dir),
        "preferred_workflow": preferred_workflow,
        "auto_start_implementation": auto_start_implementation,
    }


def load_conventions_config(
    required: bool = False, scope_context: Optional[object] = None
) -> Dict[str, str]:
    resolved_scope = resolve_execution_scope_context(scope_context)
    config = SCOPE_RUNTIME.load_merged_config(resolved_scope, "conventions")
    config_file = None if config else conventions_config_path(resolved_scope)

    if config is None and not os.path.exists(config_file):
        if required:
            raise RuntimeError(
                "Conventions config not found at '.skills/conventions.json'."
            )
        return {}

    if config is None:
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Conventions config is not valid JSON.") from exc

    if not isinstance(config, dict):
        raise RuntimeError("Conventions config must be a JSON object.")

    string_fields = (
        "id_pattern",
        "branch_extract_pattern",
        "commit_format",
        "pr_title_format",
        "issue_url_template",
    )
    normalized: Dict[str, str] = {}
    for field in string_fields:
        value = config.get(field)
        if value is None:
            continue
        if not isinstance(value, str):
            raise RuntimeError(f"Conventions config field '{field}' must be a string.")
        normalized[field] = value

    return normalized


def write_config(
    slice_dir: str,
    preferred_workflow: str = DEFAULT_PREFERRED_WORKFLOW,
    auto_start_implementation: bool = DEFAULT_AUTO_START_IMPLEMENTATION,
    scope_context: Optional[object] = None,
) -> None:
    config_file = execution_config_path(scope_context)
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "slice_dir": normalize_slice_dir(slice_dir),
                "preferred_workflow": preferred_workflow,
                "auto_start_implementation": auto_start_implementation,
            },
            f,
            indent=2,
        )
        f.write("\n")


def get_registry_paths(
    required_config: bool = True, scope_context: Optional[object] = None
) -> Tuple[str, str, str]:
    resolved_scope = resolve_execution_scope_context(scope_context)
    config = load_config(required=required_config, scope_context=resolved_scope)
    specs_dir = str(
        SCOPE_RUNTIME.resolve_scope_path(
            resolved_scope.scope_root,
            normalize_slice_dir(str(config["slice_dir"])),
        )
    )
    return (
        specs_dir,
        os.path.join(specs_dir, "README.md"),
        os.path.join(specs_dir, REGISTRY_JSON_FILE),
    )


def parse_registry_markdown(index_file: str) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    if not os.path.exists(index_file):
        return rows

    with open(index_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("|"):
                continue
            if line.startswith("| ID |") or line.startswith("|---"):
                continue
            cols = [c.strip() for c in line.strip("|").split("|")]
            if len(cols) not in {4, 6}:
                continue
            row: Dict[str, object] = {
                "id": cols[0],
                "feature": cols[1],
                "status": cols[2],
                "path": cols[-1],
            }
            if len(cols) == 6:
                row["updated_at"] = normalize_optional_timestamp(cols[3])
                row["closed_at"] = normalize_optional_timestamp(cols[4])
            rows.append(normalize_registry_row(row))
    return rows


def load_registry_json(registry_json_file: str) -> List[Dict[str, object]]:
    raw_rows = execution_repository.read_registry_json(Path(registry_json_file))
    return [normalize_registry_row(row) for row in raw_rows]


def write_registry_markdown(index_file: str, rows: List[Dict[str, object]]) -> None:
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(REGISTRY_HEADER)
        for row in rows:
            f.write(
                "| "
                + " | ".join(
                    [
                        str(row["id"]),
                        str(row["feature"]),
                        str(row["status"]),
                        format_registry_value(row.get("updated_at")),
                        format_registry_value(row.get("closed_at")),
                        str(row["path"]),
                    ]
                )
                + " |\n"
            )


def write_registry_json(registry_json_file: str, rows: List[Dict[str, object]]) -> None:
    execution_repository.write_registry_json(
        Path(registry_json_file), rows, generated_at=now_timestamp()
    )


def ensure_registry(specs_dir: str) -> None:
    os.makedirs(specs_dir, exist_ok=True)
    index_file = os.path.join(specs_dir, "README.md")
    registry_json_file = os.path.join(specs_dir, REGISTRY_JSON_FILE)

    if os.path.exists(registry_json_file):
        rows = load_registry_json(registry_json_file)
        if not os.path.exists(index_file):
            write_registry_markdown(index_file, rows)
        return

    if os.path.exists(index_file):
        rows = parse_registry_markdown(index_file)
        write_registry_markdown(index_file, rows)
        write_registry_json(registry_json_file, rows)
        return

    write_registry_markdown(index_file, [])
    write_registry_json(registry_json_file, [])


def parse_registry(scope_context: Optional[object] = None) -> List[Dict[str, object]]:
    specs_dir, index_file, registry_json_file = get_registry_paths(scope_context=scope_context)
    ensure_registry(specs_dir)
    if os.path.exists(registry_json_file):
        return load_registry_json(registry_json_file)
    return parse_registry_markdown(index_file)


def write_registry(rows: List[Dict[str, object]], scope_context: Optional[object] = None) -> None:
    specs_dir, index_file, registry_json_file = get_registry_paths(scope_context=scope_context)
    ensure_registry(specs_dir)
    normalized_rows = [normalize_registry_row(row) for row in rows]
    write_registry_markdown(index_file, normalized_rows)
    write_registry_json(registry_json_file, normalized_rows)


def get_slice_metadata_path(slice_path: str) -> str:
    return os.path.join(slice_path, SLICE_METADATA_FILE)


def load_slice_metadata(slice_path: str) -> Dict[str, object]:
    metadata = execution_repository.read_slice_metadata_raw(Path(slice_path))
    if "relations" in metadata:
        metadata["relations"] = normalize_relations(metadata.get("relations"))
    return metadata


def write_slice_metadata(slice_path: str, metadata: Dict[str, object]) -> None:
    execution_repository.write_slice_metadata_raw(Path(slice_path), metadata)


def build_slice_metadata(
    row: Dict[str, object],
    status: str,
    existing: Optional[Dict[str, object]] = None,
) -> Dict[str, object]:
    metadata = dict(existing or {})
    timestamp = now_timestamp()

    created_at = metadata.get("created_at")
    if not isinstance(created_at, str):
        metadata["created_at"] = timestamp

    metadata["updated_at"] = timestamp
    metadata["status"] = status
    metadata["slice_id"] = row["id"]
    metadata["feature"] = row["feature"]
    metadata["path"] = row["path"]
    metadata["relations"] = normalize_relations(metadata.get("relations"))
    archived_at = metadata.get("archived_at")
    if archived_at is not None:
        metadata["archived_at"] = normalize_optional_timestamp(archived_at)
    archived_from = metadata.get("archived_from")
    if archived_from is not None:
        if not isinstance(archived_from, str) or not archived_from.strip():
            raise RuntimeError("Slice metadata field 'archived_from' must be a non-empty string.")
        metadata["archived_from"] = normalize_slice_path(archived_from)

    if status == "closed":
        closed_at = metadata.get("closed_at")
        metadata["closed_at"] = closed_at if isinstance(closed_at, str) else timestamp
    else:
        metadata.pop("closed_at", None)

    return metadata


def apply_metadata_to_row(
    row: Dict[str, object], metadata: Dict[str, object]
) -> Dict[str, object]:
    updated = dict(row)
    updated["updated_at"] = normalize_optional_timestamp(metadata.get("updated_at"))
    updated["closed_at"] = normalize_optional_timestamp(metadata.get("closed_at"))
    updated["archived_at"] = normalize_optional_timestamp(metadata.get("archived_at"))
    updated["relations"] = normalize_relations(metadata.get("relations"))
    return normalize_registry_row(updated)


def sync_slice_metadata(row: Dict[str, object], metadata: Dict[str, object]) -> None:
    updated_row = apply_metadata_to_row(row, metadata)
    row.clear()
    row.update(updated_row)
    write_slice_metadata(slice_path_for_row(row), metadata)


def archive_slice(
    rows: List[Dict[str, object]],
    slice: Dict[str, object],
    archive_dir: Optional[str] = None,
    scope_context: Optional[object] = None,
) -> Tuple[bool, str, Dict[str, object]]:
    current_status = normalize_status(str(slice["status"]))
    if current_status != "closed":
        return False, "Only closed slices can be archived.", slice

    resolved_scope = resolve_execution_scope_context(scope_context)
    current_path = str(slice["path"]).rstrip("/")
    current_abs = slice_path_for_row(slice, resolved_scope)
    current_folder = os.path.basename(current_path)
    archive_root = normalize_slice_dir(
        archive_dir or default_archive_dir(scope_context=resolved_scope)
    )
    target_path = os.path.join(archive_root, current_folder)
    target_abs = str(SCOPE_RUNTIME.resolve_scope_path(resolved_scope.scope_root, target_path))

    archive_root_abs = str(
        SCOPE_RUNTIME.resolve_scope_path(resolved_scope.scope_root, archive_root)
    )
    if os.path.commonpath([current_abs, archive_root_abs]) == current_abs:
        return (
            False,
            "Archive directory cannot be inside the slice being archived.",
            slice,
        )

    current_normalized = normalize_slice_path(current_path)
    target_normalized = normalize_slice_path(target_path)
    metadata = load_slice_metadata(current_abs)
    if current_normalized == target_normalized:
        if not isinstance(metadata.get("archived_at"), str):
            metadata["archived_at"] = now_timestamp()
        if not isinstance(metadata.get("archived_from"), str):
            metadata["archived_from"] = current_normalized
        updated_metadata = build_slice_metadata(slice, current_status, existing=metadata)
        sync_slice_metadata(slice, updated_metadata)
        write_registry(rows, scope_context=resolved_scope)
        return True, f"Slice {slice['id']} is already archived at {target_normalized}", slice

    if os.path.exists(target_abs):
        return False, f"Archive target already exists: {target_abs}", slice

    os.makedirs(archive_root_abs, exist_ok=True)
    shutil.move(current_abs, target_abs)

    moved_metadata = load_slice_metadata(target_abs)
    moved_metadata["archived_at"] = (
        moved_metadata["archived_at"]
        if isinstance(moved_metadata.get("archived_at"), str)
        else now_timestamp()
    )
    moved_metadata["archived_from"] = (
        moved_metadata["archived_from"]
        if isinstance(moved_metadata.get("archived_from"), str)
        else current_normalized
    )

    slice["path"] = target_normalized
    updated_metadata = build_slice_metadata(slice, current_status, existing=moved_metadata)
    sync_slice_metadata(slice, updated_metadata)
    write_registry(rows, scope_context=resolved_scope)
    return True, f"Archived {slice['id']} to {target_normalized}", slice


def delete_slice(
    rows: List[Dict[str, object]], slice: Dict[str, object], scope_context: Optional[object] = None
) -> Tuple[bool, str, Dict[str, object]]:
    current_status = normalize_status(str(slice["status"]))
    if current_status != "closed":
        return False, "Only closed slices can be removed.", slice

    resolved_scope = resolve_execution_scope_context(scope_context)
    current_path = slice_path_for_row(slice, resolved_scope)
    if not os.path.isdir(current_path):
        return False, f"Slice directory not found: {current_path}", slice

    deleted_slice_id = str(slice["id"])
    for row in rows:
        if str(row["id"]) == deleted_slice_id:
            continue
        row_path = slice_path_for_row(row, resolved_scope)
        metadata = load_slice_metadata(row_path)
        if not metadata:
            continue
        relations = normalize_relations(metadata.get("relations"))
        retained_relations = [
            relation
            for relation in relations
            if str(relation["target_slice"]) != deleted_slice_id
        ]
        if len(retained_relations) == len(relations):
            continue
        metadata["relations"] = retained_relations
        updated_metadata = build_slice_metadata(
            row, normalize_status(str(row["status"])), existing=metadata
        )
        sync_slice_metadata(row, updated_metadata)

    shutil.rmtree(current_path)
    rows[:] = [row for row in rows if str(row["id"]) != deleted_slice_id]
    write_registry(rows, scope_context=resolved_scope)
    return True, f"Removed closed slice {deleted_slice_id}", slice


def upsert_relation_entry(
    relations: List[Dict[str, object]], relation: Dict[str, object]
) -> List[Dict[str, object]]:
    normalized = [normalize_relation(item) for item in relations]
    key = relation_key(relation)
    retained = [item for item in normalized if relation_key(item) != key]
    retained.append(relation)
    return retained


def relation_display(relation: Dict[str, object]) -> str:
    scope = relation.get("scope", {})
    parts = [f"{relation['type']} -> {relation['target_slice']}"]
    if isinstance(scope, dict) and scope:
        scope_bits: List[str] = []
        story_title = scope.get("story_title")
        if isinstance(story_title, str):
            scope_bits.append(f"story_title={story_title}")
        requirement_ids = scope.get("requirement_ids")
        if isinstance(requirement_ids, list) and requirement_ids:
            scope_bits.append("requirement_ids=" + ",".join(str(item) for item in requirement_ids))
        selector = scope.get("selector")
        if isinstance(selector, str):
            scope_bits.append(f"selector={selector}")
        if scope_bits:
            parts.append(f"({' ; '.join(scope_bits)})")
    return " ".join(parts)


def add_relation(
    rows: List[Dict[str, object]],
    source_slice: Dict[str, object],
    relation_type: str,
    target_selector: str,
    story_title: Optional[str] = None,
    requirement_ids: Optional[List[str]] = None,
    selector: Optional[str] = None,
) -> Tuple[bool, str]:
    target_slice = resolve_slice(rows, target_selector)
    if not target_slice:
        return False, f"Slice not found: {target_selector}"

    if source_slice["id"] == target_slice["id"]:
        return False, "Slice relations cannot target the same slice."

    relation = build_relation(
        relation_type,
        str(target_slice["id"]),
        story_title=story_title,
        requirement_ids=requirement_ids,
        selector=selector,
    )
    inverse_relation = build_relation(
        RELATION_INVERSES[relation["type"]],
        str(source_slice["id"]),
        story_title=story_title,
        requirement_ids=requirement_ids,
        selector=selector,
        recorded_at=str(relation.get("recorded_at") or now_timestamp()),
    )

    source_metadata = build_slice_metadata(
        source_slice,
        normalize_status(str(source_slice["status"])),
        existing=load_slice_metadata(slice_path_for_row(source_slice)),
    )
    source_metadata["relations"] = upsert_relation_entry(
        normalize_relations(source_metadata.get("relations")), relation
    )
    sync_slice_metadata(source_slice, source_metadata)

    target_metadata = build_slice_metadata(
        target_slice,
        normalize_status(str(target_slice["status"])),
        existing=load_slice_metadata(slice_path_for_row(target_slice)),
    )
    target_metadata["relations"] = upsert_relation_entry(
        normalize_relations(target_metadata.get("relations")), inverse_relation
    )
    sync_slice_metadata(target_slice, target_metadata)

    write_registry(rows)
    return True, f"Recorded relation {relation_display(relation)}"


def audit_relations(
    rows: List[Dict[str, object]], slice_selector: Optional[str] = None
) -> Dict[str, object]:
    selected_slices: List[Dict[str, object]]
    if slice_selector:
        slice = resolve_slice(rows, slice_selector)
        if not slice:
            raise RuntimeError(f"Slice not found: {slice_selector}")
        selected_slices = [slice]
    else:
        selected_slices = rows

    row_by_id = {str(row["id"]): row for row in rows}
    metadata_by_id = {
        str(row["id"]): load_slice_metadata(slice_path_for_row(row)) for row in rows
    }

    issues: List[Dict[str, str]] = []
    for row in selected_slices:
        slice_id = str(row["id"])
        relations = normalize_relations(metadata_by_id[slice_id].get("relations"))
        seen = set()
        for relation in relations:
            key = relation_key(relation)
            if key in seen:
                issues.append(
                    {
                        "slice_id": slice_id,
                        "relation_type": str(relation["type"]),
                        "target_slice": str(relation["target_slice"]),
                        "code": "duplicate_relation",
                        "message": "Duplicate relation entry detected.",
                    }
                )
                continue
            seen.add(key)

            target_slice = str(relation["target_slice"])
            if target_slice == slice_id:
                issues.append(
                    {
                        "slice_id": slice_id,
                        "relation_type": str(relation["type"]),
                        "target_slice": target_slice,
                        "code": "self_reference",
                        "message": "Relation points back to the same slice.",
                    }
                )
                continue

            target_row = row_by_id.get(target_slice)
            if not target_row:
                issues.append(
                    {
                        "slice_id": slice_id,
                        "relation_type": str(relation["type"]),
                        "target_slice": target_slice,
                        "code": "missing_target_slice",
                        "message": "Relation target slice does not exist in the registry.",
                    }
                )
                continue

            target_relations = normalize_relations(
                metadata_by_id[target_slice].get("relations")
            )
            expected_inverse = build_relation(
                RELATION_INVERSES[str(relation["type"])],
                slice_id,
                story_title=relation.get("scope", {}).get("story_title")
                if isinstance(relation.get("scope"), dict)
                else None,
                requirement_ids=relation.get("scope", {}).get("requirement_ids")
                if isinstance(relation.get("scope"), dict)
                else None,
                selector=relation.get("scope", {}).get("selector")
                if isinstance(relation.get("scope"), dict)
                else None,
                recorded_at=str(relation.get("recorded_at") or now_timestamp()),
            )
            expected_key = relation_key(expected_inverse)
            if not any(relation_key(item) == expected_key for item in target_relations):
                issues.append(
                    {
                        "slice_id": slice_id,
                        "relation_type": str(relation["type"]),
                        "target_slice": target_slice,
                        "code": "missing_reciprocal_relation",
                        "message": (
                            "Expected reciprocal relation "
                            f"{RELATION_INVERSES[str(relation['type'])]} -> {slice_id} was not found."
                        ),
                    }
                )

    return {
        "ok": len(issues) == 0,
        "slice_ids": [str(row["id"]) for row in selected_slices],
        "issues": issues,
    }


def encode_base36(data: bytes, length: int) -> str:
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    num = int.from_bytes(data, "big")
    if num == 0:
        encoded = "0"
    else:
        chars: List[str] = []
        while num > 0:
            num, rem = divmod(num, 36)
            chars.append(alphabet[rem])
        encoded = "".join(reversed(chars))
    if len(encoded) < length:
        encoded = ("0" * (length - len(encoded))) + encoded
    if len(encoded) > length:
        encoded = encoded[-length:]
    return encoded


def resolve_generated_slice_prefix() -> str:
    return DEFAULT_GENERATED_SLICE_PREFIX


def get_current_branch() -> Optional[str]:
    commands = (
        ["git", "branch", "--show-current"],
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
    )
    for command in commands:
        try:
            branch = (
                subprocess.check_output(command, stderr=subprocess.DEVNULL)
                .decode()
                .strip()
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
        if branch and branch != "HEAD":
            return branch
    return None


def infer_id_from_branch(conventions_config: Optional[Dict[str, str]] = None) -> Optional[str]:
    branch = get_current_branch()
    if not branch:
        return None

    if conventions_config:
        pattern = conventions_config.get("branch_extract_pattern")
        if pattern:
            try:
                match = re.search(pattern, branch)
            except re.error as exc:
                raise RuntimeError(
                    "Conventions config field 'branch_extract_pattern' is not a valid regex."
                ) from exc
            if not match:
                return None
            named_id = match.groupdict().get("id")
            if named_id:
                return named_id
            if match.lastindex:
                return match.group(1)
            return match.group(0)
    return None

def generate_hash_slice_id(
    rows: List[Dict[str, object]],
    name: str,
    description: str = "",
    created_at: Optional[str] = None,
) -> str:
    normalized_name = normalize_feature_name(name)
    if not normalized_name:
        raise ValueError("Feature name cannot be empty.")

    prefix = resolve_generated_slice_prefix()
    timestamp = created_at or datetime.now().isoformat()
    existing_ids = {row["id"] for row in rows}

    for length in range(6, 9):
        for nonce in range(100):
            content = f"{normalized_name}|{description}|{timestamp}|{nonce}"
            digest = hashlib.sha256(content.encode("utf-8")).digest()[:5]
            short = encode_base36(digest, length)
            candidate = f"{prefix}-{short}"
            if candidate not in existing_ids:
                return candidate

    raise RuntimeError("Failed to generate a unique slice ID.")


def resolve_slice(rows: List[Dict[str, object]], selector: str) -> Optional[Dict[str, object]]:
    selector = selector.strip().rstrip("/")
    for row in rows:
        row_path = str(row["path"]).rstrip("/")
        if row["id"] == selector or row_path.endswith(selector):
            return row
        if os.path.basename(row_path) == selector:
            return row
    return None


def find_active_slice(rows: List[Dict[str, object]]) -> Optional[Dict[str, object]]:
    priority = ["execution_ready", "blueprint_ready", "brief_ready", "draft"]
    for wanted in priority:
        matches = [r for r in rows if r["status"] == wanted]
        if matches:
            return matches[-1]
    return rows[-1] if rows else None


def expected_status_for_files(
    brief_exists: bool, requirements_exists: bool, plan_exists: bool, slices_exists: bool
) -> str:
    del slices_exists
    if not brief_exists or not requirements_exists:
        return "draft"
    if not plan_exists:
        return "brief_ready"
    return "blueprint_ready"


def validate_slice(
    row: Dict[str, object], skip_metadata_status_check: bool = False
) -> Tuple[bool, List[str], Dict[str, bool]]:
    issues: List[str] = []
    path = slice_path_for_row(row)
    brief = os.path.join(path, "brief.md")
    requirements = os.path.join(path, "checklists", "requirements.md")
    plan = os.path.join(path, "blueprint.md")
    slices = os.path.join(path, "slices.md")
    metadata = load_slice_metadata(path)
    checks = {
        "slice_dir_exists": os.path.isdir(path),
        "metadata_exists": bool(metadata),
        "brief_exists": os.path.isfile(brief),
        "requirements_exists": os.path.isfile(requirements),
        "plan_exists": os.path.isfile(plan),
        "slices_exists": os.path.isfile(slices),
        "closed_at_recorded": isinstance(metadata.get("closed_at"), str),
        "archived_at_recorded": isinstance(metadata.get("archived_at"), str),
    }

    try:
        normalized_status = normalize_status(str(row["status"]))
    except ValueError:
        issues.append(f"invalid_status:{row['status']}")
        normalized_status = str(row["status"])

    if not checks["slice_dir_exists"]:
        issues.append("missing_slice_directory")
        return False, issues, checks
    if not checks["metadata_exists"]:
        issues.append("missing_slice_metadata")

    expected = expected_status_for_files(
        checks["brief_exists"],
        checks["requirements_exists"],
        checks["plan_exists"],
        checks["slices_exists"],
    )
    if normalized_status in {"draft", "brief_ready", "blueprint_ready"}:
        if normalized_status != expected:
            issues.append(
                f"status_mismatch:status={normalized_status} expected={expected} based_on_files"
            )
    if normalized_status in {"brief_ready", "blueprint_ready", "execution_ready"} and not checks[
        "requirements_exists"
    ]:
        issues.append("missing_requirements_checklist")
    if normalized_status == "execution_ready" and not checks["plan_exists"]:
        issues.append("execution_ready_without_plan")
    if normalized_status == "execution_ready" and not checks["brief_exists"]:
        issues.append("execution_ready_without_brief")
    if normalized_status == "closed" and not (
        checks["brief_exists"] and checks["requirements_exists"] and checks["plan_exists"]
    ):
        issues.append("closed_without_core_artifacts")
    if normalized_status == "closed" and not checks["metadata_exists"]:
        issues.append("closed_without_metadata")
    if normalized_status == "closed" and not checks["closed_at_recorded"]:
        issues.append("closed_without_closed_at")

    metadata_status = metadata.get("status")
    if not skip_metadata_status_check and isinstance(metadata_status, str):
        try:
            normalized_metadata_status = normalize_status(metadata_status)
            if normalized_metadata_status != normalized_status:
                issues.append(
                    "metadata_status_mismatch:"
                    f"metadata={normalized_metadata_status} registry={normalized_status}"
                )
        except ValueError:
            issues.append(f"invalid_metadata_status:{metadata_status}")

    return len(issues) == 0, issues, checks


def create_slice(
    slice_id: str,
    name: str,
    metadata: Optional[Dict[str, object]] = None,
    scope_context: Optional[object] = None,
) -> Tuple[str, bool]:
    resolved_scope = resolve_execution_scope_context(scope_context)
    specs_dir, _, _ = get_registry_paths(scope_context=resolved_scope)
    config = load_config(required=True, scope_context=resolved_scope)
    ensure_registry(specs_dir)
    normalized_id = validate_slice_id(slice_id)
    normalized_name = normalize_feature_name(name)
    if not normalized_name:
        raise ValueError("Feature name cannot be empty.")

    slug = slugify(normalized_name)
    folder = f"{normalized_id}-{slug}"
    slice_path = os.path.join(specs_dir, folder)
    row_path = normalize_slice_path(
        os.path.join(normalize_slice_dir(str(config["slice_dir"])), folder)
    )

    rows = parse_registry(scope_context=resolved_scope)
    if any(
        r["id"] == normalized_id or str(r["path"]).rstrip("/").endswith(folder)
        for r in rows
    ):
        return folder, False

    os.makedirs(slice_path, exist_ok=True)
    row = normalize_registry_row(
        {
            "id": normalized_id,
            "feature": normalized_name,
            "status": "draft",
            "path": row_path,
            "updated_at": now_timestamp(),
            "closed_at": None,
        }
    )
    slice_metadata = build_slice_metadata(row, "draft", existing=metadata)
    write_slice_metadata(slice_path, slice_metadata)

    rows.append(apply_metadata_to_row(row, slice_metadata))
    write_registry(rows, scope_context=resolved_scope)
    return folder, True


def is_allowed_transition(current_status: str, target_status: str) -> bool:
    if current_status == target_status:
        return True
    if current_status not in STATUS_SEQUENCE or target_status not in STATUS_SEQUENCE:
        return False
    current_index = STATUS_SEQUENCE.index(current_status)
    target_index = STATUS_SEQUENCE.index(target_status)
    return target_index == current_index + 1


def validate_slice_for_status(
    row: Dict[str, object], target_status: str
) -> Tuple[bool, List[str], Dict[str, bool]]:
    candidate = dict(row)
    candidate["status"] = target_status
    ok, issues, checks = validate_slice(candidate, skip_metadata_status_check=True)
    if target_status == "closed":
        issues = [
            issue
            for issue in issues
            if issue not in {"closed_without_metadata", "closed_without_closed_at"}
        ]
        ok = len(issues) == 0
    return ok, issues, checks


def update_slice_status(
    rows: List[Dict[str, object]],
    slice: Dict[str, object],
    status: str,
    force: bool = False,
) -> Tuple[bool, str]:
    current_status = normalize_status(str(slice["status"]))
    if not force and not is_allowed_transition(current_status, status):
        return (
            False,
            "Invalid status transition: "
            f"{current_status} -> {status}. Use --force to override.",
        )

    ok, issues, _ = validate_slice_for_status(slice, status)
    if not ok and not force:
        return (
            False,
            f"Cannot set {slice['id']} to status '{status}': {', '.join(issues)}",
        )

    pre_transition_result = None
    if status == "closed":
        pre_transition_result = evaluate_slice_transition(str(slice["id"]), status)
        if pre_transition_result.outcome == "block" and not force:
            return (
                False,
                format_transition_message(
                    f"Cannot set {slice['id']} to status '{status}'", pre_transition_result
                ),
            )

    final_status = status
    auto_started = False
    if status == "blueprint_ready" and not force:
        config = load_config(required=True)
        if bool(config["auto_start_implementation"]):
            auto_ok, auto_issues, _ = validate_slice_for_status(slice, "execution_ready")
            if not auto_ok:
                return (
                    False,
                    "Cannot auto-start implementation for "
                    f"{slice['id']}: {', '.join(auto_issues)}",
                )
            final_status = "execution_ready"
            auto_started = True

    slice_path = slice_path_for_row(slice)
    metadata = load_slice_metadata(slice_path)
    updated_metadata = build_slice_metadata(slice, final_status, existing=metadata)
    write_slice_metadata(slice_path, updated_metadata)

    slice["status"] = final_status
    slice["updated_at"] = normalize_optional_timestamp(updated_metadata.get("updated_at"))
    slice["closed_at"] = normalize_optional_timestamp(updated_metadata.get("closed_at"))
    write_registry(rows)
    post_transition_result = None
    if final_status == "closed":
        post_transition_result = evaluate_slice_transition(str(slice["id"]), final_status)
    if auto_started:
        return (
            True,
            f"Updated {slice['id']} to status 'blueprint_ready' and "
            "auto-started implementation with status 'execution_ready'",
        )
    message = f"Updated {slice['id']} to status '{status}'"
    if final_status == "closed" and force and pre_transition_result is not None:
        return True, format_transition_message(message, pre_transition_result)
    if post_transition_result is not None:
        return True, format_transition_message(message, post_transition_result)
    return True, message


def cmd_init(args: argparse.Namespace) -> int:
    scope_context = resolve_execution_scope_context()
    config = load_config(required=False, scope_context=scope_context)
    slice_dir = (
        normalize_slice_dir(args.slice_dir) if args.slice_dir else config["slice_dir"]
    )
    write_config(
        str(slice_dir),
        preferred_workflow=str(config["preferred_workflow"]),
        auto_start_implementation=bool(config["auto_start_implementation"]),
        scope_context=scope_context,
    )
    ensure_registry(
        str(SCOPE_RUNTIME.resolve_scope_path(scope_context.scope_root, str(slice_dir)))
    )
    print(f"Initialized slice registry and config in '{slice_dir}/'.")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    cmd_args = args.args
    if len(cmd_args) == 1:
        id_to_use = None
        name = cmd_args[0]
    else:
        id_to_use = cmd_args[0]
        name = " ".join(cmd_args[1:])

    if not id_to_use:
        conventions_config = load_conventions_config(required=False)
        rows = parse_registry()
        id_to_use = infer_id_from_branch(conventions_config) or generate_hash_slice_id(
            rows, name
        )

    try:
        folder, created = create_slice(id_to_use, name)
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not created:
        print(f"Slice already exists: {folder}")
        return 0

    print(f"Created slice: {folder}")
    return 0


def cmd_set_status(args: argparse.Namespace) -> int:
    try:
        status = normalize_status(args.status)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    rows = parse_registry()
    slice = resolve_slice(rows, args.slice)
    if not slice:
        print(f"Slice not found: {args.slice}", file=sys.stderr)
        return 2

    success, message = update_slice_status(rows, slice, status, force=args.force)
    stream = sys.stdout if success else sys.stderr
    print(message, file=stream)
    return 0 if success else 2


def cmd_add_relation(args: argparse.Namespace) -> int:
    rows = parse_registry()
    slice = resolve_slice(rows, args.slice)
    if not slice:
        print(f"Slice not found: {args.slice}", file=sys.stderr)
        return 2

    try:
        relation_type = normalize_relation_type(args.relation_type)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    success, message = add_relation(
        rows,
        slice,
        relation_type,
        args.target_slice,
        story_title=args.story_title,
        requirement_ids=args.requirement_id,
        selector=args.selector,
    )
    stream = sys.stdout if success else sys.stderr
    print(message, file=stream)
    return 0 if success else 2


def cmd_get_active(_: argparse.Namespace) -> int:
    rows = parse_registry()
    slice = find_active_slice(rows)
    if not slice:
        print("No slices found.", file=sys.stderr)
        return 1
    print(json.dumps(slice, indent=2))
    return 0


def cmd_validate_slice(args: argparse.Namespace) -> int:
    rows = parse_registry()
    slice = resolve_slice(rows, args.slice)
    if not slice:
        print(f"Slice not found: {args.slice}", file=sys.stderr)
        return 2

    ok, issues, checks = validate_slice(slice)
    result = {"slice": slice, "ok": ok, "checks": checks, "issues": issues}
    print(json.dumps(result, indent=2))
    return 0 if ok else 3


def cmd_audit_relations(args: argparse.Namespace) -> int:
    try:
        result = audit_relations(parse_registry(), slice_selector=args.slice)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.json or result["ok"]:
        print(json.dumps(result, indent=2))
    else:
        for issue in result["issues"]:
            print(
                f"{issue['slice_id']}: {issue['code']} -> {issue['message']}",
                file=sys.stderr,
            )
    return 0 if result["ok"] else 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_p = subparsers.add_parser(
        "init", help="Initialize the slice registry and execution config"
    )
    init_p.add_argument(
        "slice_dir",
        nargs="?",
        help="Slice directory path (defaults to configured path or 'slices')",
    )

    add_p = subparsers.add_parser("add", help="Create a slice from a name or explicit opaque ID")
    add_p.add_argument("args", nargs="+", help="[ID] Name")

    set_p = subparsers.add_parser("set-status", help="Update a slice status")
    set_p.add_argument("slice", help="Slice ID, folder name, or path")
    set_p.add_argument("status", help="New status")
    set_p.add_argument(
        "--force",
        action="store_true",
        help="Override transition and validation safeguards during manual repair.",
    )

    relation_p = subparsers.add_parser(
        "add-relation", help="Record an explicit slice relation with reciprocal metadata"
    )
    relation_p.add_argument("slice", help="Source slice ID, folder name, or path")
    relation_p.add_argument("relation_type", help="Relation type, for example supersedes")
    relation_p.add_argument("target_slice", help="Target slice ID, folder name, or path")
    relation_p.add_argument(
        "--story-title",
        help="Optional soft selector describing the affected story title.",
    )
    relation_p.add_argument(
        "--requirement-id",
        action="append",
        default=[],
        help="Optional requirement ID to scope a partial relation. Repeatable.",
    )
    relation_p.add_argument(
        "--selector",
        help="Optional freeform soft selector for fuzzy story or scope references.",
    )

    subparsers.add_parser("get-active", help="Return the active slice as JSON")

    validate_p = subparsers.add_parser("validate-slice", help="Validate slice/file consistency")
    validate_p.add_argument("slice", help="Slice ID, folder name, or path")

    audit_p = subparsers.add_parser(
        "audit-relations",
        help="Audit relation metadata for missing targets or missing reciprocal links",
    )
    audit_p.add_argument(
        "--slice",
        help="Optional slice ID, folder name, or path to audit a single slice.",
    )
    audit_p.add_argument("--json", action="store_true", help="Emit JSON output.")

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            return cmd_init(args)
        if args.command == "add":
            return cmd_add(args)
        if args.command == "set-status":
            return cmd_set_status(args)
        if args.command == "add-relation":
            return cmd_add_relation(args)
        if args.command == "get-active":
            return cmd_get_active(args)
        if args.command == "validate-slice":
            return cmd_validate_slice(args)
        if args.command == "audit-relations":
            return cmd_audit_relations(args)
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
