from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional

from sirius_skills.lib.workflow_runtime.locking import locked_file


@dataclass
class LearningRecord:
    id: str
    scope: str
    topic: str
    guidance: str
    skill: str
    state: str
    evidence_refs: List[str] = field(default_factory=list)
    recorded_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict) -> "LearningRecord":
        return cls(
            id=str(payload["id"]),
            scope=str(payload["scope"]),
            topic=str(payload["topic"]),
            guidance=str(payload["guidance"]),
            skill=str(payload["skill"]),
            state=str(payload["state"]),
            evidence_refs=list(payload.get("evidence_refs", [])),
            recorded_at=str(payload.get("recorded_at", "")),
            updated_at=str(payload.get("updated_at", "")),
        )


def append_learning(path: Path, record: LearningRecord) -> None:
    with locked_file(path) as handle:
        handle.seek(0, 2)
        handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")


def read_learnings(path: Path) -> List[LearningRecord]:
    if not path.exists():
        return []
    records: List[LearningRecord] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped:
            records.append(LearningRecord.from_dict(json.loads(stripped)))
    return records


def query_learnings(
    path: Path,
    *,
    scope: Optional[str] = None,
    skill: Optional[str] = None,
    states: Optional[Iterable[str]] = None,
) -> List[LearningRecord]:
    allowed_states = set(states) if states is not None else None
    results: List[LearningRecord] = []
    for record in read_learnings(path):
        if scope is not None and record.scope != scope:
            continue
        if skill is not None and record.skill != skill:
            continue
        if allowed_states is not None and record.state not in allowed_states:
            continue
        results.append(record)
    return results


def update_learning_state(path: Path, learning_id: str, new_state: str) -> LearningRecord:
    path.parent.mkdir(parents=True, exist_ok=True)
    updated: Optional[LearningRecord] = None
    with locked_file(path) as handle:
        handle.seek(0)
        payload = handle.read()
        records = [
            LearningRecord.from_dict(json.loads(line))
            for line in payload.splitlines()
            if line.strip()
        ]
        timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        for record in records:
            if record.id == learning_id:
                record.state = new_state
                record.updated_at = timestamp
                updated = record
                break
        if updated is None:
            raise ValueError(f"Unknown learning id: {learning_id}")
        handle.seek(0)
        handle.truncate()
        handle.write(
            "".join(json.dumps(record.to_dict(), sort_keys=True) + "\n" for record in records)
        )
    return updated
