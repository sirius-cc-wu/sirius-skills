"""Repository layer for execution-slice metadata and registry file I/O.

All direct JSON reads and writes for slice metadata (``.slice-meta.json``)
and the slice registry (``registry.json`` / ``README.md``) are centralised
here.  Command modules retain normalisation and scope-resolution logic but
delegate raw file operations to these helpers.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from sirius_skills.lib.workflow_state.storage import read_text, write_json_object, write_text


SLICE_METADATA_FILE = ".slice-meta.json"
REGISTRY_JSON_KEY = "slices"
REGISTRY_HEADER = (
    "# Slice Registry\n\n"
    "| ID | Feature | Status | Updated | Closed | Path |\n"
    "|---|---|---|---|---|---|\n"
)


def slice_metadata_path(slice_dir: Path) -> Path:
    """Return the canonical metadata file path for a slice directory."""
    return slice_dir / SLICE_METADATA_FILE


def ensure_registry(specs_dir: Path) -> None:
    """Create slice registry files (README.md and registry.json) if absent.

    Only creates files when *both* are missing; the command-layer
    ``ensure_registry`` handles the migration case (markdown → JSON).
    """
    specs_dir.mkdir(parents=True, exist_ok=True)
    registry = specs_dir / "registry.json"
    readme = specs_dir / "README.md"
    if not registry.exists() and not readme.exists():
        write_text(readme, REGISTRY_HEADER)
        write_json_object(registry, {"version": 1, REGISTRY_JSON_KEY: []})


def read_registry_json(registry_path: Path) -> List[Dict[str, Any]]:
    """Load raw rows from a slice registry.json file.

    Returns an empty list if the file does not exist.
    Supports both list-form and object-form (``{"slices": [...]}``) JSON.
    """
    if not registry_path.exists():
        return []
    try:
        payload = json.loads(read_text(registry_path))
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Slice registry JSON is not valid JSON."
        ) from exc
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        rows = payload.get(REGISTRY_JSON_KEY)
        if rows is None:
            return []
        if not isinstance(rows, list):
            raise RuntimeError(
                f"Slice registry field '{REGISTRY_JSON_KEY}' must be a list."
            )
        return rows
    raise RuntimeError("Slice registry JSON must be a JSON object or list.")


def write_registry_json(
    registry_path: Path,
    rows: List[Dict[str, Any]],
    generated_at: str = "",
) -> None:
    """Write rows to the slice registry.json file.

    Includes a ``version`` field and optionally a ``generated_at`` timestamp.
    """
    payload: Dict[str, Any] = {"version": 1, REGISTRY_JSON_KEY: rows}
    if generated_at:
        payload["generated_at"] = generated_at
    write_json_object(registry_path, payload)


def read_slice_metadata_raw(slice_dir: Path) -> Dict[str, Any]:
    """Load raw slice metadata JSON.

    Returns an empty dict if the metadata file is absent.
    Raises RuntimeError on malformed JSON or non-object payload.
    """
    path = slice_metadata_path(slice_dir)
    if not path.exists():
        return {}
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Slice metadata is not valid JSON: {path}"
        ) from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"Slice metadata must be a JSON object: {path}")
    return payload


def write_slice_metadata_raw(slice_dir: Path, data: Dict[str, Any]) -> None:
    """Persist slice metadata JSON to the slice directory."""
    write_json_object(slice_metadata_path(slice_dir), data)
