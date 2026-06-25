from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=str(path.parent), delete=False
    ) as handle:
        handle.write(content)
        temp_path = Path(handle.name)
    os.replace(temp_path, path)


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{label} is not valid JSON: {path}") from exc

    if not isinstance(payload, dict):
        raise RuntimeError(f"{label} must be a JSON object: {path}")
    return payload


def write_json_object(path: Path, payload: dict[str, Any]) -> None:
    write_text(path, json.dumps(payload, indent=2) + "\n")
