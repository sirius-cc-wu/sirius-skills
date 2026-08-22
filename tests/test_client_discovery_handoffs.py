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
