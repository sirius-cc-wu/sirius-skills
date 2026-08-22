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
    profile_path.write_text(
        "# selected profile\ncurrent-skill\nexample-skill\n", encoding="utf-8"
    )

    manage_installed_skills.record_installed(profile_path, state_path)
    manage_installed_skills.record_names(["another-skill"], state_path)
    manage_installed_skills.forget_names(["example-skill"], state_path)

    assert state_path.read_text(encoding="utf-8") == "another-skill\ncurrent-skill\n"


def test_forget_retired_cleans_stale_ownership_entries(tmp_path: Path) -> None:
    ledger_path = tmp_path / "retired-skills.tsv"
    state_path = tmp_path / "managed-skills.txt"
    write_ledger(ledger_path)
    state_path.write_text("current-skill\ndesign\nold-workflow\n", encoding="utf-8")

    manage_installed_skills.forget_retired(ledger_path, state_path)

    assert state_path.read_text(encoding="utf-8") == "current-skill\n"


def test_link_profile_exposes_canonical_skills_and_is_idempotent(
    tmp_path: Path,
) -> None:
    profile_path = tmp_path / "profile.txt"
    source_dir = tmp_path / ".agents" / "skills"
    target_dir = tmp_path / ".gemini" / "config" / "skills"
    profile_path.write_text("current-skill\nexample-skill\n", encoding="utf-8")
    for name in ("current-skill", "example-skill"):
        (source_dir / name).mkdir(parents=True)
    target_dir.mkdir(parents=True)
    (target_dir / "external-skill").mkdir()

    manage_installed_skills.link_profile(
        profile_path,
        source_dir=source_dir,
        target_dir=target_dir,
    )
    manage_installed_skills.link_profile(
        profile_path,
        source_dir=source_dir,
        target_dir=target_dir,
    )

    assert (target_dir / "current-skill").is_symlink()
    assert (target_dir / "current-skill").resolve() == source_dir / "current-skill"
    assert (target_dir / "example-skill").resolve() == source_dir / "example-skill"
    assert (target_dir / "external-skill").is_dir()


def test_link_profile_rejects_conflicts_before_creating_any_links(
    tmp_path: Path,
) -> None:
    profile_path = tmp_path / "profile.txt"
    source_dir = tmp_path / ".agents" / "skills"
    target_dir = tmp_path / ".gemini" / "config" / "skills"
    profile_path.write_text("current-skill\nexample-skill\n", encoding="utf-8")
    for name in ("current-skill", "example-skill"):
        (source_dir / name).mkdir(parents=True)
    (target_dir / "example-skill").mkdir(parents=True)

    with pytest.raises(ValueError, match="refusing to replace"):
        manage_installed_skills.link_profile(
            profile_path,
            source_dir=source_dir,
            target_dir=target_dir,
        )

    assert not (target_dir / "current-skill").exists()
    assert (target_dir / "example-skill").is_dir()


def test_unlink_profile_removes_only_links_to_expected_canonical_skills(
    tmp_path: Path,
) -> None:
    profile_path = tmp_path / "profile.txt"
    source_dir = tmp_path / ".agents" / "skills"
    target_dir = tmp_path / ".gemini" / "config" / "skills"
    foreign_dir = tmp_path / "foreign"
    profile_path.write_text("current-skill\nexample-skill\n", encoding="utf-8")
    for name in ("current-skill", "example-skill"):
        (source_dir / name).mkdir(parents=True)
    target_dir.mkdir(parents=True)
    foreign_dir.mkdir()
    (target_dir / "current-skill").symlink_to(
        source_dir / "current-skill", target_is_directory=True
    )
    (target_dir / "example-skill").symlink_to(foreign_dir, target_is_directory=True)

    manage_installed_skills.unlink_profile(
        profile_path,
        source_dir=source_dir,
        target_dir=target_dir,
    )

    assert not (target_dir / "current-skill").exists()
    assert (target_dir / "example-skill").is_symlink()
    assert (target_dir / "example-skill").resolve() == foreign_dir


def test_unlink_retired_links_respects_ownership_by_default(tmp_path: Path) -> None:
    ledger_path = tmp_path / "retired-skills.tsv"
    state_path = tmp_path / "managed-skills.txt"
    source_dir = tmp_path / ".agents" / "skills"
    target_dir = tmp_path / ".gemini" / "config" / "skills"
    write_ledger(ledger_path)
    state_path.write_text("old-workflow\n", encoding="utf-8")
    source_dir.mkdir(parents=True)
    target_dir.mkdir(parents=True)
    for name in ("design", "old-workflow"):
        (target_dir / name).symlink_to(source_dir / name, target_is_directory=True)

    manage_installed_skills.unlink_retired(
        ledger_path,
        state_path=state_path,
        source_dir=source_dir,
        target_dir=target_dir,
    )

    assert (target_dir / "design").is_symlink()
    assert not (target_dir / "old-workflow").is_symlink()

    manage_installed_skills.unlink_retired(
        ledger_path,
        state_path=state_path,
        source_dir=source_dir,
        target_dir=target_dir,
        include_unowned=True,
    )

    assert not (target_dir / "design").is_symlink()


def test_remove_locked_profile_removes_only_the_expected_source(
    tmp_path: Path,
) -> None:
    profile_path = tmp_path / "external-profile.txt"
    lock_path = tmp_path / "skills-lock.json"
    skills_dir = tmp_path / ".agents/skills"
    profile_path.write_text("interview-me\nidea-refine\n", encoding="utf-8")
    lock_path.write_text(
        json.dumps(
            {
                "version": 1,
                "skills": {
                    "interview-me": {"source": "addyosmani/agent-skills"},
                    "idea-refine": {"source": "another/source"},
                    "unrelated": {"source": "another/source"},
                },
            }
        ),
        encoding="utf-8",
    )
    for name in ("interview-me", "idea-refine", "unrelated"):
        (skills_dir / name).mkdir(parents=True)
        (skills_dir / name / "SKILL.md").write_text(name, encoding="utf-8")

    manage_installed_skills.remove_locked_profile(
        profile_path,
        lock_path=lock_path,
        skills_dir=skills_dir,
        source="addyosmani/agent-skills",
    )

    assert not (skills_dir / "interview-me").exists()
    assert (skills_dir / "idea-refine/SKILL.md").read_text() == "idea-refine"
    assert (skills_dir / "unrelated/SKILL.md").read_text() == "unrelated"
    remaining = json.loads(lock_path.read_text(encoding="utf-8"))["skills"]
    assert set(remaining) == {"idea-refine", "unrelated"}


def test_remove_locked_profile_validates_all_targets_before_removal(
    tmp_path: Path,
) -> None:
    profile_path = tmp_path / "external-profile.txt"
    lock_path = tmp_path / "skills-lock.json"
    skills_dir = tmp_path / ".agents/skills"
    profile_path.write_text("interview-me\nidea-refine\n", encoding="utf-8")
    lock_path.write_text(
        json.dumps(
            {
                "version": 1,
                "skills": {
                    "interview-me": {"source": "addyosmani/agent-skills"},
                    "idea-refine": {"source": "addyosmani/agent-skills"},
                },
            }
        ),
        encoding="utf-8",
    )
    (skills_dir / "interview-me").mkdir(parents=True)
    (skills_dir / "idea-refine").parent.mkdir(parents=True, exist_ok=True)
    (skills_dir / "idea-refine").write_text("conflict", encoding="utf-8")

    with pytest.raises(ValueError, match="not a directory or symlink"):
        manage_installed_skills.remove_locked_profile(
            profile_path,
            lock_path=lock_path,
            skills_dir=skills_dir,
            source="addyosmani/agent-skills",
        )

    assert (skills_dir / "interview-me").is_dir()
    assert (skills_dir / "idea-refine").is_file()


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

    assert len(retirements) == 68
    assert not retired_names & active_names
    assert {
        "author-software-proposal",
        "behavior-driven-specification",
        "commit",
        "design",
        "dioxus-ui-ux",
        "execute-all-slices",
        "governance-update",
        "implementation-slice-briefing",
        "iterative-risk-driven-analysis-design",
        "iterative-up-analysis-design",
        "plan-up-iterations",
        "requirements-synthesis-validation",
        "reconcile-recovered-design",
        "reconstruct-software-architecture",
        "recover-system-behavior",
        "reverse-engineer-software-system",
        "rewrite-technical-artifacts",
        "run-development-iteration",
        "sb-tracker",
        "simplify",
        "spec-driver",
        "stakeholder-requirements-elicitation",
        "survey-existing-system",
    } <= retired_names
