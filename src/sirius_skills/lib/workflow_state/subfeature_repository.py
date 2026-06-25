"""Repository layer for subfeature metadata and registry file I/O.

All direct JSON reads and writes for subfeature metadata (``.subfeature-meta.json``)
and the subfeature registry under ``<feature>/subfeatures/`` are centralised
here.  Command modules retain normalisation and parent-feature lookup logic but
delegate raw file operations to these helpers.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from sirius_skills.lib.workflow_state.storage import read_text, write_json_object, write_text


METADATA_FILE = ".subfeature-meta.json"
SUBFEATURES_DIR_NAME = "subfeatures"
REGISTRY_JSON_KEY = "subfeatures"
REGISTRY_HEADER = (
    "# Subfeature Registry\n\n"
    "| Subfeature | Status | Type | Updated | Path |\n"
    "|---|---|---|---|---|\n"
)


def metadata_path(subfeature_dir: Path) -> Path:
    """Return the canonical metadata file path for a subfeature directory."""
    return subfeature_dir / METADATA_FILE


def registry_paths(feature_dir: Path) -> Tuple[Path, Path, Path]:
    """Return ``(subfeatures_dir, readme_path, registry_json_path)`` for a feature."""
    subfeatures_dir = feature_dir / SUBFEATURES_DIR_NAME
    return subfeatures_dir, subfeatures_dir / "README.md", subfeatures_dir / "registry.json"


def ensure_registry(feature_dir: Path) -> None:
    """Create subfeature registry files under ``<feature>/subfeatures/`` if absent."""
    subfeatures_dir, readme, registry = registry_paths(feature_dir)
    subfeatures_dir.mkdir(parents=True, exist_ok=True)
    if not readme.exists():
        write_text(readme, REGISTRY_HEADER)
    if not registry.exists():
        write_json_object(registry, {REGISTRY_JSON_KEY: []})


def read_registry_json(registry_path: Path) -> List[Dict[str, Any]]:
    """Load raw rows from a subfeature registry.json file.

    Returns an empty list if the file does not exist.
    Supports both list-form and object-form (``{"subfeatures": [...]}``) JSON.
    """
    if not registry_path.exists():
        return []
    try:
        payload = json.loads(read_text(registry_path))
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Subfeature registry JSON is not valid JSON."
        ) from exc
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        rows = payload.get(REGISTRY_JSON_KEY)
        if rows is None:
            return []
        if not isinstance(rows, list):
            raise RuntimeError(
                f"Subfeature registry field '{REGISTRY_JSON_KEY}' must be a list."
            )
        return rows
    raise RuntimeError("Subfeature registry JSON must be a JSON object or list.")


def write_registry_json(registry_path: Path, rows: List[Dict[str, Any]]) -> None:
    """Write rows to the subfeature registry.json file."""
    write_json_object(registry_path, {REGISTRY_JSON_KEY: rows})


def read_metadata_raw(subfeature_dir: Path) -> Dict[str, Any]:
    """Load raw subfeature metadata JSON.

    Raises RuntimeError if the metadata file is absent or malformed.
    """
    path = metadata_path(subfeature_dir)
    if not path.exists():
        raise RuntimeError(f"Subfeature metadata not found at '{path}'.")
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise RuntimeError("Subfeature metadata is not valid JSON.") from exc


def write_metadata_raw(subfeature_dir: Path, data: Dict[str, Any]) -> None:
    """Persist subfeature metadata JSON to the subfeature directory."""
    subfeature_dir.mkdir(parents=True, exist_ok=True)
    write_json_object(metadata_path(subfeature_dir), data)
