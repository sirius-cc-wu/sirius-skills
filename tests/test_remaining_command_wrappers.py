from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
LIB_DIR = REPO_ROOT / "lib"
for path in (SRC_DIR, LIB_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from sirius_skills import cli


def test_remaining_package_wrappers_show_help(capsys) -> None:
    commands = [
        "autoplan",
        "manage-execution",
        "manage-planning",
        "manage-proposals",
        "manage-subfeatures",
        "migrate-planning-model",
        "ship",
        "ship-slice",
        "ship-worktree",
    ]

    for command in commands:
        assert cli.main([command, "--help"]) == 0

    captured = capsys.readouterr()
    assert "usage:" in captured.out
