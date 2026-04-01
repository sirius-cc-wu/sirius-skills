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


def setup_execution_ready_slice(tmp_path, monkeypatch, include_legacy_slices=True):
    manage_execution = load_module(MANAGE_EXECUTION_PATH, "manage_execution")
    monkeypatch.chdir(tmp_path)

    assert run_cli(manage_execution, monkeypatch, "init", "slices") == 0
    assert run_cli(manage_execution, monkeypatch, "add", "DEMO", "Demo Feature") == 0

    slice_dir = tmp_path / "slices" / "DEMO-demo-feature"
    (slice_dir / "brief.md").write_text(
        "# Slice Brief: Demo Feature\n\n"
        "## 3. Functional Requirements\n\n"
        "- **FR-001**: System MUST store a summary entry.\n"
        "- **FR-002**: System MUST preserve backlinks.\n\n"
        "## 7. Success Criteria\n\n"
        "- **SC-001**: Teams can discover closed slices quickly.\n",
        encoding="utf-8",
    )
    (slice_dir / "checklists").mkdir()
    (slice_dir / "checklists" / "requirements.md").write_text(
        "- [x] FR-001 requirements captured\n- [x] FR-002 requirements captured\n",
        encoding="utf-8",
    )
    assert run_cli(manage_execution, monkeypatch, "set-status", "DEMO", "brief_ready") == 0

    (slice_dir / "blueprint.md").write_text(
        "# Implementation Plan: Demo Feature\n\n"
        "### Packet P01: Demo Packet\n\n"
        "- Validation:\n"
        "  - [ ] V001 Run demo integration test\n"
        "  - [ ] V002 Confirm rollback behavior\n\n"
        "### Verification Scenarios\n\n"
        "- Happy path: User can see published history entry\n"
        "- Regression checks: Existing slice artifacts remain in place\n",
        encoding="utf-8",
    )
    if include_legacy_slices:
        (slice_dir / "slices.md").write_text(
            "# Slices: Demo Feature\n\n"
            "## 1. Execution Strategy\n\n"
            "- Validation approach: Run focused tests before closing the slice\n\n"
            "## 7. Exit Criteria\n\n"
            "- [ ] Validation work is represented where required\n"
            "- [ ] The implementation agent can begin without major replanning\n",
            encoding="utf-8",
        )
    assert run_cli(manage_execution, monkeypatch, "set-status", "DEMO", "blueprint_ready") == 0
    assert run_cli(manage_execution, monkeypatch, "set-status", "DEMO", "execution_ready") == 0
    return manage_execution, slice_dir


def test_close_slice_publishes_to_explicit_file(tmp_path, monkeypatch):
    close_slice = load_module(CLOSE_SLICE_PATH, "close_slice")
    _, slice_dir = setup_execution_ready_slice(tmp_path, monkeypatch)

    assert (
        run_cli(
            close_slice,
            monkeypatch,
            "--slice",
            "DEMO",
            "--publish",
            "docs/slice-history.md",
        )
        == 0
    )

    target = tmp_path / "docs" / "slice-history.md"
    metadata = json.loads((slice_dir / ".slice-meta.json").read_text(encoding="utf-8"))
    content = target.read_text(encoding="utf-8")

    assert "### " in content
    assert "Demo Feature (`DEMO`)" in content
    assert "Functional requirements snapshot" in content
    assert "`slices/DEMO-demo-feature/brief.md`" in content
    assert "Implementation verification snapshot" in content
    assert "Run demo integration test" in content
    assert metadata["status"] == "closed"
    assert metadata["publications"][0]["target_file"] == "docs/slice-history.md"


def test_close_slice_uses_config_when_publish_target_not_passed(tmp_path, monkeypatch):
    close_slice = load_module(CLOSE_SLICE_PATH, "close_slice")
    _, slice_dir = setup_execution_ready_slice(tmp_path, monkeypatch)

    plugins_dir = tmp_path / ".skills" / "plugins"
    plugins_dir.mkdir(parents=True)
    (plugins_dir / "spec-publish.json").write_text(
        json.dumps(
            {
                "target_file": "docs/history.md",
                "document_title": "Team Slice History",
                "section_title": "Published Slices",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    assert run_cli(close_slice, monkeypatch, "--slice", "DEMO") == 0

    target = tmp_path / "docs" / "history.md"
    content = target.read_text(encoding="utf-8")
    metadata = json.loads((slice_dir / ".slice-meta.json").read_text(encoding="utf-8"))

    assert content.startswith("# Team Slice History")
    assert "## Published Slices" in content
    assert "Run focused tests before closing the slice" in content
    assert metadata["publications"][0]["target_file"] == "docs/history.md"


def test_close_slice_publishes_without_legacy_slices_md(tmp_path, monkeypatch):
    close_slice = load_module(CLOSE_SLICE_PATH, "close_slice")
    _, slice_dir = setup_execution_ready_slice(tmp_path, monkeypatch, include_legacy_slices=False)

    assert (
        run_cli(
            close_slice,
            monkeypatch,
            "--slice",
            "DEMO",
            "--publish",
            "docs/slice-history.md",
        )
        == 0
    )

    content = (tmp_path / "docs" / "slice-history.md").read_text(encoding="utf-8")
    metadata = json.loads((slice_dir / ".slice-meta.json").read_text(encoding="utf-8"))

    assert "Demo Feature (`DEMO`)" in content
    assert "Implementation verification snapshot" in content
    assert "User can see published history entry" in content
    assert metadata["status"] == "closed"


def test_close_slice_renders_issue_link_when_conventions_config_exists(tmp_path, monkeypatch):
    close_slice = load_module(CLOSE_SLICE_PATH, "close_slice")
    _, slice_dir = setup_execution_ready_slice(tmp_path, monkeypatch)

    conventions_dir = tmp_path / ".skills"
    conventions_dir.mkdir(parents=True, exist_ok=True)
    (conventions_dir / "conventions.json").write_text(
        json.dumps(
            {"issue_url_template": "https://tracker.example.com/issues/{ID}"}
        )
        + "\n",
        encoding="utf-8",
    )

    metadata = json.loads((slice_dir / ".slice-meta.json").read_text(encoding="utf-8"))
    metadata["issue"] = {
        "id": "BNC-123",
        "title": "Demo source issue",
        "status": "Done",
    }
    (slice_dir / ".slice-meta.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )

    assert (
        run_cli(
            close_slice,
            monkeypatch,
            "--slice",
            "DEMO",
            "--publish",
            "docs/slice-history.md",
        )
        == 0
    )

    content = (tmp_path / "docs" / "slice-history.md").read_text(encoding="utf-8")
    assert (
        "[BNC-123](https://tracker.example.com/issues/BNC-123) — Demo source issue; status: Done"
        in content
    )


def test_close_slice_republishes_without_duplicate_markers(tmp_path, monkeypatch):
    close_slice = load_module(CLOSE_SLICE_PATH, "close_slice")
    _, slice_dir = setup_execution_ready_slice(tmp_path, monkeypatch)

    assert (
        run_cli(
            close_slice,
            monkeypatch,
            "--slice",
            "DEMO",
            "--publish",
            "docs/slice-history.md",
        )
        == 0
    )

    (slice_dir / "brief.md").write_text(
        "# Slice Brief: Demo Feature\n\n"
        "## 3. Functional Requirements\n\n"
        "- **FR-001**: Updated summary text.\n\n"
        "## 7. Success Criteria\n\n"
        "- **SC-001**: Updated criterion.\n",
        encoding="utf-8",
    )

    assert (
        run_cli(
            close_slice,
            monkeypatch,
            "--slice",
            "DEMO",
            "--publish",
            "docs/slice-history.md",
        )
        == 0
    )

    content = (tmp_path / "docs" / "slice-history.md").read_text(encoding="utf-8")
    assert content.count("<!-- spec-publish:DEMO:start -->") == 1
    assert "Updated summary text." in content


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


def test_close_slice_records_relations_and_publishes_them(tmp_path, monkeypatch):
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
            "--publish",
            "docs/slice-history.md",
        )
        == 0
    )

    content = (tmp_path / "docs" / "slice-history.md").read_text(encoding="utf-8")
    source_meta = json.loads((slice_dir / ".slice-meta.json").read_text(encoding="utf-8"))
    target_meta = json.loads(
        (tmp_path / "slices" / "OLD-old-feature" / ".slice-meta.json").read_text(
            encoding="utf-8"
        )
    )

    assert "Slice relations:" in content
    assert "supersedes `OLD` (story: Story 2 - Legacy checkout; requirements: FR-002; selector: legacy checkout path)" in content
    assert source_meta["relations"][0]["type"] == "supersedes"
    assert target_meta["relations"][0]["type"] == "superseded_by"


def test_close_slice_can_archive_to_hidden_directory(tmp_path, monkeypatch):
    close_slice = load_module(CLOSE_SLICE_PATH, "close_slice")
    _, slice_dir = setup_execution_ready_slice(tmp_path, monkeypatch)

    assert run_cli(close_slice, monkeypatch, "--slice", "DEMO", "--archive") == 0

    archived_dir = tmp_path / "slices" / ".archived" / "DEMO-demo-feature"
    registry = json.loads((tmp_path / "slices" / "registry.json").read_text(encoding="utf-8"))
    metadata = json.loads((archived_dir / ".slice-meta.json").read_text(encoding="utf-8"))

    assert not slice_dir.exists()
    assert archived_dir.exists()
    assert metadata["status"] == "closed"
    assert metadata["archived_at"]
    assert metadata["archived_from"] == "slices/DEMO-demo-feature/"
    assert registry["slices"][0]["path"] == "slices/.archived/DEMO-demo-feature/"
    assert registry["slices"][0]["archived_at"] == metadata["archived_at"]


def test_close_slice_uses_archive_config_and_publishes_archived_paths(tmp_path, monkeypatch):
    close_slice = load_module(CLOSE_SLICE_PATH, "close_slice")
    _, slice_dir = setup_execution_ready_slice(tmp_path, monkeypatch)

    plugins_dir = tmp_path / ".skills" / "plugins"
    plugins_dir.mkdir(parents=True)
    (plugins_dir / "spec-archive.json").write_text(
        json.dumps({"target_dir": "slices/.retired"}) + "\n", encoding="utf-8"
    )

    assert (
        run_cli(
            close_slice,
            monkeypatch,
            "--slice",
            "DEMO",
            "--publish",
            "docs/slice-history.md",
        )
        == 0
    )

    archived_dir = tmp_path / "slices" / ".retired" / "DEMO-demo-feature"
    content = (tmp_path / "docs" / "slice-history.md").read_text(encoding="utf-8")
    metadata = json.loads((archived_dir / ".slice-meta.json").read_text(encoding="utf-8"))

    assert not slice_dir.exists()
    assert archived_dir.exists()
    assert "`slices/.retired/DEMO-demo-feature/brief.md`" in content
    assert metadata["archived_at"]
