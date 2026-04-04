#!/usr/bin/env python3

import argparse
import importlib.util
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
EVOLVE_SCRIPT = REPO_ROOT / "skills" / "evolve-feature" / "scripts" / "manage_feature_changes.py"
EXECUTION_SCRIPT = REPO_ROOT / "skills" / "guide-execution" / "scripts" / "manage_execution.py"
PLANNING_SCRIPT = REPO_ROOT / "skills" / "guide-planning" / "scripts" / "manage_planning.py"
FIGURES_DIR = "figures"
RECONCILABLE_FILES = [
    "discover.md",
    "system-design.md",
    "ui-design.md",
]


def now_timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Reconcile an approved feature change packet back into the canonical "
            "feature docs, remove completed execution slices, and remove the "
            "completed change packet."
        )
    )
    parser.add_argument("feature", help="Feature slug, folder name, or path")
    parser.add_argument("change", help="Change ID, folder name, or path")
    parser.add_argument(
        "--canonical-file",
        action="append",
        default=[],
        help=(
            "Canonical feature doc to reconcile. Repeatable. Defaults to all "
            "supported change-local docs present in the packet."
        ),
    )
    parser.add_argument(
        "--history-file",
        default=None,
        help="Deprecated and ignored. Reconciliation no longer publishes history files.",
    )
    parser.add_argument(
        "--no-history",
        action="store_true",
        help="Deprecated no-op. Reconciliation no longer publishes history files.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow deliberate repair when the change is not in the normal reviewed state.",
    )
    return parser.parse_args()


def relative_to_cwd(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        text = str(path)
        if text.startswith("./"):
            return text[2:]
        return text


def normalize_requested_filename(value: str) -> str:
    filename = Path(value.strip()).name
    if filename not in RECONCILABLE_FILES:
        raise RuntimeError(
            f"Unsupported canonical file '{value}'. Supported files: {RECONCILABLE_FILES}"
        )
    return filename


def select_reconciled_files(change_dir: Path, requested: list[str]) -> list[str]:
    if requested:
        selected = []
        for item in requested:
            filename = normalize_requested_filename(item)
            source_path = change_dir / filename
            if not source_path.exists():
                raise RuntimeError(
                    f"Requested change-local file '{filename}' does not exist in '{relative_to_cwd(change_dir)}'."
                )
            selected.append(filename)
        return list(dict.fromkeys(selected))

    selected = [name for name in RECONCILABLE_FILES if (change_dir / name).exists()]
    if not selected:
        raise RuntimeError(
            "No reconciliable change-local planning files were found. "
            "Expected one or more of: " + ", ".join(RECONCILABLE_FILES)
        )
    return selected


def dedupe_preserve_order(values: list[str]) -> list[str]:
    seen = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def parse_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


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


def planned_slice_ids(change_dir: Path, metadata: dict[str, object]) -> list[str]:
    planning_path = change_dir / "slice-planning.md"
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


def require_feature_complete(
    manage_execution, slice_ids: list[str], force: bool
) -> tuple[list[str], list[str]]:
    if not slice_ids:
        return [], []

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
        return missing, not_closed

    if missing or not_closed:
        problems = []
        if missing:
            problems.append("missing slices: " + ", ".join(missing))
        if not_closed:
            problems.append("open slices: " + ", ".join(not_closed))
        raise RuntimeError(
            "Feature reconciliation requires all planned slices in slice-planning.md "
            "to be closed before reconciliation can clean them up: " + "; ".join(problems)
        )

    return missing, not_closed


def rewrite_canonical_file(source_path: Path, canonical_path: Path) -> None:
    source_rel = relative_to_cwd(source_path)
    source_content = source_path.read_text(encoding="utf-8")
    if not source_content.strip():
        raise RuntimeError(f"Cannot reconcile empty change-local file '{source_rel}'.")
    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    canonical_path.write_text(source_content, encoding="utf-8")


def sync_figures(source_dir: Path, target_dir: Path) -> list[str]:
    if not source_dir.exists():
        return []

    copied: list[str] = []
    for source_path in sorted(source_dir.rglob("*")):
        if source_path.is_dir():
            continue
        relative_path = source_path.relative_to(source_dir)
        target_path = target_dir / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
        copied.append(relative_to_cwd(target_path))
    return copied


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


def update_feature_reconciliation_metadata(
    feature_dir: Path,
    feature_slug: str,
    reconciled_at: str,
    manage_planning,
) -> None:
    rows, feature, scope_context = manage_planning.resolve_feature_lookup(feature_slug)
    if not feature:
        raise RuntimeError(f"Canonical planning feature not found: {feature_slug}")

    success, message = manage_planning.update_feature_status(
        rows,
        feature,
        "implemented",
        force=True,
        scope_context=scope_context,
    )
    if not success:
        raise RuntimeError(message)

    metadata_path = feature_dir / ".planning-meta.json"
    payload: dict[str, object] = {}
    if metadata_path.exists():
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))

    payload["feature_completed_at"] = reconciled_at
    payload.pop("planning_archive_targets", None)
    payload.pop("archived_slice_paths", None)
    payload.pop("history_targets", None)
    payload["last_reconciled_at"] = reconciled_at
    metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    manage_feature_changes = load_module(EVOLVE_SCRIPT, "manage_feature_changes")
    manage_execution = load_module(EXECUTION_SCRIPT, "manage_execution")
    manage_planning = load_module(PLANNING_SCRIPT, "manage_planning")

    try:
        feature_dir_str, feature_slug = manage_feature_changes.resolve_feature_dir(args.feature)
        feature_dir = Path(feature_dir_str)
        rows = manage_feature_changes.load_registry(feature_dir_str)
        change = manage_feature_changes.find_change(rows, args.change)
        if not change:
            raise RuntimeError(f"Feature change not found: {args.change}")

        change_dir = Path(manage_feature_changes.change_dir_for_row(change))
        metadata = manage_feature_changes.read_metadata(str(change_dir))
        status = str(metadata["status"])
        if not args.force and status != "reviewed":
            raise RuntimeError(
                f"Change '{metadata['change_id']}' must be in 'reviewed' status before reconciliation. Current status: '{status}'."
            )

        review_note = str(metadata.get("review_note") or "").strip()
        if not args.force and not review_note:
            raise RuntimeError("Reconciliation requires a non-empty review note from planning review.")

        reconciled_at = now_timestamp()
        planned_ids = planned_slice_ids(change_dir, metadata)
        require_feature_complete(manage_execution, planned_ids, force=args.force)
        selected_files = select_reconciled_files(change_dir, args.canonical_file)

        reconciled_files: list[str] = []
        for filename in selected_files:
            source_path = change_dir / filename
            canonical_path = feature_dir / filename
            rewrite_canonical_file(source_path, canonical_path)
            reconciled_files.append(relative_to_cwd(canonical_path))

        if {"system-design.md", "ui-design.md"} & set(selected_files):
            copied_figures = sync_figures(change_dir / FIGURES_DIR, feature_dir / FIGURES_DIR)
            reconciled_files.extend(copied_figures)

        success, message = manage_feature_changes.update_change_status(
            feature_dir_str,
            change,
            "reconciled",
            force=args.force,
            reconciled_files=reconciled_files,
        )
        if not success:
            raise RuntimeError(message)

        refreshed_rows = manage_feature_changes.load_registry(feature_dir_str)
        refreshed_change = manage_feature_changes.find_change(refreshed_rows, str(metadata["change_id"]))
        if not refreshed_change:
            raise RuntimeError(f"Feature change disappeared from registry: {metadata['change_id']}")

        success, close_message = manage_feature_changes.update_change_status(
            feature_dir_str,
            refreshed_change,
            "closed",
            force=args.force,
        )
        if not success:
            raise RuntimeError(close_message)

        removed_slice_paths = delete_completed_slices(manage_execution, planned_ids)
        update_feature_reconciliation_metadata(
            feature_dir=feature_dir,
            feature_slug=feature_slug,
            reconciled_at=reconciled_at,
            manage_planning=manage_planning,
        )

        closed_rows = manage_feature_changes.load_registry(feature_dir_str)
        closed_change = manage_feature_changes.find_change(closed_rows, str(metadata["change_id"]))
        if not closed_change:
            raise RuntimeError(f"Feature change disappeared from registry: {metadata['change_id']}")
        success, delete_message = manage_feature_changes.delete_change(feature_dir_str, closed_change)
        if not success:
            raise RuntimeError(delete_message)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(f"Reconciled feature change: {relative_to_cwd(change_dir)}")
    for path in reconciled_files:
        print(f"- updated canonical artifact: {path}")
    for path in removed_slice_paths:
        print(f"- removed execution slice: {path}")
    print(f"- removed completed change packet: {relative_to_cwd(change_dir)}")
    print("- change status: closed and removed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
