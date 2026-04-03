import importlib.util
import json
import sys
from pathlib import Path


CLOSE_SLICE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "close_slice.py"
MANAGE_EXECUTION_PATH = (
    Path(__file__).resolve().parents[2] / "guide-execution" / "scripts" / "manage_execution.py"
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
