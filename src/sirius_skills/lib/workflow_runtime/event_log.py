from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from sirius_skills.lib.workflow_runtime.locking import locked_file


def append_event(path: Path, event: Dict[str, Any]) -> None:
    with locked_file(path) as handle:
        handle.seek(0, 2)
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def read_events(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    events: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped:
            events.append(json.loads(stripped))
    return events
