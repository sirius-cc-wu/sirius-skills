#!/usr/bin/env python3

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
SKILLS_DIR = SCRIPT_DIR.parents[1]
AUDIT_SCRIPT_DIR = SKILLS_DIR / "audit-artifacts" / "scripts"

if str(AUDIT_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(AUDIT_SCRIPT_DIR))

from artifact_inventory import load_inventory, normalize_dir_relpath  # noqa: E402


VALID_ARTIFACT_TYPES = ("proposal", "subfeature", "slice")
PROPOSAL_CANDIDATE_STATUSES = {"rejected", "superseded", "promoted"}


@dataclass
class ArchiveCandidate:
    artifact_type: str
    artifact_id: str
    status: str
    path: str
    reason: str
    archivable: bool

    def to_dict(self) -> Dict[str, object]:
        return {
            "artifact_type": self.artifact_type,
            "artifact_id": self.artifact_id,
            "status": self.status,
            "path": self.path,
            "reason": self.reason,
            "archivable": self.archivable,
        }


class ArchiveUsageError(RuntimeError):
    pass


def _safe_read_metadata(reader, path: Path) -> Optional[Dict[str, object]]:
    try:
        return reader(str(path))
    except RuntimeError:
        return None


def discover_candidates(artifact_type: Optional[str] = None) -> List[ArchiveCandidate]:
    inventory = load_inventory()
    candidates: List[ArchiveCandidate] = []
    selected = {artifact_type} if artifact_type else set(VALID_ARTIFACT_TYPES)

    if "proposal" in selected:
        for proposal_dir in inventory.proposal_dirs:
            metadata = _safe_read_metadata(inventory.context.propose.read_metadata, proposal_dir)
            if metadata is None:
                continue
            status = str(metadata.get("status", ""))
            if status not in PROPOSAL_CANDIDATE_STATUSES:
                continue
            candidates.append(
                ArchiveCandidate(
                    artifact_type="proposal",
                    artifact_id=proposal_dir.name,
                    status=status,
                    path=normalize_dir_relpath(proposal_dir),
                    reason=f"Proposal status '{status}' is archive-eligible.",
                    archivable=False,
                )
            )

    if "subfeature" in selected:
        for subfeature_dirs in inventory.subfeature_dirs_by_feature.values():
            for subfeature_dir in subfeature_dirs:
                metadata = _safe_read_metadata(
                    inventory.context.subfeatures.read_metadata, subfeature_dir
                )
                if metadata is None:
                    continue
                status = str(metadata.get("status", ""))
                if status != "finalized":
                    continue
                candidates.append(
                    ArchiveCandidate(
                        artifact_type="subfeature",
                        artifact_id=subfeature_dir.name,
                        status=status,
                        path=normalize_dir_relpath(subfeature_dir),
                        reason="Finalized subfeature is archive-eligible.",
                        archivable=False,
                    )
                )

    if "slice" in selected:
        for row in inventory.slice_rows:
            status = str(row.get("status", ""))
            if status != "closed":
                continue
            candidates.append(
                ArchiveCandidate(
                    artifact_type="slice",
                    artifact_id=str(row["id"]),
                    status=status,
                    path=str(row["path"]),
                    reason="Closed slice can be archived through the execution owner helper.",
                    archivable=True,
                )
            )

    return sorted(candidates, key=lambda item: (item.artifact_type, item.artifact_id))


def build_archive_result(
    artifact_type: Optional[str] = None,
    artifact_id: Optional[str] = None,
    apply: bool = False,
) -> Dict[str, object]:
    if artifact_id and not artifact_type:
        raise ArchiveUsageError("Use --artifact-type with --artifact-id.")

    candidates = discover_candidates(artifact_type)
    if artifact_type and artifact_id:
        candidates = [
            candidate
            for candidate in candidates
            if candidate.artifact_type == artifact_type and candidate.artifact_id == artifact_id
        ]

    applied = None
    if apply:
        if artifact_type != "slice" or not artifact_id:
            raise ArchiveUsageError(
                "Apply mode currently requires --artifact-type slice and --artifact-id."
            )
        inventory = load_inventory()
        target = next(
            (candidate for candidate in candidates if candidate.artifact_type == "slice"),
            None,
        )
        if target is None:
            raise ArchiveUsageError(f"Archivable slice not found: {artifact_id}")
        _, _, slice_registry = inventory.context.execution.get_registry_paths(required_config=False)
        rows = inventory.context.execution.load_registry_json(slice_registry)
        slice_row = inventory.context.execution.resolve_slice(rows, artifact_id)
        if slice_row is None:
            raise ArchiveUsageError(f"Slice not found: {artifact_id}")
        ok, message, updated_slice = inventory.context.execution.archive_slice(rows, slice_row)
        if not ok:
            raise ArchiveUsageError(message)
        applied = {
            "artifact_type": "slice",
            "artifact_id": str(updated_slice["id"]),
            "path": str(updated_slice["path"]),
            "message": message,
        }

    return {
        "ok": True,
        "apply": apply,
        "summary": {
            "candidate_count": len(candidates),
            "archivable_count": sum(1 for candidate in candidates if candidate.archivable),
        },
        "candidates": [candidate.to_dict() for candidate in candidates],
        "applied": applied,
    }
