#!/usr/bin/env python3
"""Shared markdown parsing and writing helpers for workflow artifact files.

This module owns the low-level markdown table parsing primitives, traceability
table helpers, slice-planning table helpers, reconciliation block extraction,
and archive-summary appendix read/write used across ship, archive_data, and
inventory.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

from sirius_skills.lib.workflow_state.models import TraceabilityRecord


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ARCHIVE_SUMMARIES_START = "<!-- archived-slice-summaries:start -->"
ARCHIVE_SUMMARIES_END = "<!-- archived-slice-summaries:end -->"
SLICE_SUMMARY_START_TEMPLATE = "<!-- archived-slice-summary:{slice_id}:start -->"
SLICE_SUMMARY_END_TEMPLATE = "<!-- archived-slice-summary:{slice_id}:end -->"

EXECUTION_RECONCILIATION_START = "<!-- execution-reconciliation:start -->"
EXECUTION_RECONCILIATION_END = "<!-- execution-reconciliation:end -->"

TRACEABILITY_HEADERS: Set[str] = {
    "story id",
    "increments",
    "planned slice ids",
    "execution slice ids",
    "notes",
}

SLICE_SUMMARY_BLOCK_PATTERN = re.compile(
    r"<!-- archived-slice-summary:(?P<slice_id>[^:]+):start -->\n"
    r"(?P<body>.*?)\n"
    r"<!-- archived-slice-summary:(?P=slice_id):end -->",
    re.DOTALL,
)

PLANTUML_BLOCK_PATTERN = re.compile(r"```plantuml[^\n]*\n.*?```", re.DOTALL)


# ---------------------------------------------------------------------------
# Table parsing primitives
# ---------------------------------------------------------------------------

def split_table_row(line: str) -> List[str]:
    stripped = line.strip().strip("|")
    return [cell.strip() for cell in stripped.split("|")]


def normalize_table_header(value: str) -> str:
    return " ".join(value.replace("-", " ").strip().lower().split())


def split_cell_values(value: str) -> List[str]:
    normalized = value.replace("<br/>", "\n").replace("<br />", "\n").replace("<br>", "\n")
    result: List[str] = []
    for part in normalized.replace(";", ",").split(","):
        for subpart in part.splitlines():
            cleaned = subpart.strip()
            if cleaned:
                result.append(cleaned)
    return result


def find_markdown_table(
    lines: Sequence[str], required_headers: Sequence[str]
) -> Tuple[Dict[str, int], int]:
    """Return (header_map, first_data_row_index) for the first matching table.

    Raises RuntimeError if no table with the required headers is found.
    """
    required = {normalize_table_header(value) for value in required_headers}
    for index in range(len(lines) - 1):
        header_line = lines[index].strip()
        divider_line = lines[index + 1].strip()
        if "|" not in header_line or "|" not in divider_line:
            continue
        headers = split_table_row(header_line)
        normalized_headers = [normalize_table_header(header) for header in headers]
        if not required.issubset(set(normalized_headers)):
            continue
        divider_cells = split_table_row(divider_line)
        if not divider_cells or not all(cell.startswith("---") for cell in divider_cells):
            continue
        return {name: pos for pos, name in enumerate(normalized_headers)}, index + 2
    raise RuntimeError("Could not locate the expected markdown table.")


# ---------------------------------------------------------------------------
# Traceability table parsing and writing
# ---------------------------------------------------------------------------

def parse_traceability_records(
    path: Path, owner_type: str, owner_id: str, owner_path: str
) -> List[TraceabilityRecord]:
    """Parse slice-traceability.md into TraceabilityRecord objects."""
    if not path.exists():
        return []

    lines = path.read_text(encoding="utf-8").splitlines()
    records: List[TraceabilityRecord] = []
    index = 0
    while index < len(lines) - 1:
        header_line = lines[index].strip()
        divider_line = lines[index + 1].strip()
        if "|" not in header_line or "|" not in divider_line:
            index += 1
            continue

        headers = split_table_row(header_line)
        normalized_headers = [normalize_table_header(header) for header in headers]
        if not TRACEABILITY_HEADERS.issubset(set(normalized_headers)):
            index += 1
            continue

        divider_cells = split_table_row(divider_line)
        if not divider_cells or not all(cell.startswith("---") for cell in divider_cells):
            index += 1
            continue

        header_map = {name: position for position, name in enumerate(normalized_headers)}
        index += 2
        while index < len(lines):
            row_line = lines[index].strip()
            if not row_line.startswith("|"):
                break
            cells = split_table_row(row_line)
            if len(cells) < len(headers):
                cells.extend([""] * (len(headers) - len(cells)))
            records.append(
                TraceabilityRecord(
                    owner_type=owner_type,
                    owner_id=owner_id,
                    owner_path=owner_path,
                    story_id=cells[header_map["story id"]],
                    story_size=(
                        cells[header_map["story size"]].strip()
                        if "story size" in header_map
                        else None
                    )
                    or None,
                    increments=cells[header_map["increments"]],
                    planned_slice_ids=split_cell_values(
                        cells[header_map["planned slice ids"]]
                    ),
                    execution_slice_ids=split_cell_values(
                        cells[header_map["execution slice ids"]]
                    ),
                    notes=cells[header_map["notes"]],
                )
            )
            index += 1
        continue
    return records


def parse_traceability_table(
    traceability_path: Path,
) -> Tuple[List[str], int, Dict[str, int], List[List[str]]]:
    """Return raw (lines, start_index, header_map, rows) for in-place edits."""
    lines = traceability_path.read_text(encoding="utf-8").splitlines()
    header_map, start_index = find_markdown_table(
        lines,
        [
            "Story ID",
            "Planned Slice IDs",
            "Execution Slice IDs",
        ],
    )
    rows: List[List[str]] = []
    index = start_index
    while index < len(lines):
        row_line = lines[index].strip()
        if not row_line.startswith("|"):
            break
        rows.append(split_table_row(row_line))
        index += 1
    return lines, start_index, header_map, rows


def record_execution_slice_id(
    traceability_path: Path, planned_slice_id: str, execution_slice_id: str
) -> None:
    """Append execution_slice_id to the traceability row for planned_slice_id."""
    lines, start_index, header_map, rows = parse_traceability_table(traceability_path)
    planned_slice_column = header_map["planned slice ids"]
    execution_slice_column = header_map["execution slice ids"]
    row_index: Optional[int] = None

    for index, row in enumerate(rows):
        if planned_slice_column >= len(row):
            continue
        planned_slice_ids = split_cell_values(row[planned_slice_column])
        if planned_slice_id not in planned_slice_ids:
            continue
        if len(planned_slice_ids) != 1:
            raise RuntimeError(
                "Batch execution requires one planned slice per traceability row. "
                f"Split the row that contains '{planned_slice_id}' before bootstrapping."
            )
        row_index = index
        execution_slice_ids = (
            split_cell_values(row[execution_slice_column])
            if execution_slice_column < len(row)
            else []
        )
        if execution_slice_id not in execution_slice_ids:
            execution_slice_ids.append(execution_slice_id)
        while len(row) <= execution_slice_column:
            row.append("")
        row[execution_slice_column] = ", ".join(execution_slice_ids)
        break

    if row_index is None:
        raise RuntimeError(
            f"Could not find a traceability row for planned slice '{planned_slice_id}'."
        )

    for offset, row in enumerate(rows):
        line_index = start_index + offset
        lines[line_index] = "| " + " | ".join(row) + " |"
    traceability_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Slice planning table parsing
# ---------------------------------------------------------------------------

def extract_slice_ids_from_planning_text(markdown: str) -> List[str]:
    """Extract Slice IDs from the first slice table in a slice-planning.md string."""
    lines = markdown.splitlines()
    in_slice_table = False
    collected: List[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_slice_table:
                break
            continue
        if not stripped.startswith("|"):
            if in_slice_table and stripped.startswith("## "):
                break
            continue

        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells:
            continue
        first = cells[0]
        if first == "Slice ID":
            in_slice_table = True
            continue
        if not in_slice_table or first.startswith("---"):
            continue
        if first:
            collected.append(first)

    return _dedupe_preserve_order(collected)


def parse_planned_slices(slice_planning_path: Path) -> List[Dict[str, object]]:
    """Parse slice-planning.md and return a list of planned slice dicts."""
    lines = slice_planning_path.read_text(encoding="utf-8").splitlines()
    header_map, start_index = find_markdown_table(
        lines,
        [
            "Slice ID",
            "Story ID",
            "Title",
            "Depends On",
        ],
    )

    results: List[Dict[str, object]] = []
    index = start_index
    while index < len(lines):
        row_line = lines[index].strip()
        if not row_line.startswith("|"):
            break
        cells = split_table_row(row_line)
        if len(cells) <= max(header_map.values()):
            index += 1
            continue
        planned_slice_id = cells[header_map["slice id"]].strip()
        if not planned_slice_id:
            index += 1
            continue
        results.append(
            {
                "planned_slice_id": planned_slice_id,
                "story_id": cells[header_map["story id"]].strip(),
                "title": cells[header_map["title"]].strip(),
                "validation_hint": cells[header_map["validation"]].strip()
                if "validation" in header_map and len(cells) > header_map["validation"]
                else "",
                "depends_on": split_cell_values(cells[header_map["depends on"]]),
            }
        )
        index += 1
    return results


def parse_increment_plan(
    slice_planning_path: Path,
) -> Tuple[List[str], Dict[str, List[str]]]:
    """Parse the increment table from slice-planning.md.

    Returns (increment_order, increment_ids_by_planned_slice). Returns empty
    structures when no increment table is present.
    """
    lines = slice_planning_path.read_text(encoding="utf-8").splitlines()
    try:
        header_map, start_index = find_markdown_table(
            lines,
            [
                "Increment",
                "Planned Slice IDs",
            ],
        )
    except RuntimeError:
        return [], {}

    increment_order: List[str] = []
    increment_ids_by_planned_slice: Dict[str, List[str]] = {}
    index = start_index
    while index < len(lines):
        row_line = lines[index].strip()
        if not row_line.startswith("|"):
            break
        cells = split_table_row(row_line)
        if len(cells) <= max(header_map.values()):
            index += 1
            continue
        increment_id = cells[header_map["increment"]].strip()
        if not increment_id:
            index += 1
            continue
        if increment_id not in increment_order:
            increment_order.append(increment_id)
        for planned_slice_id in split_cell_values(cells[header_map["planned slice ids"]]):
            bucket = increment_ids_by_planned_slice.setdefault(planned_slice_id, [])
            if increment_id not in bucket:
                bucket.append(increment_id)
        index += 1
    return increment_order, increment_ids_by_planned_slice


# ---------------------------------------------------------------------------
# Execution reconciliation block
# ---------------------------------------------------------------------------

def extract_execution_reconciliation_block(markdown: str) -> Optional[str]:
    """Extract the body text between reconciliation HTML comment markers."""
    start = markdown.find(EXECUTION_RECONCILIATION_START)
    if start < 0:
        return None
    end = markdown.find(EXECUTION_RECONCILIATION_END, start)
    if end < 0:
        return None
    body_start = start + len(EXECUTION_RECONCILIATION_START)
    return markdown[body_start:end].strip()


def parse_execution_reconciliation_fields(block_text: str) -> Dict[str, str]:
    """Parse key: value pairs from a reconciliation block body."""
    fields: Dict[str, str] = {}
    for line in block_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("-") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        fields[_normalize_reconciliation_key(key)] = value.strip()
    return fields


def _normalize_reconciliation_key(value: str) -> str:
    return " ".join(value.strip().lower().split())


# ---------------------------------------------------------------------------
# Archive summary appendix read/write
# ---------------------------------------------------------------------------

def load_existing_summary_blocks(design_text: str) -> Dict[str, str]:
    """Return {slice_id: block_text} for all managed archived-slice-summary blocks."""
    managed_match = re.search(
        rf"(?s){re.escape(ARCHIVE_SUMMARIES_START)}\n(?P<body>.*?){re.escape(ARCHIVE_SUMMARIES_END)}",
        design_text,
    )
    if not managed_match:
        return {}
    body = managed_match.group("body")
    return {
        match.group("slice_id"): match.group(0).strip()
        for match in SLICE_SUMMARY_BLOCK_PATTERN.finditer(body)
    }


def write_summary_appendix(
    design_path: Path,
    blocks: Dict[str, str],
    structural_figures: Optional[List[str]] = None,
) -> None:
    """Upsert the managed archive-summaries appendix section in system-design.md."""
    design_text = design_path.read_text(encoding="utf-8")
    existing_blocks = load_existing_summary_blocks(design_text)
    existing_blocks.update(blocks)

    ordered_ids = list(existing_blocks.keys())
    managed_lines = [ARCHIVE_SUMMARIES_START, "## Archived Slice Summaries", ""]
    preserved_structural_figures = _dedupe_text_blocks(structural_figures or [])
    if preserved_structural_figures:
        managed_lines.append("### Structural Context")
        managed_lines.append("")
        managed_lines.append(
            "The following existing structural diagrams were preserved to anchor the behavior-focused archived slice summaries."
        )
        managed_lines.append("")
        for figure in preserved_structural_figures:
            managed_lines.append(figure)
            managed_lines.append("")
    for slice_id in ordered_ids:
        managed_lines.append(existing_blocks[slice_id])
        managed_lines.append("")
    managed_lines.append(ARCHIVE_SUMMARIES_END)
    managed_block = "\n".join(managed_lines).rstrip() + "\n"

    managed_pattern = re.compile(
        rf"(?s)\n*{re.escape(ARCHIVE_SUMMARIES_START)}\n.*?{re.escape(ARCHIVE_SUMMARIES_END)}\n?"
    )
    if managed_pattern.search(design_text):
        updated_text = managed_pattern.sub("\n\n" + managed_block, design_text).rstrip() + "\n"
    else:
        updated_text = design_text.rstrip() + "\n\n" + managed_block
    design_path.write_text(updated_text, encoding="utf-8")


# ---------------------------------------------------------------------------
# Slice summary content extraction and rendering
# ---------------------------------------------------------------------------

@dataclass
class PreparedSliceSummary:
    slice_id: str
    title: str
    brief_items: List[str]
    design_summary: Optional[str]
    blueprint_text: str


def extract_heading_title(text: str, default: str) -> str:
    """Return the first heading title from text, stripping slice-contract prefixes."""
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        title = stripped.lstrip("#").strip()
        lowered = title.lower()
        if lowered.startswith("slice specification:") or lowered.startswith("slice contract:"):
            return title.split(":", 1)[1].strip() or default
        return title or default
    return default


def extract_section_body(text: str, heading: str) -> Optional[str]:
    """Return the body of a level-2 markdown section, or None if absent."""
    pattern = re.compile(
        rf"(?ms)^##\s+{re.escape(heading)}\s*$\n(?P<body>.*?)(?=^##\s+|\Z)"
    )
    match = pattern.search(text)
    if not match:
        return None
    body = match.group("body").strip()
    return body or None


def extract_brief_items(brief_text: str) -> List[str]:
    """Return up to five bullet items from the Work Item Summary section of a brief."""
    body = extract_section_body(brief_text, "1. Work Item Summary")
    if body is None:
        body = extract_section_body(brief_text, "1. Summary")
    if body is None:
        return []
    items: List[str] = []
    current_parts: List[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            if current_parts:
                items.append(" ".join(current_parts))
            current_parts = [stripped[2:].strip()]
            continue
        if current_parts and stripped and not stripped.startswith("#"):
            current_parts.append(stripped)
            continue
        if current_parts:
            items.append(" ".join(current_parts))
            current_parts = []
    if current_parts:
        items.append(" ".join(current_parts))
    return items[:5]


def extract_blueprint_summary(blueprint_text: str) -> Optional[str]:
    """Return a one-paragraph summary from the Summary section of a blueprint."""
    body = extract_section_body(blueprint_text, "1. Summary")
    if body is None:
        return None

    paragraph_lines: List[str] = []
    bullet_lines: List[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped:
            if paragraph_lines:
                break
            continue
        if stripped.startswith("- "):
            bullet_lines.append(stripped[2:].strip())
            continue
        if stripped.startswith("#"):
            break
        paragraph_lines.append(stripped)

    if paragraph_lines:
        return " ".join(paragraph_lines)
    if bullet_lines:
        return " ".join(bullet_lines[:3])
    return None


def extract_blueprint_figures(blueprint_text: str) -> List[str]:
    """Return all PlantUML code blocks from a blueprint."""
    return [match.group(0).strip() for match in PLANTUML_BLOCK_PATTERN.finditer(blueprint_text)]


def is_structural_plantuml(block: str) -> bool:
    """Return True when a PlantUML block contains structural diagram markers."""
    structural_markers = (
        r"(?m)^\s*class\s+",
        r"(?m)^\s*component\s+",
        r"(?m)^\s*interface\s+",
        r"(?m)^\s*entity\s+",
        r"(?m)^\s*package\s+",
        r"(?m)^\s*node\s+",
        r"(?m)^\s*artifact\s+",
        r"(?m)^\s*rectangle\s+",
        r"(?m)^\s*database\s+",
        r"(?m)^\s*frame\s+",
        r"(?m)^\s*cloud\s+",
        r"(?m)^\s*folder\s+",
        r"(?m)^\s*collections\s+",
        r"(?m)^\s*queue\s+",
        r"(?m)^\s*skinparam\s+componentStyle\b",
        r"(?m)^\s*skinparam\s+classAttributeIconSize\b",
    )
    return any(re.search(pattern, block) for pattern in structural_markers)


def extract_structural_figures(text: str) -> List[str]:
    """Return deduplicated structural PlantUML blocks from text."""
    return _dedupe_text_blocks(
        [
            match.group(0).strip()
            for match in PLANTUML_BLOCK_PATTERN.finditer(text)
            if is_structural_plantuml(match.group(0))
        ]
    )


def render_slice_summary_block(summary: PreparedSliceSummary) -> str:
    """Render a single archived-slice-summary markdown block."""
    lines = [
        SLICE_SUMMARY_START_TEMPLATE.format(slice_id=summary.slice_id),
        f"### `{summary.slice_id}`: {summary.title}",
    ]
    if summary.brief_items:
        lines.append("")
        lines.append("#### Work Item Summary")
        lines.append("")
        lines.extend(f"- {item}" for item in summary.brief_items)
    if summary.design_summary:
        lines.append("")
        lines.append("#### Detailed Design Summary")
        lines.append("")
        lines.append(summary.design_summary)
    figures = extract_blueprint_figures(summary.blueprint_text)
    if figures:
        lines.append("")
        lines.append("#### Blueprint Figures")
        lines.append("")
        lines.extend(figures)
    lines.append(SLICE_SUMMARY_END_TEMPLATE.format(slice_id=summary.slice_id))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Internal deduplication helpers
# ---------------------------------------------------------------------------

def _dedupe_preserve_order(values: List[str]) -> List[str]:
    seen = set()
    ordered: List[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _dedupe_text_blocks(values: List[str]) -> List[str]:
    seen = set()
    ordered: List[str] = []
    for value in values:
        candidate = value.strip()
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        ordered.append(candidate)
    return ordered
