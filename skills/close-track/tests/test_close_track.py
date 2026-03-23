import importlib.util
import json
import sys
from pathlib import Path


CLOSE_TRACK_PATH = Path(__file__).resolve().parents[1] / "scripts" / "close_track.py"
MANAGE_SPECS_PATH = (
    Path(__file__).resolve().parents[2] / "spec-driver" / "scripts" / "manage_specs.py"
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


def setup_execution_ready_track(tmp_path, monkeypatch, include_tasks=True):
    manage_specs = load_module(MANAGE_SPECS_PATH, "manage_specs")
    monkeypatch.chdir(tmp_path)

    assert run_cli(manage_specs, monkeypatch, "init", "tracks") == 0
    assert run_cli(manage_specs, monkeypatch, "add", "DEMO", "Demo Feature") == 0

    track_dir = tmp_path / "tracks" / "DEMO-demo-feature"
    (track_dir / "spec.md").write_text(
        "# Task Specification: Demo Feature\n\n"
        "## 3. Functional Requirements\n\n"
        "- **FR-001**: System MUST store a summary entry.\n"
        "- **FR-002**: System MUST preserve backlinks.\n\n"
        "## 7. Success Criteria\n\n"
        "- **SC-001**: Teams can discover closed tracks quickly.\n",
        encoding="utf-8",
    )
    (track_dir / "checklists").mkdir()
    (track_dir / "checklists" / "requirements.md").write_text(
        "- [x] FR-001 requirements captured\n- [x] FR-002 requirements captured\n",
        encoding="utf-8",
    )
    assert run_cli(manage_specs, monkeypatch, "set-status", "DEMO", "spec_ready") == 0

    (track_dir / "plan.md").write_text(
        "# Implementation Plan: Demo Feature\n\n"
        "### Packet P01: Demo Packet\n\n"
        "- Validation:\n"
        "  - [ ] V001 Run demo integration test\n"
        "  - [ ] V002 Confirm rollback behavior\n\n"
        "### Verification Scenarios\n\n"
        "- Happy path: User can see published history entry\n"
        "- Regression checks: Existing track artifacts remain in place\n",
        encoding="utf-8",
    )
    if include_tasks:
        (track_dir / "tasks.md").write_text(
            "# Tasks: Demo Feature\n\n"
            "## 1. Execution Strategy\n\n"
            "- Validation approach: Run focused tests before closing the track\n\n"
            "## 7. Exit Criteria\n\n"
            "- [ ] Validation work is represented where required\n"
            "- [ ] The implementation agent can begin without major replanning\n",
            encoding="utf-8",
        )
    assert run_cli(manage_specs, monkeypatch, "set-status", "DEMO", "plan_ready") == 0
    assert run_cli(manage_specs, monkeypatch, "set-status", "DEMO", "execution_ready") == 0
    return manage_specs, track_dir


def test_close_track_publishes_to_explicit_file(tmp_path, monkeypatch):
    close_track = load_module(CLOSE_TRACK_PATH, "close_track")
    _, track_dir = setup_execution_ready_track(tmp_path, monkeypatch)

    assert (
        run_cli(
            close_track,
            monkeypatch,
            "--track",
            "DEMO",
            "--publish",
            "docs/spec-history.md",
        )
        == 0
    )

    target = tmp_path / "docs" / "spec-history.md"
    metadata = json.loads((track_dir / ".track-meta.json").read_text(encoding="utf-8"))
    content = target.read_text(encoding="utf-8")

    assert "### " in content
    assert "Demo Feature (`DEMO`)" in content
    assert "Functional requirements snapshot" in content
    assert "`tracks/DEMO-demo-feature/spec.md`" in content
    assert "Implementation verification snapshot" in content
    assert "Run demo integration test" in content
    assert metadata["status"] == "closed"
    assert metadata["publications"][0]["target_file"] == "docs/spec-history.md"


def test_close_track_uses_config_when_publish_target_not_passed(tmp_path, monkeypatch):
    close_track = load_module(CLOSE_TRACK_PATH, "close_track")
    _, track_dir = setup_execution_ready_track(tmp_path, monkeypatch)

    plugins_dir = tmp_path / ".skills" / "plugins"
    plugins_dir.mkdir(parents=True)
    (plugins_dir / "spec-publish.json").write_text(
        json.dumps(
            {
                "target_file": "docs/history.md",
                "document_title": "Team Spec History",
                "section_title": "Published Tracks",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    assert run_cli(close_track, monkeypatch, "--track", "DEMO") == 0

    target = tmp_path / "docs" / "history.md"
    content = target.read_text(encoding="utf-8")
    metadata = json.loads((track_dir / ".track-meta.json").read_text(encoding="utf-8"))

    assert content.startswith("# Team Spec History")
    assert "## Published Tracks" in content
    assert "Run focused tests before closing the track" in content
    assert metadata["publications"][0]["target_file"] == "docs/history.md"


def test_close_track_publishes_without_legacy_tasks_md(tmp_path, monkeypatch):
    close_track = load_module(CLOSE_TRACK_PATH, "close_track")
    _, track_dir = setup_execution_ready_track(tmp_path, monkeypatch, include_tasks=False)

    assert (
        run_cli(
            close_track,
            monkeypatch,
            "--track",
            "DEMO",
            "--publish",
            "docs/spec-history.md",
        )
        == 0
    )

    content = (tmp_path / "docs" / "spec-history.md").read_text(encoding="utf-8")
    metadata = json.loads((track_dir / ".track-meta.json").read_text(encoding="utf-8"))

    assert "Demo Feature (`DEMO`)" in content
    assert "Implementation verification snapshot" in content
    assert "User can see published history entry" in content
    assert metadata["status"] == "closed"


def test_close_track_renders_issue_link_when_identity_config_exists(tmp_path, monkeypatch):
    close_track = load_module(CLOSE_TRACK_PATH, "close_track")
    _, track_dir = setup_execution_ready_track(tmp_path, monkeypatch)

    identity_dir = tmp_path / ".skills"
    identity_dir.mkdir(parents=True, exist_ok=True)
    (identity_dir / "identity.json").write_text(
        json.dumps(
            {"issue_url_template": "https://tracker.example.com/issues/{ID}"}
        )
        + "\n",
        encoding="utf-8",
    )

    metadata = json.loads((track_dir / ".track-meta.json").read_text(encoding="utf-8"))
    metadata["issue"] = {
        "id": "BNC-123",
        "title": "Demo source issue",
        "status": "Done",
    }
    (track_dir / ".track-meta.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )

    assert (
        run_cli(
            close_track,
            monkeypatch,
            "--track",
            "DEMO",
            "--publish",
            "docs/spec-history.md",
        )
        == 0
    )

    content = (tmp_path / "docs" / "spec-history.md").read_text(encoding="utf-8")
    assert (
        "[BNC-123](https://tracker.example.com/issues/BNC-123) — Demo source issue; status: Done"
        in content
    )


def test_close_track_republishes_without_duplicate_markers(tmp_path, monkeypatch):
    close_track = load_module(CLOSE_TRACK_PATH, "close_track")
    _, track_dir = setup_execution_ready_track(tmp_path, monkeypatch)

    assert (
        run_cli(
            close_track,
            monkeypatch,
            "--track",
            "DEMO",
            "--publish",
            "docs/spec-history.md",
        )
        == 0
    )

    (track_dir / "spec.md").write_text(
        "# Task Specification: Demo Feature\n\n"
        "## 3. Functional Requirements\n\n"
        "- **FR-001**: Updated summary text.\n\n"
        "## 7. Success Criteria\n\n"
        "- **SC-001**: Updated criterion.\n",
        encoding="utf-8",
    )

    assert (
        run_cli(
            close_track,
            monkeypatch,
            "--track",
            "DEMO",
            "--publish",
            "docs/spec-history.md",
        )
        == 0
    )

    content = (tmp_path / "docs" / "spec-history.md").read_text(encoding="utf-8")
    assert content.count("<!-- spec-publish:DEMO:start -->") == 1
    assert "Updated summary text." in content


def test_close_track_requires_confirm_impact_for_relations(tmp_path, monkeypatch, capsys):
    close_track = load_module(CLOSE_TRACK_PATH, "close_track")
    manage_specs, _ = setup_execution_ready_track(tmp_path, monkeypatch)

    assert run_cli(manage_specs, monkeypatch, "add", "OLD", "Old Feature") == 0

    exit_code = run_cli(
        close_track,
        monkeypatch,
        "--track",
        "DEMO",
        "--relate",
        "supersedes",
        "OLD",
    )
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "--confirm-impact" in captured.err


def test_close_track_records_relations_and_publishes_them(tmp_path, monkeypatch):
    close_track = load_module(CLOSE_TRACK_PATH, "close_track")
    manage_specs, track_dir = setup_execution_ready_track(tmp_path, monkeypatch)

    assert run_cli(manage_specs, monkeypatch, "add", "OLD", "Old Feature") == 0

    assert (
        run_cli(
            close_track,
            monkeypatch,
            "--track",
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
            "docs/spec-history.md",
        )
        == 0
    )

    content = (tmp_path / "docs" / "spec-history.md").read_text(encoding="utf-8")
    source_meta = json.loads((track_dir / ".track-meta.json").read_text(encoding="utf-8"))
    target_meta = json.loads(
        (tmp_path / "tracks" / "OLD-old-feature" / ".track-meta.json").read_text(
            encoding="utf-8"
        )
    )

    assert "Spec relations:" in content
    assert "supersedes `OLD` (story: Story 2 - Legacy checkout; requirements: FR-002; selector: legacy checkout path)" in content
    assert source_meta["relations"][0]["type"] == "supersedes"
    assert target_meta["relations"][0]["type"] == "superseded_by"
