"""Repository layer for proposal metadata and registry file I/O.

All direct JSON reads and writes for proposal metadata (``.proposal-meta.json``)
and the proposal registry (``registry.json`` / ``README.md``) are centralised
here.  Command modules retain normalisation and scope-resolution logic but
delegate raw file operations to these helpers.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from sirius_skills.lib.workflow_state.storage import read_text, write_json_object, write_text


METADATA_FILE = ".proposal-meta.json"
REGISTRY_JSON_KEY = "proposals"
REGISTRY_HEADER = (
    "# Proposal Registry\n\n"
    "| Proposal | Status | Updated | Path |\n"
    "|---|---|---|---|\n"
)


def metadata_path(proposal_dir: Path) -> Path:
    """Return the canonical metadata file path for a proposal directory."""
    return proposal_dir / METADATA_FILE


def ensure_registry(proposal_dir: Path) -> None:
    """Create proposal registry files (README.md and registry.json) if absent."""
    proposal_dir.mkdir(parents=True, exist_ok=True)
    readme = proposal_dir / "README.md"
    registry = proposal_dir / "registry.json"
    if not readme.exists():
        write_text(readme, REGISTRY_HEADER)
    if not registry.exists():
        write_json_object(registry, {REGISTRY_JSON_KEY: []})


def read_registry_json(registry_path: Path) -> List[Dict[str, Any]]:
    """Load raw rows from a proposal registry.json file.

    Returns an empty list if the file does not exist.
    Supports both list-form and object-form (``{"proposals": [...]}``) JSON.
    """
    if not registry_path.exists():
        return []
    try:
        payload = json.loads(read_text(registry_path))
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Proposal registry JSON is not valid JSON."
        ) from exc
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        rows = payload.get(REGISTRY_JSON_KEY)
        if rows is None:
            return []
        if not isinstance(rows, list):
            raise RuntimeError(
                f"Proposal registry field '{REGISTRY_JSON_KEY}' must be a list."
            )
        return rows
    raise RuntimeError("Proposal registry JSON must be a JSON object or list.")


def write_registry_json(registry_path: Path, rows: List[Dict[str, Any]]) -> None:
    """Write rows to the proposal registry.json file."""
    write_json_object(registry_path, {REGISTRY_JSON_KEY: rows})


def read_metadata_raw(proposal_dir: Path) -> Dict[str, Any]:
    """Load raw proposal metadata JSON.

    Raises RuntimeError if the metadata file is absent or malformed.
    """
    path = metadata_path(proposal_dir)
    if not path.exists():
        raise RuntimeError(f"Proposal metadata not found at '{path}'.")
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise RuntimeError("Proposal metadata is not valid JSON.") from exc


def write_metadata_raw(proposal_dir: Path, data: Dict[str, Any]) -> None:
    """Persist proposal metadata JSON to the proposal directory."""
    proposal_dir.mkdir(parents=True, exist_ok=True)
    write_json_object(metadata_path(proposal_dir), data)
