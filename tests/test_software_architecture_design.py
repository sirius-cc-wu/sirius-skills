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
        "components, boundaries, deployment, or quality trade-offs → "
        "design-software-architecture"
    ) in relationships


def test_iteration_relationship_view_matches_current_routing_groups() -> None:
    relationships = read("catalog/skill-relationships.md")
    iteration_view = relationships.split(
        "@startuml iterative-design-skill-relationships", maxsplit=1
    )[1].split("@enduml", maxsplit=1)[0]
    routed_names = {
        "inception",
        "use-case-modeling",
        "domain-modeling",
        "system-sequence-diagrams",
        "operation-contracts",
        "design-software-architecture",
        "grasp-responsibility-design",
        "use-case-realization",
        "uml-class-diagram-design",
        "design-pattern-application",
        "software-design-language-adaptation",
        "design-rust-lifecycles",
    }

    assert iteration_view.count("iterative ..>") == 4
    assert "The groups are not phases" in iteration_view
    assert "inception --> usecases" not in iteration_view
    assert "architecture --> grasp" not in iteration_view
    for name in routed_names:
        assert name in iteration_view


def test_implementation_relationship_view_matches_current_direct_routes() -> None:
    relationships = read("catalog/skill-relationships.md")
    implementation_view = relationships.split(
        "@startuml implementation-repository-skill-relationships", maxsplit=1
    )[1].split("@enduml", maxsplit=1)[0]

    for text in (
        "approved independent oracle → test-driven-development",
        "non-trivial in-flight claim → doubt-driven-development",
        "completed change → code-review-and-quality",
        "routine clarity → code-simplification",
        "established structural ownership → behavior-preserving-refactoring",
        "material boundary change → iterative-risk-driven-development",
        "Git, branch, worktree, release, or version guidance",
        "consequential decision or durable context",
        "revision-fixed or snapshot-fixed change tour → walkthrough-me",
        "committed work ready for pull-request publication → create-pr",
    ):
        assert text in implementation_view

    assert implementation_view.count("selected ..>") == 4
    assert "already committed" not in implementation_view


def test_feedback_view_includes_current_detailed_design_owners() -> None:
    relationships = read("catalog/skill-relationships.md")
    feedback_view = relationships.split("@startuml sirius-skill-feedback", maxsplit=1)[
        1
    ].split("@enduml", maxsplit=1)[0]

    assert "language realization → software-design-language-adaptation" in feedback_view
    assert "ownership or lifecycle → design-rust-lifecycles" in feedback_view
    assert feedback_view.count("evidence ..>") == 4
    assert feedback_view.count("refactoring ..>") == 3
    assert "Re-enter an owner only when evidence changes its canonical knowledge" in (
        feedback_view
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
