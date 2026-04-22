from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class CheckpointRecord:
    run_id: str
    state: str
    payload: Dict[str, Any] = field(default_factory=dict)
    stale_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "CheckpointRecord":
        return cls(
            run_id=str(payload["run_id"]),
            state=str(payload["state"]),
            payload=dict(payload.get("payload", {})),
            stale_reason=payload.get("stale_reason"),
        )


def write_checkpoint(path: Path, record: CheckpointRecord) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record.to_dict(), indent=2) + "\n", encoding="utf-8")


def load_checkpoint(path: Path) -> CheckpointRecord:
    return CheckpointRecord.from_dict(json.loads(path.read_text(encoding="utf-8")))


def mark_checkpoint_stale(path: Path, reason: str) -> CheckpointRecord:
    record = load_checkpoint(path)
    record.stale_reason = reason
    write_checkpoint(path, record)
    return record
