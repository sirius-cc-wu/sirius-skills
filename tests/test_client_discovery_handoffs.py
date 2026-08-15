from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_evidence_to_synthesis_handoff_preserves_provenance_and_authority() -> None:
    elicitation = read("skills/stakeholder-requirements-elicitation/SKILL.md")
    synthesis = read("skills/requirements-synthesis-validation/SKILL.md")

    for field in (
        "Opaque source ID",
        "Authority:",
        "Claim status and confidence:",
        "Sensitivity and handling:",
        "Limits and conflicts:",
    ):
        assert field in elicitation

    assert "../stakeholder-requirements-elicitation/SKILL.md" in synthesis
    for field in (
        "Source evidence IDs:",
        "Validation and approval:",
        "candidate | validated | approved | contested | superseded",
    ):
        assert field in synthesis


def test_synthesis_to_briefing_handoff_preserves_status_and_freshness() -> None:
    briefing = read("skills/implementation-slice-briefing/SKILL.md")

    assert "requirements-synthesis-validation" in briefing
    assert "Do not promote `candidate`, `validated`, `contested`" in briefing
    assert "Source | Revision | Status | Authority | Used for" in briefing
    assert "Stop and route to [owner]" in briefing
    assert "Source-change and unresolved-decision stop conditions" in briefing
    assert "Link to protected evidence without reproducing" in briefing


def test_client_to_code_track_links_active_skills_in_handoff_order() -> None:
    track = read("catalog/tracks/client-to-code.md")
    skill_links = [
        "../../skills/stakeholder-requirements-elicitation/SKILL.md",
        "../../skills/requirements-synthesis-validation/SKILL.md",
        "../../skills/implementation-slice-briefing/SKILL.md",
    ]

    positions = [track.index(link) for link in skill_links]

    assert positions == sorted(positions)


def test_behavioral_fixtures_exercise_adjacent_handoff_shapes() -> None:
    synthesis_input = read(
        "evals/fixtures/requirements-synthesis/evidence/stakeholder-evidence.md"
    )
    briefing_input = read(
        "evals/fixtures/implementation-slice-briefing/requirements/"
        "approved-requirements.md"
    )

    assert 'type: "Stakeholder Evidence Record"' in synthesis_input
    assert "### SRC-SPONSOR-ALPHA" in synthesis_input
    assert 'type: "Requirements Discovery Brief"' in briefing_input
    assert "Source evidence IDs:" in briefing_input


def test_iterative_coordinator_preserves_intent_ownership_and_promotion() -> None:
    iterative = read("skills/iterative-risk-driven-development/SKILL.md")
    track = read("catalog/tracks/iterative-analysis-design.md")
    normalized_iterative = " ".join(iterative.split())
    normalized_track = " ".join(track.split())

    for text in (
        "Confirm canonical knowledge ownership",
        "Treat code, tests, runtime observations, and historical iteration",
        "assess-development-input",
        "requirements-synthesis-validation",
        "Reconcile durable knowledge and promotion pressure",
        "a second consumer appears",
        "design-repository-artifact-layout",
        "Do not create a layout document",
    ):
        assert text in normalized_iterative

    assert "Treat code, tests, observations, and historical iteration records as" in normalized_track
    assert "Reapply artifact selection when enabling behavior gains reuse" in normalized_track


def test_layout_skill_handles_missing_guidance_without_inventing_taxonomy() -> None:
    layout = read("skills/design-repository-artifact-layout/SKILL.md")
    normalized_layout = " ".join(layout.split())

    assert "no explicit artifact guide or established convention" in normalized_layout
    assert "absence of a layout guide" in normalized_layout
    assert "generic" in normalized_layout
