from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
LIB_DIR = REPO_ROOT / "lib"
for path in (SRC_DIR, LIB_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from sirius_skills.commands import bootstrap, migrate_slices


def test_package_migrate_slices_requires_exactly_one_target(capsys) -> None:
    result = migrate_slices.main(["scan"])

    captured = capsys.readouterr()
    assert result == 2
    assert "Specify exactly one target: a feature or --all." in captured.err


def test_package_migrate_slices_moves_active_and_archived_slices(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    assert bootstrap.main(["--mode", "default"]) == 0

    from sirius_skills.commands import manage_execution, manage_planning

    _, created = manage_planning.create_feature("checkout")
    assert created is True

    active_folder, created = manage_execution.create_slice("SPC-001", "checkout")
    assert created is True

    archived_folder, created = manage_execution.create_slice("SPC-002", "checkout")
    assert created is True

    rows = manage_execution.parse_registry()
    archived_row = manage_execution.resolve_slice(rows, archived_folder)
    assert archived_row is not None
    ok, message = manage_execution.update_slice_status(rows, archived_row, "closed", force=True)
    assert ok, message

    rows = manage_execution.parse_registry()
    archived_row = manage_execution.resolve_slice(rows, archived_folder)
    assert archived_row is not None
    ok, message, archived_row = manage_execution.archive_slice(rows, archived_row)
    assert ok, message
    assert archived_row["path"].startswith("slices/.archived/")

    assert migrate_slices.main(["migrate", "--all"]) == 0

    feature_slice_root = tmp_path / "docs" / "features" / "checkout" / "slices"
    assert (feature_slice_root / active_folder).exists()
    assert (feature_slice_root / ".archived" / archived_folder).exists()
    assert (tmp_path / "docs" / "features" / "checkout" / ".skills" / "planning.json").exists()
    assert (tmp_path / "docs" / "features" / "checkout" / ".skills" / "execution.json").exists()

    feature_registry = json.loads((feature_slice_root / "registry.json").read_text(encoding="utf-8"))
    assert feature_registry["version"] == 1
    assert len(feature_registry["slices"]) == 2
    assert {row["id"] for row in feature_registry["slices"]} == {"SPC-001", "SPC-002"}
    archived_rows = [row for row in feature_registry["slices"] if row["path"].startswith("slices/.archived/")]
    assert len(archived_rows) == 1
    assert archived_rows[0]["id"] == "SPC-002"

    root_registry = json.loads((tmp_path / "slices" / "registry.json").read_text(encoding="utf-8"))
    assert root_registry["slices"] == []


def test_package_migrate_slices_scan_does_not_create_feature_scope(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    assert bootstrap.main(["--mode", "default"]) == 0

    from sirius_skills.commands import manage_execution, manage_planning

    _, created = manage_planning.create_feature("checkout")
    assert created is True

    _, created = manage_execution.create_slice("SPC-001", "checkout")
    assert created is True

    assert migrate_slices.main(["scan", "--all"]) == 0
    capsys.readouterr()

    assert not (tmp_path / "docs" / "features" / "checkout" / ".skills").exists()
