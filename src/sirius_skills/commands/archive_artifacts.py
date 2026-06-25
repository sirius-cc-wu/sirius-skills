#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path
from typing import Dict


from sirius_skills.commands.archive_data import (
    ArchiveUsageError,
    VALID_ARTIFACT_TYPES,
    build_archive_result,
)


ERROR_EXIT_CODE = 2


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Report archive candidates and archive closed slices explicitly, "
            "including feature or subfeature scoped archival with design summaries."
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
        "--include-structural-diagrams",
        action="store_true",
        help=(
            "When applying a feature or subfeature archive, preserve existing "
            "class/component-style PlantUML diagrams from the blueprint or "
            "canonical system-design.md inside the archived summary appendix."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable output.",
    )
    return parser.parse_args(argv)


def render_text(result: Dict[str, object]) -> str:
    def consolidation_suffix(candidate: Dict[str, object]) -> str:
        consolidation = candidate.get("consolidation")
        if not isinstance(consolidation, dict):
            return ""
        historical = consolidation.get("historical_artifacts", [])
        return (
            " "
            f"[consolidation={consolidation.get('disposition', 'unknown')}, "
            f"historical={len(historical) if isinstance(historical, list) else 0}]"
        )

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
            f"{consolidation_suffix(candidate)}"
        )
    if result["applied"]:
        lines.append(f"Applied: {result['applied']['message']}")
    return "\n".join(lines)


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        result = build_archive_result(
            args.artifact_type,
            args.artifact_id,
            args.apply,
            include_structural_diagrams=args.include_structural_diagrams,
        )
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
