from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from sirius_skills.lib.workflow_state import (
    load_merged_config,
    resolve_scope_context,
    resolve_scope_path,
)
from sirius_skills.lib.workflow_state.storage import load_json_object, read_text, write_json_object, write_text


def write_scope_config(scope_root: Path, payload: dict[str, object]) -> None:
    skills_dir = scope_root / ".skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    (skills_dir / "planning.json").write_text(json.dumps(payload) + "\n", encoding="utf-8")


def init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init", "--quiet"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Copilot Test"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "copilot@example.test"], cwd=root, check=True)


def test_resolve_scope_context_prefers_nearest_planning_config_root(tmp_path: Path, monkeypatch) -> None:
    init_git_repo(tmp_path)
    write_scope_config(
        tmp_path,
        {"planning_dir": "docs/features", "proposal_dir": "docs/proposals"},
    )
    nested = tmp_path / "apps" / "payments"
    write_scope_config(
        nested,
        {"planning_dir": "planning/features", "proposal_dir": "planning/proposals"},
    )
    monkeypatch.chdir(nested)

    scope_context = resolve_scope_context()

    assert scope_context.repo_root == tmp_path
    assert scope_context.scope_root == nested.resolve()
    assert scope_context.planning_config_path == nested / ".skills" / "planning.json"
    assert load_merged_config(scope_context, "planning") == {
        "planning_dir": "planning/features",
        "proposal_dir": "planning/proposals",
    }
    assert resolve_scope_path(scope_context.scope_root, "docs/features") == str(
        nested / "docs" / "features"
    )


def test_resolve_scope_context_rejects_scope_outside_repo_root(tmp_path: Path, monkeypatch) -> None:
    init_git_repo(tmp_path)
    write_scope_config(
        tmp_path,
        {"planning_dir": "docs/features", "proposal_dir": "docs/proposals"},
    )
    outside = tmp_path.parent / "outside"
    outside.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError, match="outside repository root"):
        resolve_scope_context(explicit_scope=outside)


def test_scope_runtime_shim_reexports_library_module() -> None:
    legacy_scope_runtime = importlib.import_module("sirius_skills.commands.scope_runtime")
    library_scope_runtime = importlib.import_module("sirius_skills.lib.workflow_state.scope_runtime")

    assert legacy_scope_runtime.resolve_scope_context is library_scope_runtime.resolve_scope_context
    assert legacy_scope_runtime.ScopeContext is library_scope_runtime.ScopeContext
    assert legacy_scope_runtime.SCOPE_RUNTIME is library_scope_runtime.SCOPE_RUNTIME


def test_storage_helpers_round_trip_and_validate_json(tmp_path: Path) -> None:
    json_path = tmp_path / "state" / "payload.json"
    text_path = tmp_path / "state" / "notes.txt"

    write_json_object(json_path, {"alpha": 1, "nested": {"beta": True}})
    write_text(text_path, "hello\n")

    assert load_json_object(json_path, "Payload") == {"alpha": 1, "nested": {"beta": True}}
    assert read_text(text_path) == "hello\n"

    json_path.write_text("[]\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="Payload must be a JSON object"):
        load_json_object(json_path, "Payload")
