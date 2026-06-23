#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from sirius_skills.commands.report_data import (  # noqa: E402
    VALID_ARTIFACT_TYPES,
    VALID_GROUP_BY,
    build_report_result,
)


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("stale days must be greater than zero")
    return parsed


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Report operational workflow state across proposals, features, "
            "subfeatures, and slices."
        )
    )
    parser.add_argument(
        "--artifact-type",
        action="append",
        choices=VALID_ARTIFACT_TYPES,
        default=[],
        help="Limit reporting to one or more artifact types. Repeatable.",
    )
    parser.add_argument(
        "--group-by",
        choices=VALID_GROUP_BY,
        default="overview",
        help="Choose how to group the report output.",
    )
    parser.add_argument(
        "--stale-days",
        type=positive_int,
        default=30,
        help="Mark artifacts stale when updated at or before this day threshold.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable report output.",
    )
    parser.add_argument(
        "--check-packaged-parity",
        action="store_true",
        help="Include installed packaged-skill parity findings in the report output.",
    )
    return parser.parse_args(argv)


def run_report(
    artifact_types: List[str],
    group_by: str,
    stale_days: int,
    check_packaged_parity: bool,
) -> Dict[str, object]:
    return build_report_result(
        artifact_types=artifact_types,
        group_by=group_by,
        stale_days=stale_days,
        check_packaged_parity=check_packaged_parity,
    )


def render_text(result: Dict[str, object]) -> str:
    def consolidation_suffix(record: Dict[str, object]) -> str:
        consolidation = record.get("consolidation")
        if not isinstance(consolidation, dict):
            return ""
        targets = consolidation.get("targets", [])
        historical = consolidation.get("historical_artifacts", [])
        return (
            " "
            f"[consolidation={consolidation.get('disposition', 'unknown')}, "
            f"targets={len(targets) if isinstance(targets, list) else 0}, "
            f"historical={len(historical) if isinstance(historical, list) else 0}]"
        )

    def metrics_suffix(record: Dict[str, object]) -> str:
        metrics = record.get("implementation_metrics")
        if not isinstance(metrics, dict):
            return ""
        story_size = metrics.get("story_size", {})
        slices = metrics.get("slices", {})
        size_points = (
            story_size.get("sum_points") if isinstance(story_size, dict) else None
        )
        planned_count = (
            slices.get("planned_count") if isinstance(slices, dict) else None
        )
        execution_mode = metrics.get("execution_mode", "unknown")
        return (
            " "
            f"[metrics mode={execution_mode}, "
            f"size={size_points if size_points is not None else 'unavailable'}, "
            f"planned_slices={planned_count if planned_count is not None else 'unavailable'}]"
        )

    lines = [
        f"Artifact report ({result['group_by']}, stale threshold: {result['stale_days']} days)",
        f"Total artifacts: {result['summary']['total']}",
        f"Stale artifacts: {result['summary']['stale']}",
        f"Semantic preview findings: {result['summary']['semantic_preview_count']}",
        "Groups:",
    ]
    if result.get("check_packaged_parity"):
        lines.insert(
            3,
            f"Installed parity findings: {result['summary']['installed_parity_count']}",
        )
    for group in result["groups"]:
        lines.append(f"- {group['key']}: {group['count']} total, {group['stale']} stale")
    lines.append("Records:")
    for record in result["records"]:
        stale_marker = " stale" if record["is_stale"] else ""
        parent_suffix = f", parent={record['parent_feature']}" if record["parent_feature"] else ""
        lines.append(
            f"- {record['artifact_type']}:{record['artifact_id']} "
            f"[{record['status']}{stale_marker}] ({record['path']}{parent_suffix})"
            f"{metrics_suffix(record)}"
            f"{consolidation_suffix(record)}"
        )
    if result.get("check_packaged_parity") and result["installed_parity"]:
        lines.append("Installed parity:")
        for parity in result["installed_parity"]:
            lines.append(
                f"- {parity['skill_name']} [{parity['code']}] "
                f"{parity['message']} ({parity['relative_path']})"
            )
    if result["semantic_preview"]:
        lines.append("Semantic preview:")
        for preview in result["semantic_preview"]:
            lines.append(
                f"- {preview['artifact_type']}:{preview['artifact_id']} "
                f"[{preview['code']}] {preview['message']}"
            )
    return "\n".join(lines)


def main(argv=None) -> int:
    args = parse_args(argv)
    result = run_report(
        args.artifact_type,
        args.group_by,
        args.stale_days,
        args.check_packaged_parity,
    )
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
