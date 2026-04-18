#!/usr/bin/env python3

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parents[1]
REPO_ROOT = SCRIPT_DIR.parents[2]
REPO_LIB_DIR = REPO_ROOT / "lib"
SKILL_LIB_DIR = SKILL_ROOT / "lib"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
if REPO_LIB_DIR.is_dir() and str(REPO_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(REPO_LIB_DIR))
if SKILL_LIB_DIR.is_dir() and str(SKILL_LIB_DIR) not in sys.path:
    sys.path.append(str(SKILL_LIB_DIR))

from workflow_state import inspect_installed_skill_parity  # noqa: E402
from workflow_state.inventory import (  # noqa: E402
    iter_subfeature_dirs,
    iter_traceability_records,
    load_inventory,
    normalize_dir_relpath,
    normalize_registry_path,
    planning_row_artifact_type,
)
from workflow_state.models import (  # noqa: E402
    Inventory,
    RegistryStatus,
    TraceabilityRecord,
)


VALID_ARTIFACT_TYPES = ("proposal", "feature", "subfeature", "slice")
FINDINGS_EXIT_CODE = 3


@dataclass(frozen=True)
class Finding:
    artifact_type: str
    artifact_id: str
    path: str
    category: str
    code: str
    severity: str
    message: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "artifact_type": self.artifact_type,
            "artifact_id": self.artifact_id,
            "path": self.path,
            "category": self.category,
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit proposals, features, subfeatures, and slices for missing files, "
            "registry drift, and broken cross-artifact links."
        )
    )
    parser.add_argument(
        "--artifact-type",
        action="append",
        choices=VALID_ARTIFACT_TYPES,
        default=[],
        help="Limit the audit to one or more artifact types. Repeatable.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a machine-readable result instead of human-readable text.",
    )
    return parser.parse_args()


def selected_types(raw_types: Sequence[str]) -> Set[str]:
    return set(raw_types) if raw_types else set(VALID_ARTIFACT_TYPES)


def include_artifact(selected: Set[str], artifact_type: str) -> bool:
    return artifact_type in selected


def add_finding(
    findings: List[Finding],
    selected: Set[str],
    artifact_type: str,
    artifact_id: str,
    path: str,
    category: str,
    code: str,
    severity: str,
    message: str,
) -> None:
    if include_artifact(selected, artifact_type):
        findings.append(
            Finding(
                artifact_type=artifact_type,
                artifact_id=artifact_id,
                path=path,
                category=category,
                code=code,
                severity=severity,
                message=message,
            )
        )


def _registry_findings(
    findings: List[Finding],
    selected: Set[str],
    status: RegistryStatus,
    observed_paths: Sequence[Path],
) -> None:
    should_report = status.root_exists or status.readme_exists or status.registry_exists or bool(
        observed_paths
    )
    if not should_report:
        return

    artifact_id = status.owner_id or f"{status.artifact_type}-registry"
    if not status.readme_exists:
        add_finding(
            findings,
            selected,
            status.artifact_type,
            artifact_id,
            status.readme_path,
            "validation",
            "missing_registry_readme",
            "warning",
            f"Missing README.md for the {status.artifact_type} registry.",
        )
    if not status.registry_exists:
        add_finding(
            findings,
            selected,
            status.artifact_type,
            artifact_id,
            status.registry_path,
            "validation",
            "missing_registry_json",
            "error",
            f"Missing registry.json for the {status.artifact_type} registry.",
        )
    if status.error:
        add_finding(
            findings,
            selected,
            status.artifact_type,
            artifact_id,
            status.registry_path,
            "validation",
            "invalid_registry_json",
            "error",
            status.error,
        )


def _compare_paths(
    findings: List[Finding],
    selected: Set[str],
    artifact_type: str,
    registry_paths: Set[str],
    disk_paths: Set[str],
    missing_code: str,
    orphan_code: str,
    owner_label: Optional[str] = None,
) -> None:
    owner_suffix = f" for {owner_label}" if owner_label else ""
    for path in sorted(registry_paths - disk_paths):
        add_finding(
            findings,
            selected,
            artifact_type,
            path.rstrip("/").split("/")[-1],
            path,
            "registry_drift",
            missing_code,
            "error",
            f"Registry entry points to a missing {artifact_type} directory{owner_suffix}.",
        )
    for path in sorted(disk_paths - registry_paths):
        add_finding(
            findings,
            selected,
            artifact_type,
            path.rstrip("/").split("/")[-1],
            path,
            "registry_drift",
            orphan_code,
            "warning",
            f"{artifact_type.title()} directory exists on disk but is missing from the registry{owner_suffix}.",
        )


def _safe_read_metadata(reader, artifact_type: str, artifact_id: str, path: Path) -> Tuple[Optional[Dict[str, object]], Optional[Finding]]:
    try:
        return reader(str(path)), None
    except (RuntimeError, ValueError) as exc:
        return None, Finding(
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            path=normalize_dir_relpath(path),
            category="validation",
            code="metadata_read_error",
            severity="error",
            message=str(exc),
        )


def _audit_proposals(
    inventory: Inventory, findings: List[Finding], selected: Set[str]
) -> Dict[str, Dict[str, object]]:
    metadata_by_id: Dict[str, Dict[str, object]] = {}
    for proposal_dir in inventory.proposal_dirs:
        proposal_id = proposal_dir.name
        metadata, error_finding = _safe_read_metadata(
            inventory.context.propose.read_metadata, "proposal", proposal_id, proposal_dir
        )
        if error_finding is not None:
            add_finding(
                findings,
                selected,
                error_finding.artifact_type,
                error_finding.artifact_id,
                error_finding.path,
                error_finding.category,
                error_finding.code,
                error_finding.severity,
                error_finding.message,
            )
            continue
        assert metadata is not None
        metadata_by_id[proposal_id] = metadata
        ok, issues, _ = inventory.context.propose.validate_proposal_state(
            str(proposal_dir), metadata
        )
        if ok:
            continue
        for issue in issues:
            add_finding(
                findings,
                selected,
                "proposal",
                proposal_id,
                normalize_dir_relpath(proposal_dir),
                "validation",
                "proposal_validation",
                "error",
                issue,
            )
    return metadata_by_id


def _audit_features(
    inventory: Inventory, findings: List[Finding], selected: Set[str]
) -> Dict[str, Dict[str, object]]:
    metadata_by_path: Dict[str, Dict[str, object]] = {}
    for feature_dir in inventory.feature_dirs:
        feature_id = feature_dir.name
        metadata, error_finding = _safe_read_metadata(
            inventory.context.planning.read_metadata, "feature", feature_id, feature_dir
        )
        if error_finding is not None:
            add_finding(
                findings,
                selected,
                error_finding.artifact_type,
                error_finding.artifact_id,
                error_finding.path,
                error_finding.category,
                error_finding.code,
                error_finding.severity,
                error_finding.message,
            )
            continue
        assert metadata is not None
        metadata_by_path[normalize_dir_relpath(feature_dir)] = metadata
        ok, issues, _ = inventory.context.planning.validate_feature_state(
            str(feature_dir), metadata
        )
        if ok:
            continue
        for issue in issues:
            add_finding(
                findings,
                selected,
                "feature",
                feature_id,
                normalize_dir_relpath(feature_dir),
                "validation",
                "feature_validation",
                "error",
                issue,
            )
    return metadata_by_path


def _audit_subfeatures(
    inventory: Inventory, findings: List[Finding], selected: Set[str]
) -> Dict[str, Dict[str, object]]:
    metadata_by_path: Dict[str, Dict[str, object]] = {}
    for subfeature_dir in iter_subfeature_dirs(inventory):
        subfeature_id = subfeature_dir.name
        metadata, error_finding = _safe_read_metadata(
            inventory.context.subfeatures.read_metadata,
            "subfeature",
            subfeature_id,
            subfeature_dir,
        )
        if error_finding is not None:
            add_finding(
                findings,
                selected,
                error_finding.artifact_type,
                error_finding.artifact_id,
                error_finding.path,
                error_finding.category,
                error_finding.code,
                error_finding.severity,
                error_finding.message,
            )
            continue
        assert metadata is not None
        metadata_by_path[normalize_dir_relpath(subfeature_dir)] = metadata
        ok, issues, _ = inventory.context.subfeatures.validate_subfeature_state(
            str(subfeature_dir), metadata
        )
        if ok:
            continue
        for issue in issues:
            add_finding(
                findings,
                selected,
                "subfeature",
                subfeature_id,
                normalize_dir_relpath(subfeature_dir),
                "validation",
                "subfeature_validation",
                "error",
                issue,
            )
    return metadata_by_path


def _audit_slices(
    inventory: Inventory, findings: List[Finding], selected: Set[str]
) -> None:
    slice_row_paths = {
        normalize_registry_path(str(row["path"])): dict(row) for row in inventory.slice_rows
    }
    for row in inventory.slice_rows:
        ok, issues, _ = inventory.context.execution.validate_slice(dict(row))
        if ok:
            continue
        for issue in issues:
            add_finding(
                findings,
                selected,
                "slice",
                str(row["id"]),
                normalize_registry_path(str(row["path"])),
                "validation",
                issue,
                "error",
                issue,
            )
    for slice_dir in inventory.slice_dirs:
        relpath = normalize_dir_relpath(slice_dir)
        if relpath in slice_row_paths:
            continue
        try:
            inventory.context.execution.load_slice_metadata(str(slice_dir))
        except RuntimeError as exc:
            add_finding(
                findings,
                selected,
                "slice",
                slice_dir.name,
                relpath,
                "validation",
                "metadata_read_error",
                "error",
                str(exc),
            )


def _subfeature_artifact_id(relpath: str, metadata: Dict[str, object]) -> str:
    subfeature_id = metadata.get("subfeature_id")
    if isinstance(subfeature_id, str) and subfeature_id.strip():
        return subfeature_id.strip()
    return Path(relpath.rstrip("/")).name


def _normalize_string_list(value: object) -> List[str]:
    if not isinstance(value, list):
        return []
    result = []
    for item in value:
        if isinstance(item, str):
            normalized = item.strip()
            if normalized:
                result.append(normalized)
    return sorted(set(result))


def _audit_cross_links(
    inventory: Inventory,
    findings: List[Finding],
    selected: Set[str],
    proposal_metadata: Dict[str, Dict[str, object]],
    feature_metadata: Dict[str, Dict[str, object]],
    subfeature_metadata: Dict[str, Dict[str, object]],
) -> None:
    canonical_feature_slugs = {
        str(metadata["feature_slug"]) for metadata in feature_metadata.values() if "feature_slug" in metadata
    }
    canonical_feature_paths = {
        str(metadata["feature_slug"]): relpath
        for relpath, metadata in feature_metadata.items()
        if "feature_slug" in metadata
    }
    feature_statuses = {
        str(metadata["feature_slug"]): str(metadata.get("status") or "")
        for metadata in feature_metadata.values()
        if "feature_slug" in metadata
    }
    traceability_by_owner: Dict[Tuple[str, str], List[TraceabilityRecord]] = {}
    for record in iter_traceability_records(inventory):
        traceability_by_owner.setdefault((record.owner_type, record.owner_path), []).append(record)
    slice_rows_by_feature: Dict[str, List[Dict[str, object]]] = {}
    slice_rows_by_id = {str(row["id"]): dict(row) for row in inventory.slice_rows}
    for row in inventory.slice_rows:
        feature_slug = str(row.get("feature") or "").strip()
        if feature_slug:
            slice_rows_by_feature.setdefault(feature_slug, []).append(dict(row))

    for proposal_id, metadata in proposal_metadata.items():
        proposal_path = normalize_dir_relpath(inventory.context.proposal_root / proposal_id)
        target_feature = metadata.get("target_feature")
        if isinstance(target_feature, str) and target_feature and target_feature not in canonical_feature_slugs:
            add_finding(
                findings,
                selected,
                "proposal",
                proposal_id,
                proposal_path,
                "broken_link",
                "missing_target_feature",
                "error",
                f"Proposal target_feature '{target_feature}' does not match a canonical feature.",
            )
        promoted_feature = metadata.get("promoted_feature")
        if isinstance(promoted_feature, str) and promoted_feature and promoted_feature not in canonical_feature_slugs:
            add_finding(
                findings,
                selected,
                "proposal",
                proposal_id,
                proposal_path,
                "broken_link",
                "missing_promoted_feature",
                "error",
                f"Proposal promoted_feature '{promoted_feature}' does not match a canonical feature.",
            )

    for relpath, metadata in subfeature_metadata.items():
        subfeature_id = _subfeature_artifact_id(relpath, metadata)
        subfeature_status = str(metadata.get("status") or "")
        parent_feature_slug = str(metadata.get("parent_feature_slug") or "")
        if parent_feature_slug not in canonical_feature_slugs:
            add_finding(
                findings,
                selected,
                "subfeature",
                subfeature_id,
                relpath,
                "broken_link",
                "missing_parent_feature",
                "error",
                f"Subfeature parent_feature_slug '{parent_feature_slug}' does not match a canonical feature.",
            )
        parts = Path(relpath.rstrip("/")).parts
        if "subfeatures" in parts:
            index = parts.index("subfeatures")
            if index > 0:
                expected_parent = parts[index - 1]
                if expected_parent != parent_feature_slug:
                    add_finding(
                        findings,
                        selected,
                        "subfeature",
                        subfeature_id,
                        relpath,
                        "broken_link",
                        "parent_path_mismatch",
                        "error",
                        "Subfeature metadata parent_feature_slug does not match the parent folder path.",
                    )

        traceability_records = traceability_by_owner.get(("subfeature", relpath), [])
        execution_slice_ids = sorted(
            {
                slice_id
                for record in traceability_records
                for slice_id in record.execution_slice_ids
                if slice_id in slice_rows_by_id
            }
        )
        missing_execution_slice_ids = sorted(
            {
                slice_id
                for record in traceability_records
                for slice_id in record.execution_slice_ids
                if slice_id not in slice_rows_by_id
            }
        )
        if missing_execution_slice_ids:
            add_finding(
                findings,
                selected,
                "subfeature",
                subfeature_id,
                relpath,
                "broken_link",
                "missing_traceability_execution_slice",
                "error",
                (
                    "Subfeature traceability lists execution slices that do not exist in the "
                    f"slice registry: {', '.join(missing_execution_slice_ids)}."
                ),
            )

        if not execution_slice_ids:
            continue

        closed_execution_slice_ids = sorted(
            slice_id
            for slice_id in execution_slice_ids
            if str(slice_rows_by_id[slice_id].get("status") or "") == "closed"
        )
        if len(closed_execution_slice_ids) != len(execution_slice_ids):
            continue

        affected_slice_ids = _normalize_string_list(metadata.get("affected_slice_ids"))
        if affected_slice_ids != execution_slice_ids:
            recorded = ", ".join(affected_slice_ids) if affected_slice_ids else "(none)"
            traced = ", ".join(execution_slice_ids)
            add_finding(
                findings,
                selected,
                "subfeature",
                subfeature_id,
                relpath,
                "cross_layer_drift",
                "subfeature_affected_slice_ids_out_of_sync",
                "warning",
                (
                    "Subfeature metadata affected_slice_ids "
                    f"({recorded}) does not match the closed execution slices recorded in "
                    f"traceability ({traced})."
                ),
            )
        if subfeature_status != "finalized":
            add_finding(
                findings,
                selected,
                "subfeature",
                subfeature_id,
                relpath,
                "cross_layer_drift",
                "subfeature_status_precedes_closed_execution",
                "warning",
                (
                    f"Subfeature status '{subfeature_status}' predates closed execution slices: "
                    f"{', '.join(execution_slice_ids)}."
                ),
            )

    for feature_slug, rows in slice_rows_by_feature.items():
        if feature_slug not in canonical_feature_slugs:
            continue
        feature_status = feature_statuses.get(feature_slug, "")
        if feature_status in {"slice_ready", "implemented"}:
            continue
        slice_ids = ", ".join(sorted(str(row["id"]) for row in rows))
        add_finding(
            findings,
            selected,
            "feature",
            feature_slug,
            canonical_feature_paths[feature_slug],
            "cross_layer_drift",
            "planning_status_precedes_execution",
            "warning",
            (
                f"Feature planning status '{feature_status}' predates execution handoff, "
                f"but execution slices already exist: {slice_ids}."
            ),
        )


def _audit_relations(inventory: Inventory, findings: List[Finding], selected: Set[str]) -> None:
    if not include_artifact(selected, "slice") or not inventory.slice_rows:
        return
    result = inventory.context.execution.audit_relations(list(inventory.slice_rows))
    row_by_id = {str(row["id"]): dict(row) for row in inventory.slice_rows}
    for issue in result["issues"]:
        slice_id = str(issue["slice_id"])
        row = row_by_id.get(slice_id)
        path = normalize_registry_path(str(row["path"])) if row else ""
        add_finding(
            findings,
            selected,
            "slice",
            slice_id,
            path,
            "relation",
            str(issue["code"]),
            "error",
            str(issue["message"]),
        )


def dedupe_findings(findings: Iterable[Finding]) -> List[Finding]:
    seen = set()
    result: List[Finding] = []
    for finding in findings:
        key = (
            finding.artifact_type,
            finding.artifact_id,
            finding.path,
            finding.category,
            finding.code,
            finding.message,
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(finding)
    return sorted(
        result,
        key=lambda item: (
            item.artifact_type,
            item.path,
            item.category,
            item.code,
            item.message,
        ),
    )


def summarize(findings: Sequence[Finding]) -> Dict[str, object]:
    by_artifact_type: Dict[str, int] = {}
    by_category: Dict[str, int] = {}
    by_severity: Dict[str, int] = {}
    for finding in findings:
        by_artifact_type[finding.artifact_type] = by_artifact_type.get(finding.artifact_type, 0) + 1
        by_category[finding.category] = by_category.get(finding.category, 0) + 1
        by_severity[finding.severity] = by_severity.get(finding.severity, 0) + 1
    return {
        "total": len(findings),
        "by_artifact_type": by_artifact_type,
        "by_category": by_category,
        "by_severity": by_severity,
    }


def _audit_installed_parity(
    findings: List[Finding], installed_skills: Optional[Sequence[Dict[str, object]]] = None
) -> None:
    for record in inspect_installed_skill_parity(installed_skills=installed_skills):
        findings.append(
            Finding(
                artifact_type="skill",
                artifact_id=record.skill_name,
                path=record.relative_path,
                category="installed_parity",
                code=record.code,
                severity="warning",
                message=record.message,
            )
        )


def run_audit(
    artifact_types: Optional[Iterable[str]] = None,
    installed_skills: Optional[Sequence[Dict[str, object]]] = None,
) -> Dict[str, object]:
    selected = set(artifact_types) if artifact_types is not None else set(VALID_ARTIFACT_TYPES)
    inventory = load_inventory()
    findings: List[Finding] = []

    proposal_status = next(
        status for status in inventory.registry_statuses if status.artifact_type == "proposal"
    )
    planning_status = next(
        status
        for status in inventory.registry_statuses
        if status.artifact_type == "feature" and status.owner_id is None
    )
    slice_status = next(
        status for status in inventory.registry_statuses if status.artifact_type == "slice"
    )

    _registry_findings(findings, selected, proposal_status, inventory.proposal_dirs)
    _registry_findings(findings, selected, planning_status, inventory.feature_dirs + iter_subfeature_dirs(inventory))
    _registry_findings(findings, selected, slice_status, inventory.slice_dirs)

    for status in inventory.registry_statuses:
        if status.artifact_type == "subfeature" and status.owner_id is not None:
            _registry_findings(
                findings,
                selected,
                status,
                inventory.subfeature_dirs_by_feature.get(status.owner_id, []),
            )

    _compare_paths(
        findings,
        selected,
        "proposal",
        {normalize_registry_path(str(row["path"])) for row in inventory.proposal_rows},
        {normalize_dir_relpath(path) for path in inventory.proposal_dirs},
        "proposal_registry_path_missing",
        "proposal_registry_entry_missing",
    )
    _compare_paths(
        findings,
        selected,
        "feature",
        {
            normalize_registry_path(str(row["path"]))
            for row in inventory.planning_rows
            if planning_row_artifact_type(row) == "feature"
        },
        {normalize_dir_relpath(path) for path in inventory.feature_dirs},
        "planning_registry_path_missing",
        "planning_registry_entry_missing",
    )
    _compare_paths(
        findings,
        selected,
        "subfeature",
        {
            normalize_registry_path(str(row["path"]))
            for row in inventory.planning_rows
            if planning_row_artifact_type(row) == "subfeature"
        },
        {normalize_dir_relpath(path) for path in iter_subfeature_dirs(inventory)},
        "planning_registry_path_missing",
        "planning_registry_entry_missing",
    )
    _compare_paths(
        findings,
        selected,
        "slice",
        {normalize_registry_path(str(row["path"])) for row in inventory.slice_rows},
        {normalize_dir_relpath(path) for path in inventory.slice_dirs},
        "slice_registry_path_missing",
        "slice_registry_entry_missing",
    )

    for feature_dir in inventory.feature_dirs:
        feature_slug = feature_dir.name
        _compare_paths(
            findings,
            selected,
            "subfeature",
            {
                normalize_registry_path(str(row["path"]))
                for row in inventory.subfeature_registry_rows.get(feature_slug, [])
            },
            {
                normalize_dir_relpath(path)
                for path in inventory.subfeature_dirs_by_feature.get(feature_slug, [])
            },
            "subfeature_registry_path_missing",
            "subfeature_registry_entry_missing",
            owner_label=f"feature '{feature_slug}'",
        )

    proposal_metadata = _audit_proposals(inventory, findings, selected)
    feature_metadata = _audit_features(inventory, findings, selected)
    subfeature_metadata = _audit_subfeatures(inventory, findings, selected)
    _audit_slices(inventory, findings, selected)
    _audit_cross_links(
        inventory,
        findings,
        selected,
        proposal_metadata,
        feature_metadata,
        subfeature_metadata,
    )
    _audit_relations(inventory, findings, selected)
    _audit_installed_parity(findings, installed_skills)

    deduped = dedupe_findings(findings)
    return {
        "ok": not deduped,
        "filters": sorted(selected),
        "summary": summarize(deduped),
        "findings": [finding.to_dict() for finding in deduped],
    }


def render_text(result: Dict[str, object]) -> str:
    if bool(result["ok"]):
        return "Audit passed: no findings."

    summary = result["summary"]
    lines = [f"Audit found {summary['total']} finding(s).", "", "By artifact type:"]
    for artifact_type, count in sorted(summary["by_artifact_type"].items()):
        lines.append(f"- {artifact_type}: {count}")
    lines.append("")
    lines.append("Findings:")
    for finding in result["findings"]:
        lines.append(
            "- "
            f"{finding['artifact_type']}:{finding['artifact_id']} "
            f"[{finding['category']}/{finding['code']}] "
            f"{finding['message']} ({finding['path']})"
        )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    result = run_audit(args.artifact_type if args.artifact_type else None)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        output = render_text(result)
        stream = sys.stdout if result["ok"] else sys.stderr
        print(output, file=stream)
    return 0 if result["ok"] else FINDINGS_EXIT_CODE


if __name__ == "__main__":
    sys.exit(main())
