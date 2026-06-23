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

from sirius_skills.commands import bootstrap_slice


def test_package_bootstrap_slice_creates_default_slice(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)

    result = bootstrap_slice.main(["DEMO", "Demo Feature"])

    assert result == 0
    metadata = json.loads(
        (tmp_path / "slices" / "DEMO-demo-feature" / ".slice-meta.json").read_text(
            encoding="utf-8"
        )
    )
    assert metadata["slice_id"] == "DEMO"
    assert metadata["feature"] == "Demo Feature"


def test_package_bootstrap_slice_rejects_empty_feature_name(capsys) -> None:
    result = bootstrap_slice.main(["DEMO", "   "])

    captured = capsys.readouterr()
    assert result == 2
    assert "Feature name cannot be empty." in captured.err
