#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path
from typing import Dict


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from archive_data import (  # noqa: E402
    ArchiveUsageError,
    VALID_ARTIFACT_TYPES,
    build_archive_result,
)


ERROR_EXIT_CODE = 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Report archive candidates and archive one closed slice explicitly "
            "through the execution owner helper."
        )
    )
    parser.add_argument(
        "--artifact-type",
        choices=VALID_ARTIFACT_TYPES,
        help="Filter candidate discovery to one artifact type.",
    )
    parser.add_argument(
        "--artifact-id",
        help="Inspect or archive one specific artifact when used with --artifact-type.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Archive one supported target instead of only reporting candidates.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable output.",
    )
    return parser.parse_args()


def render_text(result: Dict[str, object]) -> str:
    lines = [
        f"Archive candidates: {result['summary']['candidate_count']}",
        f"Directly archivable now: {result['summary']['archivable_count']}",
        "Candidates:",
    ]
    for candidate in result["candidates"]:
        archivable_suffix = " archivable" if candidate["archivable"] else " candidate-only"
        lines.append(
            f"- {candidate['artifact_type']}:{candidate['artifact_id']} "
            f"[{candidate['status']}{archivable_suffix}] ({candidate['path']})"
        )
    if result["applied"]:
        lines.append(f"Applied: {result['applied']['message']}")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    try:
        result = build_archive_result(args.artifact_type, args.artifact_id, args.apply)
    except ArchiveUsageError as exc:
        print(str(exc), file=sys.stderr)
        return ERROR_EXIT_CODE

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
