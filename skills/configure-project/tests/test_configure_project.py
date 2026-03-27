import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "configure_project.py"


def load_module():
    spec = importlib.util.spec_from_file_location("configure_project", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_cli(module, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["configure_project.py", *args])
    return module.main()


def test_default_mode_writes_generic_config_files(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "--mode", "default") == 0

    planning = json.loads(
        (tmp_path / ".skills" / "planning.json").read_text(encoding="utf-8")
    )
    execution = json.loads(
        (tmp_path / ".skills" / "execution.json").read_text(encoding="utf-8")
    )
    conventions = json.loads(
        (tmp_path / ".skills" / "conventions.json").read_text(encoding="utf-8")
    )

    assert planning == {"planning_dir": "docs/features"}
    assert execution == {"slice_dir": "slices", "preferred_workflow": "TDD"}
    assert conventions == {}


def test_jira_mode_sets_jira_conventions_and_preserves_other_keys(
    tmp_path, monkeypatch
):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    skills_dir = tmp_path / ".skills"
    skills_dir.mkdir()
    (skills_dir / "conventions.json").write_text(
        json.dumps({"custom_key": "keep-me"}) + "\n",
        encoding="utf-8",
    )

    assert (
        run_cli(
            module,
            monkeypatch,
            "--mode",
            "jira",
            "--issue-url-template",
            "https://jira.acme.test/browse/{ID}",
        )
        == 0
    )

    conventions = json.loads(
        (skills_dir / "conventions.json").read_text(encoding="utf-8")
    )

    assert conventions["custom_key"] == "keep-me"
    assert conventions["issue_sliceer"] == "jira"
    assert conventions["id_pattern"] == r"^[A-Z][A-Z0-9]*-[0-9]+$"
    assert conventions["branch_extract_pattern"] == r"^([A-Z][A-Z0-9]*-[0-9]+)-(.+)$"
    assert conventions["commit_format"] == "{ID}: {summary}"
    assert conventions["pr_title_format"] == "{ID}: {summary}"
    assert conventions["issue_url_template"] == "https://jira.acme.test/browse/{ID}"


def test_default_mode_preserves_existing_conventions_file(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    skills_dir = tmp_path / ".skills"
    skills_dir.mkdir()
    (skills_dir / "conventions.json").write_text(
        json.dumps({"commit_format": "{scope}: {summary}"}) + "\n",
        encoding="utf-8",
    )

    assert run_cli(module, monkeypatch, "--mode", "default") == 0

    conventions = json.loads(
        (skills_dir / "conventions.json").read_text(encoding="utf-8")
    )
    assert conventions == {"commit_format": "{scope}: {summary}"}


def test_invalid_existing_json_returns_error(tmp_path, monkeypatch, capsys):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    skills_dir = tmp_path / ".skills"
    skills_dir.mkdir()
    (skills_dir / "planning.json").write_text("{bad json\n", encoding="utf-8")

    exit_code = run_cli(module, monkeypatch, "--mode", "default")
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Invalid JSON in" in captured.err
