from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from sirius_skills.legacy import load_legacy_module


SUBFEATURE_METADATA_FILE = ".subfeature-meta.json"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Record reviewed planning readiness for a feature or subfeature."
    )
    parser.add_argument("target", help="Feature selector or planning packet path.")
    parser.add_argument("--scope", default=None, help="Optional planning scope path.")
    parser.add_argument("--review-note", required=True, help="Readiness note to persist.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force the reviewed transition when deliberate repair is required.",
    )
    return parser.parse_args(argv)


def is_subfeature_target(target_dir: Path) -> bool:
    return (target_dir / SUBFEATURE_METADATA_FILE).is_file()


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    planning = load_legacy_module(
        "record_review_manage_planning",
        ("skills", "guide-planning", "scripts"),
        "manage_planning.py",
    )
    subfeatures = load_legacy_module(
        "record_review_manage_subfeatures",
        ("skills", "add-subfeature", "scripts"),
        "manage_subfeatures.py",
    )

    try:
        rows, feature, scope_context = planning.resolve_feature_lookup(
            args.target, explicit_scope=args.scope
        )
        if feature is None:
            raise RuntimeError(f"Planning target not found: {args.target}")
        target_dir = Path(planning.feature_dir_for_row(feature, scope_context=scope_context))

        if not is_subfeature_target(target_dir):
            success, message = planning.sync_feature_status(
                rows,
                feature,
                through="planning_reviewed",
                review_note=args.review_note,
                scope_context=scope_context,
            )
        else:
            metadata = subfeatures.read_metadata(str(target_dir))
            parent_feature_dir, _, subfeature_scope_context = subfeatures.resolve_parent_feature(
                planning, str(metadata["parent_feature_slug"])
            )
            subfeature_rows = subfeatures.load_registry(parent_feature_dir)
            subfeature_row = subfeatures.find_subfeature(
                subfeature_rows, str(metadata["subfeature_id"])
            )
            if subfeature_row is None:
                raise RuntimeError(
                    f"Subfeature '{metadata['subfeature_id']}' is missing from the parent registry."
                )
            success, message = subfeatures.update_subfeature_status(
                planning,
                parent_feature_dir,
                subfeature_row,
                "reviewed",
                subfeature_scope_context,
                force=args.force,
                review_note=args.review_note,
            )

        if not success:
            raise RuntimeError(message)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(message)
    return 0
