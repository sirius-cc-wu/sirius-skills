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
    assert "rectangle softwareDesign #F3EEFF [" in relationships
    assert "design-software-architecture" in relationships
    assert (
        'rectangle "design-software-\\narchitecture" as architecture' in relationships
    )


def test_relationship_overview_stays_embedded_compact_and_rendered() -> None:
    relationships = read("catalog/skill-relationships.md")
    readme = read("README.md")
    rendered_overview = read("catalog/skill-relationships.svg")
    overview = relationships.split("@startuml sirius-skills-birds-eye", maxsplit=1)[
        1
    ].split("@enduml", maxsplit=1)[0]
    external_names = {
        line
        for profile in (REPO_ROOT / "catalog/external-skill-sets").glob("*.txt")
        for line in profile.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    }

    assert relationships.count("```plantuml") == 4
    assert overview.count("-->") + overview.count("..>") <= 10
    assert "catalog/skill-relationships.svg" in readme
    assert "embedded PlantUML remains its canonical source" in readme
    assert "<svg " in rendered_overview

    for name in profile_names("skill-sets/all.txt") | external_names:
        assert name in overview
        assert name in rendered_overview
