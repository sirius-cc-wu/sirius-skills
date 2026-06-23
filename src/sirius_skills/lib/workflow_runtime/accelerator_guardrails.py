from __future__ import annotations

from typing import Any, Iterable, Mapping, Optional


_STOP_KIND_SYNONYMS = {
    "review_required": "review_boundary",
}


def normalize_reason_code(value: object) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    text = text.replace("-", "_").replace(" ", "_")
    while "__" in text:
        text = text.replace("__", "_")
    return _STOP_KIND_SYNONYMS.get(text, text)


def dedupe_reason_codes(values: Iterable[object]) -> list[str]:
    result: list[str] = []
    for item in values:
        code = normalize_reason_code(item)
        if code and code not in result:
            result.append(code)
    return result


def normalize_stop_reason(
    stop_reason: object, *, default_kind: Optional[str] = None
) -> Optional[dict[str, Any]]:
    default_code = normalize_reason_code(default_kind)
    if isinstance(stop_reason, Mapping):
        payload = dict(stop_reason)
        payload_kind = normalize_reason_code(payload.get("kind"))
        if payload_kind is None:
            payload_kind = default_code
        if payload_kind is None:
            return None
        payload["kind"] = payload_kind
        return payload
    if default_code is None:
        return None
    return {"kind": default_code}


def classify_stop_reason_from_message(message: str, *, stage: str) -> str:
    lowered = message.lower()
    if stage == "planning":
        if "missing required file" in lowered or "requires a non-empty review note" in lowered:
            return "missing_required_input"
        if "ambiguous" in lowered:
            return "ambiguity"
        if "invalid status transition" in lowered:
            return "invalid_transition"
        return "validation_failed"
    if stage == "execution":
        if (
            "missing_" in lowered
            or "_without_" in lowered
            or "missing " in lowered
            or "without_" in lowered
            or "without " in lowered
            or "status_mismatch" in lowered
        ):
            return "missing_required_input"
        if "invalid status transition" in lowered:
            return "invalid_transition"
        return "verification_failed"
    raise ValueError(f"Unsupported stop-reason classification stage: {stage}")


def _normalize_approval_gate(payload: Optional[Mapping[str, Any]]) -> dict[str, Any]:
    source = dict(payload) if isinstance(payload, Mapping) else {}
    required = bool(source.get("required", False))
    state = normalize_reason_code(source.get("state"))
    if not state:
        state = "waiting_approval" if required else "not_required"
    if required and state == "not_required":
        state = "waiting_approval"
    result: dict[str, Any] = {"required": required, "state": state}
    if "reason" in source:
        result["reason"] = source.get("reason")
    if "approval_path" in source:
        result["approval_path"] = source.get("approval_path")
    return result


def _normalize_commit_checkpoint(payload: Optional[Mapping[str, Any]]) -> dict[str, Any]:
    source = dict(payload) if isinstance(payload, Mapping) else {}
    required = bool(source.get("required", False))
    state = normalize_reason_code(source.get("state"))
    if not state:
        state = "waiting_commit" if required else "not_required"
    if required and state == "not_required":
        state = "waiting_commit"
    result: dict[str, Any] = {"required": required, "state": state}
    if "slice_id" in source:
        result["slice_id"] = source.get("slice_id")
    return result


def build_accelerator_readiness(
    *,
    next_owner: Optional[str],
    automatable_owners: Iterable[str],
    blocked_by: Iterable[object],
    stop_reason: object = None,
    approval_gate: Optional[Mapping[str, Any]] = None,
    commit_checkpoint: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    normalized_stop_reason = normalize_stop_reason(stop_reason)
    normalized_blocked_by = dedupe_reason_codes(blocked_by)
    if normalized_stop_reason is not None:
        reason_kind = normalize_reason_code(normalized_stop_reason.get("kind"))
        if reason_kind and reason_kind not in normalized_blocked_by:
            normalized_blocked_by.append(reason_kind)

    owner = str(next_owner) if isinstance(next_owner, str) else next_owner
    allowed_owners = {
        str(item).strip()
        for item in automatable_owners
        if isinstance(item, str) and str(item).strip()
    }

    normalized_approval_gate = _normalize_approval_gate(approval_gate)
    normalized_commit_checkpoint = _normalize_commit_checkpoint(commit_checkpoint)
    return {
        "can_proceed": bool(owner in allowed_owners and not normalized_blocked_by),
        "next_owner": owner,
        "blocked_by": normalized_blocked_by,
        "stop_reason": normalized_stop_reason,
        "approval_gate": normalized_approval_gate,
        "commit_checkpoint": normalized_commit_checkpoint,
    }
