from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
LIB_DIR = REPO_ROOT / "lib"
for path in (SRC_DIR, LIB_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from sirius_skills.commands import archive_artifacts


def test_package_archive_render_text_reports_candidates() -> None:
    rendered = archive_artifacts.render_text(
        {
            "summary": {
                "candidate_count": 1,
                "archivable_count": 1,
            },
            "candidates": [
                {
                    "artifact_type": "slice",
                    "artifact_id": "CHK-101",
                    "status": "closed",
                    "path": "slices/CHK-101-checkout",
                    "archivable": True,
                }
            ],
            "applied": None,
        }
    )

    assert "Archive candidates: 1" in rendered
    assert "Directly archivable now: 1" in rendered
    assert "slice:CHK-101 [closed archivable]" in rendered


def test_package_archive_unsupported_apply_returns_usage_error(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    result = archive_artifacts.main(
        [
            "--artifact-type",
            "proposal",
            "--artifact-id",
            "missing-proposal",
            "--apply",
        ]
    )

    captured = capsys.readouterr()
    assert result == archive_artifacts.ERROR_EXIT_CODE
    assert "requires --artifact-type slice, feature, or subfeature" in captured.err
