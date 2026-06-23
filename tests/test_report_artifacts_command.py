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

from sirius_skills.commands import report_artifacts


def test_package_report_render_text_includes_metrics_and_consolidation() -> None:
    rendered = report_artifacts.render_text(
        {
            "group_by": "overview",
            "stale_days": 30,
            "check_packaged_parity": False,
            "summary": {
                "total": 1,
                "stale": 0,
                "semantic_preview_count": 0,
            },
            "groups": [
                {
                    "key": "feature",
                    "count": 1,
                    "stale": 0,
                }
            ],
            "records": [
                {
                    "artifact_type": "feature",
                    "artifact_id": "checkout",
                    "status": "implemented",
                    "path": "docs/features/checkout/",
                    "parent_feature": None,
                    "is_stale": False,
                    "implementation_metrics": {
                        "execution_mode": "guided",
                        "story_size": {"sum_points": 3},
                        "slices": {"planned_count": 2},
                    },
                    "consolidation": {
                        "disposition": "narrowing",
                        "targets": [{"kind": "subfeature"}],
                        "historical_artifacts": ["docs/features/checkout/discover.md"],
                    },
                }
            ],
            "installed_parity": [],
            "semantic_preview": [],
        }
    )

    assert "Artifact report (overview, stale threshold: 30 days)" in rendered
    assert "metrics mode=guided, size=3, planned_slices=2" in rendered
    assert "consolidation=narrowing" in rendered


def test_package_report_rejects_non_positive_stale_days() -> None:
    with pytest.raises(SystemExit) as exc_info:
        report_artifacts.parse_args(["--stale-days", "0"])

    assert exc_info.value.code == 2
