import importlib.util
import json
import sys
from pathlib import Path


CLOSE_SLICE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "close_slice.py"
MANAGE_EXECUTION_PATH = (
    Path(__file__).resolve().parents[2] / "guide-execution" / "scripts" / "manage_execution.py"
)
MANAGE_PLANNING_PATH = (
    Path(__file__).resolve().parents[2] / "guide-planning" / "scripts" / "manage_planning.py"
)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_cli(module, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", [module.__file__, *args])
    return module.main()


def write_planning_config(scope_root: Path):
    skills_dir = scope_root / ".skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    (skills_dir / "planning.json").write_text(
        json.dumps({"planning_dir": "docs/features", "proposal_dir": "docs/proposals"}) + "\n",
        encoding="utf-8",
    )


def write_transition_guardrail_feature(
    tmp_path: Path,
    slice_id: str,
    *,
    feature_status: str = "planning_reviewed",
    feature_ready_slice_ids: list[str] | None = None,
    subfeature_status: str = "reviewed",
    include_subfeature: bool = True,
):
    feature_dir = tmp_path / "docs" / "features" / "checkout"
    subfeature_dir = feature_dir / "subfeatures" / "replace-legacy-flow"
    if include_subfeature:
        subfeature_dir.mkdir(parents=True, exist_ok=True)
    else:
        feature_dir.mkdir(parents=True, exist_ok=True)
    (feature_dir / "discover.md").write_text("# Discover\n", encoding="utf-8")
    (feature_dir / "system-design.md").write_text("# Design\n", encoding="utf-8")
    (feature_dir / "slice-planning.md").write_text("# Slice Planning\n", encoding="utf-8")
    (feature_dir / "slice-traceability.md").write_text(
        "# Slice Traceability\n\n"
        "| Story ID | Increments | Planned Slice IDs | Execution Slice IDs | Notes |\n"
        "| --- | --- | --- | --- | --- |\n"
        f"| CHK-01 | I1 | {slice_id} | {slice_id} | demo |\n",
        encoding="utf-8",
    )
    (feature_dir / ".planning-meta.json").write_text(
        json.dumps(
            {
                "feature_slug": "checkout",
                "status": feature_status,
                "created_at": "2026-01-01T00:00:00",
                "updated_at": "2026-01-01T00:00:00",
                "requires_ui_flow": False,
                "review_note": "ready",
                "ready_slice_ids": feature_ready_slice_ids
                if feature_ready_slice_ids is not None
                else [slice_id],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    if not include_subfeature:
        return
    (subfeature_dir / "discover.md").write_text("# Discover\n", encoding="utf-8")
    (subfeature_dir / "impact-analysis.md").write_text("# Impact\n", encoding="utf-8")
    (subfeature_dir / "system-design.md").write_text("# Design\n", encoding="utf-8")
    (subfeature_dir / "slice-planning.md").write_text("# Slice Planning\n", encoding="utf-8")
    (subfeature_dir / ".subfeature-meta.json").write_text(
        json.dumps(
            {
                "parent_feature_slug": "checkout",
                "subfeature_id": "replace-legacy-flow",
                "status": subfeature_status,
                "created_at": "2026-01-01T00:00:00",
                "updated_at": "2026-01-01T00:00:00",
                "subfeature_type": "replacement",
                "summary": "Replace legacy flow",
                "affected_artifacts": [],
                "affected_story_ids": [],
                "affected_slice_ids": [slice_id],
                "review_note": "ready",
                "finalized_at": None,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (subfeature_dir / "slice-traceability.md").write_text(
        "# Slice Traceability\n\n"
        "| Story ID | Increments | Planned Slice IDs | Execution Slice IDs | Notes |\n"
        "| --- | --- | --- | --- | --- |\n"
        f"| CHK-01 | I2 | {slice_id} | {slice_id} | demo |\n",
        encoding="utf-8",
    )


def setup_execution_ready_slice(tmp_path, monkeypatch):
    manage_execution = load_module(MANAGE_EXECUTION_PATH, "manage_execution")
    monkeypatch.chdir(tmp_path)

    assert run_cli(manage_execution, monkeypatch, "init", "slices") == 0
    assert run_cli(manage_execution, monkeypatch, "add", "DEMO", "Demo Feature") == 0

    slice_dir = tmp_path / "slices" / "DEMO-demo-feature"
    (slice_dir / "brief.md").write_text(
        "# Slice Brief: Demo Feature\n\n"
        "## 3. Functional Requirements\n\n"
        "- **FR-001**: System MUST store closure metadata.\n",
        encoding="utf-8",
    )
    (slice_dir / "checklists").mkdir()
    (slice_dir / "checklists" / "requirements.md").write_text(
        "- [x] FR-001 requirements captured\n", encoding="utf-8"
    )
    assert run_cli(manage_execution, monkeypatch, "set-status", "DEMO", "brief_ready") == 0

    (slice_dir / "blueprint.md").write_text(
        "# Implementation Plan: Demo Feature\n\n"
        "- Validation:\n"
        "  - [ ] V001 Close the slice cleanly\n",
        encoding="utf-8",
    )
    assert run_cli(manage_execution, monkeypatch, "set-status", "DEMO", "blueprint_ready") == 0
    assert run_cli(manage_execution, monkeypatch, "set-status", "DEMO", "execution_ready") == 0
    return manage_execution, slice_dir


def test_close_slice_marks_slice_closed(tmp_path, monkeypatch):
    close_slice = load_module(CLOSE_SLICE_PATH, "close_slice")
    _, slice_dir = setup_execution_ready_slice(tmp_path, monkeypatch)

    assert run_cli(close_slice, monkeypatch, "--slice", "DEMO") == 0

    metadata = json.loads((slice_dir / ".slice-meta.json").read_text(encoding="utf-8"))
    registry = json.loads((tmp_path / "slices" / "registry.json").read_text(encoding="utf-8"))

    assert metadata["status"] == "closed"
    assert metadata["closed_at"]
    assert registry["slices"][0]["status"] == "closed"


def test_close_slice_requires_confirm_impact_for_relations(tmp_path, monkeypatch, capsys):
    close_slice = load_module(CLOSE_SLICE_PATH, "close_slice")
    manage_execution, _ = setup_execution_ready_slice(tmp_path, monkeypatch)

    assert run_cli(manage_execution, monkeypatch, "add", "OLD", "Old Feature") == 0

    exit_code = run_cli(
        close_slice,
        monkeypatch,
        "--slice",
        "DEMO",
        "--relate",
        "supersedes",
        "OLD",
    )
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "--confirm-impact" in captured.err


def test_close_slice_records_relations_without_archiving_or_publishing(
    tmp_path, monkeypatch
):
    close_slice = load_module(CLOSE_SLICE_PATH, "close_slice")
    manage_execution, slice_dir = setup_execution_ready_slice(tmp_path, monkeypatch)

    assert run_cli(manage_execution, monkeypatch, "add", "OLD", "Old Feature") == 0

    assert (
        run_cli(
            close_slice,
            monkeypatch,
            "--slice",
            "DEMO",
            "--relate",
            "supersedes",
            "OLD",
            "--story-title",
            "Story 2 - Legacy checkout",
            "--requirement-id",
            "FR-002",
            "--selector",
            "legacy checkout path",
            "--confirm-impact",
        )
        == 0
    )

    source_meta = json.loads((slice_dir / ".slice-meta.json").read_text(encoding="utf-8"))
    target_meta = json.loads(
        (tmp_path / "slices" / "OLD-old-feature" / ".slice-meta.json").read_text(
            encoding="utf-8"
        )
    )

    assert source_meta["relations"][0]["type"] == "supersedes"
    assert target_meta["relations"][0]["type"] == "superseded_by"
    assert "publications" not in source_meta
    assert "archived_at" not in source_meta


def test_close_slice_blocks_when_linked_subfeature_is_not_finalized(
    tmp_path, monkeypatch, capsys
):
    close_slice = load_module(CLOSE_SLICE_PATH, "close_slice")
    _, _ = setup_execution_ready_slice(tmp_path, monkeypatch)
    write_planning_config(tmp_path)
    write_transition_guardrail_feature(
        tmp_path,
        "DEMO",
        subfeature_status="draft",
    )

    exit_code = run_cli(close_slice, monkeypatch, "--slice", "DEMO")
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "transition_subfeature_review_required" in captured.err


def test_close_slice_marks_feature_implemented_when_last_slice_closes(tmp_path, monkeypatch):
    close_slice = load_module(CLOSE_SLICE_PATH, "close_slice")
    planning = load_module(MANAGE_PLANNING_PATH, "manage_planning_close_slice")
    _, _ = setup_execution_ready_slice(tmp_path, monkeypatch)
    write_planning_config(tmp_path)
    write_transition_guardrail_feature(
        tmp_path,
        "DEMO",
        feature_status="slice_ready",
        include_subfeature=False,
    )

    assert run_cli(close_slice, monkeypatch, "--slice", "DEMO") == 0

    feature_metadata = json.loads(
        (tmp_path / "docs" / "features" / "checkout" / ".planning-meta.json").read_text(
            encoding="utf-8"
        )
    )
    registry = json.loads(
        (tmp_path / "docs" / "features" / "registry.json").read_text(encoding="utf-8")
    )

    assert feature_metadata["status"] == "implemented"
    assert feature_metadata["ready_slice_ids"] == []
    feature_row = next(row for row in registry["features"] if row["feature"] == "checkout")
    assert feature_row["status"] == "implemented"

    monkeypatch.setattr(
        sys,
        "argv",
        ["manage_planning.py", "validate-feature", "checkout"],
    )
    assert planning.main() == 0


def test_close_slice_keeps_feature_slice_ready_when_other_planned_slices_remain(
    tmp_path, monkeypatch
):
    close_slice = load_module(CLOSE_SLICE_PATH, "close_slice")
    planning = load_module(MANAGE_PLANNING_PATH, "manage_planning_close_slice_remaining")
    _, _ = setup_execution_ready_slice(tmp_path, monkeypatch)
    write_planning_config(tmp_path)
    write_transition_guardrail_feature(
        tmp_path,
        "DEMO",
        feature_status="slice_ready",
        feature_ready_slice_ids=["DEMO", "NEXT"],
        include_subfeature=False,
    )
    feature_dir = tmp_path / "docs" / "features" / "checkout"
    (feature_dir / "slice-traceability.md").write_text(
        "# Slice Traceability\n\n"
        "| Story ID | Increments | Planned Slice IDs | Execution Slice IDs | Notes |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| CHK-01 | I1 | DEMO | DEMO | closed slice |\n"
        "| CHK-02 | I1 | NEXT | NEXT | remaining slice |\n",
        encoding="utf-8",
    )

    assert run_cli(close_slice, monkeypatch, "--slice", "DEMO") == 0

    planning.sync_registry(scope_context=planning.SCOPE_RUNTIME.resolve_scope_context())
    feature_metadata = json.loads(
        (feature_dir / ".planning-meta.json").read_text(encoding="utf-8")
    )
    registry = json.loads(
        (tmp_path / "docs" / "features" / "registry.json").read_text(encoding="utf-8")
    )

    assert feature_metadata["status"] == "slice_ready"
    assert feature_metadata["ready_slice_ids"] == ["DEMO", "NEXT"]
    feature_row = next(row for row in registry["features"] if row["feature"] == "checkout")
    assert feature_row["status"] == "slice_ready"

    monkeypatch.setattr(
        sys,
        "argv",
        ["manage_planning.py", "validate-feature", "checkout"],
    )
    assert planning.main() == 0


def test_close_slice_finalizes_reviewed_subfeature_when_last_slice_closes(
    tmp_path, monkeypatch
):
    close_slice = load_module(CLOSE_SLICE_PATH, "close_slice")
    _, _ = setup_execution_ready_slice(tmp_path, monkeypatch)
    write_planning_config(tmp_path)
    write_transition_guardrail_feature(
        tmp_path,
        "DEMO",
        feature_status="planning_reviewed",
        feature_ready_slice_ids=[],
        subfeature_status="reviewed",
    )

    assert run_cli(close_slice, monkeypatch, "--slice", "DEMO") == 0

    subfeature_dir = (
        tmp_path / "docs" / "features" / "checkout" / "subfeatures" / "replace-legacy-flow"
    )
    subfeature_metadata = json.loads(
        (subfeature_dir / ".subfeature-meta.json").read_text(encoding="utf-8")
    )
    planning = load_module(MANAGE_PLANNING_PATH, "manage_planning_close_slice_subfeature")
    planning_metadata = planning.read_metadata(str(subfeature_dir))

    assert subfeature_metadata["status"] == "finalized"
    assert subfeature_metadata["affected_slice_ids"] == ["DEMO"]
    assert subfeature_metadata["finalized_at"]
    assert not (subfeature_dir / ".planning-meta.json").exists()
    assert planning_metadata["status"] == "implemented"
    assert planning_metadata["ready_slice_ids"] == []
