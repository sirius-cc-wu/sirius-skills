from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
LIB_DIR = REPO_ROOT / "lib"
for path in (SRC_DIR, LIB_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from sirius_skills.commands import scaffold_design


def test_package_scaffold_design_reuses_helper_behaviors(tmp_path: Path) -> None:
    stories_path = tmp_path / "user-stories.md"
    stories_path.write_text(
        "# Stories\n\n- **CHK-01 (M)**: Update checkout.\n- **CHK-02**: Confirm checkout.\n",
        encoding="utf-8",
    )

    assert scaffold_design.title_from_slug("replace-legacy_flow") == "Replace Legacy Flow"
    assert scaffold_design.collect_story_ids(tmp_path, None) == ["CHK-01", "CHK-02"]
    assert (
        scaffold_design.render_story_list([])
        == "- `TBD`: replace this placeholder with the stories the design directly serves."
    )


def test_package_scaffold_design_requires_known_target(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    result = scaffold_design.main(["missing-target"])

    captured = capsys.readouterr()
    assert result == 2
    assert "Planning target not found: missing-target" in captured.err
