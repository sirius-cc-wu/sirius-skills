from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
LIB_DIR = REPO_ROOT / "lib"
for path in (SRC_DIR, LIB_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from sirius_skills.commands import research


def test_package_research_reuses_helper_behaviors() -> None:
    assert research.derive_wiki_dir_name("docs/features") == "docs/wiki"
    assert research.derive_wiki_dir_name("planning/features") == "planning/wiki"
    assert research.default_wiki_status(True) == "skipped"
    assert research.default_wiki_status(False) == "deferred"
    assert research.format_title("reference-research-patterns") == "Reference Research Patterns"


def test_package_research_requires_source(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    result = research.main(
        [
            "planning-workflow",
            "--question",
            "Which reference should be preferred?",
            "--chosen-reference",
            "references/OpenHarness/",
            "--decision",
            "Prefer OpenHarness.",
        ]
    )

    captured = capsys.readouterr()
    assert result == 2
    assert "At least one --source entry is required." in captured.err
