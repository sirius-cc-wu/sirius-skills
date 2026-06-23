from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
LIB_DIR = REPO_ROOT / "lib"
for path in (SRC_DIR, LIB_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from sirius_skills.commands import close_slice


def test_package_close_slice_reuses_helper_behaviors() -> None:
    assert close_slice.dedupe_preserve_order(["FR-1", "FR-1", "FR-2"]) == [
        "FR-1",
        "FR-2",
    ]
    assert close_slice.normalize_list_item("- [x] done") == "done"
    assert close_slice.normalize_list_item("plain text") is None


def test_package_close_slice_reports_missing_active_slice(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    result = close_slice.main([])

    captured = capsys.readouterr()
    assert result == 2
    assert "Slice config not found" in captured.err or "No active slice found." in captured.err
