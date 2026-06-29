from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
GUIDE_SCOPE_SKILL = REPO_ROOT / "skills" / "guide-scope" / "SKILL.md"


@dataclass(frozen=True)
class GuideScopeFollowupEvalCase:
    """One follow-on routing scenario for the guide-scope skill."""

    name: str
    prompt: str
    expected_route: str
    required_phrases: tuple[str, ...]


GUIDE_SCOPE_FOLLOWUP_EVALS: tuple[GuideScopeFollowupEvalCase, ...] = (
    GuideScopeFollowupEvalCase(
        name="regression-routes-to-planning",
        prompt="A shipped feature has a regression and needs follow-on work.",
        expected_route="route into planning",
        required_phrases=(
            "If the request is a follow-on fix or missing behavior report for shipped work",
            "route into planning",
            "subfeature-scoped delta work",
        ),
    ),
    GuideScopeFollowupEvalCase(
        name="new-issue-for-implemented-feature",
        prompt="An implemented feature has a new missing behavior report.",
        expected_route="route to guide-planning",
        required_phrases=(
            "the user is reporting a new issue, regression, or follow-on capability for an existing implemented feature",
            "route to `guide-planning`",
            "whether `add-subfeature` is required",
        ),
    ),
    GuideScopeFollowupEvalCase(
        name="do-not-jump-to-archive",
        prompt="Do not send follow-on work straight to archive.",
        expected_route="do not jump straight to archive",
        required_phrases=(
            "do not jump straight to archive",
            "treat the existing packet as the active execution scope automatically",
        ),
    ),
    GuideScopeFollowupEvalCase(
        name="planning-layer-over-execution-shortcut",
        prompt="Prefer planning-layer routing over stale execution state.",
        expected_route="prefer planning-layer routing",
        required_phrases=(
            "Prefer planning-layer routing over archive/execution shortcuts",
            "new delta work",
            "route into planning",
        ),
    ),
)


def read_guide_scope_skill() -> str:
    return GUIDE_SCOPE_SKILL.read_text(encoding="utf-8")


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


@pytest.mark.parametrize("case", GUIDE_SCOPE_FOLLOWUP_EVALS, ids=lambda case: case.name)
def test_guide_scope_followup_routing_evals(case: GuideScopeFollowupEvalCase) -> None:
    skill_text = normalize_whitespace(read_guide_scope_skill())

    for phrase in case.required_phrases:
        assert normalize_whitespace(phrase) in skill_text, f"{case.name} missing phrase: {phrase!r}"


def test_guide_scope_followup_mentions_subfeature_scoped_delta_work() -> None:
    skill_text = normalize_whitespace(read_guide_scope_skill())

    assert "subfeature-scoped delta work" in skill_text
    assert "add-subfeature" in skill_text
