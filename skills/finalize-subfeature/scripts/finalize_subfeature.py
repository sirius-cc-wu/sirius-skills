#!/usr/bin/env python3

import argparse
import importlib.util
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
SUBFEATURE_SCRIPT = (
    REPO_ROOT / "skills" / "add-subfeature" / "scripts" / "manage_subfeatures.py"
)
EXECUTION_SCRIPT = REPO_ROOT / "skills" / "guide-execution" / "scripts" / "manage_execution.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Finalize a reviewed subfeature by verifying its planned slices are closed, "
            "cleaning up completed execution slices, and marking the durable subfeature implemented."
        )
    )
    parser.add_argument("feature", help="Parent feature slug, folder name, or path")
    parser.add_argument("subfeature", help="Subfeature ID, folder name, or path")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow deliberate repair when the subfeature is not in the normal reviewed state.",
    )
    return parser.parse_args()


def parse_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def dedupe_preserve_order(values: list[str]) -> list[str]:
    seen = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def extract_slice_ids_from_planning_text(markdown: str) -> list[str]:
    lines = markdown.splitlines()
    in_slice_table = False
    collected: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_slice_table:
                break
            continue
        if not stripped.startswith("|"):
            if in_slice_table and stripped.startswith("## "):
                break
            continue

        cells = parse_markdown_row(stripped)
        if not cells:
            continue
        first = cells[0]
        if first == "Slice ID":
            in_slice_table = True
            continue
        if not in_slice_table or first.startswith("---"):
            continue
        if first:
            collected.append(first)

    return dedupe_preserve_order(collected)


def planned_slice_ids(subfeature_dir: Path, metadata: dict[str, object]) -> list[str]:
    planning_path = subfeature_dir / "slice-planning.md"
    if planning_path.exists():
        extracted = extract_slice_ids_from_planning_text(
            planning_path.read_text(encoding="utf-8")
        )
        if extracted:
            return extracted

    affected = metadata.get("affected_slice_ids")
    if isinstance(affected, list):
        return dedupe_preserve_order(
            [item.strip() for item in affected if isinstance(item, str) and item.strip()]
        )

    return []


def require_subfeature_complete(manage_execution, slice_ids: list[str], force: bool) -> None:
    if not slice_ids:
        return

    rows = manage_execution.parse_registry()
    missing: list[str] = []
    not_closed: list[str] = []

    for slice_id in slice_ids:
        row = manage_execution.resolve_slice(rows, slice_id)
        if not row:
            missing.append(slice_id)
            continue
        if manage_execution.normalize_status(str(row["status"])) != "closed":
            not_closed.append(slice_id)

    if force:
        return

    if missing or not_closed:
        problems = []
        if missing:
            problems.append("missing slices: " + ", ".join(missing))
        if not_closed:
            problems.append("open slices: " + ", ".join(not_closed))
        raise RuntimeError(
            "Subfeature finalization requires all planned slices in slice-planning.md "
            "to be closed before cleanup can remove them: " + "; ".join(problems)
        )


def delete_completed_slices(manage_execution, slice_ids: list[str]) -> list[str]:
    removed_paths: list[str] = []
    if not slice_ids:
        return removed_paths

    rows = manage_execution.parse_registry()
    for slice_id in slice_ids:
        row = manage_execution.resolve_slice(rows, slice_id)
        if not row:
            continue
        if manage_execution.normalize_status(str(row["status"])) != "closed":
            continue
        removed_paths.append(str(row["path"]))
        success, message, _ = manage_execution.delete_slice(rows, row)
        if not success:
            raise RuntimeError(message)
        rows = manage_execution.parse_registry()

    return dedupe_preserve_order(removed_paths)


def main() -> int:
    args = parse_args()
    manage_subfeatures = load_module(SUBFEATURE_SCRIPT, "manage_subfeatures")
    manage_execution = load_module(EXECUTION_SCRIPT, "manage_execution")

    try:
        feature_dir, _, scope_context = manage_subfeatures.resolve_parent_feature(
            manage_subfeatures.load_manage_planning_module(), args.feature
        )
        rows = manage_subfeatures.load_registry(feature_dir)
        subfeature = manage_subfeatures.find_subfeature(rows, args.subfeature)
        if not subfeature:
            raise RuntimeError(f"Subfeature not found: {args.subfeature}")

        subfeature_dir = Path(
            manage_subfeatures.subfeature_dir_for_row(subfeature, scope_context)
        )
        metadata = manage_subfeatures.read_metadata(str(subfeature_dir))
        status = str(metadata["status"])
        if not args.force and status != "reviewed":
            raise RuntimeError(
                f"Subfeature '{metadata['subfeature_id']}' must be in 'reviewed' status before finalization. Current status: '{status}'."
            )

        review_note = str(metadata.get("review_note") or "").strip()
        if not args.force and not review_note:
            raise RuntimeError(
                "Subfeature finalization requires a non-empty review note from planning review."
            )

        slice_ids = planned_slice_ids(subfeature_dir, metadata)
        require_subfeature_complete(manage_execution, slice_ids, force=args.force)
        removed_slice_paths = delete_completed_slices(manage_execution, slice_ids)

        success, message = manage_subfeatures.update_subfeature_status(
            manage_subfeatures.load_manage_planning_module(),
            feature_dir,
            subfeature,
            "finalized",
            scope_context,
            force=args.force,
        )
        if not success:
            raise RuntimeError(message)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(f"Finalized subfeature: {subfeature_dir}")
    for path in removed_slice_paths:
        print(f"- removed execution slice: {path}")
    print("- subfeature status: finalized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
