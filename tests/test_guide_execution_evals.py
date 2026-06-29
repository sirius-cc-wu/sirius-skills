from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
GUIDE_EXECUTION_SKILL = REPO_ROOT / "skills" / "guide-execution" / "SKILL.md"


@dataclass(frozen=True)
class GuideExecutionEvalCase:
    """One execution-router scenario for the guide-execution skill."""

    name: str
    prompt: str
    expected_route: str
    required_phrases: tuple[str, ...]


GUIDE_EXECUTION_EVALS: tuple[GuideExecutionEvalCase, ...] = (
    GuideExecutionEvalCase(
        name="feature-scoped-work",
        prompt="Send feature-scoped work back to planning.",
        expected_route="send it back to guide-planning",
        required_phrases=(
            "If the work is still feature-scoped or story-scoped",
            "send it back to `guide-planning`",
            "feature-scoped or story-scoped",
        ),
    ),
    GuideExecutionEvalCase(
        name="bootstrap-slice-handoff",
        prompt="Bootstrap execution when no slice exists yet.",
        expected_route="route to slice",
        required_phrases=(
            "If there is one execution-ready work item but no slice-scoped execution slice yet",
            "route to `slice`",
            "approved and committed",
        ),
    ),
    GuideExecutionEvalCase(
        name="active-slice-exists",
        prompt="Keep routing inside execution when a slice is already resolved.",
        expected_route="stay in guide-execution",
        required_phrases=(
            "If a slice exists or can be resolved",
            "stay in `guide-execution`",
            "route inside the execution layer",
        ),
    ),
    GuideExecutionEvalCase(
        name="execution-layer-targets",
        prompt="Recognize the execution-layer lifecycle targets.",
        expected_route="brief blueprint review-execution close-slice",
        required_phrases=(
            "`brief`",
            "`blueprint`",
            "`review-execution`",
            "`close-slice`",
        ),
    ),
    GuideExecutionEvalCase(
        name="auto-start-implementation",
        prompt="Honor the automatic implementation handoff after blueprint readiness.",
        expected_route="continue directly into code changes",
        required_phrases=(
            "When `.skills/execution.json` sets `auto_start_implementation` to `true`",
            "treat `blueprint_ready` as an automatic handoff into implementation",
            "continue directly into code changes instead of stopping for a second manual handoff",
        ),
    ),
)


def read_guide_execution_skill() -> str:
    return GUIDE_EXECUTION_SKILL.read_text(encoding="utf-8")


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


@pytest.mark.parametrize("case", GUIDE_EXECUTION_EVALS, ids=lambda case: case.name)
def test_guide_execution_core_routing_evals(case: GuideExecutionEvalCase) -> None:
    skill_text = normalize_whitespace(read_guide_execution_skill())

    for phrase in case.required_phrases:
        assert normalize_whitespace(phrase) in skill_text, f"{case.name} missing phrase: {phrase!r}"


def test_guide_execution_documented_handoff_lists_core_targets() -> None:
    skill_text = normalize_whitespace(read_guide_execution_skill())

    assert "guide-planning -> discover -> design -> ui-flow -> breakdown -> review-planning -> human approval -> commit -> slice -> guide-execution" in skill_text
    assert "`guide-execution` owns orchestration and readiness only" in skill_text
