#!/usr/bin/env python3

import argparse
import importlib.util
import re
import sys
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
EVOLVE_SCRIPT = REPO_ROOT / "skills" / "evolve-feature" / "scripts" / "manage_feature_changes.py"
RECONCILIATION_FILE = "reconciliation.md"
DEFAULT_HISTORY_FILE = "changes/history.md"
RECONCILABLE_FILES = [
    "discover.md",
    "system-design.md",
    "slice-planning.md",
    "slice-traceability.md",
]


def now_timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def load_manage_feature_changes_module():
    spec = importlib.util.spec_from_file_location("manage_feature_changes", EVOLVE_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Reconcile an approved feature change packet back into the canonical "
            "feature docs, publish retained history, and close the change."
        )
    )
    parser.add_argument("feature", help="Feature slug, folder name, or path")
    parser.add_argument("change", help="Change ID, folder name, or path")
    parser.add_argument(
        "--canonical-file",
        action="append",
        default=[],
        help=(
            "Canonical planning file to reconcile. Repeatable. Defaults to all "
            "supported change-local planning files present in the packet."
        ),
    )
    parser.add_argument(
        "--history-file",
        default=DEFAULT_HISTORY_FILE,
        help=(
            "Feature-local history file, relative to the canonical feature root. "
            f"Defaults to '{DEFAULT_HISTORY_FILE}'."
        ),
    )
    parser.add_argument(
        "--no-history",
        action="store_true",
        help="Close without publishing a feature-local history entry.",
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


def format_code_list(items: list[str], empty: str) -> str:
    if not items:
        return f"- {empty}"
    return "\n".join(f"- `{item}`" for item in items)


def normalize_history_file(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise RuntimeError("History file cannot be empty.")
    normalized = normalized.rstrip("/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    if Path(normalized).is_absolute():
        raise RuntimeError("History file must be relative to the canonical feature root.")
    return normalized


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


def strip_top_heading(text: str) -> str:
    lines = text.strip().splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
        while lines and not lines[0].strip():
            lines = lines[1:]
    return "\n".join(lines).strip()


def title_for_filename(filename: str) -> str:
    stem = filename.replace(".md", "").replace("-", " ")
    return "# " + stem.title()


def upsert_marked_block(content: str, start_marker: str, end_marker: str, block: str) -> str:
    pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), re.DOTALL)
    if pattern.search(content):
        updated = pattern.sub(block, content)
    else:
        base = content.rstrip()
        updated = (base + "\n\n" if base else "") + block
    return updated.rstrip() + "\n"


def append_reconciliation_block(
    canonical_path: Path,
    change_id: str,
    change_type: str,
    review_note: str,
    source_path: Path,
    reconciled_at: str,
) -> None:
    source_rel = relative_to_cwd(source_path)
    source_content = strip_top_heading(source_path.read_text(encoding="utf-8"))
    if not source_content:
        raise RuntimeError(f"Cannot reconcile empty change-local file '{source_rel}'.")

    start_marker = f"<!-- reconcile-feature:start {change_id} {canonical_path.name} -->"
    end_marker = f"<!-- reconcile-feature:end {change_id} {canonical_path.name} -->"
    block = (
        f"{start_marker}\n"
        f"## Reconciled Change Packet: {change_id}\n\n"
        f"- Reconciled at: `{reconciled_at}`\n"
        f"- Change type: `{change_type}`\n"
        f"- Source change doc: `{source_rel}`\n"
        f"- Review note: {review_note}\n\n"
        "### Adopted Change Content\n\n"
        f"{source_content}\n"
        f"{end_marker}"
    )

    if canonical_path.exists():
        existing = canonical_path.read_text(encoding="utf-8")
    else:
        existing = title_for_filename(canonical_path.name) + "\n"
    canonical_path.write_text(
        upsert_marked_block(existing, start_marker, end_marker, block),
        encoding="utf-8",
    )


def write_reconciliation_summary(
    change_dir: Path,
    feature_slug: str,
    change_id: str,
    change_type: str,
    review_note: str,
    reconciled_files: list[str],
    history_targets: list[str],
    reconciled_at: str,
) -> Path:
    reconciliation_path = change_dir / RECONCILIATION_FILE
    content = (
        f"# Reconciliation: {change_id}\n\n"
        "## Target Feature\n\n"
        f"- Feature: `{feature_slug}`\n"
        f"- Change ID: `{change_id}`\n"
        f"- Change type: `{change_type}`\n"
        f"- Reconciled at: `{reconciled_at}`\n\n"
        "## Canonical Files Updated\n\n"
        f"{format_code_list(reconciled_files, 'No canonical files were updated.')}\n\n"
        "## Review Note\n\n"
        f"{review_note}\n\n"
        "## History Targets\n\n"
        f"{format_code_list(history_targets, 'No feature-local history file was updated.')}\n"
    )
    reconciliation_path.write_text(content, encoding="utf-8")
    return reconciliation_path


def publish_history(
    feature_dir: Path,
    change_dir: Path,
    feature_slug: str,
    change_id: str,
    change_type: str,
    review_note: str,
    reconciled_files: list[str],
    history_file: str,
    reconciled_at: str,
) -> Path:
    history_path = feature_dir / history_file
    history_path.parent.mkdir(parents=True, exist_ok=True)

    if history_path.exists():
        existing = history_path.read_text(encoding="utf-8")
    else:
        existing = "# Feature Change History\n\n"

    change_rel = relative_to_cwd(change_dir)
    start_marker = f"<!-- reconcile-feature:history:start {change_id} -->"
    end_marker = f"<!-- reconcile-feature:history:end {change_id} -->"
    block = (
        f"{start_marker}\n"
        f"## Closed Change: {change_id}\n\n"
        f"- Closed at: `{reconciled_at}`\n"
        f"- Feature: `{feature_slug}`\n"
        f"- Change type: `{change_type}`\n"
        f"- Change packet: `{change_rel}/`\n\n"
        "### Canonical Files Updated\n\n"
        f"{format_code_list(reconciled_files, 'No canonical files were updated.')}\n\n"
        "### Review Note\n\n"
        f"{review_note}\n"
        f"{end_marker}"
    )
    history_path.write_text(
        upsert_marked_block(existing, start_marker, end_marker, block),
        encoding="utf-8",
    )
    return history_path


def main() -> int:
    args = parse_args()
    manage_feature_changes = load_manage_feature_changes_module()

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
        selected_files = select_reconciled_files(change_dir, args.canonical_file)
        reconciled_files: list[str] = []
        for filename in selected_files:
            source_path = change_dir / filename
            canonical_path = feature_dir / filename
            append_reconciliation_block(
                canonical_path=canonical_path,
                change_id=str(metadata["change_id"]),
                change_type=str(metadata["change_type"]),
                review_note=review_note or "No review note recorded.",
                source_path=source_path,
                reconciled_at=reconciled_at,
            )
            reconciled_files.append(relative_to_cwd(canonical_path))

        history_targets: list[str] = []
        if not args.no_history:
            history_path = publish_history(
                feature_dir=feature_dir,
                change_dir=change_dir,
                feature_slug=feature_slug,
                change_id=str(metadata["change_id"]),
                change_type=str(metadata["change_type"]),
                review_note=review_note or "No review note recorded.",
                reconciled_files=reconciled_files,
                history_file=normalize_history_file(args.history_file),
                reconciled_at=reconciled_at,
            )
            history_targets.append(relative_to_cwd(history_path))

        write_reconciliation_summary(
            change_dir=change_dir,
            feature_slug=feature_slug,
            change_id=str(metadata["change_id"]),
            change_type=str(metadata["change_type"]),
            review_note=review_note or "No review note recorded.",
            reconciled_files=reconciled_files,
            history_targets=history_targets,
            reconciled_at=reconciled_at,
        )

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
            history_targets=history_targets,
        )
        if not success:
            raise RuntimeError(close_message)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(f"Reconciled change packet: {relative_to_cwd(change_dir)}")
    for path in reconciled_files:
        print(f"- updated canonical doc: {path}")
    if history_targets:
        for path in history_targets:
            print(f"- updated history: {path}")
    print(f"- change status: closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
