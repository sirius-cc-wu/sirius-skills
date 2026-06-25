import argparse
import importlib.util
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


DEFAULT_CONFIG_PATH = Path(".skills/plugins/spec-publish.json")
DEFAULT_ARCHIVE_CONFIG_PATH = Path(".skills/plugins/spec-archive.json")
DEFAULT_DOCUMENT_TITLE = "Execution Slice History"
DEFAULT_SECTION_TITLE = "Closed Slices"
OUTGOING_RELATION_TYPES = {
    "supersedes",
    "invalidates",
    "narrows",
    "replaces_partially",
}
COMMAND_DIR = Path(__file__).resolve().parent
GUIDE_EXECUTION_SCRIPT = COMMAND_DIR / "manage_execution.py"

from sirius_skills.lib.workflow_state import sync_owner_completion  # noqa: E402


def now_timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def load_manage_specs_module():
    from sirius_skills.commands import manage_execution
    return manage_execution


def load_publish_config(config_path: Path) -> Dict[str, str]:
    if not config_path.exists():
        return {}

    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Publish config is not valid JSON: {config_path}") from exc

    if not isinstance(payload, dict):
        raise RuntimeError(f"Publish config must be a JSON object: {config_path}")

    normalized: Dict[str, str] = {}
    for field in ("target_file", "document_title", "section_title"):
        value = payload.get(field)
        if value is None:
            continue
        if not isinstance(value, str) or not value.strip():
            raise RuntimeError(
                f"Publish config field '{field}' must be a non-empty string."
            )
        normalized[field] = value.strip()
    return normalized


def load_archive_config(config_path: Path) -> Dict[str, str]:
    if not config_path.exists():
        return {}

    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Archive config is not valid JSON: {config_path}") from exc

    if not isinstance(payload, dict):
        raise RuntimeError(f"Archive config must be a JSON object: {config_path}")

    normalized: Dict[str, str] = {}
    target_dir = payload.get("target_dir")
    if target_dir is not None:
        if not isinstance(target_dir, str) or not target_dir.strip():
            raise RuntimeError("Archive config field 'target_dir' must be a non-empty string.")
        normalized["target_dir"] = target_dir.strip()
    return normalized


def resolve_slice(module, selector: Optional[str]) -> Tuple[List[Dict[str, object]], Dict[str, object]]:
    rows = module.parse_registry()
    slice = module.resolve_slice(rows, selector) if selector else module.find_active_slice(rows)
    if not slice:
        if selector:
            raise RuntimeError(f"Slice not found: {selector}")
        raise RuntimeError("No active slice found.")
    return rows, slice


def normalize_relation_request(
    module, relation_type: str, target_slice: str
) -> Tuple[str, str]:
    normalized_type = module.normalize_relation_type(relation_type)
    if normalized_type not in OUTGOING_RELATION_TYPES:
        raise RuntimeError(
            "Only outgoing relation types are supported here: "
            f"{sorted(OUTGOING_RELATION_TYPES)}"
        )
    return normalized_type, target_slice


def ensure_slice_closed(
    module, rows: List[Dict[str, object]], slice: Dict[str, object], force: bool
) -> Tuple[List[Dict[str, object]], Dict[str, object], str]:
    status = module.normalize_status(str(slice["status"]))
    if status == "closed":
        refreshed_rows = module.parse_registry()
        refreshed_slice = module.resolve_slice(refreshed_rows, str(slice["id"]))
        if not refreshed_slice:
            raise RuntimeError(f"Slice disappeared after refresh: {slice['id']}")
        return refreshed_rows, refreshed_slice, f"Closed slice {slice['id']}"

    success, message = module.update_slice_status(rows, slice, "closed", force=force)
    if not success:
        raise RuntimeError(message)

    refreshed_rows = module.parse_registry()
    refreshed_slice = module.resolve_slice(refreshed_rows, str(slice["id"]))
    if not refreshed_slice:
        raise RuntimeError(f"Slice disappeared after close: {slice['id']}")
    return refreshed_rows, refreshed_slice, message


def read_text_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def resolve_brief_path(slice_path: Path) -> Path:
    return slice_path / "brief.md"


def normalize_list_item(stripped: str) -> Optional[str]:
    if stripped.startswith("- [ ] "):
        return stripped[6:].strip()
    if stripped.startswith("- [x] ") or stripped.startswith("- [X] "):
        return stripped[6:].strip()
    if stripped.startswith("- "):
        return stripped[2:].strip()
    return None


def dedupe_preserve_order(values: List[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def extract_list_section(markdown: str, heading_fragment: str, limit: int = 3) -> List[str]:
    lines = markdown.splitlines()
    wanted = heading_fragment.strip().lower()
    in_section = False
    bullets: List[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            heading_text = stripped.lstrip("#").strip().lower()
            if in_section and heading_text != wanted:
                break
            in_section = heading_text == wanted
            continue
        if not in_section:
            continue
        item = normalize_list_item(stripped)
        if item:
            bullets.append(item)
            if len(bullets) >= limit:
                break
    return bullets


def extract_keyed_values(markdown: str, prefixes: List[str], limit: int = 3) -> List[str]:
    results: List[str] = []
    for line in markdown.splitlines():
        stripped = line.strip()
        for prefix in prefixes:
            if stripped.startswith(prefix):
                value = stripped[len(prefix) :].strip()
                if value:
                    results.append(value)
                break
        if len(results) >= limit:
            break
    return results


def extract_nested_list_after_label(markdown: str, label: str, limit: int = 4) -> List[str]:
    lines = markdown.splitlines()
    results: List[str] = []
    capture_indent: Optional[int] = None

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped != label:
            continue

        for nested_line in lines[index + 1 :]:
            nested_stripped = nested_line.strip()
            if not nested_stripped:
                if capture_indent is None:
                    continue
                break
            if nested_stripped.startswith("#"):
                break
            indent = len(nested_line) - len(nested_line.lstrip(" "))
            if capture_indent is None:
                item = normalize_list_item(nested_stripped)
                if item is None:
                    break
                capture_indent = indent
            elif indent < capture_indent:
                break

            item = normalize_list_item(nested_stripped)
            if item:
                results.append(item)
            elif capture_indent is not None and indent <= capture_indent:
                break

            if len(results) >= limit:
                return results
        if results:
            break
    return results


def extract_verification_summary(
    plan_text: str, slices_text: str, limit: int = 6
) -> List[str]:
    items: List[str] = []
    items.extend(extract_nested_list_after_label(plan_text, "- Validation:", limit=limit))
    items.extend(
        extract_keyed_values(
            plan_text,
            prefixes=["- Happy path:", "- Edge case:", "- Regression checks:"],
            limit=limit,
        )
    )
    items.extend(
        extract_keyed_values(slices_text, prefixes=["- Validation approach:"], limit=limit)
    )
    items.extend(extract_list_section(slices_text, "7. exit criteria", limit=limit))
    return dedupe_preserve_order(items)[:limit]


def render_issue_reference(
    metadata: Dict[str, object], issue_url_template: Optional[str]
) -> Optional[str]:
    issue = metadata.get("issue")
    if not isinstance(issue, dict):
        return None
    issue_id = issue.get("id")
    if not isinstance(issue_id, str) or not issue_id:
        return None

    issue_title = issue.get("title")
    issue_status = issue.get("status")
    suffix_parts = []
    if isinstance(issue_title, str) and issue_title.strip():
        suffix_parts.append(issue_title.strip())
    if isinstance(issue_status, str) and issue_status.strip():
        suffix_parts.append(f"status: {issue_status.strip()}")

    if issue_url_template:
        reference = f"[{issue_id}]({issue_url_template.replace('{ID}', issue_id)})"
    else:
        reference = f"`{issue_id}`"

    if suffix_parts:
        return f"{reference} — {'; '.join(suffix_parts)}"
    return reference


def render_relation_scope(scope: Dict[str, object]) -> Optional[str]:
    if not isinstance(scope, dict) or not scope:
        return None

    parts: List[str] = []
    story_title = scope.get("story_title")
    if isinstance(story_title, str) and story_title.strip():
        parts.append(f"story: {story_title.strip()}")
    requirement_ids = scope.get("requirement_ids")
    if isinstance(requirement_ids, list) and requirement_ids:
        parts.append("requirements: " + ", ".join(str(item) for item in requirement_ids))
    selector = scope.get("selector")
    if isinstance(selector, str) and selector.strip():
        parts.append(f"selector: {selector.strip()}")
    if not parts:
        return None
    return "; ".join(parts)


def render_relation_summary(metadata: Dict[str, object]) -> List[str]:
    relations = metadata.get("relations")
    if not isinstance(relations, list):
        return []

    summaries: List[str] = []
    for relation in relations:
        if not isinstance(relation, dict):
            continue
        relation_type = relation.get("type")
        target_slice = relation.get("target_slice")
        if relation_type not in OUTGOING_RELATION_TYPES or not isinstance(target_slice, str):
            continue
        summary = f"{relation_type} `{target_slice}`"
        scope_text = render_relation_scope(relation.get("scope", {}))
        if scope_text:
            summary += f" ({scope_text})"
        summaries.append(summary)
    return summaries


def render_publication_entry(
    slice: Dict[str, object],
    metadata: Dict[str, object],
    issue_reference: Optional[str],
    requirements: List[str],
    success_criteria: List[str],
    relation_summary: List[str],
    verification_summary: List[str],
) -> str:
    slice_path = Path(str(slice["path"]).rstrip("/"))
    artifacts = [f"`{resolve_brief_path(slice_path)}`", f"`{slice_path / 'blueprint.md'}`"]
    slices_path = slice_path / "slices.md"
    if slices_path.exists():
        artifacts.append(f"`{slices_path}`")

    closed_at = str(slice.get("closed_at") or metadata.get("closed_at") or now_timestamp())
    closed_day = closed_at.split("T", 1)[0]
    lines = [
        f"### {closed_day} — {slice['feature']} (`{slice['id']}`)",
        "",
        f"- Slice: `{slice['id']}`",
        f"- Closed: `{closed_at}`",
    ]

    if issue_reference:
        lines.append(f"- Source issue: {issue_reference}")

    lines.append("- Artifacts:")
    lines.extend([f"  - {artifact}" for artifact in artifacts])

    if requirements:
        lines.append("- Functional requirements snapshot:")
        lines.extend([f"  - {item}" for item in requirements])

    if success_criteria:
        lines.append("- Success criteria snapshot:")
        lines.extend([f"  - {item}" for item in success_criteria])

    if relation_summary:
        lines.append("- Slice relations:")
        lines.extend([f"  - {item}" for item in relation_summary])

    if verification_summary:
        lines.append("- Implementation verification snapshot:")
        lines.extend([f"  - {item}" for item in verification_summary])

    return "\n".join(lines).rstrip() + "\n"


def ensure_document_scaffold(
    content: str, document_title: str, section_title: str
) -> str:
    stripped = content.strip()
    if not stripped:
        return f"# {document_title}\n\n## {section_title}\n\n"

    if f"\n## {section_title}\n" in f"\n{content}\n":
        return content if content.endswith("\n") else content + "\n"

    suffix = "" if content.endswith("\n") else "\n"
    return f"{content}{suffix}\n## {section_title}\n\n"


def upsert_publication_entry(
    target_file: Path,
    document_title: str,
    section_title: str,
    slice_id: str,
    entry: str,
) -> None:
    start_marker = f"<!-- spec-publish:{slice_id}:start -->"
    end_marker = f"<!-- spec-publish:{slice_id}:end -->"
    wrapped_entry = f"{start_marker}\n{entry}{end_marker}\n"

    content = ensure_document_scaffold(
        read_text_if_exists(target_file), document_title, section_title
    )
    pattern = re.compile(
        re.escape(start_marker) + r".*?" + re.escape(end_marker) + r"\n?",
        re.DOTALL,
    )

    if pattern.search(content):
        updated = pattern.sub(wrapped_entry, content)
    else:
        updated = content
        if not updated.endswith("\n"):
            updated += "\n"
        updated += wrapped_entry

    target_file.parent.mkdir(parents=True, exist_ok=True)
    target_file.write_text(updated, encoding="utf-8")


def update_publication_metadata(
    module,
    slice: Dict[str, object],
    target_file: Path,
    document_title: str,
    section_title: str,
) -> Dict[str, object]:
    slice_path = Path(str(slice["path"]).rstrip("/"))
    metadata = module.load_slice_metadata(str(slice_path))
    publications = metadata.get("publications")
    if not isinstance(publications, list):
        publications = []

    publication_record = {
        "published_at": now_timestamp(),
        "target_file": str(target_file),
        "document_title": document_title,
        "section_title": section_title,
    }

    retained: List[Dict[str, object]] = []
    replaced = False
    for item in publications:
        if not isinstance(item, dict):
            continue
        if item.get("target_file") == publication_record["target_file"]:
            retained.append(publication_record)
            replaced = True
        else:
            retained.append(item)
    if not replaced:
        retained.append(publication_record)

    metadata["publications"] = retained
    module.write_slice_metadata(str(slice_path), metadata)
    return metadata


def build_result(slice: Dict[str, object], metadata: Dict[str, object]) -> Dict[str, object]:
    result = {
        "slice_id": slice["id"],
        "feature": slice["feature"],
        "status": slice["status"],
        "path": slice["path"],
        "closed_at": slice.get("closed_at"),
    }
    relations = metadata.get("relations")
    if isinstance(relations, list):
        result["relations"] = relations
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slice", help="Slice ID, folder name, or path. Defaults to active slice.")
    parser.add_argument(
        "--relate",
        action="append",
        nargs=2,
        metavar=("TYPE", "SLICE"),
        help="Record an explicit impact relation such as supersedes OLD-123. Repeatable.",
    )
    parser.add_argument(
        "--story-title",
        help="Optional soft selector for the affected story title when the relation is partial.",
    )
    parser.add_argument(
        "--requirement-id",
        action="append",
        default=[],
        help="Optional requirement ID for partial invalidation. Repeatable.",
    )
    parser.add_argument(
        "--selector",
        help="Optional freeform selector text for partial invalidation.",
    )
    parser.add_argument(
        "--confirm-impact",
        action="store_true",
        help="Explicitly confirm relation-bearing closure or invalidation at close time.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force close through temporary inconsistencies after manual verification.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        module = load_manage_specs_module()
        rows, slice = resolve_slice(module, args.slice)
        slice_path = Path(str(slice["path"]).rstrip("/"))
        metadata = module.load_slice_metadata(str(slice_path))
        relation_requests = [
            normalize_relation_request(module, relation_type, target_slice)
            for relation_type, target_slice in (args.relate or [])
        ]
        relation_confirmation_required = (
            bool(relation_requests)
            or (
                module.normalize_status(str(slice["status"])) != "closed"
                and bool(metadata.get("relations"))
            )
        )
        if relation_confirmation_required and not args.confirm_impact and not args.force:
            raise RuntimeError(
                "Closing a slice with invalidation or supersession relations requires "
                "--confirm-impact."
            )

        _, slice, close_message = ensure_slice_closed(module, rows, slice, force=args.force)
        rows = module.parse_registry()
        slice = module.resolve_slice(rows, str(slice["id"]))
        if not slice:
            raise RuntimeError("Slice disappeared after close.")
        slice_path = Path(str(slice["path"]).rstrip("/"))
        metadata = module.load_slice_metadata(str(slice_path))
        owner_sync = sync_owner_completion(str(slice["id"]))

        if relation_requests:
            for relation_type, target_slice in relation_requests:
                success, message = module.add_relation(
                    rows,
                    slice,
                    relation_type,
                    target_slice,
                    story_title=args.story_title,
                    requirement_ids=args.requirement_id,
                    selector=args.selector,
                )
                if not success:
                    raise RuntimeError(message)
            audit_result = module.audit_relations(rows, slice_selector=str(slice["id"]))
            if not audit_result["ok"] and not args.force:
                raise RuntimeError(
                    "Relation audit failed after recording impacts: "
                    + "; ".join(issue["message"] for issue in audit_result["issues"])
                )
            rows = module.parse_registry()
            slice = module.resolve_slice(rows, str(slice["id"]))
            if not slice:
                raise RuntimeError("Slice disappeared after relation update.")
            slice_path = Path(str(slice["path"]).rstrip("/"))
            metadata = module.load_slice_metadata(str(slice_path))
        result = build_result(slice, metadata)
        result["message"] = close_message
        if owner_sync:
            result["owner_sync"] = owner_sync
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(close_message)
            for item in owner_sync:
                print(item["message"])
        return 0
    except (RuntimeError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
