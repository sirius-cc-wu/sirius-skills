import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "bootstrap_slice.py"


def load_module():
    spec = importlib.util.spec_from_file_location("bootstrap_slice", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_cli(module, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["bootstrap_slice.py", *args])
    return module.main()


def write_scope_config(scope_root: Path, filename: str, data: dict):
    skills_dir = scope_root / ".skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    (skills_dir / filename).write_text(json.dumps(data) + "\n", encoding="utf-8")


def test_bootstrap_initializes_default_execution_registry(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "DEMO", "Demo Feature") == 0

    execution = json.loads(
        (tmp_path / ".skills" / "execution.json").read_text(encoding="utf-8")
    )
    registry = json.loads((tmp_path / "slices" / "registry.json").read_text(encoding="utf-8"))
    metadata = json.loads(
        (tmp_path / "slices" / "DEMO-demo-feature" / ".slice-meta.json").read_text(
            encoding="utf-8"
        )
    )

    assert execution == {
        "slice_dir": "slices",
        "preferred_workflow": "TDD",
        "auto_start_implementation": True,
    }
    assert registry["slices"][0]["id"] == "DEMO"
    assert metadata["status"] == "draft"


def test_bootstrap_uses_explicit_slice_dir_when_config_missing(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    assert (
        run_cli(
            module,
            monkeypatch,
            "--slice-dir",
            "work/slices",
            "DEMO",
            "Demo Feature",
        )
        == 0
    )

    execution = json.loads(
        (tmp_path / ".skills" / "execution.json").read_text(encoding="utf-8")
    )
    assert execution["slice_dir"] == "work/slices"
    assert (tmp_path / "work" / "slices" / "DEMO-demo-feature").exists()


def test_bootstrap_reuses_existing_execution_config_and_deduplicates(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    skills_dir = tmp_path / ".skills"
    skills_dir.mkdir()
    (skills_dir / "execution.json").write_text(
        json.dumps({"slice_dir": "custom-slices", "preferred_workflow": "BDD"}) + "\n",
        encoding="utf-8",
    )

    assert run_cli(module, monkeypatch, "DEMO", "Demo Feature") == 0
    assert run_cli(module, monkeypatch, "DEMO", "Demo Feature") == 0

    registry = json.loads(
        (tmp_path / "custom-slices" / "registry.json").read_text(encoding="utf-8")
    )
    execution = json.loads(
        (tmp_path / ".skills" / "execution.json").read_text(encoding="utf-8")
    )

    assert len(registry["slices"]) == 1
    assert registry["slices"][0]["id"] == "DEMO"
    assert execution == {"slice_dir": "custom-slices", "preferred_workflow": "BDD"}


def test_bootstrap_uses_child_scope_registry_with_inherited_execution_config(
    tmp_path, monkeypatch
):
    module = load_module()
    (tmp_path / ".git").mkdir()
    write_scope_config(
        tmp_path,
        "planning.json",
        {"planning_dir": "docs/features", "proposal_dir": "docs/proposals"},
    )
    write_scope_config(
        tmp_path,
        "execution.json",
        {"slice_dir": "team-slices", "preferred_workflow": "BDD"},
    )

    child_scope = tmp_path / "apps" / "payments"
    write_scope_config(child_scope, "planning.json", {})

    monkeypatch.chdir(child_scope)
    assert run_cli(module, monkeypatch, "DEMO", "Demo Feature") == 0

    registry = json.loads(
        (child_scope / "team-slices" / "registry.json").read_text(encoding="utf-8")
    )

    assert registry["slices"][0]["id"] == "DEMO"
    assert (child_scope / "team-slices" / "DEMO-demo-feature" / ".slice-meta.json").exists()
    assert not (child_scope / ".skills" / "execution.json").exists()
    assert not (tmp_path / "team-slices" / "DEMO-demo-feature").exists()
