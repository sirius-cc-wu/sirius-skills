"""Repository layer for planning feature metadata and registry file I/O.

All direct JSON reads and writes for planning metadata (``.planning-meta.json``)
and the planning registry (``registry.json`` / ``README.md``) are centralised
here.  Command modules retain normalisation and scope-resolution logic but
delegate raw file operations to these helpers.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from sirius_skills.lib.workflow_state.storage import read_text, write_json_object, write_text


METADATA_FILE = ".planning-meta.json"
SUBFEATURE_METADATA_FILE = ".subfeature-meta.json"
REGISTRY_JSON_KEY = "features"
REGISTRY_HEADER = (
    "# Planning Registry\n\n"
    "| Feature | Status | Updated | Path |\n"
    "|---|---|---|---|\n"
)


def metadata_path(feature_dir: Path) -> Path:
    """Return the canonical metadata file path for a planning feature directory."""
    return feature_dir / METADATA_FILE


def subfeature_metadata_path(feature_dir: Path) -> Path:
    """Return the subfeature-meta sidecar path inside a feature directory."""
    return feature_dir / SUBFEATURE_METADATA_FILE


def ensure_registry(planning_dir: Path) -> None:
    """Create planning registry files (README.md and registry.json) if absent."""
    planning_dir.mkdir(parents=True, exist_ok=True)
    readme = planning_dir / "README.md"
    registry = planning_dir / "registry.json"
    if not readme.exists():
        write_text(readme, REGISTRY_HEADER)
    if not registry.exists():
        write_json_object(registry, {REGISTRY_JSON_KEY: []})


def read_registry_json(registry_path: Path) -> List[Dict[str, Any]]:
    """Load raw rows from a planning registry.json file.

    Returns an empty list if the file does not exist.
    Supports both list-form and object-form (``{"features": [...]}``) JSON.
    """
    if not registry_path.exists():
        return []
    try:
        payload = json.loads(read_text(registry_path))
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Planning registry JSON is not valid JSON."
        ) from exc
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        rows = payload.get(REGISTRY_JSON_KEY)
        if rows is None:
            return []
        if not isinstance(rows, list):
            raise RuntimeError(
                f"Planning registry field '{REGISTRY_JSON_KEY}' must be a list."
            )
        return rows
    raise RuntimeError("Planning registry JSON must be a JSON object or list.")


def write_registry_json(registry_path: Path, rows: List[Dict[str, Any]]) -> None:
    """Write rows to the planning registry.json file."""
    write_json_object(registry_path, {REGISTRY_JSON_KEY: rows})


def read_metadata_raw(feature_dir: Path) -> Dict[str, Any]:
    """Load raw planning metadata JSON for a feature directory.

    Raises RuntimeError if the metadata file is absent or malformed.
    """
    path = metadata_path(feature_dir)
    if not path.exists():
        raise RuntimeError(f"Planning metadata not found at '{path}'.")
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise RuntimeError("Planning metadata is not valid JSON.") from exc


def write_metadata_raw(feature_dir: Path, data: Dict[str, Any]) -> None:
    """Persist planning metadata JSON to the feature directory."""
    feature_dir.mkdir(parents=True, exist_ok=True)
    write_json_object(metadata_path(feature_dir), data)
