from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


GUARDRAILS_MODULE = (
    Path(__file__).resolve().parents[3] / "src" / "sirius_skills" / "lib" / "workflow_runtime" / "accelerator_guardrails.py"
)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_normalize_stop_reason_and_synonyms() -> None:
    guardrails = load_module(
        GUARDRAILS_MODULE, "accelerator_guardrails_test_normalize"
    )

    payload = guardrails.normalize_stop_reason({"kind": "approval_required"})
    assert payload is not None
    assert payload["kind"] == "approval_required"

    fallback = guardrails.normalize_stop_reason(None, default_kind="review-required")
    assert fallback == {"kind": "review_boundary"}


def test_classify_stop_reason_from_message_by_stage() -> None:
    guardrails = load_module(
        GUARDRAILS_MODULE, "accelerator_guardrails_test_classify"
    )

    assert (
        guardrails.classify_stop_reason_from_message(
            "Missing required file: discover.md", stage="planning"
        )
        == "missing_required_input"
    )
    assert (
        guardrails.classify_stop_reason_from_message(
            "status_mismatch: expected execution_ready", stage="execution"
        )
        == "missing_required_input"
    )


def test_build_readiness_dedupes_and_enforces_guardrails() -> None:
    guardrails = load_module(
        GUARDRAILS_MODULE, "accelerator_guardrails_test_readiness"
    )

    blocked = guardrails.build_accelerator_readiness(
        next_owner="approval",
        automatable_owners={"discover", "design"},
        blocked_by=["approval_required", "approval_required"],
        stop_reason={"kind": "approval_required"},
        approval_gate={"required": True, "state": "not_required"},
        commit_checkpoint={"required": False, "state": "not_required"},
    )
    assert blocked["can_proceed"] is False
    assert blocked["blocked_by"] == ["approval_required"]
    assert blocked["approval_gate"]["state"] == "waiting_approval"
    assert blocked["stop_reason"]["kind"] == "approval_required"

    clear = guardrails.build_accelerator_readiness(
        next_owner="design",
        automatable_owners={"discover", "design"},
        blocked_by=[],
        stop_reason=None,
        approval_gate={"required": False, "state": "not_required"},
        commit_checkpoint={"required": False, "state": "not_required"},
    )
    assert clear["can_proceed"] is True
    assert clear["blocked_by"] == []
