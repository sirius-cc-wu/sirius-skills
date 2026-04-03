import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "bootstrap.py"


def load_module():
    spec = importlib.util.spec_from_file_location("bootstrap", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_cli(module, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["bootstrap.py", *args])
    return module.main()


def write_scope_config(scope_root: Path, filename: str, data: dict):
    skills_dir = scope_root / ".skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    (skills_dir / filename).write_text(json.dumps(data) + "\n", encoding="utf-8")


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

    assert planning == {
        "planning_dir": "docs/features",
        "proposal_dir": "docs/proposals",
        "design_diagram_mode": "embedded",
    }
    assert execution == {
        "slice_dir": "slices",
        "preferred_workflow": "TDD",
        "auto_start_implementation": True,
    }
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


def test_bootstrap_writes_custom_design_diagram_mode(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    assert (
        run_cli(
            module,
            monkeypatch,
            "--mode",
            "default",
            "--design-diagram-mode",
            "linked_svg",
        )
        == 0
    )

    planning = json.loads(
        (tmp_path / ".skills" / "planning.json").read_text(encoding="utf-8")
    )

    assert planning["design_diagram_mode"] == "linked_svg"


def test_bootstrap_preserves_unrelated_existing_planning_keys(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    skills_dir = tmp_path / ".skills"
    skills_dir.mkdir()
    (skills_dir / "planning.json").write_text(
        json.dumps({"custom_key": "keep-me"}) + "\n",
        encoding="utf-8",
    )

    assert run_cli(module, monkeypatch, "--mode", "default") == 0

    planning = json.loads((skills_dir / "planning.json").read_text(encoding="utf-8"))

    assert planning["custom_key"] == "keep-me"
    assert planning["planning_dir"] == "docs/features"
    assert planning["proposal_dir"] == "docs/proposals"
    assert planning["design_diagram_mode"] == "embedded"


def test_bootstrap_child_scope_inherits_parent_configs_before_applying_overrides(
    tmp_path, monkeypatch
):
    module = load_module()
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".git").mkdir()

    write_scope_config(
        tmp_path,
        "planning.json",
        {
            "planning_dir": "planning/features",
            "proposal_dir": "planning/proposals",
            "design_diagram_mode": "linked_svg",
            "custom_key": "keep-me",
        },
    )
    write_scope_config(
        tmp_path,
        "execution.json",
        {
            "slice_dir": "root-slices",
            "preferred_workflow": "BDD",
            "auto_start_implementation": False,
            "custom_exec": "keep-exec",
        },
    )
    write_scope_config(
        tmp_path,
        "conventions.json",
        {
            "commit_format": "{scope}: {summary}",
            "custom_conv": "keep-conv",
        },
    )

    child_scope = tmp_path / "apps" / "payments"
    child_scope.mkdir(parents=True)

    assert (
        run_cli(
            module,
            monkeypatch,
            "--mode",
            "default",
            "--repo-root",
            str(child_scope),
            "--slice-dir",
            "team-slices",
        )
        == 0
    )

    planning = json.loads(
        (child_scope / ".skills" / "planning.json").read_text(encoding="utf-8")
    )
    execution = json.loads(
        (child_scope / ".skills" / "execution.json").read_text(encoding="utf-8")
    )
    conventions = json.loads(
        (child_scope / ".skills" / "conventions.json").read_text(encoding="utf-8")
    )

    assert planning == {
        "planning_dir": "planning/features",
        "proposal_dir": "planning/proposals",
        "design_diagram_mode": "linked_svg",
        "custom_key": "keep-me",
    }
    assert execution == {
        "slice_dir": "team-slices",
        "preferred_workflow": "BDD",
        "auto_start_implementation": False,
        "custom_exec": "keep-exec",
    }
    assert conventions == {
        "commit_format": "{scope}: {summary}",
        "custom_conv": "keep-conv",
    }


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
