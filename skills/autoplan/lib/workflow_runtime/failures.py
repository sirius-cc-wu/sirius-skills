from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from workflow_runtime.accelerator_guardrails import normalize_reason_code
from workflow_runtime.event_log import append_event


FAILURE_REASON_KINDS = frozenset(
    {
        "ambiguity",
        "formatter_scope",
        "invalid_configuration",
        "invalid_transition",
        "missing_required_input",
        "owned_file_conflict",
        "resolution_failed",
        "runtime_error",
        "validation_failed",
        "verification_failed",
    }
)


@dataclass
class FailureContext:
    skill: str
    stage: str
    reason_code: str
    message: str
    logged_to: str
    recovery_suggestions: list[str] = field(default_factory=list)
    improvement_suggestions: list[str] = field(default_factory=list)
    target_id: str = ""
    slice_id: str = ""
    next_owner: str = ""
    owner: str = ""
    evidence_refs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _dedupe(items: Sequence[str]) -> list[str]:
    result: list[str] = []
    for item in items:
        text = item.strip()
        if text and text not in result:
            result.append(text)
    return result


def _normalize_text(value: object) -> str:
    return str(value).strip() if value is not None else ""


def _coerce_refs(values: Sequence[str] | None) -> list[str]:
    if values is None:
        return []
    return _dedupe([str(value) for value in values if str(value).strip()])


def is_failure_reason(reason_code: object) -> bool:
    normalized = normalize_reason_code(reason_code)
    return normalized in FAILURE_REASON_KINDS


def _failure_suggestions(
    *, reason_code: str, skill: str, next_owner: str = "", owner: str = ""
) -> tuple[list[str], list[str]]:
    owner_name = owner or next_owner
    owner_label = owner_name if owner_name else "the owning skill"

    if reason_code == "missing_required_input":
        return (
            _dedupe(
                [
                    "Inspect the blocking message and create or repair the missing artifacts before retrying.",
                    f"Invoke {owner_label} directly if it owns the missing artifact creation step.",
                    f"Re-run {skill} after the required inputs are present.",
                ]
            ),
            _dedupe(
                [
                    "Add or improve preflight checks so required artifacts are identified before the owner chain starts.",
                    "Teach the upstream handoff to scaffold predictable required artifacts automatically when safe.",
                ]
            ),
        )
    if reason_code == "invalid_configuration":
        return (
            [
                "Fix the referenced accelerator configuration value before retrying.",
                "Compare the local config shape with the skill documentation and working test fixtures.",
            ],
            [
                "Add schema-like validation or clearer config diagnostics closer to config load time.",
                "Keep config examples in docs and tests aligned with the accepted shape.",
            ],
        )
    if reason_code == "resolution_failed":
        return (
            [
                "Retry with an explicit target or handoff payload instead of relying on implicit resolution.",
                "Confirm the referenced feature or slice exists in the canonical registry before rerunning.",
            ],
            [
                "Strengthen selector disambiguation and missing-target diagnostics with concrete candidate hints.",
            ],
        )
    if reason_code == "invalid_transition":
        return (
            [
                "Refresh the current planning or execution status from repo artifacts before retrying the transition.",
                f"Use {owner_label} only after the source-of-truth status reaches the required prerequisite state.",
            ],
            [
                "Add earlier transition guards so impossible status moves fail before downstream work begins.",
            ],
        )
    if reason_code == "ambiguity":
        return (
            [
                "Retry with an explicit scope or selector so the skill can resolve one target unambiguously.",
            ],
            [
                "Improve ambiguity diagnostics so the conflicting candidates are listed directly in the failure output.",
            ],
        )
    if reason_code == "owned_file_conflict":
        return (
            [
                "Separate unrelated dirty files from the owned execution slice before retrying.",
                "Resolve the conflicting owned-file changes or commit them intentionally before continuing.",
            ],
            [
                "Tighten owned-file detection and conflict reporting so mixed worktrees are flagged earlier.",
            ],
        )
    if reason_code == "formatter_scope":
        return (
            [
                "Constrain formatting to the owned path set before retrying the automation tail.",
            ],
            [
                "Prefer a path-aware formatter wrapper so auto-formatting cannot spill outside owned files.",
            ],
        )
    if reason_code == "validation_failed":
        return (
            [
                "Repair the cited planning validation issue before retrying.",
                f"Re-run {owner_label} once the blocking artifact state is corrected.",
            ],
            [
                "Expose the blocking validation rule earlier in the workflow so maintainers can fix it sooner.",
            ],
        )
    if reason_code == "verification_failed":
        return (
            [
                "Repair the cited execution verification problem before retrying.",
                f"Re-run {owner_label} only after the slice artifacts satisfy the current execution checks.",
            ],
            [
                "Improve execution-side diagnostics so verification failures point directly at the blocking artifact or rule.",
            ],
        )
    return (
        [
            "Inspect the logged failure details and retry only after the blocking issue is repaired.",
            "Re-run the accelerator with --json to capture structured failure details if you need to automate the recovery.",
        ],
        [
            "Add narrower diagnostics or preflight checks so this runtime failure becomes easier to classify and prevent.",
        ],
    )


def build_failure_context(
    *,
    event_log_path: Path,
    skill: str,
    stage: str,
    reason_code: object,
    message: object,
    target_id: str = "",
    slice_id: str = "",
    next_owner: str = "",
    owner: str = "",
    evidence_refs: Sequence[str] | None = None,
) -> FailureContext:
    normalized_reason = normalize_reason_code(reason_code) or "runtime_error"
    recovery_suggestions, improvement_suggestions = _failure_suggestions(
        reason_code=normalized_reason,
        skill=skill,
        next_owner=next_owner,
        owner=owner,
    )
    return FailureContext(
        skill=skill,
        stage=stage,
        reason_code=normalized_reason,
        message=_normalize_text(message),
        logged_to=str(event_log_path),
        recovery_suggestions=recovery_suggestions,
        improvement_suggestions=improvement_suggestions,
        target_id=_normalize_text(target_id),
        slice_id=_normalize_text(slice_id),
        next_owner=_normalize_text(next_owner),
        owner=_normalize_text(owner),
        evidence_refs=_coerce_refs(evidence_refs),
    )


def record_failure(
    event_log_path: Path,
    *,
    skill: str,
    stage: str,
    reason_code: object,
    message: object,
    target_id: str = "",
    slice_id: str = "",
    next_owner: str = "",
    owner: str = "",
    evidence_refs: Sequence[str] | None = None,
) -> FailureContext:
    context = build_failure_context(
        event_log_path=event_log_path,
        skill=skill,
        stage=stage,
        reason_code=reason_code,
        message=message,
        target_id=target_id,
        slice_id=slice_id,
        next_owner=next_owner,
        owner=owner,
        evidence_refs=evidence_refs,
    )
    payload: dict[str, Any] = {
        "timestamp": _utc_now(),
        "event": "failure",
        "skill": context.skill,
        "stage": context.stage,
        "reason_code": context.reason_code,
        "message": context.message,
        "recovery_suggestions": list(context.recovery_suggestions),
        "improvement_suggestions": list(context.improvement_suggestions),
        "evidence_refs": list(context.evidence_refs),
    }
    if context.target_id:
        payload["target_id"] = context.target_id
    if context.slice_id:
        payload["slice_id"] = context.slice_id
    if context.next_owner:
        payload["next_owner"] = context.next_owner
    if context.owner:
        payload["owner"] = context.owner
    append_event(event_log_path, payload)
    return context


def record_failure_for_stop_reason(
    event_log_path: Path,
    *,
    skill: str,
    stage: str,
    stop_reason: Mapping[str, Any] | None,
    target_id: str = "",
    slice_id: str = "",
    next_owner: str = "",
    evidence_refs: Sequence[str] | None = None,
) -> FailureContext | None:
    if stop_reason is None:
        return None
    reason_code = normalize_reason_code(stop_reason.get("kind"))
    if not is_failure_reason(reason_code):
        return None

    refs = _coerce_refs(evidence_refs)
    paths = stop_reason.get("paths")
    if isinstance(paths, list):
        refs = _dedupe([*refs, *[str(item) for item in paths if str(item).strip()]])
    message = _normalize_text(stop_reason.get("message")) or (
        f"{skill} stopped with {reason_code}."
    )
    return record_failure(
        event_log_path,
        skill=skill,
        stage=stage,
        reason_code=reason_code,
        message=message,
        target_id=target_id,
        slice_id=slice_id,
        next_owner=next_owner,
        owner=_normalize_text(stop_reason.get("owner")),
        evidence_refs=refs,
    )


def render_failure_summary(context: FailureContext) -> str:
    lines = [
        f"Failure [{context.reason_code}]: {context.message}",
        f"Logged failure to {context.logged_to}.",
    ]
    if context.recovery_suggestions:
        lines.append("Recovery suggestions:")
        lines.extend(f"- {item}" for item in context.recovery_suggestions)
    if context.improvement_suggestions:
        lines.append("Improvement suggestions:")
        lines.extend(f"- {item}" for item in context.improvement_suggestions)
    return "\n".join(lines)
