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

from sirius_skills.commands import repair_artifacts


def test_package_repair_render_text_reports_actions() -> None:
    rendered = repair_artifacts.render_text(
        {
            "apply": False,
            "summary": {
                "planned_actions": 1,
                "applied_actions": 0,
                "skipped_artifacts": 0,
                "semantic_preview_count": 1,
            },
            "actions": [
                {
                    "artifact_type": "slice",
                    "owner_id": None,
                    "changed": True,
                    "applied": False,
                    "current_count": 0,
                    "rebuilt_count": 1,
                }
            ],
            "skipped": [],
            "semantic_preview": [
                {
                    "artifact_type": "feature",
                    "artifact_id": "checkout",
                    "code": "repair_planning_status_handoff",
                    "message": "Feature status can be repaired.",
                }
            ],
        }
    )

    assert "Artifact repair (dry-run)" in rendered
    assert "- slice: changed, 0 -> 1 rows" in rendered
    assert "Semantic preview:" in rendered
    assert "repair_planning_status_handoff" in rendered


def test_package_repair_json_runs_for_empty_repo(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    result = repair_artifacts.main(["--artifact-type", "slice", "--json"])

    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["ok"] is True
    assert payload["summary"]["planned_actions"] == 0
    assert payload["actions"][0]["artifact_type"] == "slice"
    assert payload["actions"][0]["changed"] is False
