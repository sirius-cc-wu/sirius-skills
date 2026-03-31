import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "manage_planning.py"


def load_manage_planning_module():
    spec = importlib.util.spec_from_file_location("manage_planning", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_cli(module, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["manage_planning.py", *args])
    return module.main()


def write_file(path: Path, content: str = "# doc\n"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_init_defaults_to_docs_features_directory(tmp_path, monkeypatch):
    module = load_manage_planning_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init") == 0

    config = json.loads((tmp_path / ".skills" / "planning.json").read_text(encoding="utf-8"))
    registry = json.loads((tmp_path / "docs" / "features" / "registry.json").read_text(encoding="utf-8"))

    assert config["planning_dir"] == "docs/features"
    assert config["proposal_dir"] == "docs/proposals"
    assert config["design_diagram_mode"] == "embedded"
    assert registry["features"] == []


def test_init_preserves_existing_planning_config_keys(tmp_path, monkeypatch):
    module = load_manage_planning_module()
    monkeypatch.chdir(tmp_path)

    skills_dir = tmp_path / ".skills"
    skills_dir.mkdir()
    (skills_dir / "planning.json").write_text(
        json.dumps(
            {
                "planning_dir": "planning/features",
                "proposal_dir": "planning/proposals",
                "design_diagram_mode": "linked_svg",
                "custom_key": "keep-me",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    assert run_cli(module, monkeypatch, "init", "docs/features") == 0

    config = json.loads((skills_dir / "planning.json").read_text(encoding="utf-8"))

    assert config == {
        "planning_dir": "docs/features",
        "proposal_dir": "planning/proposals",
        "design_diagram_mode": "linked_svg",
        "custom_key": "keep-me",
    }


def test_add_creates_feature_metadata_and_registry_entries(tmp_path, monkeypatch):
    module = load_manage_planning_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init") == 0
    assert run_cli(module, monkeypatch, "add", "habit-tracker") == 0

    feature_dir = tmp_path / "docs" / "features" / "habit-tracker"
    metadata = json.loads((feature_dir / ".planning-meta.json").read_text(encoding="utf-8"))
    registry = json.loads((tmp_path / "docs" / "features" / "registry.json").read_text(encoding="utf-8"))

    assert metadata["feature_slug"] == "habit-tracker"
    assert metadata["status"] == "discovery_pending"
    assert metadata["requires_ui_flow"] is False
    assert registry["features"][0]["feature"] == "habit-tracker"


def test_discovery_ready_requires_discover_file(tmp_path, monkeypatch, capsys):
    module = load_manage_planning_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init") == 0
    assert run_cli(module, monkeypatch, "add", "habit-tracker") == 0

    exit_code = run_cli(module, monkeypatch, "set-status", "habit-tracker", "discovery_ready")
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Missing required file 'discover.md'." in captured.err


def test_ui_required_blocks_design_ready_without_ui_design(tmp_path, monkeypatch, capsys):
    module = load_manage_planning_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init") == 0
    assert run_cli(module, monkeypatch, "add", "habit-tracker", "--require-ui-flow") == 0

    feature_dir = tmp_path / "docs" / "features" / "habit-tracker"
    write_file(feature_dir / "discover.md")
    assert run_cli(module, monkeypatch, "set-status", "habit-tracker", "discovery_ready") == 0

    write_file(feature_dir / "system-design.md")
    exit_code = run_cli(module, monkeypatch, "set-status", "habit-tracker", "design_ready")
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Missing required file 'ui-design.md'." in captured.err


def test_slice_ready_requires_review_note_and_slice_ids(tmp_path, monkeypatch, capsys):
    module = load_manage_planning_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init") == 0
    assert run_cli(module, monkeypatch, "add", "habit-tracker") == 0

    feature_dir = tmp_path / "docs" / "features" / "habit-tracker"
    write_file(feature_dir / "discover.md")
    write_file(feature_dir / "system-design.md")
    write_file(feature_dir / "slice-planning.md")
    write_file(feature_dir / "slice-traceability.md")

    assert run_cli(module, monkeypatch, "set-status", "habit-tracker", "discovery_ready") == 0
    assert run_cli(module, monkeypatch, "set-status", "habit-tracker", "design_ready") == 0
    assert run_cli(module, monkeypatch, "set-status", "habit-tracker", "breakdown_ready") == 0

    exit_code = run_cli(module, monkeypatch, "set-status", "habit-tracker", "planning_reviewed")
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Planning review requires a non-empty review note." in captured.err

    assert (
        run_cli(
            module,
            monkeypatch,
            "set-status",
            "habit-tracker",
            "planning_reviewed",
            "--review-note",
            "Planning artifacts reviewed and ready for tracker bootstrap.",
        )
        == 0
    )

    exit_code = run_cli(module, monkeypatch, "set-status", "habit-tracker", "slice_ready")
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Slice readiness requires at least one ready slice ID." in captured.err

    assert (
        run_cli(
            module,
            monkeypatch,
            "set-status",
            "habit-tracker",
            "slice_ready",
            "--slice-id",
            "HAB-101",
        )
        == 0
    )

    metadata = json.loads((feature_dir / ".planning-meta.json").read_text(encoding="utf-8"))
    assert metadata["ready_slice_ids"] == ["HAB-101"]


def test_validate_feature_reports_success_for_ready_feature(tmp_path, monkeypatch):
    module = load_manage_planning_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init") == 0
    assert run_cli(module, monkeypatch, "add", "habit-tracker") == 0

    feature_dir = tmp_path / "docs" / "features" / "habit-tracker"
    write_file(feature_dir / "discover.md")
    write_file(feature_dir / "system-design.md")
    write_file(feature_dir / "slice-planning.md")
    write_file(feature_dir / "slice-traceability.md")

    assert run_cli(module, monkeypatch, "set-status", "habit-tracker", "discovery_ready") == 0
    assert run_cli(module, monkeypatch, "set-status", "habit-tracker", "design_ready") == 0
    assert run_cli(module, monkeypatch, "set-status", "habit-tracker", "breakdown_ready") == 0
    assert (
        run_cli(
            module,
            monkeypatch,
            "set-status",
            "habit-tracker",
            "planning_reviewed",
            "--review-note",
            "Reviewed for scope, sequencing, and validation readiness.",
        )
        == 0
    )
    assert (
        run_cli(
            module,
            monkeypatch,
            "set-status",
            "habit-tracker",
            "slice_ready",
            "--slice-id",
            "HAB-101",
        )
        == 0
    )

    monkeypatch.setattr(sys, "argv", ["manage_planning.py", "validate-feature", "habit-tracker"])
    exit_code = module.main()
    assert exit_code == 0
