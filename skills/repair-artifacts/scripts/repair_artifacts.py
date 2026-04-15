#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path
from typing import Dict


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from repair_data import VALID_ARTIFACT_TYPES, build_repair_result  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Preview and optionally repair active workflow registries from durable "
            "directories and valid metadata."
        )
    )
    parser.add_argument(
        "--artifact-type",
        action="append",
        choices=VALID_ARTIFACT_TYPES,
        default=[],
        help="Limit repair to one or more artifact types. Repeatable.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the rebuilt registry/readme writes instead of printing a dry-run plan.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable repair output.",
    )
    return parser.parse_args()


def render_text(result: Dict[str, object]) -> str:
    mode = "apply" if result["apply"] else "dry-run"
    lines = [
        f"Artifact repair ({mode})",
        f"Changed layers: {result['summary']['planned_actions']}",
        f"Applied layers: {result['summary']['applied_actions']}",
        f"Skipped artifacts: {result['summary']['skipped_artifacts']}",
        f"Suggested repairs: {result['summary']['suggested_repairs']}",
        "Actions:",
    ]
    for action in result["actions"]:
        changed_marker = "changed" if action["changed"] else "no-change"
        applied_marker = ", applied" if action["applied"] else ""
        owner_suffix = f" ({action['owner_id']})" if action["owner_id"] else ""
        lines.append(
            f"- {action['artifact_type']}{owner_suffix}: {changed_marker}{applied_marker}, "
            f"{action['current_count']} -> {action['rebuilt_count']} rows"
        )
    if result["skipped"]:
        lines.append("Skipped:")
        for skipped in result["skipped"]:
            lines.append(f"- {skipped['artifact_type']}:{skipped['artifact_id']} ({skipped['message']})")
    if result["suggestions"]:
        lines.append("Suggestions:")
        for suggestion in result["suggestions"]:
            lines.append(
                f"- {suggestion['artifact_type']}:{suggestion['artifact_id']} "
                f"[{suggestion['code']}] {suggestion['message']}"
            )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    result = build_repair_result(artifact_types=args.artifact_type, apply=args.apply)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
