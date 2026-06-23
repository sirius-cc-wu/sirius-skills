from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
LIB_DIR = REPO_ROOT / "lib"
for path in (SRC_DIR, LIB_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from sirius_skills.commands import record_review


def test_package_record_review_detects_subfeature_target(tmp_path: Path) -> None:
    feature_dir = tmp_path / "docs" / "features" / "checkout"
    subfeature_dir = feature_dir / "subfeatures" / "replace-legacy-flow"
    subfeature_dir.mkdir(parents=True)
    (subfeature_dir / ".subfeature-meta.json").write_text("{}\n", encoding="utf-8")

    assert record_review.is_subfeature_target(subfeature_dir) is True
    assert record_review.is_subfeature_target(feature_dir) is False


def test_package_record_review_missing_target_returns_usage_error(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    result = record_review.main(
        ["missing-target", "--review-note", "Ready for approval"]
    )

    captured = capsys.readouterr()
    assert result == 2
    assert "Planning target not found: missing-target" in captured.err
