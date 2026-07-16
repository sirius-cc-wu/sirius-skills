from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
LIB_DIR = REPO_ROOT / "lib"
for path in (SRC_DIR, LIB_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from sirius_skills.commands import bootstrap


def test_package_bootstrap_reuses_helper_behaviors() -> None:
    assert bootstrap.derive_wiki_dir("docs/features") == "docs/wiki"
    assert bootstrap.derive_wiki_dir("features") == "wiki"
    assert bootstrap.build_planning_config({}, None, None, None)["planning_dir"] == "docs/features"


def test_package_bootstrap_writes_default_config(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    result = bootstrap.main(["--mode", "default"])

    assert result == 0
    planning = json.loads(
        (tmp_path / ".skills" / "planning.json").read_text(encoding="utf-8")
    )
    execution = json.loads(
        (tmp_path / ".skills" / "execution.json").read_text(encoding="utf-8")
    )
    assert planning["planning_dir"] == "docs/features"
    assert "slice_dir" not in execution
    assert execution["preferred_workflow"] == "TDD"
