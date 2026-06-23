from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
LIB_DIR = REPO_ROOT / "lib"
for path in (SRC_DIR, LIB_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from sirius_skills.commands import measure_artifacts


def test_package_measure_render_text_matches_cli_shape() -> None:
    rendered = measure_artifacts.render_text(
        {
            "artifact_type": "feature",
            "artifact_id": "checkout",
            "status": "implemented",
            "execution_mode": "direct",
            "story_size": {
                "sum_points": 3,
                "unsupported_sizes": [],
            },
            "slices": {
                "planned_count": 1,
                "linked_slice_ids": [],
            },
            "implementation_churn": {
                "confidence": "unavailable",
                "total_changed_lines": None,
            },
        },
        sidecar_path="docs/features/checkout/implementation-metrics.json",
        wrote=False,
    )

    assert "Measurement target: feature checkout" in rendered
    assert "Execution mode: direct" in rendered
    assert "total changed lines: unavailable" in rendered
    assert "preview only" in rendered


def test_package_measure_missing_target_returns_usage_error(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    result = measure_artifacts.main(["missing-target"])

    captured = capsys.readouterr()
    assert result == measure_artifacts.ERROR_EXIT_CODE
    assert "Measurement target not found: missing-target" in captured.err
