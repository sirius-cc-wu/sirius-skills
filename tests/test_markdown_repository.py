"""Tests for lib/workflow_state/markdown_repository.py (dalc-repo-markdown slice).

Covers:
- Table parsing primitives
- Traceability record parsing
- Raw traceability table parsing and record_execution_slice_id write path
- Slice planning parsing (parse_planned_slices, parse_increment_plan,
  extract_slice_ids_from_planning_text)
- Reconciliation block extraction and field parsing
- Archive summary appendix read/write (load_existing_summary_blocks,
  write_summary_appendix)
- Slice summary content extraction helpers
- Render slice summary block
- Command-level smoke tests (inventory.parse_traceability_records delegates,
  archive_data helpers delegate)
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from sirius_skills.lib.workflow_state import markdown_repository


# ---------------------------------------------------------------------------
# Table parsing primitives
# ---------------------------------------------------------------------------


class TestTablePrimitives:
    def test_split_table_row_basic(self) -> None:
        cells = markdown_repository.split_table_row("| alpha | beta | gamma |")
        assert cells == ["alpha", "beta", "gamma"]

    def test_split_table_row_strips_whitespace(self) -> None:
        cells = markdown_repository.split_table_row("|  a  |  b  |")
        assert cells == ["a", "b"]

    def test_normalize_table_header_lowercases_and_replaces_dashes(self) -> None:
        assert markdown_repository.normalize_table_header("Planned-Slice-IDs") == "planned slice ids"
        assert markdown_repository.normalize_table_header("  Story ID  ") == "story id"
        assert markdown_repository.normalize_table_header("NOTES") == "notes"

    def test_split_cell_values_comma_separated(self) -> None:
        assert markdown_repository.split_cell_values("a, b, c") == ["a", "b", "c"]

    def test_split_cell_values_br_separated(self) -> None:
        result = markdown_repository.split_cell_values("a<br/>b<br>c")
        assert result == ["a", "b", "c"]

    def test_split_cell_values_semicolons(self) -> None:
        result = markdown_repository.split_cell_values("x; y; z")
        assert result == ["x", "y", "z"]

    def test_split_cell_values_empty(self) -> None:
        assert markdown_repository.split_cell_values("") == []

    def test_find_markdown_table_returns_correct_header_map(self) -> None:
        lines = [
            "| Slice ID | Story ID | Title | Depends On |",
            "| --- | --- | --- | --- |",
            "| S-01 | US-1 | Foo | |",
        ]
        header_map, start_index = markdown_repository.find_markdown_table(
            lines, ["Slice ID", "Story ID", "Depends On"]
        )
        assert start_index == 2
        assert header_map["slice id"] == 0
        assert header_map["story id"] == 1
        assert header_map["title"] == 2
        assert header_map["depends on"] == 3

    def test_find_markdown_table_raises_when_not_found(self) -> None:
        lines = ["No table here.", "Just prose."]
        with pytest.raises(RuntimeError, match="Could not locate"):
            markdown_repository.find_markdown_table(lines, ["Slice ID"])

    def test_find_markdown_table_skips_table_missing_required_headers(self) -> None:
        lines = [
            "| Name | Value |",
            "| --- | --- |",
            "| foo | bar |",
        ]
        with pytest.raises(RuntimeError):
            markdown_repository.find_markdown_table(lines, ["Slice ID"])


# ---------------------------------------------------------------------------
# Traceability record parsing
# ---------------------------------------------------------------------------

_TRACEABILITY_MD = """\
# Slice Traceability

| Story ID | Increments | Planned Slice IDs | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- |
| US-1 | I1 | P-01 | E-01 | First row |
| US-2 | I1, I2 | P-02, P-03 | E-02 | Second row |
"""


class TestTraceabilityRecordParsing:
    def test_parse_returns_correct_records(self, tmp_path: Path) -> None:
        path = tmp_path / "slice-traceability.md"
        path.write_text(_TRACEABILITY_MD, encoding="utf-8")
        records = markdown_repository.parse_traceability_records(
            path, "feature", "my-feat", "docs/features/my-feat/"
        )
        assert len(records) == 2
        assert records[0].story_id == "US-1"
        assert records[0].planned_slice_ids == ["P-01"]
        assert records[0].execution_slice_ids == ["E-01"]
        assert records[0].notes == "First row"
        assert records[1].story_id == "US-2"
        assert records[1].planned_slice_ids == ["P-02", "P-03"]

    def test_parse_returns_empty_when_file_absent(self, tmp_path: Path) -> None:
        records = markdown_repository.parse_traceability_records(
            tmp_path / "nonexistent.md", "feature", "x", "x/"
        )
        assert records == []

    def test_parse_returns_empty_when_no_traceability_table(self, tmp_path: Path) -> None:
        path = tmp_path / "slice-traceability.md"
        path.write_text("# No table here\n\nJust prose.\n", encoding="utf-8")
        records = markdown_repository.parse_traceability_records(
            path, "feature", "x", "x/"
        )
        assert records == []

    def test_parse_owner_fields_propagated(self, tmp_path: Path) -> None:
        path = tmp_path / "slice-traceability.md"
        path.write_text(_TRACEABILITY_MD, encoding="utf-8")
        records = markdown_repository.parse_traceability_records(
            path, "subfeature", "sf-1", "docs/features/f/subfeatures/sf-1/"
        )
        assert records[0].owner_type == "subfeature"
        assert records[0].owner_id == "sf-1"
        assert records[0].owner_path == "docs/features/f/subfeatures/sf-1/"

    def test_parse_optional_story_size_column(self, tmp_path: Path) -> None:
        md = (
            "| Story ID | Story Size | Increments | Planned Slice IDs | Execution Slice IDs | Notes |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            "| US-X | M | I1 | P-X | E-X | note |\n"
        )
        path = tmp_path / "t.md"
        path.write_text(md, encoding="utf-8")
        records = markdown_repository.parse_traceability_records(path, "feature", "f", "f/")
        assert records[0].story_size == "M"


# ---------------------------------------------------------------------------
# parse_traceability_table and record_execution_slice_id
# ---------------------------------------------------------------------------

_WRITE_TRACEABILITY_MD = """\
| Story ID | Planned Slice IDs | Execution Slice IDs | Notes |
| --- | --- | --- | --- |
| US-1 | P-01 |  | first |
| US-2 | P-02 |  | second |
"""


class TestTraceabilityWrite:
    def test_parse_traceability_table_returns_raw_lines(self, tmp_path: Path) -> None:
        path = tmp_path / "t.md"
        path.write_text(_WRITE_TRACEABILITY_MD, encoding="utf-8")
        lines, start_index, header_map, rows = markdown_repository.parse_traceability_table(path)
        assert "planned slice ids" in header_map
        assert "execution slice ids" in header_map
        assert len(rows) == 2

    def test_record_execution_slice_id_appends_id(self, tmp_path: Path) -> None:
        path = tmp_path / "t.md"
        path.write_text(_WRITE_TRACEABILITY_MD, encoding="utf-8")
        markdown_repository.record_execution_slice_id(path, "P-01", "E-01")
        lines, _, header_map, rows = markdown_repository.parse_traceability_table(path)
        exec_col = header_map["execution slice ids"]
        exec_ids = markdown_repository.split_cell_values(rows[0][exec_col])
        assert "E-01" in exec_ids

    def test_record_execution_slice_id_is_idempotent(self, tmp_path: Path) -> None:
        path = tmp_path / "t.md"
        path.write_text(_WRITE_TRACEABILITY_MD, encoding="utf-8")
        markdown_repository.record_execution_slice_id(path, "P-01", "E-01")
        markdown_repository.record_execution_slice_id(path, "P-01", "E-01")
        _, _, header_map, rows = markdown_repository.parse_traceability_table(path)
        exec_ids = markdown_repository.split_cell_values(
            rows[0][header_map["execution slice ids"]]
        )
        assert exec_ids.count("E-01") == 1

    def test_record_execution_slice_id_raises_when_not_found(self, tmp_path: Path) -> None:
        path = tmp_path / "t.md"
        path.write_text(_WRITE_TRACEABILITY_MD, encoding="utf-8")
        with pytest.raises(RuntimeError, match="Could not find a traceability row"):
            markdown_repository.record_execution_slice_id(path, "P-MISSING", "E-X")

    def test_record_execution_slice_id_raises_for_batch_row(self, tmp_path: Path) -> None:
        md = (
            "| Story ID | Planned Slice IDs | Execution Slice IDs | Notes |\n"
            "| --- | --- | --- | --- |\n"
            "| US-1 | P-01, P-02 |  | batch |\n"
        )
        path = tmp_path / "t.md"
        path.write_text(md, encoding="utf-8")
        with pytest.raises(RuntimeError, match="Batch execution"):
            markdown_repository.record_execution_slice_id(path, "P-01", "E-01")


# ---------------------------------------------------------------------------
# Slice planning parsing
# ---------------------------------------------------------------------------

_SLICE_PLANNING_MD = """\
# Slice Planning

## Slices

| Slice ID | Story ID | Title | Depends On | Validation |
| --- | --- | --- | --- | --- |
| S-01 | US-1 | First slice | | pytest |
| S-02 | US-2 | Second slice | S-01 done | pytest |
"""

_INCREMENT_PLANNING_MD = """\
# Increments

| Increment | Planned Slice IDs |
| --- | --- |
| I1 | S-01 |
| I2 | S-02 |
"""


class TestSlicePlanningParsing:
    def test_parse_planned_slices_returns_list(self, tmp_path: Path) -> None:
        path = tmp_path / "slice-planning.md"
        path.write_text(_SLICE_PLANNING_MD, encoding="utf-8")
        slices = markdown_repository.parse_planned_slices(path)
        assert len(slices) == 2
        assert slices[0]["planned_slice_id"] == "S-01"
        assert slices[0]["story_id"] == "US-1"
        assert slices[0]["title"] == "First slice"
        assert slices[0]["depends_on"] == []
        assert slices[1]["planned_slice_id"] == "S-02"
        assert slices[1]["depends_on"] == ["S-01 done"]

    def test_parse_planned_slices_validation_hint(self, tmp_path: Path) -> None:
        path = tmp_path / "slice-planning.md"
        path.write_text(_SLICE_PLANNING_MD, encoding="utf-8")
        slices = markdown_repository.parse_planned_slices(path)
        assert slices[0]["validation_hint"] == "pytest"

    def test_parse_increment_plan_returns_order_and_map(self, tmp_path: Path) -> None:
        path = tmp_path / "slice-planning.md"
        path.write_text(_INCREMENT_PLANNING_MD, encoding="utf-8")
        order, by_slice = markdown_repository.parse_increment_plan(path)
        assert order == ["I1", "I2"]
        assert "S-01" in by_slice
        assert "I1" in by_slice["S-01"]

    def test_parse_increment_plan_returns_empty_when_no_table(self, tmp_path: Path) -> None:
        path = tmp_path / "slice-planning.md"
        path.write_text("# No increments here\n", encoding="utf-8")
        order, by_slice = markdown_repository.parse_increment_plan(path)
        assert order == []
        assert by_slice == {}

    def test_extract_slice_ids_from_planning_text(self) -> None:
        result = markdown_repository.extract_slice_ids_from_planning_text(_SLICE_PLANNING_MD)
        assert result == ["S-01", "S-02"]

    def test_extract_slice_ids_deduplicates(self) -> None:
        md = (
            "| Slice ID | Story ID | Title | Depends On |\n"
            "| --- | --- | --- | --- |\n"
            "| S-01 | U1 | T | |\n"
            "| S-01 | U2 | T2 | |\n"
        )
        result = markdown_repository.extract_slice_ids_from_planning_text(md)
        assert result == ["S-01"]


# ---------------------------------------------------------------------------
# Reconciliation block extraction
# ---------------------------------------------------------------------------

_DESIGN_WITH_RECONCILIATION = """\
# System Design

## Overview

Some content.

<!-- execution-reconciliation:start -->
Status: aligned
Reviewed Planned Slice IDs: S-01, S-02
<!-- execution-reconciliation:end -->
"""


class TestReconciliationBlock:
    def test_extract_block_found(self) -> None:
        block = markdown_repository.extract_execution_reconciliation_block(
            _DESIGN_WITH_RECONCILIATION
        )
        assert block is not None
        assert "aligned" in block

    def test_extract_block_absent(self) -> None:
        assert markdown_repository.extract_execution_reconciliation_block("# No block") is None

    def test_parse_fields_extracts_status(self) -> None:
        block = markdown_repository.extract_execution_reconciliation_block(
            _DESIGN_WITH_RECONCILIATION
        )
        fields = markdown_repository.parse_execution_reconciliation_fields(block)
        assert fields["status"] == "aligned"
        assert fields["reviewed planned slice ids"] == "S-01, S-02"

    def test_parse_fields_empty_block(self) -> None:
        assert markdown_repository.parse_execution_reconciliation_fields("") == {}

    def test_parse_fields_skips_bullet_lines(self) -> None:
        block = "- this is a note\nStatus: draft"
        fields = markdown_repository.parse_execution_reconciliation_fields(block)
        assert "status" in fields
        assert len(fields) == 1


# ---------------------------------------------------------------------------
# Archive summary appendix
# ---------------------------------------------------------------------------

_DESIGN_WITH_SUMMARIES = """\
# System Design

## Overview

Content.

<!-- archived-slice-summaries:start -->
## Archived Slice Summaries

<!-- archived-slice-summary:S-01:start -->
### `S-01`: First Slice
<!-- archived-slice-summary:S-01:end -->

<!-- archived-slice-summaries:end -->
"""


class TestArchiveSummaryAppendix:
    def test_load_existing_summary_blocks_finds_slice(self) -> None:
        blocks = markdown_repository.load_existing_summary_blocks(_DESIGN_WITH_SUMMARIES)
        assert "S-01" in blocks
        assert "First Slice" in blocks["S-01"]

    def test_load_existing_summary_blocks_empty_when_no_section(self) -> None:
        blocks = markdown_repository.load_existing_summary_blocks("# No summaries\n")
        assert blocks == {}

    def test_write_summary_appendix_creates_section(self, tmp_path: Path) -> None:
        design_path = tmp_path / "system-design.md"
        design_path.write_text("# System Design\n\nContent.\n", encoding="utf-8")
        blocks = {
            "S-01": (
                "<!-- archived-slice-summary:S-01:start -->\n"
                "### `S-01`: New Slice\n"
                "<!-- archived-slice-summary:S-01:end -->"
            )
        }
        markdown_repository.write_summary_appendix(design_path, blocks)
        updated = design_path.read_text(encoding="utf-8")
        assert "archived-slice-summaries:start" in updated
        assert "S-01" in updated
        assert "New Slice" in updated

    def test_write_summary_appendix_updates_existing_section(self, tmp_path: Path) -> None:
        design_path = tmp_path / "system-design.md"
        design_path.write_text(_DESIGN_WITH_SUMMARIES, encoding="utf-8")
        new_block = (
            "<!-- archived-slice-summary:S-02:start -->\n"
            "### `S-02`: Second Slice\n"
            "<!-- archived-slice-summary:S-02:end -->"
        )
        markdown_repository.write_summary_appendix(design_path, {"S-02": new_block})
        updated = design_path.read_text(encoding="utf-8")
        # Both S-01 (pre-existing) and S-02 (new) must appear
        assert "S-01" in updated
        assert "S-02" in updated
        assert "Second Slice" in updated

    def test_write_summary_appendix_preserves_structural_figures(self, tmp_path: Path) -> None:
        design_path = tmp_path / "system-design.md"
        design_path.write_text("# System Design\n\nContent.\n", encoding="utf-8")
        blocks = {
            "S-01": (
                "<!-- archived-slice-summary:S-01:start -->\n"
                "### `S-01`: T\n"
                "<!-- archived-slice-summary:S-01:end -->"
            )
        }
        figures = ["```plantuml\n@startuml\ncomponent Foo\n@enduml\n```"]
        markdown_repository.write_summary_appendix(design_path, blocks, structural_figures=figures)
        updated = design_path.read_text(encoding="utf-8")
        assert "Structural Context" in updated
        assert "component Foo" in updated

    def test_write_summary_appendix_is_idempotent(self, tmp_path: Path) -> None:
        design_path = tmp_path / "system-design.md"
        design_path.write_text("# System Design\n\nContent.\n", encoding="utf-8")
        block = (
            "<!-- archived-slice-summary:S-01:start -->\n"
            "### `S-01`: T\n"
            "<!-- archived-slice-summary:S-01:end -->"
        )
        markdown_repository.write_summary_appendix(design_path, {"S-01": block})
        text_after_first = design_path.read_text(encoding="utf-8")
        markdown_repository.write_summary_appendix(design_path, {"S-01": block})
        text_after_second = design_path.read_text(encoding="utf-8")
        assert text_after_first == text_after_second


# ---------------------------------------------------------------------------
# Slice summary content extraction helpers
# ---------------------------------------------------------------------------

_BRIEF_MD = """\
# Slice Contract: Do Something

## 1. Summary

- Work item alpha
- Work item beta
- Work item gamma
"""

_BLUEPRINT_MD = """\
# Blueprint

## 1. Summary

This is a paragraph summary for the design.

## 2. Architecture

More content.

```plantuml
@startuml
component Auth
component App
App --> Auth
@enduml
```
"""

_STRUCTURAL_BLUEPRINT_MD = """\
```plantuml
@startuml
component Foo
component Bar
Foo --> Bar
@enduml
```
"""


class TestSliceSummaryContentExtraction:
    def test_extract_heading_title_from_contract(self) -> None:
        title = markdown_repository.extract_heading_title(_BRIEF_MD, "default")
        assert title == "Do Something"

    def test_extract_heading_title_plain_heading(self) -> None:
        title = markdown_repository.extract_heading_title("# My Feature\n", "default")
        assert title == "My Feature"

    def test_extract_heading_title_returns_default_when_no_heading(self) -> None:
        assert markdown_repository.extract_heading_title("No heading\n", "fallback") == "fallback"

    def test_extract_section_body_finds_section(self) -> None:
        body = markdown_repository.extract_section_body(_BRIEF_MD, "1. Summary")
        assert body is not None
        assert "Work item alpha" in body

    def test_extract_section_body_returns_none_when_absent(self) -> None:
        assert markdown_repository.extract_section_body(_BRIEF_MD, "Nonexistent Section") is None

    def test_extract_brief_items_returns_up_to_five(self) -> None:
        items = markdown_repository.extract_brief_items(_BRIEF_MD)
        assert items == ["Work item alpha", "Work item beta", "Work item gamma"]

    def test_extract_brief_items_empty_when_no_section(self) -> None:
        assert markdown_repository.extract_brief_items("# No section\n") == []

    def test_extract_blueprint_summary_returns_paragraph(self) -> None:
        summary = markdown_repository.extract_blueprint_summary(_BLUEPRINT_MD)
        assert summary is not None
        assert "paragraph summary" in summary

    def test_extract_blueprint_summary_returns_none_when_no_summary(self) -> None:
        assert markdown_repository.extract_blueprint_summary("# No summary\n") is None

    def test_extract_blueprint_figures_returns_plantuml_blocks(self) -> None:
        figures = markdown_repository.extract_blueprint_figures(_BLUEPRINT_MD)
        assert len(figures) == 1
        assert "component Auth" in figures[0]

    def test_is_structural_plantuml_detects_component(self) -> None:
        block = "```plantuml\n@startuml\ncomponent Foo\n@enduml\n```"
        assert markdown_repository.is_structural_plantuml(block) is True

    def test_is_structural_plantuml_rejects_sequence(self) -> None:
        block = "```plantuml\n@startuml\nAlice -> Bob\n@enduml\n```"
        assert markdown_repository.is_structural_plantuml(block) is False

    def test_extract_structural_figures_only_returns_structural(self) -> None:
        mixed = (
            "```plantuml\n@startuml\ncomponent Foo\n@enduml\n```\n"
            "```plantuml\n@startuml\nAlice -> Bob\n@enduml\n```\n"
        )
        figures = markdown_repository.extract_structural_figures(mixed)
        assert len(figures) == 1
        assert "component Foo" in figures[0]


# ---------------------------------------------------------------------------
# render_slice_summary_block
# ---------------------------------------------------------------------------


class TestRenderSliceSummaryBlock:
    def _make_summary(self, **kwargs) -> markdown_repository.PreparedSliceSummary:
        defaults = {
            "slice_id": "S-01",
            "title": "Test Slice",
            "brief_items": [],
            "design_summary": None,
            "blueprint_text": "",
        }
        defaults.update(kwargs)
        return markdown_repository.PreparedSliceSummary(**defaults)

    def test_render_contains_slice_id_and_title(self) -> None:
        summary = self._make_summary()
        rendered = markdown_repository.render_slice_summary_block(summary)
        assert "S-01" in rendered
        assert "Test Slice" in rendered
        assert "archived-slice-summary:S-01:start" in rendered
        assert "archived-slice-summary:S-01:end" in rendered

    def test_render_includes_brief_items(self) -> None:
        summary = self._make_summary(brief_items=["Do X", "Do Y"])
        rendered = markdown_repository.render_slice_summary_block(summary)
        assert "Work Item Summary" in rendered
        assert "- Do X" in rendered

    def test_render_includes_design_summary(self) -> None:
        summary = self._make_summary(design_summary="This is the design.")
        rendered = markdown_repository.render_slice_summary_block(summary)
        assert "Detailed Design Summary" in rendered
        assert "This is the design." in rendered

    def test_render_includes_blueprint_figures(self) -> None:
        summary = self._make_summary(
            blueprint_text="```plantuml\n@startuml\ncomponent X\n@enduml\n```"
        )
        rendered = markdown_repository.render_slice_summary_block(summary)
        assert "Blueprint Figures" in rendered
        assert "component X" in rendered

    def test_render_no_brief_items_skips_section(self) -> None:
        rendered = markdown_repository.render_slice_summary_block(self._make_summary())
        assert "Work Item Summary" not in rendered

    def test_rendered_block_parseable_by_load_existing(self) -> None:
        summary = self._make_summary(brief_items=["Item A"])
        rendered = markdown_repository.render_slice_summary_block(summary)
        blocks = markdown_repository.load_existing_summary_blocks(
            f"<!-- archived-slice-summaries:start -->\n{rendered}\n<!-- archived-slice-summaries:end -->\n"
        )
        assert "S-01" in blocks


# ---------------------------------------------------------------------------
# Command compatibility: inventory.parse_traceability_records delegates
# ---------------------------------------------------------------------------


class TestInventoryDelegation:
    """Verify that inventory.parse_traceability_records still works after
    delegating to markdown_repository."""

    def test_inventory_parse_traceability_records_matches_repo(self, tmp_path: Path) -> None:
        from sirius_skills.lib.workflow_state.inventory import parse_traceability_records as inv_parse

        path = tmp_path / "slice-traceability.md"
        path.write_text(_TRACEABILITY_MD, encoding="utf-8")

        inv_records = inv_parse(path, "feature", "f", "f/")
        repo_records = markdown_repository.parse_traceability_records(path, "feature", "f", "f/")

        assert len(inv_records) == len(repo_records)
        for inv_r, repo_r in zip(inv_records, repo_records):
            assert inv_r.story_id == repo_r.story_id
            assert inv_r.planned_slice_ids == repo_r.planned_slice_ids
            assert inv_r.execution_slice_ids == repo_r.execution_slice_ids


# ---------------------------------------------------------------------------
# Command compatibility: archive_data helpers delegate
# ---------------------------------------------------------------------------


class TestArchiveDataDelegation:
    """Verify that archive_data local delegates still behave correctly."""

    def test_extract_heading_title_matches_repo(self) -> None:
        from sirius_skills.commands.archive_data import _extract_heading_title

        assert _extract_heading_title(_BRIEF_MD, "default") == \
            markdown_repository.extract_heading_title(_BRIEF_MD, "default")

    def test_extract_brief_items_matches_repo(self) -> None:
        from sirius_skills.commands.archive_data import _extract_brief_items

        assert _extract_brief_items(_BRIEF_MD) == markdown_repository.extract_brief_items(_BRIEF_MD)

    def test_write_summary_appendix_through_archive_data(self, tmp_path: Path) -> None:
        from sirius_skills.commands.archive_data import _write_summary_appendix

        design_path = tmp_path / "system-design.md"
        design_path.write_text("# Design\n", encoding="utf-8")
        block = (
            "<!-- archived-slice-summary:S-99:start -->\n"
            "### `S-99`: Via archive_data\n"
            "<!-- archived-slice-summary:S-99:end -->"
        )
        _write_summary_appendix(design_path, {"S-99": block})
        text = design_path.read_text(encoding="utf-8")
        assert "S-99" in text
        assert "Via archive_data" in text
