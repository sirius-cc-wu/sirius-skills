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

DEFAULT_PLANNING_DIR = "docs/features"
DEFAULT_PROPOSAL_DIR = "docs/proposals"
CONFIG_DIR = ".skills"
CONFIG_FILE = os.path.join(CONFIG_DIR, "planning.json")
SCOPE_RUNTIME_PATH = (
    Path(__file__).resolve().parents[2] / "guide-planning" / "scripts" / "scope_runtime.py"
)
REGISTRY_JSON_FILE = "registry.json"
REGISTRY_HEADER = (
    "# Proposal Registry\n\n"
    "| Proposal | Status | Updated | Path |\n"
    "|---|---|---|---|\n"
)
METADATA_FILE = ".proposal-meta.json"
DISCOVER_FILE = "discover.md"
USER_STORIES_FILE = "user-stories.md"
SLUG_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
STATUS_SEQUENCE = ["draft", "reviewed", "accepted", "rejected", "promoted"]
VALID_STATUSES = set(STATUS_SEQUENCE)
STATUS_ALIASES = {
    "draft": "draft",
    "reviewed": "reviewed",
    "review_ready": "reviewed",
    "review-ready": "reviewed",
    "accepted": "accepted",
    "approved": "accepted",
    "rejected": "rejected",
    "declined": "rejected",
    "promoted": "promoted",
}
TERMINAL_STATUSES = {"rejected", "promoted"}


def now_timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def load_scope_runtime_module():
    spec = importlib.util.spec_from_file_location("scope_runtime", SCOPE_RUNTIME_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


SCOPE_RUNTIME = load_scope_runtime_module()


def normalize_dir(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} cannot be empty.")
    if normalized in {".", "./"}:
        raise ValueError(f"{field_name} cannot be the repository root.")
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


def normalize_path(path: str) -> str:
    normalized = path.rstrip("/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized + "/"


def load_config(
    required: bool = False, scope_context: Optional[object] = None
) -> Dict[str, str]:
    if scope_context is None:
        scope_context = SCOPE_RUNTIME.resolve_scope_context()
    config = SCOPE_RUNTIME.load_merged_config(scope_context, "planning")
    if not config:
        config_file = str(scope_context.planning_config_path)
        if required:
            raise RuntimeError(
                f"Planning config not found at '{config_file}'. "
                "Ask the user where planning and proposal docs should be created, then run "
                "`manage_proposals.py init`."
            )
        return {
            "planning_dir": DEFAULT_PLANNING_DIR,
            "proposal_dir": DEFAULT_PROPOSAL_DIR,
        }

    planning_dir = config.get("planning_dir", DEFAULT_PLANNING_DIR)
    proposal_dir = config.get("proposal_dir", DEFAULT_PROPOSAL_DIR)
    if not isinstance(planning_dir, str):
        raise RuntimeError("Planning config field 'planning_dir' must be a string.")
    if not isinstance(proposal_dir, str):
        raise RuntimeError("Planning config field 'proposal_dir' must be a string.")

    return {
        "planning_dir": normalize_dir(planning_dir, "Planning directory"),
        "proposal_dir": normalize_dir(proposal_dir, "Proposal directory"),
    }


def write_config(planning_dir: str, proposal_dir: str) -> None:
    config_file = SCOPE_RUNTIME.resolve_scope_context().planning_config_path
    os.makedirs(config_file.parent, exist_ok=True)
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "planning_dir": normalize_dir(planning_dir, "Planning directory"),
                "proposal_dir": normalize_dir(proposal_dir, "Proposal directory"),
            },
            f,
            indent=2,
        )
        f.write("\n")


def get_registry_paths(
    required_config: bool = False, scope_context: Optional[object] = None
) -> Tuple[str, str, str]:
    if scope_context is None:
        scope_context = SCOPE_RUNTIME.resolve_scope_context()
    config = load_config(required=required_config, scope_context=scope_context)
    proposal_dir = SCOPE_RUNTIME.resolve_scope_path(
        scope_context.scope_root,
        normalize_dir(config["proposal_dir"], "Proposal directory"),
    )
    return (
        proposal_dir,
        os.path.join(proposal_dir, "README.md"),
        os.path.join(proposal_dir, REGISTRY_JSON_FILE),
    )


def ensure_registry(proposal_dir: str) -> None:
    normalized_proposal_dir = normalize_dir(proposal_dir, "Proposal directory")
    index_file = os.path.join(normalized_proposal_dir, "README.md")
    registry_json_file = os.path.join(normalized_proposal_dir, REGISTRY_JSON_FILE)
    os.makedirs(normalized_proposal_dir, exist_ok=True)
    if not os.path.exists(index_file):
        with open(index_file, "w", encoding="utf-8") as f:
            f.write(REGISTRY_HEADER)
    if not os.path.exists(registry_json_file):
        with open(registry_json_file, "w", encoding="utf-8") as f:
            json.dump({"proposals": []}, f, indent=2)
            f.write("\n")


def normalize_registry_row(row: Dict[str, object]) -> Dict[str, object]:
    proposal_value = row.get("proposal")
    path_value = row.get("path")
    if not isinstance(proposal_value, str):
        raise RuntimeError("Registry row field 'proposal' must be a string.")
    if not isinstance(path_value, str):
        raise RuntimeError("Registry row field 'path' must be a string.")

    return {
        "proposal": validate_slug(proposal_value, "Proposal slug"),
        "status": normalize_status(str(row.get("status", ""))),
        "updated_at": normalize_optional_timestamp(row.get("updated_at")),
        "path": normalize_path(path_value),
    }


def load_registry(scope_context: Optional[object] = None) -> List[Dict[str, object]]:
    proposal_dir, _, registry_json_file = get_registry_paths(
        required_config=False, scope_context=scope_context
    )
    ensure_registry(proposal_dir)
    try:
        with open(registry_json_file, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Proposal registry JSON is not valid JSON.") from exc

    if isinstance(payload, list):
        raw_rows = payload
    elif isinstance(payload, dict):
        raw_rows = payload.get("proposals")
    else:
        raise RuntimeError("Proposal registry JSON must be a JSON object or list.")

    if raw_rows is None:
        raw_rows = []
    if not isinstance(raw_rows, list):
        raise RuntimeError("Proposal registry field 'proposals' must be a list.")
    return [normalize_registry_row(row) for row in raw_rows]


def write_registry(rows: List[Dict[str, object]], scope_context: Optional[object] = None) -> None:
    proposal_dir, index_file, registry_json_file = get_registry_paths(
        required_config=False, scope_context=scope_context
    )
    ensure_registry(proposal_dir)

    sorted_rows = sorted(rows, key=lambda row: (row["proposal"], row.get("updated_at") or ""))
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(REGISTRY_HEADER)
        for row in sorted_rows:
            updated = row.get("updated_at") or "-"
            f.write(
                f"| {row['proposal']} | {row['status']} | {updated} | {row['path']} |\n"
            )

    with open(registry_json_file, "w", encoding="utf-8") as f:
        json.dump({"proposals": sorted_rows}, f, indent=2)
        f.write("\n")


def get_proposal_root(
    proposal_slug: str, scope_context: Optional[object] = None
) -> str:
    if scope_context is None:
        scope_context = SCOPE_RUNTIME.resolve_scope_context()
    config = load_config(scope_context=scope_context)
    proposal_dir = SCOPE_RUNTIME.resolve_scope_path(
        scope_context.scope_root,
        normalize_dir(config["proposal_dir"], "Proposal directory"),
    )
    return os.path.join(proposal_dir, validate_slug(proposal_slug, "Proposal slug"))


def metadata_path_for(proposal_dir: str) -> str:
    return os.path.join(proposal_dir, METADATA_FILE)


def build_metadata(
    proposal_slug: str,
    summary: Optional[str] = None,
    target_feature: Optional[str] = None,
) -> Dict[str, object]:
    timestamp = now_timestamp()
    normalized_target = (
        validate_slug(target_feature, "Target feature slug") if target_feature else None
    )
    return {
        "proposal_slug": validate_slug(proposal_slug, "Proposal slug"),
        "status": "draft",
        "created_at": timestamp,
        "updated_at": timestamp,
        "summary": normalize_optional_string(summary, "Summary"),
        "review_note": None,
        "target_feature": normalized_target,
        "promoted_feature": None,
        "promoted_at": None,
    }


def normalize_metadata(payload: object) -> Dict[str, object]:
    if not isinstance(payload, dict):
        raise RuntimeError("Proposal metadata must be a JSON object.")

    proposal_slug = payload.get("proposal_slug")
    if not isinstance(proposal_slug, str):
        raise RuntimeError("Proposal metadata field 'proposal_slug' must be a string.")

    target_feature = payload.get("target_feature")
    promoted_feature = payload.get("promoted_feature")
    if target_feature is not None and not isinstance(target_feature, str):
        raise RuntimeError("Proposal metadata field 'target_feature' must be a string when present.")
    if promoted_feature is not None and not isinstance(promoted_feature, str):
        raise RuntimeError("Proposal metadata field 'promoted_feature' must be a string when present.")

    return {
        "proposal_slug": validate_slug(proposal_slug, "Proposal slug"),
        "status": normalize_status(str(payload.get("status", ""))),
        "created_at": normalize_optional_timestamp(payload.get("created_at")) or now_timestamp(),
        "updated_at": normalize_optional_timestamp(payload.get("updated_at")) or now_timestamp(),
        "summary": normalize_optional_string(payload.get("summary"), "Summary"),
        "review_note": normalize_optional_string(payload.get("review_note"), "Review note"),
        "target_feature": validate_slug(target_feature, "Target feature slug")
        if isinstance(target_feature, str) and target_feature.strip()
        else None,
        "promoted_feature": validate_slug(promoted_feature, "Promoted feature slug")
        if isinstance(promoted_feature, str) and promoted_feature.strip()
        else None,
        "promoted_at": normalize_optional_timestamp(payload.get("promoted_at")),
    }


def read_metadata(proposal_dir: str) -> Dict[str, object]:
    path = metadata_path_for(proposal_dir)
    if not os.path.exists(path):
        raise RuntimeError(f"Proposal metadata not found at '{path}'.")
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Proposal metadata is not valid JSON.") from exc
    return normalize_metadata(payload)


def write_metadata(proposal_dir: str, metadata: Dict[str, object]) -> None:
    os.makedirs(proposal_dir, exist_ok=True)
    with open(metadata_path_for(proposal_dir), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        f.write("\n")


def proposal_dir_for_row(
    row: Dict[str, object], scope_context: Optional[object] = None
) -> str:
    if scope_context is None:
        scope_context = SCOPE_RUNTIME.resolve_scope_context()
    return SCOPE_RUNTIME.resolve_scope_path(
        scope_context.scope_root,
        str(row["path"]).rstrip("/"),
    )


def find_proposal(
    rows: List[Dict[str, object]],
    selector: str,
    scope_context: Optional[object] = None,
) -> Optional[Dict[str, object]]:
    normalized_selector = selector.rstrip("/")
    if normalized_selector.startswith("./"):
        normalized_selector = normalized_selector[2:]

    for row in rows:
        if row["proposal"] == normalized_selector:
            return row
        path_value = str(row["path"]).rstrip("/")
        if path_value == normalized_selector:
            return row
        absolute_path = proposal_dir_for_row(row, scope_context=scope_context).rstrip("/")
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


def resolve_proposal_lookup(
    selector: str, explicit_scope: Optional[str] = None
) -> Tuple[List[Dict[str, object]], Optional[Dict[str, object]], object]:
    scope_context = SCOPE_RUNTIME.resolve_scope_context(explicit_scope=explicit_scope)
    rows = load_registry(scope_context=scope_context)

    if explicit_scope is not None or not is_slug_selector(selector):
        return rows, find_proposal(rows, selector, scope_context=scope_context), scope_context

    matches: List[Tuple[object, List[Dict[str, object]], Dict[str, object]]] = []
    for candidate_scope_context in list_plausible_scope_contexts(scope_context):
        candidate_rows = load_registry(scope_context=candidate_scope_context)
        proposal = find_proposal(
            candidate_rows, selector, scope_context=candidate_scope_context
        )
        if proposal:
            matches.append((candidate_scope_context, candidate_rows, proposal))

    if not matches:
        return rows, None, scope_context

    if len(matches) == 1:
        candidate_scope_context, candidate_rows, proposal = matches[0]
        if candidate_scope_context.scope_root != scope_context.scope_root:
            raise RuntimeError(
                f"Proposal not found in active scope "
                f"'{scope_label(scope_context.scope_root, scope_context.repo_root)}'. "
                f"Found matching proposal in scope "
                f"'{scope_label(candidate_scope_context.scope_root, scope_context.repo_root)}'. "
                "Re-run with --scope <path>."
            )
        return candidate_rows, proposal, candidate_scope_context

    candidate_labels = sorted(
        {
            scope_label(
                candidate_scope_context.scope_root, candidate_scope_context.repo_root
            )
            for candidate_scope_context, _, _ in matches
        }
    )
    raise RuntimeError(
        f"Ambiguous proposal selector '{selector}'. Matching scopes: "
        f"{', '.join(candidate_labels)}. Re-run with --scope <path>."
    )


def find_active_proposal(rows: List[Dict[str, object]]) -> Optional[Dict[str, object]]:
    if not rows:
        return None
    open_rows = [row for row in rows if row["status"] not in TERMINAL_STATUSES]
    candidates = open_rows or rows
    return max(candidates, key=lambda row: (row.get("updated_at") or "", row["proposal"]))


def write_discover_stub(proposal_dir: str, proposal_slug: str, summary: Optional[str]) -> None:
    path = os.path.join(proposal_dir, DISCOVER_FILE)
    if os.path.exists(path):
        return
    discover_text = (
        f"# Discover: {proposal_slug.replace('-', ' ').title()}\n\n"
        "## Problem\n\n"
        f"{summary or 'Describe the problem or opportunity this proposal explores.'}\n\n"
        "## Why This Is Still A Proposal\n\n"
        "- The work is not yet accepted as a canonical feature.\n"
        "- Keep speculative notes here until the team decides to promote or reject it.\n"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(discover_text)


def validate_required_file(proposal_dir: str, filename: str) -> Tuple[bool, str]:
    path = os.path.join(proposal_dir, filename)
    if not os.path.exists(path):
        return False, f"Missing required file '{filename}'."
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    if not content:
        return False, f"Required file '{filename}' is empty."
    return True, f"Found '{filename}'."


def validate_proposal_state(
    proposal_dir: str, metadata: Dict[str, object]
) -> Tuple[bool, List[str], List[Dict[str, object]]]:
    checks: List[Dict[str, object]] = []
    issues: List[str] = []
    status = str(metadata["status"])

    def record_check(name: str, ok: bool, detail: str) -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})
        if not ok:
            issues.append(detail)

    exists = os.path.isdir(proposal_dir)
    record_check(
        "proposal_dir",
        exists,
        "Proposal directory exists." if exists else "Proposal directory does not exist.",
    )
    if not exists:
        return False, issues, checks

    if status in {"reviewed", "accepted", "rejected", "promoted"}:
        ok, detail = validate_required_file(proposal_dir, DISCOVER_FILE)
        record_check("discover", ok, detail)
        review_note = metadata.get("review_note")
        ok = isinstance(review_note, str) and bool(review_note.strip())
        record_check(
            "review_note",
            ok,
            "Proposal review note recorded."
            if ok
            else "Proposal review requires a non-empty review note.",
        )

    if status == "promoted":
        promoted_feature = metadata.get("promoted_feature")
        ok = isinstance(promoted_feature, str) and bool(promoted_feature.strip())
        record_check(
            "promoted_feature",
            ok,
            "Promoted feature recorded."
            if ok
            else "Promoted proposals must record the canonical feature slug.",
        )
        promoted_at = metadata.get("promoted_at")
        ok = isinstance(promoted_at, str) and bool(promoted_at.strip())
        record_check(
            "promoted_at",
            ok,
            "Promotion timestamp recorded."
            if ok
            else "Promoted proposals must record promoted_at.",
        )

    return not issues, issues, checks


def create_proposal(
    proposal_slug: str,
    summary: Optional[str] = None,
    target_feature: Optional[str] = None,
    scope_context: Optional[object] = None,
) -> Tuple[str, bool]:
    if scope_context is None:
        scope_context = SCOPE_RUNTIME.resolve_scope_context()
    rows = load_registry(scope_context=scope_context)
    existing = find_proposal(rows, proposal_slug, scope_context=scope_context)
    if existing:
        return proposal_dir_for_row(existing, scope_context=scope_context), False

    proposal_dir = get_proposal_root(proposal_slug, scope_context=scope_context)
    metadata = build_metadata(
        proposal_slug, summary=summary, target_feature=target_feature
    )
    write_metadata(proposal_dir, metadata)
    write_discover_stub(proposal_dir, proposal_slug, summary)
    config = load_config(required=False, scope_context=scope_context)
    row_path = normalize_path(
        os.path.join(
            normalize_dir(config["proposal_dir"], "Proposal directory"),
            proposal_slug,
        )
    )

    rows.append(
        {
            "proposal": proposal_slug,
            "status": metadata["status"],
            "updated_at": metadata["updated_at"],
            "path": row_path,
        }
    )
    write_registry(rows, scope_context=scope_context)
    return proposal_dir, True


def can_transition(current: str, target: str) -> bool:
    if current == target:
        return True
    allowed_transitions = {
        "draft": {"reviewed"},
        "reviewed": {"accepted", "rejected"},
        "accepted": {"promoted"},
        "rejected": set(),
        "promoted": set(),
    }
    return target in allowed_transitions[current]


def update_proposal_status(
    rows: List[Dict[str, object]],
    proposal: Dict[str, object],
    status: str,
    force: bool = False,
    review_note: Optional[str] = None,
    summary: Optional[str] = None,
    target_feature: Optional[str] = None,
    scope_context: Optional[object] = None,
) -> Tuple[bool, str]:
    proposal_dir = proposal_dir_for_row(proposal, scope_context=scope_context)
    metadata = read_metadata(proposal_dir)
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
        updated_metadata["review_note"] = normalize_optional_string(
            review_note, "Review note"
        )
    if summary is not None:
        updated_metadata["summary"] = normalize_optional_string(summary, "Summary")
    if target_feature is not None:
        updated_metadata["target_feature"] = validate_slug(
            target_feature, "Target feature slug"
        )

    ok, issues, _ = validate_proposal_state(proposal_dir, updated_metadata)
    if not force and not ok:
        return False, "Cannot set status: " + "; ".join(issues)

    write_metadata(proposal_dir, updated_metadata)
    proposal["status"] = status
    proposal["updated_at"] = updated_metadata["updated_at"]
    write_registry(rows, scope_context=scope_context)
    return True, f"Updated {proposal['proposal']} to status '{status}'"


def validate_proposal(
    proposal: Dict[str, object], scope_context: Optional[object] = None
) -> Tuple[bool, List[str], List[Dict[str, object]]]:
    proposal_dir = proposal_dir_for_row(proposal, scope_context=scope_context)
    metadata = read_metadata(proposal_dir)
    return validate_proposal_state(proposal_dir, metadata)


def cmd_init(args: argparse.Namespace) -> int:
    config = load_config(required=False)
    scope_context = SCOPE_RUNTIME.resolve_scope_context()
    planning_dir = config["planning_dir"]
    proposal_dir = (
        normalize_dir(args.proposal_dir, "Proposal directory")
        if args.proposal_dir
        else config["proposal_dir"]
    )
    write_config(planning_dir, proposal_dir)
    ensure_registry(SCOPE_RUNTIME.resolve_scope_path(scope_context.scope_root, proposal_dir))
    print(f"Initialized proposal registry and config in '{proposal_dir}/'.")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    try:
        proposal_slug = validate_slug(args.proposal_slug, "Proposal slug")
        proposal_dir, created = create_proposal(
            proposal_slug,
            summary=args.summary,
            target_feature=args.target_feature,
        )
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not created:
        print(f"Proposal folder already exists: {proposal_dir}")
        return 0

    print(f"Created proposal: {proposal_dir}")
    return 0


def cmd_set_status(args: argparse.Namespace) -> int:
    try:
        status = normalize_status(args.status)
        rows, proposal, scope_context = resolve_proposal_lookup(
            args.proposal, explicit_scope=args.scope
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not proposal:
        print(f"Proposal not found: {args.proposal}", file=sys.stderr)
        return 2

    success, message = update_proposal_status(
        rows,
        proposal,
        status,
        force=args.force,
        review_note=args.review_note,
        summary=args.summary,
        target_feature=args.target_feature,
        scope_context=scope_context,
    )
    stream = sys.stdout if success else sys.stderr
    print(message, file=stream)
    return 0 if success else 2


def cmd_get_active(_: argparse.Namespace) -> int:
    rows = load_registry()
    proposal = find_active_proposal(rows)
    if not proposal:
        print("No proposals found.", file=sys.stderr)
        return 1
    print(json.dumps(proposal, indent=2))
    return 0


def cmd_validate_proposal(args: argparse.Namespace) -> int:
    try:
        _, proposal, scope_context = resolve_proposal_lookup(
            args.proposal, explicit_scope=args.scope
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if not proposal:
        print(f"Proposal not found: {args.proposal}", file=sys.stderr)
        return 2

    ok, issues, checks = validate_proposal(proposal, scope_context=scope_context)
    result = {"proposal": proposal, "ok": ok, "checks": checks, "issues": issues}
    print(json.dumps(result, indent=2))
    return 0 if ok else 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_p = subparsers.add_parser(
        "init", help="Initialize the proposal registry and proposal config"
    )
    init_p.add_argument(
        "proposal_dir",
        nargs="?",
        help="Proposal directory path (defaults to configured path or 'docs/proposals')",
    )

    add_p = subparsers.add_parser("add", help="Create a proposal folder and metadata")
    add_p.add_argument("proposal_slug", help="Proposal slug")
    add_p.add_argument("--summary", help="Short proposal summary.")
    add_p.add_argument(
        "--target-feature",
        help="Expected canonical feature slug if promotion target is already known.",
    )

    set_p = subparsers.add_parser("set-status", help="Update a proposal status")
    set_p.add_argument("proposal", help="Proposal slug, folder name, or path")
    set_p.add_argument("status", help="New status")
    set_p.add_argument(
        "--review-note",
        help="Decision note to persist when proposal review is complete.",
    )
    set_p.add_argument("--summary", help="Short proposal summary.")
    set_p.add_argument(
        "--target-feature",
        help="Expected canonical feature slug if promotion target is already known.",
    )
    set_p.add_argument(
        "--force",
        action="store_true",
        help="Override transition and validation safeguards during manual repair.",
    )
    set_p.add_argument(
        "--scope",
        help="Explicit scope path to use for proposal lookup.",
    )

    subparsers.add_parser("get-active", help="Return the active proposal as JSON")

    validate_p = subparsers.add_parser(
        "validate-proposal", help="Validate proposal/file consistency"
    )
    validate_p.add_argument("proposal", help="Proposal slug, folder name, or path")
    validate_p.add_argument(
        "--scope",
        help="Explicit scope path to use for proposal lookup.",
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
        if args.command == "validate-proposal":
            return cmd_validate_proposal(args)
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
