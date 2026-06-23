from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class HandoffPayload:
    target_type: str
    target_id: str
    planned_slice_id: str
    execution_slice_id: str
    execution_slice_path: str
    slice_status: str
    next_owner: str
    action: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "HandoffPayload":
        required = {
            "target_type",
            "target_id",
            "planned_slice_id",
            "execution_slice_id",
            "execution_slice_path",
            "slice_status",
            "next_owner",
            "action",
        }
        missing = sorted(required.difference(payload))
        if missing:
            raise ValueError(f"Missing handoff payload fields: {', '.join(missing)}")
        return cls(**{key: payload[key] for key in sorted(required)})


def write_handoff_payload(path: Path, payload: HandoffPayload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload.to_dict(), indent=2) + "\n", encoding="utf-8")


def read_handoff_payload(path: Path) -> HandoffPayload:
    return HandoffPayload.from_dict(json.loads(path.read_text(encoding="utf-8")))
