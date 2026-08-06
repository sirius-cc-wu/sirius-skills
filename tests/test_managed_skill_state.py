from __future__ import annotations

import json
from pathlib import Path

import pytest

from sirius_skills.commands import manage_installed_skills


REPO_ROOT = Path(__file__).resolve().parents[1]


def write_ledger(path: Path) -> None:
    path.write_text(
        "# skill<TAB>retired revision\n"
        "design\t36f7542d39225e1160c3a4b36c76dfd067fd0281\n"
        "old-workflow\t3b78f0001ca391e321f52f5ebbd8043c7762f2ac\n",
        encoding="utf-8",
    )


def test_select_retired_skills_removes_only_owned_names_by_default(
    tmp_path: Path,
) -> None:
    ledger_path = tmp_path / "retired-skills.tsv"
    state_path = tmp_path / "managed-skills.txt"
    write_ledger(ledger_path)
    state_path.write_text("old-workflow\ncurrent-skill\n", encoding="utf-8")
    installed_json = json.dumps(
        [
            {"name": "design"},
            {"name": "old-workflow"},
            {"name": "external:skill"},
            {"name": "unrelated"},
        ]
    )

    selected, unowned = manage_installed_skills.select_retired_skills(
        installed_json,
        ledger_path=ledger_path,
        state_path=state_path,
    )

    assert selected == ["old-workflow"]
    assert unowned == ["design"]


def test_select_retired_skills_can_include_unowned_legacy_candidates(
    tmp_path: Path,
) -> None:
    ledger_path = tmp_path / "retired-skills.tsv"
    write_ledger(ledger_path)

    selected, unowned = manage_installed_skills.select_retired_skills(
        json.dumps([{"name": "design"}, {"name": "old-workflow"}]),
        ledger_path=ledger_path,
        state_path=tmp_path / "missing-state.txt",
        include_unowned=True,
    )

    assert selected == ["design", "old-workflow"]
    assert unowned == []


def test_record_install_and_removal_maintain_host_local_ownership(
    tmp_path: Path,
) -> None:
    state_path = tmp_path / "state" / "managed-skills.txt"
    profile_path = tmp_path / "profile.txt"
    profile_path.write_text("# selected profile\ncommit\nsimplify\n", encoding="utf-8")

    manage_installed_skills.record_installed(profile_path, state_path)
    manage_installed_skills.record_names(["another-skill"], state_path)
    manage_installed_skills.forget_names(["simplify"], state_path)

    assert state_path.read_text(encoding="utf-8") == "another-skill\ncommit\n"


def test_forget_retired_cleans_stale_ownership_entries(tmp_path: Path) -> None:
    ledger_path = tmp_path / "retired-skills.tsv"
    state_path = tmp_path / "managed-skills.txt"
    write_ledger(ledger_path)
    state_path.write_text("current-skill\ndesign\nold-workflow\n", encoding="utf-8")

    manage_installed_skills.forget_retired(ledger_path, state_path)

    assert state_path.read_text(encoding="utf-8") == "current-skill\n"


@pytest.mark.parametrize(
    "line",
    [
        "Bad_Name\t36f7542d39225e1160c3a4b36c76dfd067fd0281\n",
        "design\tnot-a-revision\n",
        "design\t36f7542d39225e1160c3a4b36c76dfd067fd0281\textra\n",
    ],
)
def test_retirement_ledger_rejects_malformed_entries(
    tmp_path: Path, line: str
) -> None:
    ledger_path = tmp_path / "retired-skills.tsv"
    ledger_path.write_text(line, encoding="utf-8")

    with pytest.raises(ValueError, match="retired-skills.tsv:1"):
        manage_installed_skills.read_retirements(ledger_path)


def test_retirement_ledger_rejects_duplicate_names(tmp_path: Path) -> None:
    ledger_path = tmp_path / "retired-skills.tsv"
    ledger_path.write_text(
        "design\t36f7542d39225e1160c3a4b36c76dfd067fd0281\n"
        "design\t3b78f0001ca391e321f52f5ebbd8043c7762f2ac\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate retired skill design"):
        manage_installed_skills.read_retirements(ledger_path)


def test_repository_retirement_ledger_is_disjoint_from_active_skills() -> None:
    retirements = manage_installed_skills.read_retirements(
        REPO_ROOT / "catalog/retired-skills.tsv"
    )
    retired_names = {entry.name for entry in retirements}
    active_names = {
        path.parent.name for path in (REPO_ROOT / "skills").glob("*/SKILL.md")
    }

    assert len(retirements) == 50
    assert not retired_names & active_names
    assert {
        "design",
        "dioxus-ui-ux",
        "execute-all-slices",
        "sb-tracker",
        "spec-driver",
    } <= retired_names
