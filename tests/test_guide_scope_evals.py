from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
GUIDE_SCOPE_SKILL = REPO_ROOT / "skills" / "guide-scope" / "SKILL.md"


@dataclass(frozen=True)
class GuideScopeEvalCase:
    """One routing scenario for the guide-scope skill."""

    name: str
    prompt: str
    expected_route: str
    required_phrases: tuple[str, ...]


GUIDE_SCOPE_EVALS: tuple[GuideScopeEvalCase, ...] = (
    GuideScopeEvalCase(
        name="single-scope-repo",
        prompt="Run planning from a repo with one obvious scope.",
        expected_route="guide-scope stays optional and direct entry through guide-planning or guide-execution remains valid",
        required_phrases=(
            "If the repository effectively has one scope",
            "`guide-scope` is optional",
            "direct entry through `guide-planning` or `guide-execution` remains valid",
        ),
    ),
    GuideScopeEvalCase(
        name="ambiguous-nested-scope",
        prompt="Resolve a nested directory when multiple scopes are plausible.",
        expected_route="stop and ask the user to choose the scope explicitly",
        required_phrases=(
            "When slug-only lookups or nested-scope context make the target ambiguous",
            "stop and ask the user to choose the scope explicitly",
            "Surface candidate scopes or ask for an explicit scope path when ambiguity matters.",
        ),
    ),
    GuideScopeEvalCase(
        name="planning-request",
        prompt="Route feature planning work to the planning layer.",
        expected_route="route to guide-planning",
        required_phrases=(
            "If the next work is feature planning",
            "route to `guide-planning`",
            "planning-layer or execution-layer work",
        ),
    ),
    GuideScopeEvalCase(
        name="execution-request",
        prompt="Route an active slice handoff to execution.",
        expected_route="route to guide-execution",
        required_phrases=(
            "execution-layer readiness is the next question",
            "route to `guide-execution`",
            "If an execution slice already exists",
        ),
    ),
    GuideScopeEvalCase(
        name="bootstrap-request",
        prompt="Initialize nested .skills configuration for a selected scope.",
        expected_route="route to bootstrap",
        required_phrases=(
            "If the request is to initialize or update `.skills/` configuration",
            "route to `bootstrap`",
            "configure a nested scope with `bootstrap`",
        ),
    ),
)


def read_guide_scope_skill() -> str:
    return GUIDE_SCOPE_SKILL.read_text(encoding="utf-8")


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


@pytest.mark.parametrize("case", GUIDE_SCOPE_EVALS, ids=lambda case: case.name)
def test_guide_scope_core_routing_evals(case: GuideScopeEvalCase) -> None:
    skill_text = normalize_whitespace(read_guide_scope_skill())

    for phrase in case.required_phrases:
        assert normalize_whitespace(phrase) in skill_text, f"{case.name} missing phrase: {phrase!r}"


def test_guide_scope_documented_handoff_lists_all_targets() -> None:
    skill_text = normalize_whitespace(read_guide_scope_skill())

    assert "guide-scope -> guide-planning" in skill_text
    assert "guide-scope -> guide-execution" in skill_text
    assert "guide-scope -> bootstrap" in skill_text
