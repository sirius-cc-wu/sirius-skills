from __future__ import annotations

import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
LIB_DIR = REPO_ROOT / "lib"
for path in (SRC_DIR, LIB_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from sirius_skills.commands import migrate_subfeatures


def test_package_migrate_subfeatures_reuses_helper_behaviors() -> None:
    assert migrate_subfeatures.normalize_optional_string("  Retire   legacy  ") == "Retire legacy"
    assert migrate_subfeatures.normalize_string_list(["CHK-01", "CHK-01"], "Stories") == ["CHK-01"]
    assert migrate_subfeatures.normalize_legacy_status("review-ready") == "reviewed"
    assert migrate_subfeatures.map_legacy_status("closed") == "finalized"


def test_package_migrate_subfeatures_rejects_invalid_legacy_status() -> None:
    with pytest.raises(RuntimeError, match="Unsupported legacy change status"):
        migrate_subfeatures.normalize_legacy_status("unknown")


def test_package_migrate_subfeatures_requires_exactly_one_target(capsys) -> None:
    result = migrate_subfeatures.main(["scan"])

    captured = capsys.readouterr()
    assert result == 2
    assert "Specify exactly one target: a feature or --all." in captured.err
