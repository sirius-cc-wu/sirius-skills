import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


EXECUTION_SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "guide-execution"
    / "scripts"
    / "manage_execution.py"
)
PLANNING_SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "guide-planning"
    / "scripts"
    / "manage_planning.py"
)


def load_execution_module():
    spec = importlib.util.spec_from_file_location(
        "manage_execution", EXECUTION_SCRIPT_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_planning_module():
    spec = importlib.util.spec_from_file_location(
        "manage_planning", PLANNING_SCRIPT_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


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


def ensure_execution_registry(module, requested_slice_dir: Optional[str]) -> Optional[str]:
    scope_context = module.resolve_execution_scope_context()
    merged_config = module.SCOPE_RUNTIME.load_merged_config(scope_context, "execution")
    if merged_config:
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


def resolve_slice_id(module, requested_id: Optional[str], name: str) -> str:
    if requested_id:
        return requested_id

    conventions_config = module.load_conventions_config(required=False)
    rows = module.parse_registry()
    return module.infer_id_from_branch(conventions_config) or module.generate_hash_slice_id(
        rows, name
    )


def sync_planning_handoff(feature_name: str, slice_id: str) -> Optional[Dict[str, object]]:
    planning = load_planning_module()
    scope_context = planning.SCOPE_RUNTIME.resolve_scope_context()
    merged_config = planning.SCOPE_RUNTIME.load_merged_config(scope_context, "planning")
    if not merged_config:
        return None

    rows = planning.parse_registry(scope_context=scope_context)
    feature = planning.find_feature(rows, feature_name, scope_context=scope_context)
    if feature is None:
        return None

    feature_dir = planning.feature_dir_for_row(feature, scope_context=scope_context)
    metadata = planning.read_metadata(feature_dir)
    current_status = str(metadata["status"])
    if current_status not in {"planning_reviewed", "slice_ready"}:
        raise RuntimeError(
            f"Planning feature '{feature['feature']}' must be in 'planning_reviewed' "
            f"or 'slice_ready' before slice bootstrap. Current status: '{current_status}'."
        )

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
    initialized_slice_dir = ensure_execution_registry(module, requested_slice_dir)
    slice_id = resolve_slice_id(module, requested_id, name)

    folder, created = module.create_slice(slice_id, name)
    rows = module.parse_registry()
    row = module.resolve_slice(rows, folder)
    if row is None:
        raise RuntimeError(f"Bootstrapped slice could not be resolved: {folder}")

    ok, issues, checks = module.validate_slice(row)
    if not ok:
        raise RuntimeError(
            "Bootstrapped slice failed validation: " + ", ".join(issues)
        )

    config = module.load_config(required=True)
    planning_sync = sync_planning_handoff(name, str(row["id"]))
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


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
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
