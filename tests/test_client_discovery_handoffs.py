from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_client_to_code_track_routes_retired_capabilities_to_active_owners() -> None:
    track = read("catalog/tracks/client-to-code.md")

    for name in (
        "stakeholder-requirements-elicitation",
        "requirements-synthesis-validation",
        "implementation-slice-briefing",
    ):
        assert name in track

    normalized_track = " ".join(track.split())
    assert "are retired" in normalized_track
    assert "responsible external process" in normalized_track

    skill_links = [
        "../../skills/assess-development-input/SKILL.md",
        "../../skills/inception/SKILL.md",
        "../../skills/use-case-modeling/SKILL.md",
        "../../skills/operation-contracts/SKILL.md",
    ]
    positions = [track.index(link) for link in skill_links]

    assert positions == sorted(positions)
    assert "implementation-evolution.md" in track


def test_assessment_owns_entry_routing_without_replacing_iteration_coordination() -> None:
    assessment = " ".join(
        read("skills/assess-development-input/SKILL.md").split()
    )
    iterative = " ".join(
        read("skills/iterative-risk-driven-development/SKILL.md").split()
    )
    relationships = " ".join(read("catalog/skill-relationships.md").split())

    assert "This skill owns entry routing" in assessment
    assert "select one initial route without executing it" in assessment
    for group in (
        "Requirements Analysis",
        "System Analysis",
        "Software/System Design",
        "Detailed Design",
        "Implementation and Evolution",
        "Review",
        "Repository Workflow",
        "Integrate and ship",
        "Cross-cutting Support",
        "Iterative Coordination",
    ):
        assert group in assessment

    active_names = {
        line
        for line in read("skill-sets/all.txt").splitlines()
        if line and not line.startswith("#")
    }
    external_names = {
        line
        for profile in (REPO_ROOT / "catalog/external-skill-sets").glob("*.txt")
        for line in profile.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    }
    for name in (active_names - {"assess-development-input"}) | external_names:
        assert f"`{name}`" in assessment

    assert "## In-Iteration Routing" in iterative
    assert "Approved coordinated objective begins" in iterative
    assert "return to assess-development-input" in iterative
    assert "No coordination remains" in iterative
    assert "Select in-iteration owners" in iterative
    assert "does not own session-start skill discovery" in iterative
    assert "owns operational entry routing" in relationships


def test_external_authoring_and_visual_routes_keep_narrow_boundaries() -> None:
    assessment = " ".join(
        read("skills/assess-development-input/SKILL.md").split()
    )
    relationships = " ".join(read("catalog/skill-relationships.md").split())
    track = " ".join(read("catalog/tracks/repository-workflow.md").split())

    assert "reusable Codex-compatible skill needs creation or update" in assessment
    assert "current topic needs a concise visual explanation" in assessment
    assert "does not own a revision-fixed, checkpointed change tour" in relationships
    assert "does not make its outputs active Sirius skills automatically" in track


def test_doubt_driven_addon_challenges_claims_without_claiming_recovery() -> None:
    assessment = " ".join(
        read("skills/assess-development-input/SKILL.md").split()
    )
    relationships = " ".join(read("catalog/skill-relationships.md").split())
    track = " ".join(read("catalog/tracks/implementation-evolution.md").split())

    assert "doubt-driven-development" in assessment
    assert "fresh-context adversarial review" in relationships
    assert "does not recover undocumented design" in relationships
    assert "instead of treating adversarial review as design recovery" in track


def test_iterative_coordinator_preserves_intent_ownership_and_promotion() -> None:
    iterative = read("skills/iterative-risk-driven-development/SKILL.md")
    track = read("catalog/tracks/iterative-analysis-design.md")
    normalized_iterative = " ".join(iterative.split())
    normalized_track = " ".join(track.split())

    for text in (
        "Confirm canonical knowledge ownership",
        "Treat code, tests, runtime observations, and historical iteration",
        "assess-development-input",
        "external prerequisite",
        "Reconcile durable knowledge and promotion pressure",
        "a second consumer appears",
        "design-repository-artifact-layout",
        "Do not create a layout document",
    ):
        assert text in normalized_iterative

    assert (
        "Treat code, tests, observations, and historical iteration records as"
        in normalized_track
    )
    assert (
        "Reapply artifact selection when enabling behavior gains reuse"
        in normalized_track
    )


def test_layout_skill_handles_missing_guidance_without_inventing_taxonomy() -> None:
    layout = read("skills/design-repository-artifact-layout/SKILL.md")
    normalized_layout = " ".join(layout.split())

    assert (
        "no explicit artifact guide or established convention" in normalized_layout
    )
    assert "absence of a layout guide" in normalized_layout
    assert "generic" in normalized_layout
