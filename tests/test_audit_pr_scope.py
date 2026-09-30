from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def profile_names(relative_path: str) -> set[str]:
    return {
        line
        for line in read(relative_path).splitlines()
        if line and not line.startswith("#")
    }


def test_audit_pr_scope_skill_preserves_boundaries_and_structure() -> None:
    skill = " ".join(read("skills/audit-pr-scope/SKILL.md").split())

    for text in (
        "Audits whether a pull request's scope matches its motivating problem.",
        "Motivating Problem",
        "Over-engineering",
        "Under-engineering",
        "Slice A",
        "Slice B",
        "flowchart",
        "Maintains strict read-only boundaries.",
    ):
        assert text in skill


def test_audit_pr_scope_skill_is_active_and_routable() -> None:
    name = "audit-pr-scope"

    assert name in profile_names("skill-sets/all.txt")
    assert name in profile_names("skill-sets/workflow.txt")
    assert name not in profile_names("skill-sets/iterative-design.txt")
    assert name not in profile_names("skill-sets/applying-uml-and-patterns.txt")
    assert name not in profile_names("skill-sets/reverse-engineering.txt")
