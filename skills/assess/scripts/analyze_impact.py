#!/usr/bin/env python3

import argparse
import importlib.util
import os
import re
import sys
from pathlib import Path
from typing import Iterable, List, Optional


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
EVOLVE_SCRIPT = REPO_ROOT / "skills" / "evolve-feature" / "scripts" / "manage_feature_changes.py"
FEATURE_META_FILE = ".planning-meta.json"
IMPACT_FILE = "impact-analysis.md"
SLUG_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*$")
BOLD_STORY_PATTERN = re.compile(r"\*\*([A-Za-z][A-Za-z0-9._-]+)(?:\s+\([^)]*\))?\*\*")
TABLE_ROW_PATTERN = re.compile(r"^\|(.+)\|$")


def load_manage_feature_changes_module():
    spec = importlib.util.spec_from_file_location("manage_feature_changes", EVOLVE_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate impact-analysis.md for an existing feature change packet."
    )
    parser.add_argument("feature", help="Feature slug, folder name, or path")
    parser.add_argument("change", help="Change ID, folder name, or path")
    parser.add_argument(
        "--affected-artifact",
        action="append",
        default=[],
        help="Additional affected artifact path to include. Repeatable.",
    )
    parser.add_argument(
        "--story-id",
        action="append",
        default=[],
        help="Additional affected story ID to include. Repeatable.",
    )
    parser.add_argument(
        "--slice-id",
        action="append",
        default=[],
        help="Additional affected slice ID to include. Repeatable.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing impact-analysis.md and repair state if needed.",
    )
    return parser.parse_args()


def normalize_relpath(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        text = str(path)
        if text.startswith("./"):
            return text[2:]
        return text


def dedupe(items: Iterable[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for item in items:
        cleaned = item.strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        result.append(cleaned)
    return result


def read_text_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def extract_section_lines(text: str, heading: str) -> List[str]:
    lines = text.splitlines()
    captured: List[str] = []
    in_section = False
    for line in lines:
        if line.startswith("## "):
            if line.strip() == heading:
                in_section = True
                continue
            if in_section:
                break
        if in_section:
            captured.append(line)
    return captured


def extract_first_column_ids(section_lines: List[str]) -> List[str]:
    ids: List[str] = []
    for line in section_lines:
        match = TABLE_ROW_PATTERN.match(line.strip())
        if not match:
            continue
        cells = [cell.strip() for cell in match.group(1).split("|")]
        if not cells:
            continue
        first = cells[0]
        if first in {"---", "Story ID", "Slice ID", "Increment"}:
            continue
        if SLUG_PATTERN.fullmatch(first):
            ids.append(first)
    return ids


def collect_canonical_artifacts(feature_dir: Path) -> List[str]:
    artifact_names = [
        "discover.md",
        "system-design.md",
        "user-stories.md",
        "slice-planning.md",
        "slice-traceability.md",
    ]
    paths = [feature_dir / name for name in artifact_names if (feature_dir / name).exists()]
    return dedupe(normalize_relpath(path) for path in paths)


def collect_story_ids(feature_dir: Path) -> List[str]:
    story_ids: List[str] = []

    user_stories_text = read_text_if_exists(feature_dir / "user-stories.md")
    story_ids.extend(BOLD_STORY_PATTERN.findall(user_stories_text))

    slice_planning_text = read_text_if_exists(feature_dir / "slice-planning.md")
    story_ids.extend(
        extract_first_column_ids(extract_section_lines(slice_planning_text, "## 2. Story Decisions"))
    )

    traceability_text = read_text_if_exists(feature_dir / "slice-traceability.md")
    story_ids.extend(extract_first_column_ids(traceability_text.splitlines()))
    return dedupe(story_ids)


def collect_slice_ids(feature_dir: Path) -> List[str]:
    slice_ids: List[str] = []
    slice_planning_text = read_text_if_exists(feature_dir / "slice-planning.md")
    slice_ids.extend(
        extract_first_column_ids(
            extract_section_lines(slice_planning_text, "## 4. Execution Slice Backlog")
        )
    )

    feature_meta_path = feature_dir / FEATURE_META_FILE
    if feature_meta_path.exists():
        import json

        payload = json.loads(feature_meta_path.read_text(encoding="utf-8"))
        ready_slice_ids = payload.get("ready_slice_ids", [])
        if isinstance(ready_slice_ids, list):
            slice_ids.extend(item for item in ready_slice_ids if isinstance(item, str))
    return dedupe(slice_ids)


def collect_increment_ids(feature_dir: Path) -> List[str]:
    increment_ids: List[str] = []
    slice_planning_text = read_text_if_exists(feature_dir / "slice-planning.md")
    candidates = extract_first_column_ids(
        extract_section_lines(slice_planning_text, "## 3. Increment Plan")
    )
    increment_ids.extend(candidate for candidate in candidates if candidate.startswith("I"))
    return dedupe(increment_ids)


def format_bullets(items: List[str], empty_line: str) -> str:
    if not items:
        return f"- {empty_line}"
    return "\n".join(f"- `{item}`" for item in items)


def write_impact_analysis(
    change_dir: Path,
    feature_slug: str,
    change_id: str,
    change_type: str,
    summary: Optional[str],
    current_status: str,
    affected_artifacts: List[str],
    affected_story_ids: List[str],
    affected_slice_ids: List[str],
    increment_ids: List[str],
    force: bool,
) -> Path:
    impact_path = change_dir / IMPACT_FILE
    if impact_path.exists() and not force:
        raise RuntimeError(
            f"Impact analysis already exists at '{normalize_relpath(impact_path)}'. Use --force to overwrite it."
        )

    summary_line = summary or "Describe why this existing feature needs a scoped impact review."
    content = f"""# Impact Analysis: {change_id.replace('-', ' ').title()}

## Target Change

- Feature: `{feature_slug}`
- Change ID: `{change_id}`
- Change Type: `{change_type}`
- Current Change Status: `{current_status}`

## Change Summary

{summary_line}

## Canonical Baseline Reviewed

{format_bullets(affected_artifacts, 'No canonical planning artifacts detected.')}

## Candidate Affected Story IDs

{format_bullets(affected_story_ids, 'No candidate story IDs detected from the canonical baseline.')}

## Candidate Affected Increment IDs

{format_bullets(increment_ids, 'No candidate increment IDs detected from the canonical baseline.')}

## Candidate Affected Slice IDs

{format_bullets(affected_slice_ids, 'No candidate slice IDs detected from the canonical baseline.')}

## Impact Notes

- Confirm whether this change keeps existing stories intact or narrows, supersedes, or replaces them.
- Confirm whether existing planned slices remain valid or need new change-local slices.
- Use this analysis to drive change-local `system-design.md` and later `slice-planning.md`.
"""
    impact_path.write_text(content, encoding="utf-8")
    return impact_path


def main() -> int:
    args = parse_args()
    manage_feature_changes = load_manage_feature_changes_module()

    try:
        feature_dir_str, feature_slug = manage_feature_changes.resolve_feature_dir(args.feature)
        feature_dir = Path(feature_dir_str)
        rows = manage_feature_changes.load_registry(feature_dir_str)
        change = manage_feature_changes.find_change(rows, args.change)
        if not change:
            raise RuntimeError(f"Feature change not found: {args.change}")
        change_dir = Path(manage_feature_changes.change_dir_for_row(change))
        metadata = manage_feature_changes.read_metadata(str(change_dir))

        affected_artifacts = dedupe(
            collect_canonical_artifacts(feature_dir) + args.affected_artifact
        )
        affected_story_ids = dedupe(collect_story_ids(feature_dir) + args.story_id)
        affected_slice_ids = dedupe(collect_slice_ids(feature_dir) + args.slice_id)
        increment_ids = collect_increment_ids(feature_dir)

        impact_path = write_impact_analysis(
            change_dir,
            feature_slug,
            str(metadata["change_id"]),
            str(metadata["change_type"]),
            metadata.get("summary"),
            str(metadata["status"]),
            affected_artifacts,
            affected_story_ids,
            affected_slice_ids,
            increment_ids,
            force=args.force,
        )

        current_status = str(metadata["status"])
        target_status = "impact_ready" if current_status == "draft" else current_status
        success, message = manage_feature_changes.update_change_status(
            feature_dir_str,
            change,
            target_status,
            force=args.force,
            affected_artifacts=affected_artifacts,
            affected_story_ids=affected_story_ids,
            affected_slice_ids=affected_slice_ids,
        )
        if not success:
            raise RuntimeError(message)
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(f"Generated impact analysis: {normalize_relpath(impact_path)}")
    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
