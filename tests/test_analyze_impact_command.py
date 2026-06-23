from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
LIB_DIR = REPO_ROOT / "lib"
for path in (SRC_DIR, LIB_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from sirius_skills.commands import analyze_impact


def test_package_analyze_impact_reuses_helper_behaviors(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "docs" / "features" / "checkout" / "discover.md"

    assert analyze_impact.normalize_relpath(target) == "docs/features/checkout/discover.md"
    assert analyze_impact.dedupe([" CHK-01 ", "CHK-01", "", "CHK-02"]) == [
        "CHK-01",
        "CHK-02",
    ]
    assert analyze_impact.format_bullets(["CHK-01"], "none") == "- `CHK-01`"


def test_package_analyze_impact_missing_subfeature_returns_usage_error(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    result = analyze_impact.main(["checkout", "missing-subfeature"])

    captured = capsys.readouterr()
    assert result == 2
    assert "Canonical feature not found: checkout" in captured.err
