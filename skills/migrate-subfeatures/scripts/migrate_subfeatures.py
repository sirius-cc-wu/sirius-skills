#!/usr/bin/env python3

import argparse
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple


PLANNING_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "guide-planning"
    / "scripts"
    / "manage_planning.py"
)
SUBFEATURE_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "add-subfeature"
    / "scripts"
    / "manage_subfeatures.py"
)

LEGACY_CHANGES_DIR = "changes"
LEGACY_METADATA_FILE = ".feature-change-meta.json"
LEGACY_REGISTRY_FILE = "registry.json"
LEGACY_REGISTRY_README = "README.md"
LEGACY_REGISTRY_HEADER = (
    "# Feature Change Registry\n\n"
    "| Change | Status | Type | Updated | Path |\n"
    "|---|---|---|---|---|\n"
)
LEGACY_STATUS_ALIASES = {
    "draft": "draft",
    "impact_ready": "impact_ready",
    "impact-ready": "impact_ready",
    "design_ready": "design_ready",
    "design-ready": "design_ready",
    "breakdown_ready": "breakdown_ready",
    "breakdown-ready": "breakdown_ready",
    "reviewed": "reviewed",
    "review_ready": "reviewed",
    "review-ready": "reviewed",
    "reconciled": "reconciled",
    "closed": "closed",
}
LEGACY_TO_SUBFEATURE_STATUS = {
    "draft": "draft",
    "impact_ready": "impact_ready",
    "design_ready": "design_ready",
    "breakdown_ready": "breakdown_ready",
    "reviewed": "reviewed",
    "reconciled": "finalized",
    "closed": "finalized",
}


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_manage_planning_module():
    return load_module(PLANNING_SCRIPT, "manage_planning")


def load_manage_subfeatures_module():
    return load_module(SUBFEATURE_SCRIPT, "manage_subfeatures")


def normalize_optional_string(value: object) -> Optional[str]:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise RuntimeError("Expected an optional string field.")
    cleaned = " ".join(value.strip().split())
    return cleaned or None


def normalize_optional_timestamp(value: object) -> Optional[str]:
    if value is None or value == "" or value == "-":
        return None
    if not isinstance(value, str):
        raise RuntimeError("Timestamp fields must be strings when present.")
    return value


def normalize_string_list(value: object, field_name: str) -> List[str]:
    if value is None or value == "":
        return []
    if not isinstance(value, list):
        raise RuntimeError(f"{field_name} must be stored as a list.")
    normalized: List[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise RuntimeError(f"{field_name} must contain non-empty strings.")
        normalized.append(item.strip())
    return list(dict.fromkeys(normalized))


def normalize_legacy_status(value: object) -> str:
    if not isinstance(value, str):
        raise RuntimeError("Legacy change status must be a string.")
    normalized = value.strip().lower()
    if normalized not in LEGACY_STATUS_ALIASES:
        raise RuntimeError(f"Unsupported legacy change status '{value}'.")
    return LEGACY_STATUS_ALIASES[normalized]


def map_legacy_status(value: object) -> str:
    legacy_status = normalize_legacy_status(value)
    return LEGACY_TO_SUBFEATURE_STATUS[legacy_status]


def load_json_file(path: Path, description: str) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{description} is not valid JSON: {path}") from exc


def resolve_feature_dir(
    manage_planning, selector: str
) -> Tuple[str, str, object]:
    try:
        rows, feature, scope_context = manage_planning.resolve_feature_lookup(selector)
        if feature:
            feature_dir = manage_planning.feature_dir_for_row(
                feature, scope_context=scope_context
            )
            return feature_dir, str(feature["feature"]), scope_context
    except RuntimeError:
        pass

    scope_context = manage_planning.SCOPE_RUNTIME.resolve_scope_context()
    candidate = Path(selector)
    if not candidate.is_absolute():
        candidate = (Path.cwd() / selector).resolve()
    if not candidate.is_dir():
        raise RuntimeError(f"Feature not found: {selector}")

    metadata = manage_planning.read_metadata(str(candidate))
    return str(candidate), str(metadata["feature_slug"]), scope_context


def discover_feature_dirs_with_legacy_changes(manage_planning, scope_context: object) -> List[Tuple[str, str]]:
    planning_dir, _, _ = manage_planning.get_registry_paths(
        required_config=False, scope_context=scope_context
    )
    root = Path(planning_dir)
    if not root.exists():
        return []

    discovered: List[Tuple[str, str]] = []
    seen: set[str] = set()
    for changes_dir in sorted(path for path in root.rglob(LEGACY_CHANGES_DIR) if path.is_dir()):
        feature_dir = changes_dir.parent.resolve()
        normalized = str(feature_dir)
        if normalized in seen:
            continue
        metadata = manage_planning.read_metadata(normalized)
        discovered.append((normalized, str(metadata["feature_slug"])))
        seen.add(normalized)
    return discovered


def load_legacy_registry(changes_dir: Path) -> List[Dict[str, object]]:
    registry_path = changes_dir / LEGACY_REGISTRY_FILE
    if not registry_path.exists():
        return []

    payload = load_json_file(registry_path, "Legacy change registry")
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict):
        rows = payload.get("changes", [])
    else:
        raise RuntimeError("Legacy change registry must be a JSON object or list.")

    if not isinstance(rows, list):
        raise RuntimeError("Legacy change registry field 'changes' must be a list.")

    normalized_rows: List[Dict[str, object]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise RuntimeError("Legacy change registry rows must be JSON objects.")
        normalized_rows.append(row)
    return normalized_rows


def discover_legacy_change_ids(changes_dir: Path, registry_rows: Sequence[Dict[str, object]]) -> List[str]:
    identifiers: set[str] = set()
    for row in registry_rows:
        change_id = row.get("change_id")
        if isinstance(change_id, str) and change_id.strip():
            identifiers.add(change_id.strip())
            continue
        path_value = row.get("path")
        if isinstance(path_value, str) and path_value.strip():
            identifiers.add(Path(path_value.rstrip("/")).name)

    for child in changes_dir.iterdir():
        if child.is_dir():
            identifiers.add(child.name)

    return sorted(identifiers)


def convert_legacy_metadata(
    legacy_payload: object,
    fallback_change_id: str,
    feature_slug: str,
    manage_subfeatures,
) -> Tuple[Dict[str, object], str]:
    if not isinstance(legacy_payload, dict):
        raise RuntimeError("Legacy change metadata must be a JSON object.")

    change_id = manage_subfeatures.validate_slug(
        str(legacy_payload.get("change_id", fallback_change_id)), "Change ID"
    )
    legacy_feature_slug = manage_subfeatures.validate_slug(
        str(legacy_payload.get("feature_slug", feature_slug)), "Feature slug"
    )
    if legacy_feature_slug != feature_slug:
        raise RuntimeError(
            f"Legacy metadata feature slug '{legacy_feature_slug}' does not match feature '{feature_slug}'."
        )

    legacy_status = normalize_legacy_status(legacy_payload.get("status", "draft"))
    mapped_status = LEGACY_TO_SUBFEATURE_STATUS[legacy_status]
    subfeature_type = manage_subfeatures.normalize_subfeature_type(
        str(legacy_payload.get("change_type", "additive"))
    )
    summary = normalize_optional_string(legacy_payload.get("summary"))
    review_note = normalize_optional_string(legacy_payload.get("review_note"))
    if mapped_status in {"reviewed", "finalized"} and not review_note:
        review_note = f"Migrated from legacy change state '{legacy_status}'."

    created_at = normalize_optional_timestamp(legacy_payload.get("created_at")) or manage_subfeatures.now_timestamp()
    updated_at = normalize_optional_timestamp(legacy_payload.get("updated_at")) or created_at
    finalized_at = None
    if mapped_status == "finalized":
        finalized_at = (
            normalize_optional_timestamp(legacy_payload.get("reconciled_at"))
            or updated_at
        )

    metadata = manage_subfeatures.build_metadata(
        feature_slug,
        change_id,
        subfeature_type=subfeature_type,
        summary=summary,
    )
    metadata.update(
        {
            "status": mapped_status,
            "created_at": created_at,
            "updated_at": updated_at,
            "affected_artifacts": normalize_string_list(
                legacy_payload.get("affected_artifacts"), "Affected artifacts"
            ),
            "affected_story_ids": normalize_string_list(
                legacy_payload.get("affected_story_ids"), "Affected story IDs"
            ),
            "affected_slice_ids": normalize_string_list(
                legacy_payload.get("affected_slice_ids"), "Affected slice IDs"
            ),
            "review_note": review_note,
            "finalized_at": finalized_at,
        }
    )
    return metadata, legacy_status


def build_planning_metadata(manage_planning, manage_subfeatures, subfeature_id: str, metadata: Dict[str, object]) -> Dict[str, object]:
    planning_metadata = manage_planning.build_metadata(subfeature_id, requires_ui_flow=False)
    planning_metadata["created_at"] = metadata["created_at"]
    planning_metadata["updated_at"] = metadata["updated_at"]
    planning_metadata["status"] = manage_subfeatures.PLANNING_STATUS_BY_SUBFEATURE_STATUS[
        str(metadata["status"])
    ]
    planning_metadata["review_note"] = metadata.get("review_note")
    planning_metadata["ready_slice_ids"] = []
    return planning_metadata


def build_report_item(
    feature_slug: str,
    legacy_dir: Path,
    target_dir: Path,
    metadata: Optional[Dict[str, object]] = None,
    legacy_status: Optional[str] = None,
    reason: Optional[str] = None,
) -> Dict[str, object]:
    item: Dict[str, object] = {
        "feature": feature_slug,
        "change_id": legacy_dir.name,
        "legacy_path": str(legacy_dir),
        "target_path": str(target_dir),
    }
    if metadata is not None:
        item["mapped_status"] = metadata["status"]
        item["subfeature_type"] = metadata["subfeature_type"]
        item["summary"] = metadata.get("summary")
    if legacy_status is not None:
        item["legacy_status"] = legacy_status
    if reason is not None:
        item["reason"] = reason
    return item


def scan_feature(
    feature_dir: str,
    feature_slug: str,
    manage_subfeatures,
) -> Dict[str, object]:
    feature_path = Path(feature_dir)
    changes_dir = feature_path / LEGACY_CHANGES_DIR
    report: Dict[str, object] = {
        "feature": feature_slug,
        "feature_path": str(feature_path),
        "legacy_changes_dir": str(changes_dir),
        "changes_found": 0,
        "candidates": [],
        "blocked": [],
    }
    if not changes_dir.is_dir():
        return report

    registry_rows = load_legacy_registry(changes_dir)
    change_ids = discover_legacy_change_ids(changes_dir, registry_rows)
    report["changes_found"] = len(change_ids)

    for change_id in change_ids:
        legacy_dir = changes_dir / change_id
        target_dir = feature_path / "subfeatures" / change_id
        if not legacy_dir.is_dir():
            report["blocked"].append(
                build_report_item(
                    feature_slug,
                    legacy_dir,
                    target_dir,
                    reason="Legacy change directory is missing.",
                )
            )
            continue
        if target_dir.exists():
            report["blocked"].append(
                build_report_item(
                    feature_slug,
                    legacy_dir,
                    target_dir,
                    reason="Target subfeature already exists.",
                )
            )
            continue

        legacy_metadata_path = legacy_dir / LEGACY_METADATA_FILE
        if not legacy_metadata_path.exists():
            report["blocked"].append(
                build_report_item(
                    feature_slug,
                    legacy_dir,
                    target_dir,
                    reason=f"Missing legacy metadata file '{LEGACY_METADATA_FILE}'.",
                )
            )
            continue

        try:
            metadata, legacy_status = convert_legacy_metadata(
                load_json_file(legacy_metadata_path, "Legacy change metadata"),
                change_id,
                feature_slug,
                manage_subfeatures,
            )
        except RuntimeError as exc:
            report["blocked"].append(
                build_report_item(
                    feature_slug,
                    legacy_dir,
                    target_dir,
                    reason=str(exc),
                )
            )
            continue

        report["candidates"].append(
            build_report_item(
                feature_slug,
                legacy_dir,
                target_dir,
                metadata=metadata,
                legacy_status=legacy_status,
            )
        )

    return report


def copy_legacy_contents(legacy_dir: Path, target_dir: Path) -> None:
    for child in legacy_dir.iterdir():
        if child.name == LEGACY_METADATA_FILE:
            continue
        destination = target_dir / child.name
        if destination.exists():
            raise RuntimeError(f"Target already contains '{destination.name}'.")
        if child.is_dir():
            shutil.copytree(child, destination)
        else:
            shutil.copy2(child, destination)


def upsert_subfeature_registry_row(
    feature_dir: str,
    target_dir: str,
    metadata: Dict[str, object],
    scope_context: object,
    manage_planning,
    manage_subfeatures,
) -> None:
    rows = manage_subfeatures.load_registry(feature_dir)
    rows = [
        row
        for row in rows
        if str(row["subfeature_id"]) != str(metadata["subfeature_id"])
    ]
    rows.append(
        {
            "subfeature_id": metadata["subfeature_id"],
            "status": metadata["status"],
            "subfeature_type": metadata["subfeature_type"],
            "updated_at": metadata["updated_at"],
            "path": manage_planning.relative_path_from_scope_root(
                target_dir, scope_context
            ),
        }
    )
    manage_subfeatures.write_registry(feature_dir, rows)


def cleanup_or_rewrite_legacy_registry(
    feature_dir: str,
    feature_slug: str,
    scope_context: object,
    manage_planning,
) -> None:
    changes_dir = Path(feature_dir) / LEGACY_CHANGES_DIR
    if not changes_dir.exists():
        return

    remaining_dirs = sorted(child for child in changes_dir.iterdir() if child.is_dir())
    unexpected_files = [
        child
        for child in changes_dir.iterdir()
        if child.is_file() and child.name not in {LEGACY_REGISTRY_FILE, LEGACY_REGISTRY_README}
    ]
    if not remaining_dirs and not unexpected_files:
        shutil.rmtree(changes_dir)
        return

    rows: List[Dict[str, object]] = []
    for legacy_dir in remaining_dirs:
        metadata_path = legacy_dir / LEGACY_METADATA_FILE
        if metadata_path.exists():
            payload = load_json_file(metadata_path, "Legacy change metadata")
            if not isinstance(payload, dict):
                raise RuntimeError(
                    f"Legacy change metadata must be a JSON object: {metadata_path}"
                )
            status = normalize_legacy_status(payload.get("status", "draft"))
            change_type = str(payload.get("change_type", "additive"))
            updated_at = normalize_optional_timestamp(payload.get("updated_at"))
        else:
            status = "draft"
            change_type = "additive"
            updated_at = None
        rows.append(
            {
                "change_id": legacy_dir.name,
                "status": status,
                "change_type": change_type,
                "updated_at": updated_at,
                "path": manage_planning.relative_path_from_scope_root(
                    str(legacy_dir), scope_context
                ),
            }
        )

    readme_path = changes_dir / LEGACY_REGISTRY_README
    registry_path = changes_dir / LEGACY_REGISTRY_FILE
    with readme_path.open("w", encoding="utf-8") as handle:
        handle.write(LEGACY_REGISTRY_HEADER)
        for row in rows:
            updated_at = row["updated_at"] or "-"
            handle.write(
                f"| {row['change_id']} | {row['status']} | {row['change_type']} | {updated_at} | {row['path']} |\n"
            )
    with registry_path.open("w", encoding="utf-8") as handle:
        json.dump({"changes": rows}, handle, indent=2)
        handle.write("\n")


def migrate_change_packet(
    feature_dir: str,
    feature_slug: str,
    change_id: str,
    scope_context: object,
    manage_planning,
    manage_subfeatures,
) -> Dict[str, object]:
    feature_path = Path(feature_dir)
    legacy_dir = feature_path / LEGACY_CHANGES_DIR / change_id
    target_dir = feature_path / "subfeatures" / change_id
    metadata, legacy_status = convert_legacy_metadata(
        load_json_file(legacy_dir / LEGACY_METADATA_FILE, "Legacy change metadata"),
        change_id,
        feature_slug,
        manage_subfeatures,
    )
    planning_metadata = build_planning_metadata(
        manage_planning, manage_subfeatures, change_id, metadata
    )

    manage_subfeatures.ensure_subfeature_registry(feature_dir)
    if target_dir.exists():
        raise RuntimeError("Target subfeature already exists.")

    try:
        target_dir.mkdir(parents=True, exist_ok=False)
        manage_planning.write_metadata(str(target_dir), planning_metadata)
        copy_legacy_contents(legacy_dir, target_dir)
        manage_subfeatures.write_metadata(str(target_dir), metadata)
        ok, issues, _ = manage_subfeatures.validate_subfeature_state(
            str(target_dir), metadata
        )
        if not ok:
            raise RuntimeError("; ".join(issues))
        upsert_subfeature_registry_row(
            feature_dir,
            str(target_dir),
            metadata,
            scope_context,
            manage_planning,
            manage_subfeatures,
        )
    except Exception:
        if target_dir.exists():
            shutil.rmtree(target_dir)
        raise

    shutil.rmtree(legacy_dir)
    return build_report_item(
        feature_slug,
        legacy_dir,
        target_dir,
        metadata=metadata,
        legacy_status=legacy_status,
    )


def run_scan(args: argparse.Namespace) -> Tuple[Dict[str, object], int]:
    manage_planning = load_manage_planning_module()
    manage_subfeatures = load_manage_subfeatures_module()
    scope_context = manage_planning.SCOPE_RUNTIME.resolve_scope_context()

    if args.all:
        targets = discover_feature_dirs_with_legacy_changes(manage_planning, scope_context)
    else:
        feature_dir, feature_slug, feature_scope_context = resolve_feature_dir(
            manage_planning, args.feature
        )
        targets = [(feature_dir, feature_slug)]
        scope_context = feature_scope_context

    features = [
        scan_feature(feature_dir, feature_slug, manage_subfeatures)
        for feature_dir, feature_slug in targets
    ]
    result = {
        "mode": "scan",
        "scope_root": str(scope_context.scope_root),
        "features": features,
        "ok": True,
    }
    return result, 0


def run_migrate(args: argparse.Namespace) -> Tuple[Dict[str, object], int]:
    manage_planning = load_manage_planning_module()
    manage_subfeatures = load_manage_subfeatures_module()
    scope_context = manage_planning.SCOPE_RUNTIME.resolve_scope_context()

    if args.all:
        targets = discover_feature_dirs_with_legacy_changes(manage_planning, scope_context)
    else:
        feature_dir, feature_slug, feature_scope_context = resolve_feature_dir(
            manage_planning, args.feature
        )
        targets = [(feature_dir, feature_slug)]
        scope_context = feature_scope_context

    features: List[Dict[str, object]] = []
    overall_ok = True
    for feature_dir, feature_slug in targets:
        scan_report = scan_feature(feature_dir, feature_slug, manage_subfeatures)
        feature_result = {
            "feature": feature_slug,
            "feature_path": feature_dir,
            "dry_run": args.dry_run,
            "planned": list(scan_report["candidates"]),
            "migrated": [],
            "blocked": list(scan_report["blocked"]),
        }

        if args.dry_run:
            features.append(feature_result)
            continue

        for candidate in scan_report["candidates"]:
            try:
                migrated = migrate_change_packet(
                    feature_dir,
                    feature_slug,
                    str(candidate["change_id"]),
                    scope_context,
                    manage_planning,
                    manage_subfeatures,
                )
                feature_result["migrated"].append(migrated)
            except RuntimeError as exc:
                feature_result["blocked"].append(
                    {
                        **candidate,
                        "reason": str(exc),
                    }
                )

        cleanup_or_rewrite_legacy_registry(
            feature_dir, feature_slug, scope_context, manage_planning
        )
        features.append(feature_result)
        if feature_result["blocked"]:
            overall_ok = False

    if not args.dry_run:
        manage_planning.sync_registry(scope_context=scope_context)

    result = {
        "mode": "migrate",
        "scope_root": str(scope_context.scope_root),
        "dry_run": args.dry_run,
        "features": features,
        "ok": overall_ok,
    }
    exit_code = 0 if args.dry_run or overall_ok else 3
    return result, exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_p = subparsers.add_parser(
        "scan", help="Inspect legacy feature-local changes/ packets"
    )
    scan_p.add_argument(
        "feature",
        nargs="?",
        help="Feature slug, folder name, or path. Omit when using --all.",
    )
    scan_p.add_argument(
        "--all",
        action="store_true",
        help="Scan the whole planning tree for legacy changes.",
    )

    migrate_p = subparsers.add_parser(
        "migrate", help="Convert legacy changes/ packets into durable subfeatures"
    )
    migrate_p.add_argument(
        "feature",
        nargs="?",
        help="Feature slug, folder name, or path. Omit when using --all.",
    )
    migrate_p.add_argument(
        "--all",
        action="store_true",
        help="Migrate all features that still contain legacy changes.",
    )
    migrate_p.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview migrations without modifying files.",
    )

    return parser


def validate_target_args(args: argparse.Namespace) -> None:
    if bool(args.all) == bool(getattr(args, "feature", None)):
        raise RuntimeError("Specify exactly one target: a feature or --all.")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        validate_target_args(args)
        if args.command == "scan":
            result, exit_code = run_scan(args)
        elif args.command == "migrate":
            result, exit_code = run_migrate(args)
        else:
            parser.error(f"Unknown command: {args.command}")
            return 2
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
