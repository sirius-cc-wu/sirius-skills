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


def test_architecture_skill_selects_minimal_views_and_preserves_boundaries() -> None:
    skill = " ".join(read("skills/design-software-architecture/SKILL.md").split())

    for text in (
        "measurable quality-attribute scenarios",
        "## View Selection",
        "Do not create every C4 level, UML view, or deployment diagram",
        "designs intended major structure",
        "grasp-responsibility-design",
        "software-design-language-adaptation",
        "design-rust-lifecycles",
        "documentation-and-adrs",
        'type: "Software Architecture Design"',
    ):
        assert text in skill


def test_architecture_skill_is_in_design_profiles_only() -> None:
    name = "design-software-architecture"

    assert name in profile_names("skill-sets/all.txt")
    assert name in profile_names("skill-sets/iterative-design.txt")
    assert name in profile_names("skill-sets/applying-uml-and-patterns.txt")
    assert name not in profile_names("skill-sets/workflow.txt")
    assert name not in profile_names("skill-sets/reverse-engineering.txt")


def test_entry_and_iteration_routers_include_architecture_design() -> None:
    assessment = read("skills/assess-development-input/SKILL.md")
    iterative = read("skills/iterative-risk-driven-development/SKILL.md")
    relationships = read("catalog/skill-relationships.md")

    assert "design-software-architecture" in assessment
    assert "design-software-architecture" in iterative
    assert 'rectangle "design-software-architecture" as architecture' in relationships
    assert 'rectangle "design-software-\\narchitecture" as architecture' in relationships
