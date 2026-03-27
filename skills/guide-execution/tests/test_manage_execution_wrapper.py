import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "manage_execution.py"


def load_module():
    spec = importlib.util.spec_from_file_location("guide_manage_execution", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_cli(module, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["manage_execution.py", *args])
    return module.main()


def test_wrapper_runs_execution_init(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init") == 0

    config = json.loads((tmp_path / ".skills" / "execution.json").read_text(encoding="utf-8"))
    assert config["slice_dir"] == "slices"
