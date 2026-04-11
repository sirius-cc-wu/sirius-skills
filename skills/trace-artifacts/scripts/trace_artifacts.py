#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from trace_data import (  # noqa: E402
    NODE_TYPES,
    TraceLookupError,
    build_trace_graph,
    build_trace_result,
    normalize_artifact_type,
)


ERROR_EXIT_CODE = 2
VALID_ARTIFACT_TYPES = tuple(sorted(set(NODE_TYPES + ("planned_slice", "execution-slice"))))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Trace durable lineage across proposals, features, subfeatures, "
            "planned slices, and execution slices."
        )
    )
    parser.add_argument(
        "--artifact-type",
        choices=VALID_ARTIFACT_TYPES,
        help="Trace one artifact type instead of printing the full lineage summary.",
    )
    parser.add_argument(
        "--artifact-id",
        help="Trace one artifact ID instead of printing the full lineage summary.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable lineage output.",
    )
    args = parser.parse_args()
    if bool(args.artifact_type) != bool(args.artifact_id):
        parser.error("Use --artifact-type and --artifact-id together.")
    return args


def run_trace(artifact_type: Optional[str] = None, artifact_id: Optional[str] = None) -> Dict[str, object]:
    graph = build_trace_graph()
    normalized_type = normalize_artifact_type(artifact_type) if artifact_type else None
    return build_trace_result(graph, normalized_type, artifact_id)


def render_text(result: Dict[str, object]) -> str:
    lines: List[str] = []
    target = result.get("target")
    if isinstance(target, dict):
        lines.append(f"Trace target: {target['artifact_type']} {target['artifact_id']}")
    else:
        lines.append("Lineage summary")

    summary = result["summary"]
    node_counts = summary["node_counts"]
    edge_counts = summary["edge_counts"]
    lines.append("Node counts:")
    for artifact_type in sorted(node_counts):
        lines.append(f"- {artifact_type}: {node_counts[artifact_type]}")
    lines.append("Edge counts:")
    if edge_counts:
        for relation in sorted(edge_counts):
            lines.append(f"- {relation}: {edge_counts[relation]}")
    else:
        lines.append("- none")

    lines.append("Nodes:")
    for node in result["nodes"]:
        path_suffix = f" ({node['path']})" if node["path"] else ""
        lines.append(f"- {node['artifact_type']}:{node['artifact_id']}{path_suffix}")

    lines.append("Edges:")
    if result["edges"]:
        for edge in result["edges"]:
            lines.append(
                f"- {edge['source_type']}:{edge['source_id']} -[{edge['relation']}]-> "
                f"{edge['target_type']}:{edge['target_id']}"
            )
    else:
        lines.append("- none")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    try:
        result = run_trace(args.artifact_type, args.artifact_id)
    except TraceLookupError as exc:
        print(str(exc), file=sys.stderr)
        return ERROR_EXIT_CODE
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return ERROR_EXIT_CODE

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
