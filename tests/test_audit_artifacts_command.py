from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
LIB_DIR = REPO_ROOT / "lib"
for path in (SRC_DIR, LIB_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from sirius_skills.commands import audit_artifacts


def test_package_audit_render_text_reports_success() -> None:
    assert audit_artifacts.render_text({"ok": True}) == "Audit passed: no findings."


def test_package_audit_render_text_reports_findings() -> None:
    rendered = audit_artifacts.render_text(
        {
            "ok": False,
            "summary": {
                "total": 1,
                "by_artifact_type": {"feature": 1},
            },
            "findings": [
                {
                    "artifact_type": "feature",
                    "artifact_id": "checkout",
                    "category": "validation",
                    "code": "missing_design",
                    "message": "system-design.md is missing.",
                    "path": "docs/features/checkout/",
                }
            ],
        }
    )

    assert "Audit found 1 finding(s)." in rendered
    assert "- feature: 1" in rendered
    assert "feature:checkout [validation/missing_design]" in rendered
