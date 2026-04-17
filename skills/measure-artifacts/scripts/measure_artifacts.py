#!/usr/bin/env python3

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from metrics_engine import build_metrics_for_target, resolve_measurement_target  # noqa: E402
from metrics_store import sidecar_path_for, write_metrics  # noqa: E402


ERROR_EXIT_CODE = 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compute durable implementation metrics for a completed feature or subfeature."
        )
    )
    parser.add_argument("target", help="Feature slug, subfeature slug, or planning packet path.")
    parser.add_argument(
        "--scope",
        help="Optional planning scope path when the target is outside the active scope.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Persist the normalized implementation-metrics.json sidecar.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable metrics output.",
    )
    return parser.parse_args()


def render_text(record: dict, sidecar_path: str | None = None, wrote: bool = False) -> str:
    story_size = record["story_size"]
    slices = record["slices"]
    churn = record["implementation_churn"]
    lines = [
        f"Measurement target: {record['artifact_type']} {record['artifact_id']}",
        f"Status: {record['status']}",
        f"Execution mode: {record['execution_mode']}",
        "Story size:",
        f"- points: {story_size['sum_points'] if story_size['sum_points'] is not None else 'unavailable'}",
        f"- unsupported sizes: {', '.join(story_size['unsupported_sizes']) if story_size['unsupported_sizes'] else 'none'}",
        "Slices:",
        f"- planned count: {slices['planned_count'] if slices['planned_count'] is not None else 'unavailable'}",
        f"- linked execution slices: {', '.join(slices['linked_slice_ids']) if slices['linked_slice_ids'] else 'none'}",
        "Implementation churn:",
        f"- confidence: {churn['confidence']}",
        f"- total changed lines: {churn['total_changed_lines'] if churn['total_changed_lines'] is not None else 'unavailable'}",
    ]
    if sidecar_path is not None:
        action = "written" if wrote else "preview only"
        lines.append(f"Sidecar: {sidecar_path} ({action})")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    try:
        target = resolve_measurement_target(args.target, explicit_scope=args.scope)
        record = build_metrics_for_target(
            target, computed_at=datetime.now().isoformat(timespec="seconds")
        )
        sidecar_path = str(sidecar_path_for(target.artifact_path))
        if args.write:
            write_metrics(target.artifact_path, record)
        if args.json:
            payload = dict(record)
            payload["sidecar_path"] = sidecar_path
            payload["persisted"] = bool(args.write)
            print(json.dumps(payload, indent=2))
        else:
            print(render_text(record, sidecar_path=sidecar_path, wrote=bool(args.write)))
        return 0
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return ERROR_EXIT_CODE


if __name__ == "__main__":
    raise SystemExit(main())
