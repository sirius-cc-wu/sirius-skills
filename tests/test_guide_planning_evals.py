from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
GUIDE_PLANNING_SKILL = REPO_ROOT / "skills" / "guide-planning" / "SKILL.md"


@dataclass(frozen=True)
class GuidePlanningEvalCase:
    """One planning-router scenario for the guide-planning skill."""

    name: str
    prompt: str
    expected_route: str
    required_phrases: tuple[str, ...]


GUIDE_PLANNING_EVALS: tuple[GuidePlanningEvalCase, ...] = (
    GuidePlanningEvalCase(
        name="proposal-promotion",
        prompt="Promote an accepted proposal into canonical planning.",
        expected_route="route to discover after proposal promotion",
        required_phrases=(
            "If the user wants an accepted proposal promoted into canonical planning",
            "perform that promotion here and then route to `discover`",
            "accepted proposal",
        ),
    ),
    GuidePlanningEvalCase(
        name="new-feature-discovery",
        prompt="Start planning for a new feature with no existing planning folder.",
        expected_route="initialize one and route to discover",
        required_phrases=(
            "If no feature planning folder exists yet",
            "initialize one and route to `discover`",
            "discover",
        ),
    ),
    GuidePlanningEvalCase(
        name="add-subfeature",
        prompt="Reshape a durable child capability under an existing feature.",
        expected_route="route to add-subfeature",
        required_phrases=(
            "If the request adds or reshapes a durable child capability under an existing feature",
            "route to `add-subfeature`",
            "durable child capability",
        ),
    ),
    GuidePlanningEvalCase(
        name="research",
        prompt="Choose between upstream patterns before planning.",
        expected_route="route to research",
        required_phrases=(
            "If the user explicitly asks for reference-project research or wiki synthesis",
            "route to `research`",
            "multiple upstream patterns",
        ),
    ),
    GuidePlanningEvalCase(
        name="design",
        prompt="Resolve architecture, interfaces, and validation strategy.",
        expected_route="route to design",
        required_phrases=(
            "If the architecture, interfaces, or validation strategy are still unresolved",
            "route to `design`",
            "validation strategy",
        ),
    ),
    GuidePlanningEvalCase(
        name="review-planning-stop",
        prompt="Stop at planning review until approval is explicit.",
        expected_route="stop for human approval",
        required_phrases=(
            "If planning artifacts need a readiness pass before approval and execution bootstrap",
            "route to `review-planning`",
            "stop for human approval instead of advancing into execution",
        ),
    ),
)


def read_guide_planning_skill() -> str:
    return GUIDE_PLANNING_SKILL.read_text(encoding="utf-8")


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


@pytest.mark.parametrize("case", GUIDE_PLANNING_EVALS, ids=lambda case: case.name)
def test_guide_planning_core_routing_evals(case: GuidePlanningEvalCase) -> None:
    skill_text = normalize_whitespace(read_guide_planning_skill())

    for phrase in case.required_phrases:
        assert normalize_whitespace(phrase) in skill_text, f"{case.name} missing phrase: {phrase!r}"


def test_guide_planning_documented_handoff_lists_core_targets() -> None:
    skill_text = normalize_whitespace(read_guide_planning_skill())

    assert "guide-planning -> propose/add-subfeature/research/discover" in skill_text
    assert "-> design -> ui-flow -> breakdown -> review-planning -> human approval -> commit -> slice -> guide-execution" in skill_text
