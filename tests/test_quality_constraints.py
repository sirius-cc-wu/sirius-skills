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


def test_quality_constraint_skill_preserves_requirements_and_design_boundary() -> None:
    skill = " ".join(
        read("skills/specify-quality-constraints/SKILL.md").split()
    )

    for text in (
        "stimulus, operating condition, affected scope, required response, and measure",
        "candidate, approved, contested, inferred, and unknown",
        "type: \"Supplementary Specification\"",
        "design-software-architecture",
        "responsible external product or portfolio process",
        "External `idea-refine` can prepare a candidate direction, not approve it",
    ):
        assert text in skill


def test_quality_constraint_skill_is_active_and_routable() -> None:
    name = "specify-quality-constraints"

    assert name in profile_names("skill-sets/all.txt")
    assert name in profile_names("skill-sets/iterative-design.txt")
    assert name in profile_names("skill-sets/applying-uml-and-patterns.txt")
    assert name not in profile_names("skill-sets/workflow.txt")
    assert name not in profile_names("skill-sets/reverse-engineering.txt")

    for relative_path in (
        "skills/assess-development-input/SKILL.md",
        "skills/iterative-risk-driven-development/SKILL.md",
        "catalog/skill-relationships.md",
    ):
        assert name in read(relative_path)
