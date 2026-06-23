#!/usr/bin/env python3

from datetime import datetime, timedelta, timezone
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set


SCRIPT_DIR = Path(__file__).resolve().parent
IMPORT_PATH_CANDIDATES = (
    SCRIPT_DIR,
    SCRIPT_DIR.parent / "lib",
    SCRIPT_DIR.parents[2] / "lib",
    SCRIPT_DIR.parents[1] / "lib",
)

for candidate in reversed(IMPORT_PATH_CANDIDATES):
    if candidate.is_dir() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from sirius_skills.lib.workflow_state import build_semantic_preview, inspect_installed_skill_parity  # noqa: E402
from sirius_skills.lib.workflow_state.inventory import (  # noqa: E402
    iter_active_slice_rows,
    load_inventory,
    normalize_dir_relpath,
)
from sirius_skills.commands.metrics_store import read_metrics  # noqa: E402


VALID_ARTIFACT_TYPES = ("proposal", "feature", "subfeature", "slice")
VALID_GROUP_BY = ("overview", "status", "parent")


@dataclass
class ReportRecord:
    artifact_type: str
    artifact_id: str
    status: str
    path: str
    updated_at: Optional[str]
    parent_feature: Optional[str]
    is_stale: bool
    consolidation: Optional[Dict[str, object]] = None
    implementation_metrics: Optional[Dict[str, object]] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "artifact_type": self.artifact_type,
            "artifact_id": self.artifact_id,
            "status": self.status,
            "path": self.path,
            "updated_at": self.updated_at,
            "parent_feature": self.parent_feature,
            "is_stale": self.is_stale,
            "consolidation": self.consolidation,
            "implementation_metrics": self.implementation_metrics,
        }


def selected_types(raw_types: Sequence[str]) -> Set[str]:
    return set(raw_types) if raw_types else set(VALID_ARTIFACT_TYPES)


def parse_timestamp(value: object) -> Optional[datetime]:
    if not isinstance(value, str) or not value.strip():
        return None
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def is_stale(updated_at: Optional[str], stale_days: int, now: Optional[datetime] = None) -> bool:
    timestamp = parse_timestamp(updated_at)
    if timestamp is None:
        return False
    reference = now or datetime.now(timezone.utc)
    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=timezone.utc)
    else:
        reference = reference.astimezone(timezone.utc)
    return timestamp <= reference - timedelta(days=stale_days)


def _safe_read_metadata(reader, path: Path) -> Optional[Dict[str, object]]:
    try:
        return reader(str(path))
    except (RuntimeError, ValueError):
        return None


def _load_raw_metadata(path: Path) -> Optional[Dict[str, object]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def _load_metrics_sidecar(path: Path) -> Optional[Dict[str, object]]:
    try:
        return read_metrics(path)
    except RuntimeError:
        return None


def _normalize_string_list(value: object) -> List[str]:
    if not isinstance(value, list):
        return []
    normalized: List[str] = []
    seen = set()
    for item in value:
        if not isinstance(item, str):
            continue
        candidate = item.strip()
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        normalized.append(candidate)
    return normalized


def _extract_consolidation_summary(metadata: Optional[Dict[str, object]]) -> Optional[Dict[str, object]]:
    if not isinstance(metadata, dict):
        return None
    raw = metadata.get("consolidation")
    if not isinstance(raw, dict):
        return None
    disposition = raw.get("disposition")
    if not isinstance(disposition, str) or not disposition.strip():
        return None
    targets: List[Dict[str, str]] = []
    for item in raw.get("targets", []):
        if not isinstance(item, dict):
            continue
        kind = item.get("kind")
        ref = item.get("ref")
        change = item.get("change")
        if not all(isinstance(field, str) and field.strip() for field in (kind, ref, change)):
            continue
        targets.append(
            {
                "kind": kind.strip(),
                "ref": ref.strip(),
                "change": change.strip(),
            }
        )
    justification = raw.get("justification")
    return {
        "disposition": disposition.strip().lower(),
        "targets": targets,
        "historical_artifacts": _normalize_string_list(raw.get("historical_artifacts")),
        "surface_simplifications": _normalize_string_list(raw.get("surface_simplifications")),
        "justification": justification.strip() if isinstance(justification, str) and justification.strip() else None,
    }


def load_report_records(
    artifact_types: Optional[Sequence[str]] = None,
    stale_days: int = 30,
    now: Optional[datetime] = None,
    inventory=None,
) -> List[ReportRecord]:
    inventory = inventory or load_inventory()
    selected = selected_types(artifact_types or [])
    records: List[ReportRecord] = []

    if "proposal" in selected:
        for proposal_dir in inventory.proposal_dirs:
            metadata = _safe_read_metadata(inventory.context.propose.read_metadata, proposal_dir)
            if metadata is None:
                continue
            parent_feature = metadata.get("target_feature") or metadata.get("promoted_feature")
            records.append(
                ReportRecord(
                    artifact_type="proposal",
                    artifact_id=proposal_dir.name,
                    status=str(metadata.get("status", "unknown")),
                    path=normalize_dir_relpath(proposal_dir),
                    updated_at=metadata.get("updated_at") if isinstance(metadata.get("updated_at"), str) else None,
                    parent_feature=parent_feature if isinstance(parent_feature, str) and parent_feature.strip() else None,
                    is_stale=is_stale(metadata.get("updated_at"), stale_days, now),
                    consolidation=_extract_consolidation_summary(metadata),
                )
            )

    if "feature" in selected:
        for feature_dir in inventory.feature_dirs:
            metadata = _safe_read_metadata(inventory.context.planning.read_metadata, feature_dir)
            if metadata is None:
                continue
            records.append(
                ReportRecord(
                    artifact_type="feature",
                    artifact_id=feature_dir.name,
                    status=str(metadata.get("status", "unknown")),
                    path=normalize_dir_relpath(feature_dir),
                    updated_at=metadata.get("updated_at") if isinstance(metadata.get("updated_at"), str) else None,
                    parent_feature=feature_dir.name,
                    is_stale=is_stale(metadata.get("updated_at"), stale_days, now),
                    consolidation=_extract_consolidation_summary(metadata),
                    implementation_metrics=_load_metrics_sidecar(feature_dir),
                )
            )

    if "subfeature" in selected:
        for subfeature_dirs in inventory.subfeature_dirs_by_feature.values():
            for subfeature_dir in subfeature_dirs:
                metadata = _safe_read_metadata(inventory.context.subfeatures.read_metadata, subfeature_dir)
                if metadata is None:
                    metadata = _load_raw_metadata(subfeature_dir / ".subfeature-meta.json")
                if metadata is None:
                    continue
                parent_feature = metadata.get("parent_feature_slug")
                records.append(
                    ReportRecord(
                        artifact_type="subfeature",
                        artifact_id=subfeature_dir.name,
                        status=str(metadata.get("status", "unknown")),
                        path=normalize_dir_relpath(subfeature_dir),
                        updated_at=metadata.get("updated_at")
                        if isinstance(metadata.get("updated_at"), str)
                        else None,
                        parent_feature=parent_feature
                        if isinstance(parent_feature, str) and parent_feature.strip()
                        else None,
                        is_stale=is_stale(metadata.get("updated_at"), stale_days, now),
                        consolidation=_extract_consolidation_summary(metadata),
                        implementation_metrics=_load_metrics_sidecar(subfeature_dir),
                    )
                )

    if "slice" in selected:
        for row in iter_active_slice_rows(inventory):
            metadata = inventory.context.execution.load_slice_metadata(
                inventory.context.execution.slice_path_for_row(row)
            )
            updated_at = metadata.get("updated_at") if isinstance(metadata.get("updated_at"), str) else row.get("updated_at")
            records.append(
                ReportRecord(
                    artifact_type="slice",
                    artifact_id=str(row["id"]),
                    status=str(row.get("status", "unknown")),
                    path=str(row["path"]),
                    updated_at=updated_at if isinstance(updated_at, str) else None,
                    parent_feature=str(row.get("feature", "")) or None,
                    is_stale=is_stale(updated_at, stale_days, now),
                    consolidation=None,
                )
            )

    return sorted(records, key=lambda item: (item.artifact_type, item.artifact_id))


def summarize(records: Sequence[ReportRecord]) -> Dict[str, int]:
    return {
        "total": len(records),
        "stale": sum(1 for record in records if record.is_stale),
    }


def build_groups(records: Sequence[ReportRecord], group_by: str) -> List[Dict[str, object]]:
    buckets: Dict[str, Dict[str, object]] = {}
    for record in records:
        if group_by == "overview":
            key = record.artifact_type
        elif group_by == "status":
            key = record.status
        else:
            key = record.parent_feature or "(none)"
        bucket = buckets.setdefault(
            key,
            {
                "key": key,
                "count": 0,
                "stale": 0,
                "artifact_types": {},
            },
        )
        bucket["count"] += 1
        if record.is_stale:
            bucket["stale"] += 1
        artifact_types = bucket["artifact_types"]
        artifact_types[record.artifact_type] = artifact_types.get(record.artifact_type, 0) + 1
    return sorted(buckets.values(), key=lambda item: str(item["key"]))


def build_report_result(
    artifact_types: Optional[Sequence[str]] = None,
    group_by: str = "overview",
    stale_days: int = 30,
    now: Optional[datetime] = None,
    installed_skills: Optional[Sequence[Dict[str, object]]] = None,
    check_packaged_parity: bool = False,
) -> Dict[str, object]:
    if group_by not in VALID_GROUP_BY:
        raise ValueError(f"Unsupported group-by mode: {group_by}")
    inventory = load_inventory()
    records = load_report_records(
        artifact_types=artifact_types,
        stale_days=stale_days,
        now=now,
        inventory=inventory,
    )
    semantic_preview = build_semantic_preview(inventory, artifact_types or [])
    installed_parity = (
        inspect_installed_skill_parity(installed_skills=installed_skills)
        if check_packaged_parity
        else []
    )
    return {
        "ok": True,
        "group_by": group_by,
        "stale_days": stale_days,
        "check_packaged_parity": check_packaged_parity,
        "summary": {
            **summarize(records),
            "installed_parity_count": len(installed_parity),
            "semantic_preview_count": len(semantic_preview),
        },
        "groups": build_groups(records, group_by),
        "records": [record.to_dict() for record in records],
        "installed_parity": [record.to_dict() for record in installed_parity],
        "semantic_preview": [record.to_dict() for record in semantic_preview],
    }
