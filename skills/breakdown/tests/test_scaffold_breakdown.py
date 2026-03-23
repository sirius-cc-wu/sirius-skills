import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "scaffold_breakdown.py"


def load_module():
    spec = importlib.util.spec_from_file_location("scaffold_breakdown", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_cli(module, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["scaffold_breakdown.py", *args])
    return module.main()


def test_scaffold_defaults_to_docs_features(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "demo-feature") == 0

    target_dir = tmp_path / "docs" / "features" / "demo-feature"
    assert (target_dir / "task-planning.md").exists()
    assert (target_dir / "task-traceability.md").exists()


def test_scaffold_uses_planning_config_dir(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    config_dir = tmp_path / ".skills"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "planning.json").write_text(
        json.dumps({"planning_dir": "planning/features"}) + "\n",
        encoding="utf-8",
    )

    assert run_cli(module, monkeypatch, "demo-feature") == 0

    target_dir = tmp_path / "planning" / "features" / "demo-feature"
    assert (target_dir / "task-planning.md").exists()
    assert (target_dir / "task-traceability.md").exists()


def test_scaffold_base_dir_flag_overrides_planning_config_dir(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    config_dir = tmp_path / ".skills"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "planning.json").write_text(
        json.dumps({"planning_dir": "planning/features"}) + "\n",
        encoding="utf-8",
    )

    assert (
        run_cli(module, monkeypatch, "demo-feature", "--base-dir", "custom/planning")
        == 0
    )

    assert (tmp_path / "custom" / "planning" / "demo-feature" / "task-planning.md").exists()
    assert not (tmp_path / "planning" / "features" / "demo-feature").exists()


def test_scaffold_rejects_non_string_planning_config_dir(tmp_path, monkeypatch, capsys):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    config_dir = tmp_path / ".skills"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "planning.json").write_text(
        json.dumps({"planning_dir": 123}) + "\n",
        encoding="utf-8",
    )

    assert run_cli(module, monkeypatch, "demo-feature") == 1

    captured = capsys.readouterr()
    assert "Planning config field 'planning_dir' must be a string." in captured.err


def test_scaffold_ignores_identity_planning_dir(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    config_dir = tmp_path / ".skills"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "identity.json").write_text(
        json.dumps({"planning_dir": "legacy/features"}) + "\n",
        encoding="utf-8",
    )

    assert run_cli(module, monkeypatch, "demo-feature") == 0

    assert (tmp_path / "docs" / "features" / "demo-feature" / "task-planning.md").exists()
    assert not (tmp_path / "legacy" / "features" / "demo-feature").exists()
