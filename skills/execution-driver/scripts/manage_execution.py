import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

DEFAULT_TRACKS_DIR = "tracks"
CONFIG_DIR = ".skills"
CONFIG_FILE = os.path.join(CONFIG_DIR, "execution.json")
CONVENTIONS_CONFIG_DIR = ".skills"
CONVENTIONS_CONFIG_FILE = os.path.join(CONVENTIONS_CONFIG_DIR, "conventions.json")
DEFAULT_PREFERRED_WORKFLOW = "TDD"
REGISTRY_JSON_FILE = "registry.json"
DEFAULT_GENERATED_TRACK_PREFIX = "SPC"
REGISTRY_HEADER = (
    "# Track Registry\n\n"
    "| ID | Feature | Status | Updated | Closed | Path |\n"
    "|---|---|---|---|---|---|\n"
)
TRACK_METADATA_FILE = ".track-meta.json"
TRACK_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
STATUS_SEQUENCE = [
    "draft",
    "brief_ready",
    "plan_ready",
    "execution_ready",
    "closed",
]
VALID_STATUSES = set(STATUS_SEQUENCE)
STATUS_ALIASES = {
    "draft": "draft",
    "brief_ready": "brief_ready",
    "plan_ready": "plan_ready",
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


def now_timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "feature"


def normalize_feature_name(value: str) -> str:
    normalized = re.sub(r"\s+", " ", value.strip())
    return normalized.replace("|", "/")


def normalize_track_dir(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("Track directory cannot be empty.")
    if normalized in {".", "./"}:
        raise ValueError("Track directory cannot be the repository root.")
    normalized = normalized.rstrip("/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def validate_track_id(value: str) -> str:
    track_id = value.strip()
    if not track_id:
        raise ValueError("Track ID cannot be empty.")
    if not TRACK_ID_PATTERN.fullmatch(track_id):
        raise ValueError(
            "Invalid track ID. Use only letters, numbers, dot, underscore, and hyphen."
        )
    return track_id


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
        "target_track": validate_track_id(str(relation.get("target_track", ""))),
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
        str(relation["target_track"]),
        json.dumps(scope, sort_keys=True),
    )


def build_relation(
    relation_type: str,
    target_track: str,
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
        "target_track": validate_track_id(target_track),
        "recorded_at": recorded_at or now_timestamp(),
    }
    if scope:
        relation["scope"] = scope
    return normalize_relation(relation)


def normalize_track_path(path: str) -> str:
    normalized = path.rstrip("/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized + "/"


def normalize_registry_row(row: Dict[str, object]) -> Dict[str, object]:
    feature_value = row.get("feature")
    path_value = row.get("path")
    if not isinstance(feature_value, str) or not normalize_feature_name(feature_value):
        raise RuntimeError("Registry row field 'feature' must be a non-empty string.")
    if not isinstance(path_value, str):
        raise RuntimeError("Registry row field 'path' must be a string.")

    normalized = {
        "id": validate_track_id(str(row.get("id", ""))),
        "feature": normalize_feature_name(feature_value),
        "status": normalize_status(str(row.get("status", ""))),
        "path": normalize_track_path(path_value),
        "updated_at": normalize_optional_timestamp(row.get("updated_at")),
        "closed_at": normalize_optional_timestamp(row.get("closed_at")),
    }
    if "relations" in row:
        normalized["relations"] = normalize_relations(row.get("relations"))
    return normalized


def load_config(required: bool = True) -> Dict[str, str]:
    if not os.path.exists(CONFIG_FILE):
        if required:
            raise RuntimeError(
                "Track config not found at '.skills/execution.json'. "
                "Ask the user where tracks should be created, then run "
                "`manage_execution.py init <track-dir>`."
            )
        return {
            "track_dir": DEFAULT_TRACKS_DIR,
            "preferred_workflow": DEFAULT_PREFERRED_WORKFLOW,
        }

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Execution config is not valid JSON.") from exc

    if not isinstance(config, dict):
        raise RuntimeError("Execution config must be a JSON object.")

    track_dir = config.get("track_dir", DEFAULT_TRACKS_DIR)
    preferred_workflow = config.get(
        "preferred_workflow", DEFAULT_PREFERRED_WORKFLOW
    )

    if not isinstance(track_dir, str):
        raise RuntimeError("Execution config field 'track_dir' must be a string.")
    if not isinstance(preferred_workflow, str):
        raise RuntimeError(
            "Execution config field 'preferred_workflow' must be a string."
        )

    return {
        "track_dir": normalize_track_dir(track_dir),
        "preferred_workflow": preferred_workflow,
    }


def load_conventions_config(required: bool = False) -> Dict[str, str]:
    if not os.path.exists(CONVENTIONS_CONFIG_FILE):
        if required:
            raise RuntimeError(
                "Conventions config not found at '.skills/conventions.json'."
            )
        return {}

    try:
        with open(CONVENTIONS_CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Conventions config is not valid JSON.") from exc

    if not isinstance(config, dict):
        raise RuntimeError("Conventions config must be a JSON object.")

    string_fields = (
        "issue_tracker",
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
    track_dir: str, preferred_workflow: str = DEFAULT_PREFERRED_WORKFLOW
) -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "track_dir": normalize_track_dir(track_dir),
                "preferred_workflow": preferred_workflow,
            },
            f,
            indent=2,
        )
        f.write("\n")


def get_registry_paths(required_config: bool = True) -> Tuple[str, str, str]:
    config = load_config(required=required_config)
    specs_dir = normalize_track_dir(config["track_dir"])
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
    try:
        with open(registry_json_file, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Track registry JSON is not valid JSON.") from exc

    if isinstance(payload, list):
        raw_rows = payload
    elif isinstance(payload, dict):
        raw_rows = payload.get("tracks")
    else:
        raise RuntimeError("Track registry JSON must be a JSON object or list.")

    if not isinstance(raw_rows, list):
        raise RuntimeError("Specs registry JSON field 'tracks' must be a list.")

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
    with open(registry_json_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "version": 1,
                "generated_at": now_timestamp(),
                "tracks": rows,
            },
            f,
            indent=2,
        )
        f.write("\n")


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


def parse_registry() -> List[Dict[str, object]]:
    specs_dir, index_file, registry_json_file = get_registry_paths()
    ensure_registry(specs_dir)
    if os.path.exists(registry_json_file):
        return load_registry_json(registry_json_file)
    return parse_registry_markdown(index_file)


def write_registry(rows: List[Dict[str, object]]) -> None:
    specs_dir, index_file, registry_json_file = get_registry_paths()
    ensure_registry(specs_dir)
    normalized_rows = [normalize_registry_row(row) for row in rows]
    write_registry_markdown(index_file, normalized_rows)
    write_registry_json(registry_json_file, normalized_rows)


def get_track_metadata_path(track_path: str) -> str:
    return os.path.join(track_path, TRACK_METADATA_FILE)


def load_track_metadata(track_path: str) -> Dict[str, object]:
    metadata_path = get_track_metadata_path(track_path)
    if not os.path.exists(metadata_path):
        return {}

    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Track metadata is not valid JSON: {metadata_path}") from exc

    if not isinstance(metadata, dict):
        raise RuntimeError(f"Track metadata must be a JSON object: {metadata_path}")
    if "relations" in metadata:
        metadata["relations"] = normalize_relations(metadata.get("relations"))
    return metadata


def write_track_metadata(track_path: str, metadata: Dict[str, object]) -> None:
    metadata_path = get_track_metadata_path(track_path)
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        f.write("\n")


def build_track_metadata(
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
    metadata["track_id"] = row["id"]
    metadata["feature"] = row["feature"]
    metadata["path"] = row["path"]
    metadata["relations"] = normalize_relations(metadata.get("relations"))

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
    updated["relations"] = normalize_relations(metadata.get("relations"))
    return normalize_registry_row(updated)


def sync_track_metadata(row: Dict[str, object], metadata: Dict[str, object]) -> None:
    updated_row = apply_metadata_to_row(row, metadata)
    row.clear()
    row.update(updated_row)
    write_track_metadata(str(row["path"]).rstrip("/"), metadata)


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
    parts = [f"{relation['type']} -> {relation['target_track']}"]
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
    source_track: Dict[str, object],
    relation_type: str,
    target_selector: str,
    story_title: Optional[str] = None,
    requirement_ids: Optional[List[str]] = None,
    selector: Optional[str] = None,
) -> Tuple[bool, str]:
    target_track = resolve_track(rows, target_selector)
    if not target_track:
        return False, f"Track not found: {target_selector}"

    if source_track["id"] == target_track["id"]:
        return False, "Track relations cannot target the same track."

    relation = build_relation(
        relation_type,
        str(target_track["id"]),
        story_title=story_title,
        requirement_ids=requirement_ids,
        selector=selector,
    )
    inverse_relation = build_relation(
        RELATION_INVERSES[relation["type"]],
        str(source_track["id"]),
        story_title=story_title,
        requirement_ids=requirement_ids,
        selector=selector,
        recorded_at=str(relation.get("recorded_at") or now_timestamp()),
    )

    source_metadata = build_track_metadata(
        source_track,
        normalize_status(str(source_track["status"])),
        existing=load_track_metadata(str(source_track["path"]).rstrip("/")),
    )
    source_metadata["relations"] = upsert_relation_entry(
        normalize_relations(source_metadata.get("relations")), relation
    )
    sync_track_metadata(source_track, source_metadata)

    target_metadata = build_track_metadata(
        target_track,
        normalize_status(str(target_track["status"])),
        existing=load_track_metadata(str(target_track["path"]).rstrip("/")),
    )
    target_metadata["relations"] = upsert_relation_entry(
        normalize_relations(target_metadata.get("relations")), inverse_relation
    )
    sync_track_metadata(target_track, target_metadata)

    write_registry(rows)
    return True, f"Recorded relation {relation_display(relation)}"


def audit_relations(
    rows: List[Dict[str, object]], track_selector: Optional[str] = None
) -> Dict[str, object]:
    selected_tracks: List[Dict[str, object]]
    if track_selector:
        track = resolve_track(rows, track_selector)
        if not track:
            raise RuntimeError(f"Track not found: {track_selector}")
        selected_tracks = [track]
    else:
        selected_tracks = rows

    row_by_id = {str(row["id"]): row for row in rows}
    metadata_by_id = {
        str(row["id"]): load_track_metadata(str(row["path"]).rstrip("/")) for row in rows
    }

    issues: List[Dict[str, str]] = []
    for row in selected_tracks:
        track_id = str(row["id"])
        relations = normalize_relations(metadata_by_id[track_id].get("relations"))
        seen = set()
        for relation in relations:
            key = relation_key(relation)
            if key in seen:
                issues.append(
                    {
                        "track_id": track_id,
                        "relation_type": str(relation["type"]),
                        "target_track": str(relation["target_track"]),
                        "code": "duplicate_relation",
                        "message": "Duplicate relation entry detected.",
                    }
                )
                continue
            seen.add(key)

            target_track = str(relation["target_track"])
            if target_track == track_id:
                issues.append(
                    {
                        "track_id": track_id,
                        "relation_type": str(relation["type"]),
                        "target_track": target_track,
                        "code": "self_reference",
                        "message": "Relation points back to the same track.",
                    }
                )
                continue

            target_row = row_by_id.get(target_track)
            if not target_row:
                issues.append(
                    {
                        "track_id": track_id,
                        "relation_type": str(relation["type"]),
                        "target_track": target_track,
                        "code": "missing_target_track",
                        "message": "Relation target track does not exist in the registry.",
                    }
                )
                continue

            target_relations = normalize_relations(
                metadata_by_id[target_track].get("relations")
            )
            expected_inverse = build_relation(
                RELATION_INVERSES[str(relation["type"])],
                track_id,
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
                        "track_id": track_id,
                        "relation_type": str(relation["type"]),
                        "target_track": target_track,
                        "code": "missing_reciprocal_relation",
                        "message": (
                            "Expected reciprocal relation "
                            f"{RELATION_INVERSES[str(relation['type'])]} -> {track_id} was not found."
                        ),
                    }
                )

    return {
        "ok": len(issues) == 0,
        "track_ids": [str(row["id"]) for row in selected_tracks],
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


def resolve_generated_track_prefix() -> str:
    return DEFAULT_GENERATED_TRACK_PREFIX


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

def generate_hash_track_id(
    rows: List[Dict[str, object]],
    name: str,
    description: str = "",
    created_at: Optional[str] = None,
) -> str:
    normalized_name = normalize_feature_name(name)
    if not normalized_name:
        raise ValueError("Feature name cannot be empty.")

    prefix = resolve_generated_track_prefix()
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

    raise RuntimeError("Failed to generate a unique track ID.")


def resolve_track(rows: List[Dict[str, object]], selector: str) -> Optional[Dict[str, object]]:
    selector = selector.strip().rstrip("/")
    for row in rows:
        row_path = str(row["path"]).rstrip("/")
        if row["id"] == selector or row_path.endswith(selector):
            return row
        if os.path.basename(row_path) == selector:
            return row
    return None


def find_active_track(rows: List[Dict[str, object]]) -> Optional[Dict[str, object]]:
    priority = ["execution_ready", "plan_ready", "brief_ready", "draft"]
    for wanted in priority:
        matches = [r for r in rows if r["status"] == wanted]
        if matches:
            return matches[-1]
    return rows[-1] if rows else None


def expected_status_for_files(
    brief_exists: bool, requirements_exists: bool, plan_exists: bool, tasks_exists: bool
) -> str:
    del tasks_exists
    if not brief_exists or not requirements_exists:
        return "draft"
    if not plan_exists:
        return "brief_ready"
    return "plan_ready"


def validate_track(
    row: Dict[str, object], skip_metadata_status_check: bool = False
) -> Tuple[bool, List[str], Dict[str, bool]]:
    issues: List[str] = []
    path = str(row["path"]).rstrip("/")
    brief = os.path.join(path, "brief.md")
    requirements = os.path.join(path, "checklists", "requirements.md")
    plan = os.path.join(path, "plan.md")
    tasks = os.path.join(path, "tasks.md")
    metadata = load_track_metadata(path)
    checks = {
        "track_dir_exists": os.path.isdir(path),
        "metadata_exists": bool(metadata),
        "brief_exists": os.path.isfile(brief),
        "requirements_exists": os.path.isfile(requirements),
        "plan_exists": os.path.isfile(plan),
        "tasks_exists": os.path.isfile(tasks),
        "closed_at_recorded": isinstance(metadata.get("closed_at"), str),
    }

    try:
        normalized_status = normalize_status(str(row["status"]))
    except ValueError:
        issues.append(f"invalid_status:{row['status']}")
        normalized_status = str(row["status"])

    if not checks["track_dir_exists"]:
        issues.append("missing_track_directory")
        return False, issues, checks
    if not checks["metadata_exists"]:
        issues.append("missing_track_metadata")

    expected = expected_status_for_files(
        checks["brief_exists"],
        checks["requirements_exists"],
        checks["plan_exists"],
        checks["tasks_exists"],
    )
    if normalized_status in {"draft", "brief_ready", "plan_ready"}:
        if normalized_status != expected:
            issues.append(
                f"status_mismatch:status={normalized_status} expected={expected} based_on_files"
            )
    if normalized_status in {"brief_ready", "plan_ready", "execution_ready"} and not checks[
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


def create_track(
    track_id: str, name: str, metadata: Optional[Dict[str, object]] = None
) -> Tuple[str, bool]:
    specs_dir, _, _ = get_registry_paths()
    ensure_registry(specs_dir)
    normalized_id = validate_track_id(track_id)
    normalized_name = normalize_feature_name(name)
    if not normalized_name:
        raise ValueError("Feature name cannot be empty.")

    slug = slugify(normalized_name)
    folder = f"{normalized_id}-{slug}"
    track_path = os.path.join(specs_dir, folder)

    rows = parse_registry()
    if any(
        r["id"] == normalized_id or str(r["path"]).rstrip("/").endswith(folder)
        for r in rows
    ):
        return folder, False

    os.makedirs(track_path, exist_ok=True)
    row = normalize_registry_row(
        {
            "id": normalized_id,
            "feature": normalized_name,
            "status": "draft",
            "path": normalize_track_path(track_path),
            "updated_at": now_timestamp(),
            "closed_at": None,
        }
    )
    track_metadata = build_track_metadata(row, "draft", existing=metadata)
    write_track_metadata(track_path, track_metadata)

    rows.append(apply_metadata_to_row(row, track_metadata))
    write_registry(rows)
    return folder, True


def is_allowed_transition(current_status: str, target_status: str) -> bool:
    if current_status == target_status:
        return True
    if current_status not in STATUS_SEQUENCE or target_status not in STATUS_SEQUENCE:
        return False
    current_index = STATUS_SEQUENCE.index(current_status)
    target_index = STATUS_SEQUENCE.index(target_status)
    return target_index == current_index + 1


def validate_track_for_status(
    row: Dict[str, object], target_status: str
) -> Tuple[bool, List[str], Dict[str, bool]]:
    candidate = dict(row)
    candidate["status"] = target_status
    ok, issues, checks = validate_track(candidate, skip_metadata_status_check=True)
    if target_status == "closed":
        issues = [
            issue
            for issue in issues
            if issue not in {"closed_without_metadata", "closed_without_closed_at"}
        ]
        ok = len(issues) == 0
    return ok, issues, checks


def update_track_status(
    rows: List[Dict[str, object]],
    track: Dict[str, object],
    status: str,
    force: bool = False,
) -> Tuple[bool, str]:
    current_status = normalize_status(str(track["status"]))
    if not force and not is_allowed_transition(current_status, status):
        return (
            False,
            "Invalid status transition: "
            f"{current_status} -> {status}. Use --force to override.",
        )

    ok, issues, _ = validate_track_for_status(track, status)
    if not ok and not force:
        return (
            False,
            f"Cannot set {track['id']} to status '{status}': {', '.join(issues)}",
        )

    track_path = str(track["path"]).rstrip("/")
    metadata = load_track_metadata(track_path)
    updated_metadata = build_track_metadata(track, status, existing=metadata)
    write_track_metadata(track_path, updated_metadata)

    track["status"] = status
    track["updated_at"] = normalize_optional_timestamp(updated_metadata.get("updated_at"))
    track["closed_at"] = normalize_optional_timestamp(updated_metadata.get("closed_at"))
    write_registry(rows)
    return True, f"Updated {track['id']} to status '{status}'"


def cmd_init(args: argparse.Namespace) -> int:
    config = load_config(required=False)
    track_dir = (
        normalize_track_dir(args.track_dir) if args.track_dir else config["track_dir"]
    )
    write_config(track_dir, preferred_workflow=config["preferred_workflow"])
    ensure_registry(track_dir)
    print(f"Initialized track registry and config in '{track_dir}/'.")
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
        id_to_use = infer_id_from_branch(conventions_config) or generate_hash_track_id(
            rows, name
        )

    try:
        folder, created = create_track(id_to_use, name)
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not created:
        print(f"Track already exists: {folder}")
        return 0

    print(f"Created track: {folder}")
    return 0


def cmd_set_status(args: argparse.Namespace) -> int:
    try:
        status = normalize_status(args.status)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    rows = parse_registry()
    track = resolve_track(rows, args.track)
    if not track:
        print(f"Track not found: {args.track}", file=sys.stderr)
        return 2

    success, message = update_track_status(rows, track, status, force=args.force)
    stream = sys.stdout if success else sys.stderr
    print(message, file=stream)
    return 0 if success else 2


def cmd_add_relation(args: argparse.Namespace) -> int:
    rows = parse_registry()
    track = resolve_track(rows, args.track)
    if not track:
        print(f"Track not found: {args.track}", file=sys.stderr)
        return 2

    try:
        relation_type = normalize_relation_type(args.relation_type)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    success, message = add_relation(
        rows,
        track,
        relation_type,
        args.target_track,
        story_title=args.story_title,
        requirement_ids=args.requirement_id,
        selector=args.selector,
    )
    stream = sys.stdout if success else sys.stderr
    print(message, file=stream)
    return 0 if success else 2


def cmd_get_active(_: argparse.Namespace) -> int:
    rows = parse_registry()
    track = find_active_track(rows)
    if not track:
        print("No tracks found.", file=sys.stderr)
        return 1
    print(json.dumps(track, indent=2))
    return 0


def cmd_validate_track(args: argparse.Namespace) -> int:
    rows = parse_registry()
    track = resolve_track(rows, args.track)
    if not track:
        print(f"Track not found: {args.track}", file=sys.stderr)
        return 2

    ok, issues, checks = validate_track(track)
    result = {"track": track, "ok": ok, "checks": checks, "issues": issues}
    print(json.dumps(result, indent=2))
    return 0 if ok else 3


def cmd_audit_relations(args: argparse.Namespace) -> int:
    try:
        result = audit_relations(parse_registry(), track_selector=args.track)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.json or result["ok"]:
        print(json.dumps(result, indent=2))
    else:
        for issue in result["issues"]:
            print(
                f"{issue['track_id']}: {issue['code']} -> {issue['message']}",
                file=sys.stderr,
            )
    return 0 if result["ok"] else 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_p = subparsers.add_parser(
        "init", help="Initialize the track registry and execution config"
    )
    init_p.add_argument(
        "track_dir",
        nargs="?",
        help="Track directory path (defaults to configured path or 'tracks')",
    )

    add_p = subparsers.add_parser("add", help="Create a track from a name or explicit opaque ID")
    add_p.add_argument("args", nargs="+", help="[ID] Name")

    set_p = subparsers.add_parser("set-status", help="Update a track status")
    set_p.add_argument("track", help="Track ID, folder name, or path")
    set_p.add_argument("status", help="New status")
    set_p.add_argument(
        "--force",
        action="store_true",
        help="Override transition and validation safeguards during manual repair.",
    )

    relation_p = subparsers.add_parser(
        "add-relation", help="Record an explicit track relation with reciprocal metadata"
    )
    relation_p.add_argument("track", help="Source track ID, folder name, or path")
    relation_p.add_argument("relation_type", help="Relation type, for example supersedes")
    relation_p.add_argument("target_track", help="Target track ID, folder name, or path")
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

    subparsers.add_parser("get-active", help="Return the active track as JSON")

    validate_p = subparsers.add_parser("validate-track", help="Validate track/file consistency")
    validate_p.add_argument("track", help="Track ID, folder name, or path")

    audit_p = subparsers.add_parser(
        "audit-relations",
        help="Audit relation metadata for missing targets or missing reciprocal links",
    )
    audit_p.add_argument(
        "--track",
        help="Optional track ID, folder name, or path to audit a single track.",
    )
    audit_p.add_argument("--json", action="store_true", help="Emit JSON output.")

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
        if args.command == "add-relation":
            return cmd_add_relation(args)
        if args.command == "get-active":
            return cmd_get_active(args)
        if args.command == "validate-track":
            return cmd_validate_track(args)
        if args.command == "audit-relations":
            return cmd_audit_relations(args)
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
