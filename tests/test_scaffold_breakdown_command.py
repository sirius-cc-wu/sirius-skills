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

from sirius_skills.commands import scaffold_breakdown


def test_package_scaffold_breakdown_reuses_helper_behaviors(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    assert scaffold_breakdown.validate_feature_slug("checkout-flow") == "checkout-flow"
    assert scaffold_breakdown.resolve_base_dir("docs/features") == tmp_path / "docs" / "features"
    assert scaffold_breakdown.format_code_list(["CHK-01"], "empty") == "- `CHK-01`"
    assert "- Feature: checkout" in scaffold_breakdown.render_slice_planning("checkout")


def test_package_scaffold_breakdown_rejects_invalid_slug() -> None:
    with pytest.raises(ValueError, match="path separators"):
        scaffold_breakdown.validate_feature_slug("checkout/flow")


def test_package_scaffold_breakdown_creates_default_files(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    result = scaffold_breakdown.main(["checkout"])

    assert result == 0
    assert (tmp_path / "docs" / "features" / "checkout" / "slice-planning.md").exists()
    assert (tmp_path / "docs" / "features" / "checkout" / "slice-traceability.md").exists()
