from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


def _require_non_empty_string(payload: Dict[str, Any], field_name: str) -> str:
    value = payload.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Request handoff field '{field_name}' must be a non-empty string.")
    return value.strip()


def _normalize_optional_string(payload: Dict[str, Any], field_name: str) -> Optional[str]:
    value = payload.get(field_name)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"Request handoff field '{field_name}' must be a string when present.")
    normalized = value.strip()
    return normalized or None


def _normalize_string_list(payload: Dict[str, Any], field_name: str) -> List[str]:
    value = payload.get(field_name)
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"Request handoff field '{field_name}' must be a list of strings.")
    normalized: List[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(
                f"Request handoff field '{field_name}' must contain non-empty strings."
            )
        normalized.append(item.strip())
    return list(dict.fromkeys(normalized))


@dataclass
class RequestHandoffRecord:
    request_id: str
    source_skill: str
    target_id: str
    target_path: str
    route_decision: str
    next_owner: str
    action: str
    updated_at: str
    classification: str = "request_route"
    planning_status: Optional[str] = None
    active_subfeature: Optional[str] = None
    summary: Optional[str] = None
    reason: Optional[str] = None
    evidence_refs: List[str] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "RequestHandoffRecord":
        return cls(
            request_id=_require_non_empty_string(payload, "request_id"),
            source_skill=_require_non_empty_string(payload, "source_skill"),
            target_id=_require_non_empty_string(payload, "target_id"),
            target_path=_require_non_empty_string(payload, "target_path"),
            route_decision=_require_non_empty_string(payload, "route_decision"),
            next_owner=_require_non_empty_string(payload, "next_owner"),
            action=_require_non_empty_string(payload, "action"),
            updated_at=_require_non_empty_string(payload, "updated_at"),
            classification=_require_non_empty_string(payload, "classification"),
            planning_status=_normalize_optional_string(payload, "planning_status"),
            active_subfeature=_normalize_optional_string(payload, "active_subfeature"),
            summary=_normalize_optional_string(payload, "summary"),
            reason=_normalize_optional_string(payload, "reason"),
            evidence_refs=_normalize_string_list(payload, "evidence_refs"),
            open_questions=_normalize_string_list(payload, "open_questions"),
        )


def write_request_handoff(path: Path, payload: RequestHandoffRecord) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload.to_dict(), indent=2) + "\n", encoding="utf-8")


def read_request_handoff(path: Path) -> RequestHandoffRecord:
    return RequestHandoffRecord.from_dict(json.loads(path.read_text(encoding="utf-8")))
