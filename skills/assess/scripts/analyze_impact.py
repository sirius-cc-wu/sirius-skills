#!/usr/bin/env python3

import argparse
import importlib.util
import json
import os
import re
import sys
from pathlib import Path
from typing import Iterable, List


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
SUBFEATURE_SCRIPT = (
    REPO_ROOT / "skills" / "add-subfeature" / "scripts" / "manage_subfeatures.py"
)
IMPACT_FILE = "impact-analysis.md"
SLUG_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*$")
BOLD_STORY_PATTERN = re.compile(r"\*\*([A-Za-z][A-Za-z0-9._-]+)(?:\s+\([^)]*\))?\*\*")
TABLE_ROW_PATTERN = re.compile(r"^\|(.+)\|$")


def load_manage_subfeatures_module():
    spec = importlib.util.spec_from_file_location("manage_subfeatures", SUBFEATURE_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate impact-analysis.md for a durable subfeature."
    )
    parser.add_argument("feature", help="Parent feature slug, folder name, or path")
    parser.add_argument("subfeature", help="Subfeature ID, folder name, or path")
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


def collect_parent_artifacts(feature_dir: Path) -> List[str]:
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


def collect_slice_ids(feature_dir: Path, manage_subfeatures) -> List[str]:
    slice_ids: List[str] = []
    slice_planning_text = read_text_if_exists(feature_dir / "slice-planning.md")
    slice_ids.extend(
        extract_first_column_ids(
            extract_section_lines(slice_planning_text, "## 4. Execution Slice Backlog")
        )
    )

    feature_meta_path = feature_dir / manage_subfeatures.FEATURE_META_FILE
    if feature_meta_path.exists():
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
    subfeature_dir: Path,
    parent_feature_slug: str,
    subfeature_id: str,
    subfeature_type: str,
    summary: str | None,
    current_status: str,
    affected_artifacts: List[str],
    affected_story_ids: List[str],
    affected_slice_ids: List[str],
    increment_ids: List[str],
    force: bool,
) -> Path:
    impact_path = subfeature_dir / IMPACT_FILE
    if impact_path.exists() and not force:
        raise RuntimeError(
            f"Impact analysis already exists at '{normalize_relpath(impact_path)}'. Use --force to overwrite it."
        )

    summary_line = summary or "Describe why this existing feature needs a scoped impact review."
    content = f"""# Impact Analysis: {subfeature_id.replace('-', ' ').title()}

## Target Subfeature

- Parent Feature: `{parent_feature_slug}`
- Subfeature ID: `{subfeature_id}`
- Subfeature Type: `{subfeature_type}`
- Current Subfeature Status: `{current_status}`

## Subfeature Summary

{summary_line}

## Parent Baseline Reviewed

{format_bullets(affected_artifacts, 'No parent planning artifacts detected.')}

## Candidate Affected Story IDs

{format_bullets(affected_story_ids, 'No candidate story IDs detected from the parent baseline.')}

## Candidate Affected Increment IDs

{format_bullets(increment_ids, 'No candidate increment IDs detected from the parent baseline.')}

## Candidate Affected Slice IDs

{format_bullets(affected_slice_ids, 'No candidate slice IDs detected from the parent baseline.')}

## Impact Notes

- Confirm whether this subfeature keeps existing stories intact or narrows, supersedes, or replaces them.
- Confirm whether existing planned slices remain valid or need new subfeature-local slices.
- Use this analysis to drive subfeature-local `system-design.md` and later `slice-planning.md`.
"""
    impact_path.write_text(content, encoding="utf-8")
    return impact_path


def main() -> int:
    args = parse_args()
    manage_subfeatures = load_manage_subfeatures_module()
    manage_planning = manage_subfeatures.load_manage_planning_module()

    try:
        feature_dir_str, parent_feature_slug, scope_context = (
            manage_subfeatures.resolve_parent_feature(manage_planning, args.feature)
        )
        rows = manage_subfeatures.load_registry(feature_dir_str)
        subfeature = manage_subfeatures.find_subfeature(rows, args.subfeature)
        if not subfeature:
            raise RuntimeError(f"Subfeature not found: {args.subfeature}")
        subfeature_dir = Path(
            manage_subfeatures.subfeature_dir_for_row(subfeature, scope_context)
        )
        metadata = manage_subfeatures.read_metadata(str(subfeature_dir))
        feature_dir = Path(feature_dir_str)

        affected_artifacts = dedupe(
            collect_parent_artifacts(feature_dir) + list(args.affected_artifact)
        )
        affected_story_ids = dedupe(collect_story_ids(feature_dir) + list(args.story_id))
        affected_slice_ids = dedupe(
            collect_slice_ids(feature_dir, manage_subfeatures) + list(args.slice_id)
        )
        increment_ids = collect_increment_ids(feature_dir)

        write_impact_analysis(
            subfeature_dir,
            parent_feature_slug,
            str(metadata["subfeature_id"]),
            str(metadata["subfeature_type"]),
            metadata.get("summary"),
            str(metadata["status"]),
            affected_artifacts,
            affected_story_ids,
            affected_slice_ids,
            increment_ids,
            args.force,
        )

        success, message = manage_subfeatures.update_subfeature_status(
            manage_planning,
            feature_dir_str,
            subfeature,
            "impact_ready",
            scope_context,
            force=args.force,
            affected_artifacts=affected_artifacts,
            affected_story_ids=affected_story_ids,
            affected_slice_ids=affected_slice_ids,
        )
        if not success:
            raise RuntimeError(message)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(
        f"Generated impact analysis for subfeature '{metadata['subfeature_id']}' under feature '{parent_feature_slug}'."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
