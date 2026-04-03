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

DEFAULT_PLANNING_DIR = "docs/features"
DEFAULT_PROPOSAL_DIR = "docs/proposals"
DEFAULT_DESIGN_DIAGRAM_MODE = "embedded"
VALID_DESIGN_DIAGRAM_MODES = {"embedded", "linked_svg"}
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
FEATURE_SLUG_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
STATUS_SEQUENCE = [
    "discovery_pending",
    "discovery_ready",
    "design_ready",
    "breakdown_ready",
    "planning_reviewed",
    "slice_ready",
]
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


def load_raw_config(required: bool = False) -> Dict[str, object]:
    config_file = str(SCOPE_RUNTIME.resolve_scope_context().planning_config_path)
    if not os.path.exists(config_file):
        if required:
            raise RuntimeError(
                f"Planning config not found at '{config_file}'. "
                "Ask the user where planning docs should be created, then run "
                "`manage_planning.py init <planning-dir>`."
            )
        return {}

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Planning config is not valid JSON.") from exc

    if not isinstance(config, dict):
        raise RuntimeError("Planning config must be a JSON object.")

    return config


def load_config(required: bool = False) -> Dict[str, str]:
    config = load_raw_config(required=required)

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


def get_registry_paths(required_config: bool = False) -> Tuple[str, str, str]:
    scope_context = SCOPE_RUNTIME.resolve_scope_context()
    config = load_config(required=required_config)
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


def write_registry(rows: List[Dict[str, object]]) -> None:
    planning_dir, index_file, registry_json_file = get_registry_paths(required_config=False)
    ensure_registry(planning_dir)

    sorted_rows = sorted(rows, key=lambda row: (row["feature"], row.get("updated_at") or ""))
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


def parse_registry() -> List[Dict[str, object]]:
    planning_dir, index_file, registry_json_file = get_registry_paths(required_config=False)
    ensure_registry(planning_dir)
    if os.path.exists(registry_json_file):
        return load_registry_json(registry_json_file)
    rows = parse_registry_markdown(index_file)
    write_registry(rows)
    return rows


def metadata_path_for(feature_dir: str) -> str:
    return os.path.join(feature_dir, METADATA_FILE)


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
        "ready_slice_ids": normalize_slice_ids(payload.get("ready_slice_ids")),
    }


def read_metadata(feature_dir: str) -> Dict[str, object]:
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
    os.makedirs(feature_dir, exist_ok=True)
    with open(metadata_path_for(feature_dir), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        f.write("\n")


def feature_dir_for_row(row: Dict[str, object]) -> str:
    return SCOPE_RUNTIME.resolve_scope_path(
        SCOPE_RUNTIME.resolve_scope_context().scope_root,
        str(row["path"]).rstrip("/"),
    )


def find_feature(rows: List[Dict[str, object]], selector: str) -> Optional[Dict[str, object]]:
    normalized_selector = selector.rstrip("/")
    if normalized_selector.startswith("./"):
        normalized_selector = normalized_selector[2:]

    for row in rows:
        if row["feature"] == normalized_selector:
            return row
        path_value = str(row["path"]).rstrip("/")
        if path_value == normalized_selector:
            return row
        absolute_path = feature_dir_for_row(row).rstrip("/")
        if absolute_path == normalized_selector:
            return row
        if os.path.basename(path_value) == normalized_selector:
            return row
        if os.path.basename(absolute_path) == normalized_selector:
            return row
    return None


def find_active_feature(rows: List[Dict[str, object]]) -> Optional[Dict[str, object]]:
    if not rows:
        return None
    open_rows = [row for row in rows if row["status"] != "slice_ready"]
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

    if status_index >= STATUS_SEQUENCE.index("slice_ready"):
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


def create_feature(feature_slug: str, requires_ui_flow: bool = False) -> Tuple[str, bool]:
    rows = parse_registry()
    existing = find_feature(rows, feature_slug)
    if existing:
        return feature_dir_for_row(existing), False

    config = load_config(required=False)
    planning_dir, _, _ = get_registry_paths(required_config=False)
    ensure_registry(planning_dir)
    feature_dir = os.path.join(planning_dir, feature_slug)
    metadata = build_metadata(feature_slug, requires_ui_flow=requires_ui_flow)
    write_metadata(feature_dir, metadata)
    row_path = normalize_feature_path(
        os.path.join(normalize_planning_dir(config["planning_dir"]), feature_slug)
    )

    rows.append(
        {
            "feature": feature_slug,
            "status": metadata["status"],
            "updated_at": metadata["updated_at"],
            "path": row_path,
        }
    )
    write_registry(rows)
    return feature_dir, True


def can_transition(current: str, target: str) -> bool:
    if current == target:
        return True
    return STATUS_SEQUENCE.index(target) - STATUS_SEQUENCE.index(current) == 1


def update_feature_status(
    rows: List[Dict[str, object]],
    feature: Dict[str, object],
    status: str,
    force: bool = False,
    review_note: Optional[str] = None,
    slice_ids: Optional[List[str]] = None,
    requires_ui_flow: Optional[bool] = None,
) -> Tuple[bool, str]:
    feature_dir = feature_dir_for_row(feature)
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
    if requires_ui_flow is not None:
        updated_metadata["requires_ui_flow"] = requires_ui_flow

    ok, issues, _ = validate_feature_state(feature_dir, updated_metadata)
    if not force and not ok:
        return False, "Cannot set status: " + "; ".join(issues)

    write_metadata(feature_dir, updated_metadata)
    feature["status"] = status
    feature["updated_at"] = updated_metadata["updated_at"]
    write_registry(rows)
    return True, f"Updated {feature['feature']} to status '{status}'"


def validate_feature(feature: Dict[str, object]) -> Tuple[bool, List[str], List[Dict[str, object]]]:
    feature_dir = feature_dir_for_row(feature)
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
) -> Tuple[bool, str]:
    manage_proposals = load_manage_proposals_module()
    proposal_rows = manage_proposals.load_registry()
    proposal = manage_proposals.find_proposal(proposal_rows, proposal_selector)
    if not proposal:
        return False, f"Proposal not found: {proposal_selector}"

    proposal_dir = manage_proposals.proposal_dir_for_row(proposal)
    proposal_metadata = manage_proposals.read_metadata(proposal_dir)
    current_status = str(proposal_metadata["status"])
    if current_status != "accepted" and not force:
        return False, "Only accepted proposals can be promoted."

    target_feature = (
        feature_slug or proposal_metadata.get("target_feature") or proposal["proposal"]
    )
    try:
        normalized_feature = validate_feature_slug(str(target_feature))
        feature_dir, created = create_feature(
            normalized_feature, requires_ui_flow=require_ui_flow
        )
    except (RuntimeError, ValueError) as exc:
        return False, str(exc)

    if not created and not force:
        return False, f"Canonical feature planning folder already exists: {feature_dir}"

    copied_files: List[str] = []
    for filename in [manage_proposals.DISCOVER_FILE, manage_proposals.USER_STORIES_FILE]:
        source = os.path.join(proposal_dir, filename)
        target = os.path.join(feature_dir, filename)
        if os.path.exists(source) and not os.path.exists(target):
            shutil.copyfile(source, target)
            copied_files.append(filename)

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
    manage_proposals.write_registry(proposal_rows)

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
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    rows = parse_registry()
    feature = find_feature(rows, args.feature)
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
    rows = parse_registry()
    feature = find_feature(rows, args.feature)
    if not feature:
        print(f"Planning feature not found: {args.feature}", file=sys.stderr)
        return 2

    ok, issues, checks = validate_feature(feature)
    result = {"feature": feature, "ok": ok, "checks": checks, "issues": issues}
    print(json.dumps(result, indent=2))
    return 0 if ok else 3


def cmd_promote_proposal(args: argparse.Namespace) -> int:
    success, message = promote_proposal_to_feature(
        args.proposal,
        feature_slug=args.feature_slug,
        require_ui_flow=args.require_ui_flow,
        force=args.force,
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

    subparsers.add_parser("get-active", help="Return the active planning feature as JSON")

    validate_p = subparsers.add_parser(
        "validate-feature", help="Validate planning feature/file consistency"
    )
    validate_p.add_argument("feature", help="Feature slug, folder name, or path")

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
        if args.command == "promote-proposal":
            return cmd_promote_proposal(args)
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
