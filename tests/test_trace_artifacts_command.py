from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
LIB_DIR = REPO_ROOT / "lib"
for path in (SRC_DIR, LIB_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from sirius_skills.commands import trace_artifacts


def test_package_trace_render_text_reports_nodes_and_edges() -> None:
    rendered = trace_artifacts.render_text(
        {
            "summary": {
                "node_counts": {
                    "feature": 1,
                    "slice": 1,
                },
                "edge_counts": {
                    "bootstrapped_as": 1,
                },
            },
            "nodes": [
                {
                    "artifact_type": "feature",
                    "artifact_id": "checkout",
                    "path": "docs/features/checkout/",
                    "details": {
                        "consolidation": {
                            "disposition": "narrowing",
                            "targets": [{"kind": "subfeature"}],
                            "historical_artifacts": ["docs/features/checkout/discover.md"],
                        }
                    },
                }
            ],
            "edges": [
                {
                    "source_type": "feature",
                    "source_id": "checkout",
                    "target_type": "slice",
                    "target_id": "CHK-101",
                    "relation": "bootstrapped_as",
                    "details": {"target_ref": "slices/CHK-101-checkout/"},
                }
            ],
        }
    )

    assert "Lineage summary" in rendered
    assert "- feature: 1" in rendered
    assert "feature:checkout" in rendered
    assert "consolidation=narrowing" in rendered
    assert "feature:checkout -[bootstrapped_as]-> slice:CHK-101" in rendered


def test_package_trace_missing_target_returns_usage_error(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    result = trace_artifacts.main(
        ["--artifact-type", "planned-slice", "--artifact-id", "MISSING-1"]
    )

    captured = capsys.readouterr()
    assert result == trace_artifacts.ERROR_EXIT_CODE
    assert "Artifact not found: planned-slice:MISSING-1" in captured.err
