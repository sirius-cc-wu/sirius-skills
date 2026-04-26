from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional


APPROVAL_GATE_FILE = ".approval-gate.json"
APPROVAL_FINGERPRINT_FILES = (
    "discover.md",
    "system-design.md",
    "ui-design.md",
    "slice-planning.md",
    "slice-traceability.md",
    "user-stories.md",
    "reference-research.md",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def approval_gate_path(target_dir: Path) -> Path:
    return target_dir / APPROVAL_GATE_FILE


def compute_planning_fingerprint(target_dir: Path) -> str:
    hasher = hashlib.sha256()
    for filename in APPROVAL_FINGERPRINT_FILES:
        path = target_dir / filename
        if not path.is_file():
            continue
        hasher.update(f"FILE:{filename}\n".encode("utf-8"))
        hasher.update(path.read_bytes())
        hasher.update(b"\n")
    return hasher.hexdigest()


def read_approval_record(path: Path) -> Optional[Dict[str, object]]:
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"_parse_error": True}
    if not isinstance(payload, dict):
        return {"_parse_error": True}
    return payload


def evaluate_planning_approval_gate(
    *,
    target_id: str,
    target_path: str,
    target_dir: Path,
    planning_metadata: Dict[str, object],
) -> Dict[str, object]:
    planning_status = str(planning_metadata["status"])
    gate_path = approval_gate_path(target_dir)
    gate_payload: Dict[str, object] = {
        "required": planning_status == "planning_reviewed",
        "decision": "not_required",
        "reason": None,
        "planning_status": planning_status,
        "planning_updated_at": str(planning_metadata.get("updated_at") or ""),
        "approval_path": str(gate_path),
    }
    if planning_status != "planning_reviewed":
        return gate_payload

    current_fingerprint = compute_planning_fingerprint(target_dir)
    record = read_approval_record(gate_path)
    gate_payload["current_planning_fingerprint"] = current_fingerprint

    if record is None:
        gate_payload["decision"] = "waiting_approval"
        gate_payload["reason"] = "approval_not_recorded"
        return gate_payload
    if record.get("_parse_error"):
        gate_payload["decision"] = "invalidated"
        gate_payload["reason"] = "approval_record_invalid"
        return gate_payload

    gate_payload["approval_record"] = dict(record)
    gate_payload["approved_at"] = record.get("approved_at")
    gate_payload["approval_note"] = record.get("approval_note")

    if not bool(record.get("approved")):
        gate_payload["decision"] = "waiting_approval"
        gate_payload["reason"] = "approval_not_granted"
        return gate_payload
    if str(record.get("target_id") or "") != target_id:
        gate_payload["decision"] = "invalidated"
        gate_payload["reason"] = "target_mismatch"
        return gate_payload
    if str(record.get("target_path") or "") != target_path:
        gate_payload["decision"] = "invalidated"
        gate_payload["reason"] = "target_path_mismatch"
        return gate_payload
    if str(record.get("planning_status") or "") != "planning_reviewed":
        gate_payload["decision"] = "invalidated"
        gate_payload["reason"] = "planning_status_mismatch"
        return gate_payload
    if str(record.get("planning_updated_at") or "") != str(
        planning_metadata.get("updated_at") or ""
    ):
        gate_payload["decision"] = "invalidated"
        gate_payload["reason"] = "planning_metadata_changed"
        return gate_payload
    if str(record.get("planning_fingerprint") or "") != current_fingerprint:
        gate_payload["decision"] = "invalidated"
        gate_payload["reason"] = "planning_artifacts_changed"
        return gate_payload

    gate_payload["decision"] = "approved"
    gate_payload["reason"] = "approval_valid"
    return gate_payload


def write_planning_approval_record(
    *,
    target_id: str,
    target_path: str,
    target_dir: Path,
    planning_metadata: Dict[str, object],
    approval_note: Optional[str] = None,
) -> Dict[str, object]:
    note = approval_note.strip() if isinstance(approval_note, str) else ""
    payload: Dict[str, object] = {
        "version": 1,
        "approved": True,
        "approved_at": utc_now(),
        "target_id": target_id,
        "target_path": target_path,
        "planning_status": str(planning_metadata["status"]),
        "planning_updated_at": str(planning_metadata.get("updated_at") or ""),
        "planning_fingerprint": compute_planning_fingerprint(target_dir),
        "approval_note": note or None,
    }
    path = approval_gate_path(target_dir)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return {
        "recorded": True,
        "approval_path": str(path),
        "target_id": target_id,
        "target_path": target_path,
        "approved_at": payload["approved_at"],
        "approval_note": payload["approval_note"],
    }
