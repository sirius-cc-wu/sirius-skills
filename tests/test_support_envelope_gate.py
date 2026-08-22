from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def normalized(relative_path: str) -> str:
    return " ".join(read(relative_path).split())


def test_coordinator_defines_bounded_support_envelope_gate() -> None:
    skill = normalized("skills/iterative-risk-driven-development/SKILL.md")

    for text in (
        "## Support-Envelope Gate",
        "one exact variant, one family, a closed catalog",
        "dynamically extensible population",
        "named siblings, aliases, revisions",
        "generic fallbacks, dynamic extensions",
        "normal, startup, degraded, offline, persisted, cached, or replayed modes",
        "Do not guess",
        "design-software-architecture",
        "operation-contracts",
        "responsible external recovery process",
        "does not recover the whole system, require a standalone support matrix",
    ):
        assert text in skill


def test_support_envelope_guidance_is_aligned_across_navigation() -> None:
    assert "support-envelope and boundary-sensitive refactoring gates" in normalized(
        "README.md"
    )
    assert "## Support-Envelope Gate" in normalized(
        "catalog/tracks/iterative-analysis-design.md"
    )
    assert "applies its support-envelope gate" in normalized(
        "catalog/skill-relationships.md"
    )
    assert "support-envelope and boundary-sensitive refactoring gates" in normalized(
        "catalog/skills.md"
    )
    assert "establish the approved support population" in normalized("PROMPT_GUIDE.md")


def test_support_envelope_eval_preserves_scope_evidence_and_completion() -> None:
    case = json.loads(read("evals/cases/iterative-risk-driven-development.json"))
    support_eval = next(
        item
        for item in case["evals"]
        if item["id"] == "support-envelope-before-specialized-change"
    )
    expectations = " ".join(support_eval["expectations"])
    prohibitions = " ".join(support_eval["prohibitions"])

    assert "supported population" in expectations
    assert "dynamic fallback" in expectations
    assert "capability sources" in expectations
    assert "software architecture design" in expectations
    assert "does not close the broader parent outcome" in expectations
    assert "Do not infer the supported population" in prohibitions
    assert "Do not guess offline capability" in prohibitions
