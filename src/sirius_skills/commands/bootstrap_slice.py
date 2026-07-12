import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


COMMAND_DIR = Path(__file__).resolve().parent
EXECUTION_SCRIPT_PATH = COMMAND_DIR / "manage_execution.py"
PLANNING_SCRIPT_PATH = COMMAND_DIR / "manage_planning.py"
SUBFEATURE_SCRIPT_PATH = COMMAND_DIR / "manage_subfeatures.py"


def load_execution_module():
    from sirius_skills.commands import manage_execution
    return manage_execution


def load_planning_module():
    from sirius_skills.commands import manage_planning
    return manage_planning


def load_subfeature_module():
    from sirius_skills.commands import manage_subfeatures
    return manage_subfeatures


def git_repo_root_for(path: Path) -> Optional[Path]:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip())


def target_dirty_worktree_paths(path: Path) -> List[str]:
    repo_root = git_repo_root_for(path)
    if repo_root is None:
        return []
    try:
        relative_path = path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return []
    result = subprocess.run(
        [
            "git",
            "-C",
            str(repo_root),
            "status",
            "--short",
            "--untracked-files=all",
            "--",
            str(relative_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError("Unable to inspect git worktree state for slice bootstrap.")
    return [line.rstrip() for line in result.stdout.splitlines() if line.strip()]


def parse_bootstrap_args(
    module, raw_args: List[str]
) -> Tuple[Optional[str], str]:
    if len(raw_args) == 1:
        requested_id = None
        name = raw_args[0]
    else:
        requested_id = module.validate_slice_id(raw_args[0])
        name = " ".join(raw_args[1:])

    normalized_name = module.normalize_feature_name(name)
    if not normalized_name:
        raise ValueError("Feature name cannot be empty.")
    return requested_id, normalized_name


def ensure_execution_registry(
    module,
    requested_slice_dir: Optional[str],
    scope_context: Optional[object] = None,
) -> Optional[str]:
    scope_context = scope_context or module.resolve_execution_scope_context()
    if module.execution_config_exists(scope_context):
        config = module.load_config(required=False, scope_context=scope_context)
        if "slice_dir" not in config:
            if requested_slice_dir is None:
                module.get_registry_paths(required_config=True, scope_context=scope_context)
                raise RuntimeError("Execution config does not define 'slice_dir'.")
            slice_dir = module.normalize_slice_dir(requested_slice_dir)
            module.write_config(
                slice_dir,
                preferred_workflow=str(config["preferred_workflow"]),
                auto_start_implementation=bool(config["auto_start_implementation"]),
                scope_context=scope_context,
            )
            module.ensure_registry(
                module.get_registry_paths(required_config=True, scope_context=scope_context)[0]
            )
            return slice_dir
        module.ensure_registry(
            module.get_registry_paths(required_config=True, scope_context=scope_context)[0]
        )
        return None

    slice_dir = module.normalize_slice_dir(
        requested_slice_dir or module.DEFAULT_SLICES_DIR
    )
    module.write_config(
        slice_dir,
        preferred_workflow=module.DEFAULT_PREFERRED_WORKFLOW,
        scope_context=scope_context,
    )
    module.ensure_registry(
        module.get_registry_paths(required_config=True, scope_context=scope_context)[0]
    )
    return slice_dir


def resolve_slice_id(
    module,
    requested_id: Optional[str],
    name: str,
    scope_context: Optional[object] = None,
) -> str:
    if requested_id:
        return requested_id

    conventions_config = module.load_conventions_config(
        required=False, scope_context=scope_context
    )
    rows = module.parse_registry(scope_context=scope_context)
    return module.infer_id_from_branch(conventions_config) or module.generate_hash_slice_id(
        rows, name
    )


def resolve_planning_handoff(
    feature_name: str,
    *,
    validate_dirty: bool = True,
    explicit_scope: Optional[str] = None,
) -> Optional[Dict[str, object]]:
    planning = load_planning_module()
    scope_context = planning.SCOPE_RUNTIME.resolve_scope_context(
        explicit_scope=explicit_scope
    )
    merged_config = planning.SCOPE_RUNTIME.load_merged_config(scope_context, "planning")
    if not merged_config:
        return None

    rows, feature, scope_context = planning.resolve_feature_lookup(
        feature_name, explicit_scope=explicit_scope
    )
    if feature is None:
        return None

    feature_dir = planning.feature_dir_for_row(feature, scope_context=scope_context)
    metadata = planning.read_metadata(feature_dir)
    current_status = str(metadata["status"])
    is_subfeature = Path(planning.subfeature_metadata_path_for(feature_dir)).exists()
    if current_status not in {"planning_reviewed", "slice_ready"}:
        raise RuntimeError(
            f"{'Subfeature' if is_subfeature else 'Planning feature'} '{feature['feature']}' "
            "must be in 'planning_reviewed' or 'slice_ready' before slice bootstrap. "
            f"Current status: '{current_status}'."
        )
    if validate_dirty:
        dirty_worktree_paths = target_dirty_worktree_paths(Path(feature_dir))
        if dirty_worktree_paths:
            raise RuntimeError(
                "Planning artifacts must be committed before slice bootstrap. "
                f"Dirty target paths: {', '.join(dirty_worktree_paths)}"
            )
    return {
        "planning": planning,
        "rows": rows,
        "feature": feature,
        "feature_dir": feature_dir,
        "metadata": metadata,
        "scope_context": scope_context,
        "is_subfeature": is_subfeature,
    }


def sync_planning_handoff(
    feature_name: str,
    slice_id: str,
    *,
    planning_handoff: Optional[Dict[str, object]] = None,
    validate_dirty: bool = True,
    explicit_scope: Optional[str] = None,
) -> Optional[Dict[str, object]]:
    handoff = planning_handoff or resolve_planning_handoff(
        feature_name,
        validate_dirty=validate_dirty,
        explicit_scope=explicit_scope,
    )
    if handoff is None:
        return None

    planning = handoff["planning"]
    rows = handoff["rows"]
    feature = handoff["feature"]
    feature_dir = str(handoff["feature_dir"])
    metadata = handoff["metadata"]
    scope_context = handoff["scope_context"]
    is_subfeature = bool(handoff["is_subfeature"])

    if is_subfeature:
        subfeatures = load_subfeature_module()
        subfeature_metadata = subfeatures.read_metadata(feature_dir)
        parent_feature_dir, _, subfeature_scope_context = subfeatures.resolve_parent_feature(
            planning, str(subfeature_metadata["parent_feature_slug"])
        )
        subfeature_rows = subfeatures.load_registry(parent_feature_dir)
        subfeature_row = subfeatures.find_subfeature(
            subfeature_rows, str(subfeature_metadata["subfeature_id"])
        )
        if subfeature_row is None:
            raise RuntimeError(
                f"Subfeature registry row not found for '{subfeature_metadata['subfeature_id']}'."
            )
        ok, message = subfeatures.update_subfeature_approval(
            planning,
            parent_feature_dir,
            subfeature_row,
            subfeature_scope_context,
            ready_slice_ids=[slice_id],
            require_existing_approval=True,
        )
        if not ok:
            raise RuntimeError(message)
        updated_metadata = planning.read_metadata(feature_dir)
        return {
            "feature": feature["feature"],
            "status": updated_metadata["status"],
            "ready_slice_ids": list(updated_metadata.get("ready_slice_ids") or []),
        }

    ready_slice_ids = list(metadata.get("ready_slice_ids") or [])
    if slice_id not in ready_slice_ids:
        ready_slice_ids.append(slice_id)

    ok, message = planning.update_feature_status(
        rows,
        feature,
        "slice_ready",
        slice_ids=ready_slice_ids,
        scope_context=scope_context,
    )
    if not ok:
        raise RuntimeError(
            f"Failed to sync planning handoff for '{feature['feature']}': {message}"
        )

    return {
        "feature": feature["feature"],
        "status": "slice_ready",
        "ready_slice_ids": ready_slice_ids,
    }


def bootstrap_slice(module, raw_args: List[str], requested_slice_dir: Optional[str]) -> Dict[str, object]:
    requested_id, name = parse_bootstrap_args(module, raw_args)
    planning_handoff = resolve_planning_handoff(name)
    execution_scope_context = module.resolve_execution_scope_context()
    if planning_handoff is not None and bool(planning_handoff["is_subfeature"]):
        execution_scope_context, _ = module.ensure_local_execution_scope(
            Path(str(planning_handoff["feature_dir"])),
            planning_handoff["scope_context"],
        )
    initialized_slice_dir = ensure_execution_registry(
        module, requested_slice_dir, scope_context=execution_scope_context
    )
    slice_id = resolve_slice_id(
        module, requested_id, name, scope_context=execution_scope_context
    )

    folder, created = module.create_slice(slice_id, name, scope_context=execution_scope_context)
    rows = module.parse_registry(scope_context=execution_scope_context)
    row = module.resolve_slice(rows, folder)
    if row is None:
        raise RuntimeError(f"Bootstrapped slice could not be resolved: {folder}")

    ok, issues, checks = module.validate_slice(row, scope_context=execution_scope_context)
    if not ok:
        raise RuntimeError(
            "Bootstrapped slice failed validation: " + ", ".join(issues)
        )

    config = module.load_config(required=True, scope_context=execution_scope_context)
    planning_sync = sync_planning_handoff(
        name,
        str(row["id"]),
        planning_handoff=planning_handoff,
    )
    return {
        "slice_id": row["id"],
        "feature": row["feature"],
        "folder": folder,
        "path": row["path"],
        "created": created,
        "initialized_config": initialized_slice_dir is not None,
        "initialized_slice_dir": initialized_slice_dir,
        "slice_dir": config["slice_dir"],
        "planning_sync": planning_sync,
        "checks": checks,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Bootstrap one execution slice from a ready work item while preserving "
            "guide-execution as the owner of execution readiness and registry state."
        )
    )
    parser.add_argument(
        "args",
        nargs="+",
        help="Pass either '<feature-name>' or '<slice-id> <feature-name>'.",
    )
    parser.add_argument(
        "--slice-dir",
        help=(
            "Slice directory to initialize when '.skills/execution.json' is missing. "
            "Defaults to 'slices'."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a machine-readable summary instead of human text.",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    module = load_execution_module()

    try:
        result = bootstrap_slice(module, args.args, args.slice_dir)
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    initialized_slice_dir = result["initialized_slice_dir"]
    if isinstance(initialized_slice_dir, str):
        print(f"Initialized execution registry and config in '{initialized_slice_dir}/'.")
    if result["created"]:
        print(f"Bootstrapped slice: {result['folder']}")
    else:
        print(f"Slice already exists: {result['folder']}")
    print(f"Validated slice: {result['slice_id']}")
    planning_sync = result.get("planning_sync")
    if isinstance(planning_sync, dict):
        print(
            f"Synced planning feature '{planning_sync['feature']}' to "
            f"'{planning_sync['status']}'."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
