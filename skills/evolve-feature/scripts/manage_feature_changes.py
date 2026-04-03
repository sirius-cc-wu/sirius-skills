#!/usr/bin/env python3

import argparse
import json
import os
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

DEFAULT_PLANNING_DIR = "docs/features"
CONFIG_DIR = ".skills"
CONFIG_FILE = os.path.join(CONFIG_DIR, "planning.json")
CHANGES_DIR_NAME = "changes"
REGISTRY_JSON_FILE = "registry.json"
REGISTRY_HEADER = (
    "# Feature Change Registry\n\n"
    "| Change | Status | Type | Updated | Path |\n"
    "|---|---|---|---|---|\n"
)
METADATA_FILE = ".feature-change-meta.json"
FEATURE_META_FILE = ".planning-meta.json"
DISCOVER_FILE = "discover.md"
IMPACT_FILE = "impact-analysis.md"
DESIGN_FILE = "system-design.md"
SLICE_PLANNING_FILE = "slice-planning.md"
SLICE_TRACEABILITY_FILE = "slice-traceability.md"
RECONCILIATION_FILE = "reconciliation.md"
SLUG_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
STATUS_SEQUENCE = [
    "draft",
    "impact_ready",
    "design_ready",
    "breakdown_ready",
    "reviewed",
    "reconciled",
    "closed",
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
    "reconciled": "reconciled",
    "closed": "closed",
}
CHANGE_TYPES = {"additive", "narrowing", "superseding", "replacement"}
CHANGE_TYPE_ALIASES = {
    "additive": "additive",
    "narrowing": "narrowing",
    "superseding": "superseding",
    "replacement": "replacement",
}


def now_timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


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


def normalize_change_type(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in CHANGE_TYPE_ALIASES:
        raise ValueError(
            f"Invalid change type '{value}'. Valid types: {sorted(CHANGE_TYPES)}"
        )
    return CHANGE_TYPE_ALIASES[normalized]


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


def normalize_path(path: str) -> str:
    normalized = path.rstrip("/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized + "/"


def load_config() -> Dict[str, str]:
    if not os.path.exists(CONFIG_FILE):
        return {"planning_dir": DEFAULT_PLANNING_DIR}

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Planning config is not valid JSON.") from exc

    if not isinstance(config, dict):
        raise RuntimeError("Planning config must be a JSON object.")

    planning_dir = config.get("planning_dir", DEFAULT_PLANNING_DIR)
    if not isinstance(planning_dir, str):
        raise RuntimeError("Planning config field 'planning_dir' must be a string.")

    return {"planning_dir": normalize_planning_dir(planning_dir)}


def get_feature_root(feature_slug: str) -> str:
    planning_dir = load_config()["planning_dir"]
    return os.path.join(planning_dir, validate_slug(feature_slug, "Feature slug"))


def resolve_feature_dir(selector: str) -> Tuple[str, str]:
    normalized_selector = selector.rstrip("/")
    if normalized_selector.startswith("./"):
        normalized_selector = normalized_selector[2:]

    candidates = [normalized_selector]
    if os.path.isdir(normalized_selector):
        candidates.append(os.path.basename(normalized_selector))
    else:
        candidates.append(get_feature_root(normalized_selector))

    seen = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        candidate_path = candidate
        if not os.path.isdir(candidate_path):
            continue
        feature_meta_path = os.path.join(candidate_path, FEATURE_META_FILE)
        if os.path.exists(feature_meta_path):
            return candidate_path, os.path.basename(candidate_path)

    feature_slug = validate_slug(os.path.basename(normalized_selector), "Feature slug")
    candidate_path = get_feature_root(feature_slug)
    if os.path.isdir(candidate_path) and os.path.exists(
        os.path.join(candidate_path, FEATURE_META_FILE)
    ):
        return candidate_path, feature_slug

    raise RuntimeError(
        "Canonical feature not found or missing .planning-meta.json: " + selector
    )


def change_registry_paths(feature_dir: str) -> Tuple[str, str, str]:
    changes_dir = os.path.join(feature_dir, CHANGES_DIR_NAME)
    return (
        changes_dir,
        os.path.join(changes_dir, "README.md"),
        os.path.join(changes_dir, REGISTRY_JSON_FILE),
    )


def ensure_change_registry(feature_dir: str) -> None:
    changes_dir, readme_path, registry_json_path = change_registry_paths(feature_dir)
    os.makedirs(changes_dir, exist_ok=True)
    if not os.path.exists(readme_path):
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(REGISTRY_HEADER)
    if not os.path.exists(registry_json_path):
        with open(registry_json_path, "w", encoding="utf-8") as f:
            json.dump({"changes": []}, f, indent=2)
            f.write("\n")


def normalize_registry_row(row: Dict[str, object]) -> Dict[str, object]:
    change_id = row.get("change_id")
    path_value = row.get("path")
    if not isinstance(change_id, str):
        raise RuntimeError("Registry row field 'change_id' must be a string.")
    if not isinstance(path_value, str):
        raise RuntimeError("Registry row field 'path' must be a string.")

    return {
        "change_id": validate_slug(change_id, "Change ID"),
        "status": normalize_status(str(row.get("status", ""))),
        "change_type": normalize_change_type(str(row.get("change_type", "additive"))),
        "updated_at": normalize_optional_timestamp(row.get("updated_at")),
        "path": normalize_path(path_value),
    }


def load_registry(feature_dir: str) -> List[Dict[str, object]]:
    ensure_change_registry(feature_dir)
    _, _, registry_json_path = change_registry_paths(feature_dir)
    try:
        with open(registry_json_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Feature change registry JSON is not valid JSON.") from exc

    if isinstance(payload, list):
        raw_rows = payload
    elif isinstance(payload, dict):
        raw_rows = payload.get("changes")
    else:
        raise RuntimeError("Feature change registry JSON must be a JSON object or list.")

    if raw_rows is None:
        raw_rows = []
    if not isinstance(raw_rows, list):
        raise RuntimeError("Feature change registry field 'changes' must be a list.")
    return [normalize_registry_row(row) for row in raw_rows]


def write_registry(feature_dir: str, rows: List[Dict[str, object]]) -> None:
    ensure_change_registry(feature_dir)
    _, readme_path, registry_json_path = change_registry_paths(feature_dir)
    sorted_rows = sorted(rows, key=lambda row: (row["change_id"], row.get("updated_at") or ""))
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(REGISTRY_HEADER)
        for row in sorted_rows:
            updated = row.get("updated_at") or "-"
            f.write(
                f"| {row['change_id']} | {row['status']} | {row['change_type']} | {updated} | {row['path']} |\n"
            )

    with open(registry_json_path, "w", encoding="utf-8") as f:
        json.dump({"changes": sorted_rows}, f, indent=2)
        f.write("\n")


def metadata_path_for(change_dir: str) -> str:
    return os.path.join(change_dir, METADATA_FILE)


def build_metadata(
    feature_slug: str,
    change_id: str,
    change_type: str = "additive",
    summary: Optional[str] = None,
) -> Dict[str, object]:
    timestamp = now_timestamp()
    return {
        "change_id": validate_slug(change_id, "Change ID"),
        "feature_slug": validate_slug(feature_slug, "Feature slug"),
        "status": "draft",
        "created_at": timestamp,
        "updated_at": timestamp,
        "change_type": normalize_change_type(change_type),
        "summary": normalize_optional_string(summary, "Summary"),
        "affected_artifacts": [],
        "affected_story_ids": [],
        "affected_slice_ids": [],
        "review_note": None,
        "active_change": True,
        "reconciled_at": None,
        "reconciled_files": [],
        "history_targets": [],
    }


def normalize_metadata(payload: object) -> Dict[str, object]:
    if not isinstance(payload, dict):
        raise RuntimeError("Feature change metadata must be a JSON object.")

    change_id = payload.get("change_id")
    feature_slug = payload.get("feature_slug")
    if not isinstance(change_id, str):
        raise RuntimeError("Feature change metadata field 'change_id' must be a string.")
    if not isinstance(feature_slug, str):
        raise RuntimeError("Feature change metadata field 'feature_slug' must be a string.")

    active_change = payload.get("active_change", True)
    if not isinstance(active_change, bool):
        raise RuntimeError("Feature change metadata field 'active_change' must be a boolean.")

    return {
        "change_id": validate_slug(change_id, "Change ID"),
        "feature_slug": validate_slug(feature_slug, "Feature slug"),
        "status": normalize_status(str(payload.get("status", ""))),
        "created_at": normalize_optional_timestamp(payload.get("created_at")) or now_timestamp(),
        "updated_at": normalize_optional_timestamp(payload.get("updated_at")) or now_timestamp(),
        "change_type": normalize_change_type(str(payload.get("change_type", "additive"))),
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
        "review_note": normalize_optional_string(payload.get("review_note"), "Review note"),
        "active_change": active_change,
        "reconciled_at": normalize_optional_timestamp(payload.get("reconciled_at")),
        "reconciled_files": normalize_string_list(
            payload.get("reconciled_files"), "Reconciled files"
        ),
        "history_targets": normalize_string_list(
            payload.get("history_targets"), "History targets"
        ),
    }


def read_metadata(change_dir: str) -> Dict[str, object]:
    path = metadata_path_for(change_dir)
    if not os.path.exists(path):
        raise RuntimeError(f"Feature change metadata not found at '{path}'.")
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Feature change metadata is not valid JSON.") from exc
    return normalize_metadata(payload)


def write_metadata(change_dir: str, metadata: Dict[str, object]) -> None:
    os.makedirs(change_dir, exist_ok=True)
    with open(metadata_path_for(change_dir), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        f.write("\n")


def change_dir_for_row(row: Dict[str, object]) -> str:
    return str(row["path"]).rstrip("/")


def find_change(rows: List[Dict[str, object]], selector: str) -> Optional[Dict[str, object]]:
    normalized_selector = selector.rstrip("/")
    if normalized_selector.startswith("./"):
        normalized_selector = normalized_selector[2:]

    for row in rows:
        if row["change_id"] == normalized_selector:
            return row
        path_value = str(row["path"]).rstrip("/")
        if path_value == normalized_selector:
            return row
        if os.path.basename(path_value) == normalized_selector:
            return row
    return None


def is_active_open_change(row: Dict[str, object]) -> bool:
    return normalize_status(str(row["status"])) != "closed"


def find_active_change(rows: List[Dict[str, object]]) -> Optional[Dict[str, object]]:
    active_rows = [row for row in rows if is_active_open_change(row)]
    if not active_rows:
        return None
    return max(active_rows, key=lambda row: (row.get("updated_at") or "", row["change_id"]))


def write_discover_stub(change_dir: str, feature_slug: str, change_id: str, change_type: str, summary: Optional[str]) -> None:
    discover_path = os.path.join(change_dir, DISCOVER_FILE)
    if os.path.exists(discover_path):
        return

    title = change_id.replace("-", " ").strip().title()
    summary_line = summary or "Describe why the canonical feature needs to change."
    content = f"# Discover: {title}\n\n## Target Feature\n\n- Feature: `{feature_slug}`\n- Change ID: `{change_id}`\n- Change Type: `{change_type}`\n\n## Problem\n\n{summary_line}\n\n## Requested Change\n\n- Describe the new or changed behavior.\n- Note whether this is additive, narrowing, superseding, or replacement work.\n\n## Affected Baseline Artifacts\n\n- `discover.md`\n- `system-design.md`\n\n## Change-local Execution Planning\n\n- Add or update `slice-planning.md` and `slice-traceability.md` inside this change packet for any new execution work.\n- Treat canonical feature breakdown docs as historical context unless impact analysis explicitly says they must change.\n\n## Risks and Open Questions\n\n- What existing stories, slices, or validation paths might this change affect?\n"  # noqa: E501
    with open(discover_path, "w", encoding="utf-8") as f:
        f.write(content)


def validate_required_file(change_dir: str, filename: str) -> Tuple[bool, str]:
    path = os.path.join(change_dir, filename)
    if not os.path.exists(path):
        return False, f"Missing required file '{filename}'."
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    if not content:
        return False, f"Required file '{filename}' is empty."
    return True, f"Found '{filename}'."


def validate_change_state(change_dir: str, metadata: Dict[str, object]) -> Tuple[bool, List[str], List[Dict[str, object]]]:
    checks: List[Dict[str, object]] = []
    issues: List[str] = []
    status = str(metadata["status"])
    status_index = STATUS_SEQUENCE.index(status)

    def record_check(name: str, ok: bool, detail: str) -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})
        if not ok:
            issues.append(detail)

    exists = os.path.isdir(change_dir)
    record_check(
        "change_dir",
        exists,
        "Feature change directory exists." if exists else "Feature change directory does not exist.",
    )
    if not exists:
        return False, issues, checks

    ok, detail = validate_required_file(change_dir, DISCOVER_FILE)
    record_check("discover", ok, detail)

    if status_index >= STATUS_SEQUENCE.index("impact_ready"):
        ok, detail = validate_required_file(change_dir, IMPACT_FILE)
        record_check("impact_analysis", ok, detail)

    if status_index >= STATUS_SEQUENCE.index("design_ready"):
        ok, detail = validate_required_file(change_dir, DESIGN_FILE)
        record_check("system_design", ok, detail)

    if status_index >= STATUS_SEQUENCE.index("breakdown_ready"):
        ok, detail = validate_required_file(change_dir, SLICE_PLANNING_FILE)
        record_check("slice_planning", ok, detail)
        ok, detail = validate_required_file(change_dir, SLICE_TRACEABILITY_FILE)
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

    if status_index >= STATUS_SEQUENCE.index("reconciled"):
        ok, detail = validate_required_file(change_dir, RECONCILIATION_FILE)
        record_check("reconciliation", ok, detail)
        reconciled_files = metadata.get("reconciled_files")
        ok = isinstance(reconciled_files, list) and len(reconciled_files) > 0
        record_check(
            "reconciled_files",
            ok,
            "Reconciled files recorded."
            if ok
            else "Reconciled state requires at least one reconciled file.",
        )

    if status == "closed":
        history_targets = metadata.get("history_targets")
        ok = isinstance(history_targets, list)
        record_check(
            "history_targets",
            ok,
            "History targets field is available for closure bookkeeping."
            if ok
            else "History targets must be stored as a list.",
        )

    return not issues, issues, checks


def can_transition(current: str, target: str) -> bool:
    if current == target:
        return True
    return STATUS_SEQUENCE.index(target) - STATUS_SEQUENCE.index(current) == 1


def create_change(
    feature_dir: str,
    feature_slug: str,
    change_id: str,
    change_type: str,
    summary: Optional[str],
) -> Tuple[str, bool]:
    rows = load_registry(feature_dir)
    existing = find_change(rows, change_id)
    if existing:
        return change_dir_for_row(existing), False

    active = find_active_change(rows)
    if active:
        raise RuntimeError(
            "Feature already has an active open change: "
            f"{active['change_id']}. Close or reconcile it before creating another change."
        )

    change_dir = os.path.join(feature_dir, CHANGES_DIR_NAME, change_id)
    metadata = build_metadata(feature_slug, change_id, change_type=change_type, summary=summary)
    write_metadata(change_dir, metadata)
    write_discover_stub(change_dir, feature_slug, change_id, metadata["change_type"], summary)

    rows.append(
        {
            "change_id": change_id,
            "status": metadata["status"],
            "change_type": metadata["change_type"],
            "updated_at": metadata["updated_at"],
            "path": normalize_path(change_dir),
        }
    )
    write_registry(feature_dir, rows)
    return change_dir, True


def update_change_status(
    feature_dir: str,
    change: Dict[str, object],
    status: str,
    force: bool = False,
    change_type: Optional[str] = None,
    summary: Optional[str] = None,
    review_note: Optional[str] = None,
    affected_artifacts: Optional[List[str]] = None,
    affected_story_ids: Optional[List[str]] = None,
    affected_slice_ids: Optional[List[str]] = None,
    reconciled_files: Optional[List[str]] = None,
    history_targets: Optional[List[str]] = None,
) -> Tuple[bool, str]:
    rows = load_registry(feature_dir)
    selected = find_change(rows, str(change["change_id"]))
    if not selected:
        return False, f"Change disappeared from registry: {change['change_id']}"

    change_dir = change_dir_for_row(selected)
    metadata = read_metadata(change_dir)
    current_status = str(metadata["status"])

    if not force and not can_transition(current_status, status):
        return (
            False,
            f"Invalid status transition from '{current_status}' to '{status}'. Allowed states: {STATUS_SEQUENCE}",
        )

    updated_metadata = dict(metadata)
    updated_metadata["status"] = status
    updated_metadata["updated_at"] = now_timestamp()
    updated_metadata["active_change"] = status != "closed"
    if change_type is not None:
        updated_metadata["change_type"] = normalize_change_type(change_type)
    if summary is not None:
        updated_metadata["summary"] = normalize_optional_string(summary, "Summary")
    if review_note is not None:
        updated_metadata["review_note"] = normalize_optional_string(review_note, "Review note")
    if affected_artifacts is not None:
        updated_metadata["affected_artifacts"] = normalize_string_list(affected_artifacts, "Affected artifacts")
    if affected_story_ids is not None:
        updated_metadata["affected_story_ids"] = normalize_string_list(affected_story_ids, "Affected story IDs")
    if affected_slice_ids is not None:
        updated_metadata["affected_slice_ids"] = normalize_string_list(affected_slice_ids, "Affected slice IDs")
    if reconciled_files is not None:
        updated_metadata["reconciled_files"] = normalize_string_list(reconciled_files, "Reconciled files")
        updated_metadata["reconciled_at"] = now_timestamp() if reconciled_files else None
    if history_targets is not None:
        updated_metadata["history_targets"] = normalize_string_list(history_targets, "History targets")

    ok, issues, _ = validate_change_state(change_dir, updated_metadata)
    if not force and not ok:
        return False, "Cannot set status: " + "; ".join(issues)

    write_metadata(change_dir, updated_metadata)
    selected["status"] = status
    selected["change_type"] = updated_metadata["change_type"]
    selected["updated_at"] = updated_metadata["updated_at"]
    write_registry(feature_dir, rows)
    return True, f"Updated {selected['change_id']} to status '{status}'"


def cmd_init_feature(args: argparse.Namespace) -> int:
    try:
        feature_dir, _ = resolve_feature_dir(args.feature)
        ensure_change_registry(feature_dir)
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(f"Initialized feature change registry: {os.path.join(feature_dir, CHANGES_DIR_NAME)}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    try:
        feature_dir, feature_slug = resolve_feature_dir(args.feature)
        ensure_change_registry(feature_dir)
        change_id = validate_slug(args.change_id, "Change ID")
        change_dir, created = create_change(
            feature_dir,
            feature_slug,
            change_id,
            normalize_change_type(args.type),
            args.summary,
        )
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not created:
        print(f"Feature change already exists: {change_dir}")
        return 0

    print(f"Created feature change: {change_dir}")
    return 0


def cmd_get_active(args: argparse.Namespace) -> int:
    try:
        feature_dir, feature_slug = resolve_feature_dir(args.feature)
        rows = load_registry(feature_dir)
        change = find_active_change(rows)
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not change:
        print(f"No active open change found for feature '{feature_slug}'.", file=sys.stderr)
        return 1

    print(json.dumps(change, indent=2))
    return 0


def cmd_set_status(args: argparse.Namespace) -> int:
    try:
        feature_dir, _ = resolve_feature_dir(args.feature)
        rows = load_registry(feature_dir)
        change = find_change(rows, args.change)
        if not change:
            print(f"Feature change not found: {args.change}", file=sys.stderr)
            return 2
        status = normalize_status(args.status)
        success, message = update_change_status(
            feature_dir,
            change,
            status,
            force=args.force,
            change_type=args.type,
            summary=args.summary,
            review_note=args.review_note,
            affected_artifacts=args.affected_artifact if args.affected_artifact else None,
            affected_story_ids=args.story_id if args.story_id else None,
            affected_slice_ids=args.slice_id if args.slice_id else None,
            reconciled_files=args.reconciled_file if args.reconciled_file else None,
            history_targets=args.history_target if args.history_target else None,
        )
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    stream = sys.stdout if success else sys.stderr
    print(message, file=stream)
    return 0 if success else 2


def cmd_validate(args: argparse.Namespace) -> int:
    try:
        feature_dir, _ = resolve_feature_dir(args.feature)
        rows = load_registry(feature_dir)
        change = find_change(rows, args.change)
        if not change:
            print(f"Feature change not found: {args.change}", file=sys.stderr)
            return 2
        change_dir = change_dir_for_row(change)
        metadata = read_metadata(change_dir)
        ok, issues, checks = validate_change_state(change_dir, metadata)
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    result = {
        "feature": os.path.basename(feature_dir.rstrip("/")),
        "change": change,
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
        "init-feature", help="Initialize feature-local change registry files"
    )
    init_p.add_argument("feature", help="Feature slug, folder name, or path")

    add_p = subparsers.add_parser(
        "add", help="Create a feature change packet for a canonical feature"
    )
    add_p.add_argument("feature", help="Feature slug, folder name, or path")
    add_p.add_argument("change_id", help="Change ID or short slug")
    add_p.add_argument(
        "--type",
        default="additive",
        help="Change type: additive, narrowing, superseding, or replacement.",
    )
    add_p.add_argument("--summary", help="Optional short summary for the change.")

    active_p = subparsers.add_parser(
        "get-active", help="Return the active open change for a canonical feature as JSON"
    )
    active_p.add_argument("feature", help="Feature slug, folder name, or path")

    set_p = subparsers.add_parser("set-status", help="Update a feature change status")
    set_p.add_argument("feature", help="Feature slug, folder name, or path")
    set_p.add_argument("change", help="Change ID, folder name, or path")
    set_p.add_argument("status", help="New status")
    set_p.add_argument("--type", help="Optional change type override.")
    set_p.add_argument("--summary", help="Optional summary override.")
    set_p.add_argument("--review-note", help="Review note to persist when reviewed state is reached.")
    set_p.add_argument(
        "--affected-artifact",
        action="append",
        default=[],
        help="Affected canonical artifact path. Repeatable.",
    )
    set_p.add_argument(
        "--story-id",
        action="append",
        default=[],
        help="Affected story ID. Repeatable.",
    )
    set_p.add_argument(
        "--slice-id",
        action="append",
        default=[],
        help="Affected slice ID. Repeatable.",
    )
    set_p.add_argument(
        "--reconciled-file",
        action="append",
        default=[],
        help="Canonical file updated during reconciliation. Repeatable.",
    )
    set_p.add_argument(
        "--history-target",
        action="append",
        default=[],
        help="History document or canonical rollup target. Repeatable.",
    )
    set_p.add_argument(
        "--force",
        action="store_true",
        help="Override transition and validation safeguards during manual repair.",
    )

    validate_p = subparsers.add_parser(
        "validate", help="Validate one feature change packet"
    )
    validate_p.add_argument("feature", help="Feature slug, folder name, or path")
    validate_p.add_argument("change", help="Change ID, folder name, or path")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init-feature":
        return cmd_init_feature(args)
    if args.command == "add":
        return cmd_add(args)
    if args.command == "get-active":
        return cmd_get_active(args)
    if args.command == "set-status":
        return cmd_set_status(args)
    if args.command == "validate":
        return cmd_validate(args)

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
