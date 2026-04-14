#!/usr/bin/env python3

import argparse
import importlib.util
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple


SCRIPT_DIR = Path(__file__).resolve().parent
SKILLS_DIR = SCRIPT_DIR.parents[1]
GUIDE_PLANNING_SCRIPT = SKILLS_DIR / "guide-planning" / "scripts" / "manage_planning.py"
GUIDE_EXECUTION_SCRIPT = (
    SKILLS_DIR / "guide-execution" / "scripts" / "manage_execution.py"
)
TRACE_DATA_SCRIPT = SKILLS_DIR / "trace-artifacts" / "scripts" / "trace_data.py"


@dataclass
class PlannedSliceBacklogEntry:
    planned_slice_id: str
    story_id: str
    title: str
    depends_on: List[str]
    execution_slice_ids: List[str]
    closed_execution_slice_ids: List[str]
    state: str


@dataclass
class BacklogResolution:
    target_type: str
    target_id: str
    target_path: str
    planning_status: str
    ready_next: List[str]
    active_execution_slices: List[str]
    entries: List[PlannedSliceBacklogEntry]

    def to_dict(self) -> Dict[str, object]:
        return {
            "target_type": self.target_type,
            "target_id": self.target_id,
            "target_path": self.target_path,
            "planning_status": self.planning_status,
            "ready_next": list(self.ready_next),
            "active_execution_slices": list(self.active_execution_slices),
            "entries": [asdict(entry) for entry in self.entries],
        }


def load_module(script_path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _split_table_row(line: str) -> List[str]:
    stripped = line.strip().strip("|")
    return [cell.strip() for cell in stripped.split("|")]


def _normalize_table_header(value: str) -> str:
    return " ".join(value.replace("-", " ").strip().lower().split())


def _split_cell_values(value: str) -> List[str]:
    normalized = value.replace("<br/>", "\n").replace("<br />", "\n").replace("<br>", "\n")
    result: List[str] = []
    for part in normalized.replace(";", ",").split(","):
        for subpart in part.splitlines():
            cleaned = subpart.strip()
            if cleaned:
                result.append(cleaned)
    return result


def _find_markdown_table(lines: Sequence[str], required_headers: Sequence[str]) -> Tuple[Dict[str, int], int]:
    required = {_normalize_table_header(value) for value in required_headers}
    for index in range(len(lines) - 1):
        header_line = lines[index].strip()
        divider_line = lines[index + 1].strip()
        if "|" not in header_line or "|" not in divider_line:
            continue
        headers = _split_table_row(header_line)
        normalized_headers = [_normalize_table_header(header) for header in headers]
        if not required.issubset(set(normalized_headers)):
            continue
        divider_cells = _split_table_row(divider_line)
        if not divider_cells or not all(cell.startswith("---") for cell in divider_cells):
            continue
        return {name: pos for pos, name in enumerate(normalized_headers)}, index + 2
    raise RuntimeError("Could not locate the expected markdown table.")


def parse_planned_slices(slice_planning_path: Path) -> List[Dict[str, object]]:
    lines = slice_planning_path.read_text(encoding="utf-8").splitlines()
    header_map, start_index = _find_markdown_table(
        lines,
        [
            "Slice ID",
            "Story ID",
            "Title",
            "Depends On",
        ],
    )

    results: List[Dict[str, object]] = []
    index = start_index
    while index < len(lines):
        row_line = lines[index].strip()
        if not row_line.startswith("|"):
            break
        cells = _split_table_row(row_line)
        if len(cells) <= max(header_map.values()):
            index += 1
            continue
        planned_slice_id = cells[header_map["slice id"]].strip()
        if not planned_slice_id:
            index += 1
            continue
        results.append(
            {
                "planned_slice_id": planned_slice_id,
                "story_id": cells[header_map["story id"]].strip(),
                "title": cells[header_map["title"]].strip(),
                "depends_on": _split_cell_values(cells[header_map["depends on"]]),
            }
        )
        index += 1
    return results


def resolve_target(planning_module, selector: str, explicit_scope: Optional[str]):
    rows, feature, scope_context = planning_module.resolve_feature_lookup(
        selector, explicit_scope=explicit_scope
    )
    if feature is None:
        raise RuntimeError(f"Planning target not found: {selector}")
    feature_dir = planning_module.feature_dir_for_row(feature, scope_context=scope_context)
    metadata = planning_module.read_metadata(feature_dir)
    status = str(metadata["status"])
    if status not in {"planning_reviewed", "slice_ready"}:
        raise RuntimeError(
            f"Planning target '{feature['feature']}' must be in 'planning_reviewed' "
            f"or 'slice_ready'. Current status: '{status}'."
        )
    target_type = "subfeature" if "/subfeatures/" in str(feature["path"]) else "feature"
    return feature, feature_dir, metadata, scope_context, target_type


def resolve_backlog(selector: str, explicit_scope: Optional[str] = None) -> BacklogResolution:
    planning_module = load_module(GUIDE_PLANNING_SCRIPT, "manage_planning")
    execution_module = load_module(GUIDE_EXECUTION_SCRIPT, "manage_execution")
    trace_data = load_module(TRACE_DATA_SCRIPT, "trace_data")

    feature, target_dir, metadata, scope_context, target_type = resolve_target(
        planning_module, selector, explicit_scope
    )

    slice_planning_path = Path(target_dir) / "slice-planning.md"
    traceability_path = Path(target_dir) / "slice-traceability.md"
    if not slice_planning_path.exists():
        raise RuntimeError(f"Missing planning file: {slice_planning_path}")
    if not traceability_path.exists():
        raise RuntimeError(f"Missing traceability file: {traceability_path}")

    planned_slices = parse_planned_slices(slice_planning_path)
    traceability_records = trace_data.parse_traceability_records(
        traceability_path,
        target_type,
        str(feature["feature"]),
        str(feature["path"]),
    )
    execution_rows = execution_module.parse_registry(scope_context=scope_context)
    execution_status_by_id = {str(row["id"]): str(row["status"]) for row in execution_rows}

    execution_ids_by_planned_slice: Dict[str, List[str]] = {}
    for record in traceability_records:
        for planned_slice_id in record.planned_slice_ids:
            bucket = execution_ids_by_planned_slice.setdefault(planned_slice_id, [])
            for execution_slice_id in record.execution_slice_ids:
                if execution_slice_id not in bucket:
                    bucket.append(execution_slice_id)

    completed_planned_slices = set()
    active_execution_slices: List[str] = []
    entries: List[PlannedSliceBacklogEntry] = []

    for planned_slice in planned_slices:
        planned_slice_id = str(planned_slice["planned_slice_id"])
        execution_slice_ids = execution_ids_by_planned_slice.get(planned_slice_id, [])
        closed_execution_slice_ids = [
            slice_id
            for slice_id in execution_slice_ids
            if execution_status_by_id.get(slice_id) == "closed"
        ]
        non_closed_execution_slice_ids = [
            slice_id
            for slice_id in execution_slice_ids
            if execution_status_by_id.get(slice_id) not in {None, "closed"}
        ]
        if closed_execution_slice_ids:
            completed_planned_slices.add(planned_slice_id)
        active_execution_slices.extend(
            slice_id for slice_id in non_closed_execution_slice_ids if slice_id not in active_execution_slices
        )
        entries.append(
            PlannedSliceBacklogEntry(
                planned_slice_id=planned_slice_id,
                story_id=str(planned_slice["story_id"]),
                title=str(planned_slice["title"]),
                depends_on=list(planned_slice["depends_on"]),
                execution_slice_ids=list(execution_slice_ids),
                closed_execution_slice_ids=list(closed_execution_slice_ids),
                state="pending",
            )
        )

    ready_next: List[str] = []
    for entry in entries:
        if entry.closed_execution_slice_ids:
            entry.state = "completed"
            continue
        if any(slice_id in active_execution_slices for slice_id in entry.execution_slice_ids):
            entry.state = "active"
            continue
        if all(dep in completed_planned_slices for dep in entry.depends_on):
            entry.state = "ready"
            ready_next.append(entry.planned_slice_id)
        else:
            entry.state = "blocked"

    return BacklogResolution(
        target_type=target_type,
        target_id=str(feature["feature"]),
        target_path=str(feature["path"]),
        planning_status=str(metadata["status"]),
        ready_next=ready_next,
        active_execution_slices=active_execution_slices,
        entries=entries,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Resolve one reviewed feature or subfeature into remaining planned slices "
            "using planning traceability and execution closure state."
        )
    )
    parser.add_argument("target", help="Feature slug, subfeature slug, or planning packet path.")
    parser.add_argument(
        "--scope",
        help="Optional planning scope path when the target is outside the active scope.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable output.")
    return parser


def render_text(result: BacklogResolution) -> str:
    lines = [
        f"Target: {result.target_type} {result.target_id}",
        f"Planning status: {result.planning_status}",
        f"Path: {result.target_path}",
        f"Ready next: {', '.join(result.ready_next) if result.ready_next else '-'}",
        f"Active execution slices: {', '.join(result.active_execution_slices) if result.active_execution_slices else '-'}",
        "",
        "Planned slices:",
    ]
    for entry in result.entries:
        suffix = ""
        if entry.depends_on:
            suffix = f" (depends on: {', '.join(entry.depends_on)})"
        lines.append(f"- {entry.planned_slice_id}: {entry.state}{suffix}")
    return "\n".join(lines)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = resolve_backlog(args.target, explicit_scope=args.scope)
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(render_text(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
