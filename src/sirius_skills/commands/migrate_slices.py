#!/usr/bin/env python3

import argparse
import json
import os
import shutil
import sys
from types import SimpleNamespace
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from sirius_skills.lib.workflow_state import markdown_repository


MIGRATION_VERSION = 1


def load_manage_planning_module():
    from sirius_skills.commands import manage_planning

    return manage_planning


def load_manage_execution_module():
    from sirius_skills.commands import manage_execution

    return manage_execution


def load_manage_proposals_module():
    from sirius_skills.commands import manage_proposals

    return manage_proposals


def normalize_optional_timestamp(value: object) -> Optional[str]:
    if value in {None, "", "-"}:
        return None
    if not isinstance(value, str):
        raise RuntimeError("Timestamp fields must be strings when present.")
    return value


def is_archived_row(row: Dict[str, object]) -> bool:
    archived_at = normalize_optional_timestamp(row.get("archived_at"))
    if archived_at:
        return True

    row_path = str(row.get("path", "")).rstrip("/")
    return "/.archived/" in row_path or row_path.endswith("/.archived")


def ensure_feature_scope(
    manage_planning,
    manage_execution,
    manage_proposals,
    feature_dir: Path,
    root_scope_context: object,
) -> bool:
    skills_dir = feature_dir / ".skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    planning_path = skills_dir / "planning.json"
    created = False

    root_planning_dir, _, _ = manage_planning.get_registry_paths(
        required_config=False, scope_context=root_scope_context
    )
    root_proposal_dir, _, _ = manage_proposals.get_registry_paths(
        required_config=False, scope_context=root_scope_context
    )
    if not planning_path.exists():
        manage_planning.write_config(
            os.path.relpath(str(Path(root_planning_dir).resolve()), feature_dir),
            os.path.relpath(str(Path(root_proposal_dir).resolve()), feature_dir),
            manage_planning.load_config(
                required=False, scope_context=root_scope_context
            )["design_diagram_mode"],
            scope_context=SimpleNamespace(planning_config_path=planning_path),
        )
        created = True

    _, execution_created = manage_execution.ensure_local_execution_scope(
        feature_dir, root_scope_context
    )
    return created or execution_created


def discover_subfeature_targets(feature_path: Path) -> List[Path]:
    subfeatures_root = feature_path / "subfeatures"
    if not subfeatures_root.exists():
        return []
    return sorted(
        path
        for path in subfeatures_root.iterdir()
        if path.is_dir() and (path / ".subfeature-meta.json").exists()
    )


def build_subfeature_owner_map(subfeature_targets: List[Path]) -> Dict[str, List[Path]]:
    owners_by_slice_id: Dict[str, List[Path]] = {}
    for subfeature_dir in subfeature_targets:
        traceability_path = subfeature_dir / "slice-traceability.md"
        if not traceability_path.exists():
            continue
        records = markdown_repository.parse_traceability_records(
            traceability_path,
            "subfeature",
            subfeature_dir.name,
            str(subfeature_dir),
        )
        for record in records:
            for execution_slice_id in record.execution_slice_ids:
                owners_by_slice_id.setdefault(execution_slice_id, []).append(subfeature_dir)
    return owners_by_slice_id


def discover_feature_targets(
    manage_planning, manage_execution, root_scope_context: object
) -> List[Tuple[str, str]]:
    rows = manage_execution.parse_registry(scope_context=root_scope_context)
    targets: List[Tuple[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        feature_slug = str(row.get("feature", "")).strip()
        if not feature_slug or feature_slug in seen:
            continue
        _, feature, _ = manage_planning.resolve_feature_lookup(
            feature_slug, explicit_scope=str(root_scope_context.scope_root)
        )
        if feature is None:
            continue
        feature_dir = manage_planning.feature_dir_for_row(feature, scope_context=root_scope_context)
        targets.append((feature_dir, str(feature["feature"])))
        seen.add(feature_slug)
    return targets


def resolve_feature_target(
    manage_planning, feature_selector: str, root_scope_context: object
) -> Tuple[str, str, object]:
    _, feature, scope_context = manage_planning.resolve_feature_lookup(
        feature_selector, explicit_scope=str(root_scope_context.scope_root)
    )
    if feature is None:
        raise RuntimeError(f"Planning feature not found: {feature_selector}")
    feature_dir = manage_planning.feature_dir_for_row(feature, scope_context=scope_context)
    return feature_dir, str(feature["feature"]), scope_context


def target_slice_root(
    manage_execution, feature_path: Path, feature_scope_context: Optional[object] = None
) -> Tuple[Path, Path]:
    if feature_scope_context is None:
        specs_dir = feature_path / "slices"
        return specs_dir, specs_dir / ".archived"

    specs_dir, _, _ = manage_execution.get_registry_paths(
        required_config=False, scope_context=feature_scope_context
    )
    archive_dir = Path(manage_execution.default_archive_dir(specs_dir))
    return Path(specs_dir), archive_dir


def target_scope_for_row(
    row: Dict[str, object],
    feature_path: Path,
    owner_map: Dict[str, List[Path]],
    subfeature_targets: List[Path],
) -> Tuple[Optional[Path], Optional[str]]:
    owners = owner_map.get(str(row.get("id") or ""), [])
    unique_owners = list(dict.fromkeys(owners))
    if len(unique_owners) == 1:
        return unique_owners[0], None
    if len(unique_owners) > 1:
        return None, "Execution slice maps to multiple subfeatures."
    if subfeature_targets:
        return None, "Execution slice is not mapped by any subfeature traceability file."
    return feature_path, None


def migrate_feature_rows(
    manage_planning,
    manage_execution,
    manage_proposals,
    root_rows: List[Dict[str, object]],
    feature_dir: str,
    feature_slug: str,
    root_scope_context: object,
    dry_run: bool,
) -> Dict[str, object]:
    feature_path = Path(feature_dir)
    subfeature_targets = discover_subfeature_targets(feature_path)
    owner_map = build_subfeature_owner_map(subfeature_targets)
    scope_created_by_target: Dict[str, bool] = {}
    existing_rows_by_target: Dict[str, List[Dict[str, object]]] = {}
    migrated_rows_by_target: Dict[str, List[Dict[str, object]]] = {}

    planned: List[Dict[str, object]] = []
    migrated: List[Dict[str, object]] = []
    blocked: List[Dict[str, object]] = []
    remaining_rows: List[Dict[str, object]] = []

    for row in root_rows:
        row_feature = str(row.get("feature", "")).strip()
        if row_feature != feature_slug:
            remaining_rows.append(row)
            continue

        target_scope, target_error = target_scope_for_row(
            row, feature_path, owner_map, subfeature_targets
        )
        if target_error is not None or target_scope is None:
            source_abs = Path(manage_execution.slice_path_for_row(row, scope_context=root_scope_context))
            entry = {
                "id": row["id"],
                "status": row["status"],
                "archived": is_archived_row(row),
                "source_path": str(source_abs.resolve().relative_to(root_scope_context.scope_root)),
                "target_path": None,
            }
            planned.append(entry)
            blocked.append({**entry, "reason": target_error or "Unable to resolve target scope."})
            remaining_rows.append(row)
            continue

        target_scope_context = None
        target_key = str(target_scope.resolve())
        if not dry_run:
            if target_scope == feature_path:
                created = ensure_feature_scope(
                    manage_planning,
                    manage_execution,
                    manage_proposals,
                    target_scope,
                    root_scope_context,
                )
                target_scope_context = manage_execution.resolve_execution_scope_context(
                    explicit_scope=target_scope
                )
            else:
                target_scope_context, created = manage_execution.ensure_local_execution_scope(
                    target_scope,
                    root_scope_context,
                )
            scope_created_by_target[target_key] = scope_created_by_target.get(target_key, False) or created
            existing_rows_by_target.setdefault(
                target_key,
                manage_execution.parse_registry(scope_context=target_scope_context),
            )

        specs_dir, archive_dir = target_slice_root(
            manage_execution, target_scope, target_scope_context
        )

        archived = is_archived_row(row)
        source_abs = Path(manage_execution.slice_path_for_row(row, scope_context=root_scope_context))
        if archived:
            target_root = archive_dir
        else:
            target_root = specs_dir

        folder_name = source_abs.name
        target_abs = target_root / folder_name
        target_rel = manage_execution.normalize_slice_path(
            os.path.relpath(str(target_abs.resolve()), str(target_scope.resolve()))
        )
        source_rel = str(source_abs.resolve().relative_to(root_scope_context.scope_root))

        entry = {
            "id": row["id"],
            "status": row["status"],
            "archived": archived,
            "source_path": source_rel,
            "target_path": target_rel,
            "target_scope": str(target_scope),
        }
        planned.append(entry)

        if dry_run:
            migrated.append(entry)
            continue

        if not source_abs.exists():
            blocked.append({**entry, "reason": "Source slice directory does not exist."})
            remaining_rows.append(row)
            continue

        if target_abs.exists():
            blocked.append({**entry, "reason": f"Target already exists: {target_abs}"})
            remaining_rows.append(row)
            continue

        target_root.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source_abs), str(target_abs))

        moved_metadata = manage_execution.load_slice_metadata(str(target_abs))
        updated_row = dict(row)
        updated_row["path"] = target_rel
        normalized_row = manage_execution.normalize_registry_row(updated_row)
        updated_metadata = manage_execution.build_slice_metadata(
            normalized_row, str(normalized_row["status"]), existing=moved_metadata
        )
        manage_execution.write_slice_metadata(str(target_abs), updated_metadata)
        migrated.append(
            {
                **entry,
                "target_path": target_rel,
            }
        )
        migrated_rows_by_target.setdefault(target_key, []).append(
            manage_execution.apply_metadata_to_row(normalized_row, updated_metadata)
        )

    if not dry_run:
        manage_execution.write_registry(remaining_rows, scope_context=root_scope_context)
        for target_key, migrated_rows in migrated_rows_by_target.items():
            target_scope = Path(target_key)
            target_scope_context = manage_execution.resolve_execution_scope_context(
                explicit_scope=target_scope
            )
            combined_rows = {
                row["id"]: dict(row) for row in existing_rows_by_target.get(target_key, [])
            }
            for migrated_row in migrated_rows:
                combined_rows[migrated_row["id"]] = dict(migrated_row)
            manage_execution.write_registry(
                list(combined_rows.values()), scope_context=target_scope_context
            )

    return {
        "feature": feature_slug,
        "feature_path": str(feature_path),
        "feature_scope_created": scope_created_by_target.get(str(feature_path.resolve()), False),
        "target_scopes_created": scope_created_by_target,
        "planned": planned,
        "migrated": migrated,
        "blocked": blocked,
    }


def resolve_targets(
    manage_planning, manage_execution, args: argparse.Namespace, root_scope_context: object
) -> List[Tuple[str, str]]:
    if args.all:
        return discover_feature_targets(manage_planning, manage_execution, root_scope_context)
    feature_dir, feature_slug, _ = resolve_feature_target(
        manage_planning, args.feature, root_scope_context
    )
    return [(feature_dir, feature_slug)]


def run_scan(args: argparse.Namespace) -> Tuple[Dict[str, object], int]:
    manage_planning = load_manage_planning_module()
    manage_execution = load_manage_execution_module()
    manage_proposals = load_manage_proposals_module()
    root_scope_context = manage_planning.SCOPE_RUNTIME.resolve_scope_context()
    root_rows = manage_execution.parse_registry(scope_context=root_scope_context)
    targets = resolve_targets(manage_planning, manage_execution, args, root_scope_context)

    features: List[Dict[str, object]] = []
    for feature_dir, feature_slug in targets:
        feature_report = migrate_feature_rows(
            manage_planning,
            manage_execution,
            manage_proposals,
            root_rows,
            feature_dir,
            feature_slug,
            root_scope_context,
            dry_run=True,
        )
        features.append(feature_report)

    result = {
        "migration_version": MIGRATION_VERSION,
        "mode": "scan",
        "scope_root": str(root_scope_context.scope_root),
        "features": features,
        "ok": True,
    }
    return result, 0


def run_migrate(args: argparse.Namespace) -> Tuple[Dict[str, object], int]:
    manage_planning = load_manage_planning_module()
    manage_execution = load_manage_execution_module()
    manage_proposals = load_manage_proposals_module()
    root_scope_context = manage_planning.SCOPE_RUNTIME.resolve_scope_context()
    root_rows = manage_execution.parse_registry(scope_context=root_scope_context)
    targets = resolve_targets(manage_planning, manage_execution, args, root_scope_context)

    features: List[Dict[str, object]] = []
    overall_ok = True
    for feature_dir, feature_slug in targets:
        if not bool(args.dry_run):
            root_rows = manage_execution.parse_registry(scope_context=root_scope_context)
        report = migrate_feature_rows(
            manage_planning,
            manage_execution,
            manage_proposals,
            root_rows,
            feature_dir,
            feature_slug,
            root_scope_context,
            dry_run=bool(args.dry_run),
        )
        features.append(report)
        if report["blocked"]:
            overall_ok = False

    result = {
        "migration_version": MIGRATION_VERSION,
        "mode": "migrate",
        "scope_root": str(root_scope_context.scope_root),
        "dry_run": bool(args.dry_run),
        "features": features,
        "ok": overall_ok or bool(args.dry_run),
    }
    exit_code = 0 if bool(args.dry_run) or overall_ok else 3
    return result, exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_p = subparsers.add_parser("scan", help="Inspect slices that can be migrated")
    scan_p.add_argument(
        "feature",
        nargs="?",
        help="Feature slug, folder name, or path. Omit when using --all.",
    )
    scan_p.add_argument(
        "--all",
        action="store_true",
        help="Scan the whole slice registry for migration candidates.",
    )

    migrate_p = subparsers.add_parser("migrate", help="Move slices into co-located feature roots")
    migrate_p.add_argument(
        "feature",
        nargs="?",
        help="Feature slug, folder name, or path. Omit when using --all.",
    )
    migrate_p.add_argument(
        "--all",
        action="store_true",
        help="Migrate all slices found in the current execution registry.",
    )
    migrate_p.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the migration without modifying files.",
    )

    return parser


def validate_target_args(args: argparse.Namespace) -> None:
    if bool(args.all) == bool(getattr(args, "feature", None)):
        raise RuntimeError("Specify exactly one target: a feature or --all.")


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

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
    raise SystemExit(main())
