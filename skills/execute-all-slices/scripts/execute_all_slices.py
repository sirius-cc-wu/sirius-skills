#!/usr/bin/env python3

import argparse
import importlib.util
import json
import subprocess
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
SUBFEATURES_SCRIPT = SKILLS_DIR / "add-subfeature" / "scripts" / "manage_subfeatures.py"
ARTIFACT_INVENTORY_SCRIPT = (
    SKILLS_DIR / "audit-artifacts" / "scripts" / "artifact_inventory.py"
)


@dataclass
class PlannedSliceBacklogEntry:
    planned_slice_id: str
    story_id: str
    title: str
    increment_ids: List[str]
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
    increment_order: List[str]
    current_increment: Optional[str]
    completed_increments: List[str]
    ready_next: List[str]
    active_execution_slices: List[str]
    entries: List[PlannedSliceBacklogEntry]

    def to_dict(self) -> Dict[str, object]:
        return {
            "target_type": self.target_type,
            "target_id": self.target_id,
            "target_path": self.target_path,
            "planning_status": self.planning_status,
            "increment_order": list(self.increment_order),
            "current_increment": self.current_increment,
            "completed_increments": list(self.completed_increments),
            "ready_next": list(self.ready_next),
            "active_execution_slices": list(self.active_execution_slices),
            "entries": [asdict(entry) for entry in self.entries],
        }


@dataclass
class BootstrapResult:
    backlog: BacklogResolution
    bootstrapped_slice_id: Optional[str]
    bootstrapped_slice_path: Optional[str]
    slice_status: Optional[str]
    checkpoint_slice_id: Optional[str]
    dirty_worktree_paths: List[str]
    next_owner: Optional[str]
    completed: bool
    action: str

    def to_dict(self) -> Dict[str, object]:
        payload = self.backlog.to_dict()
        payload["bootstrapped_slice_id"] = self.bootstrapped_slice_id
        payload["bootstrapped_slice_path"] = self.bootstrapped_slice_path
        payload["slice_status"] = self.slice_status
        payload["checkpoint_slice_id"] = self.checkpoint_slice_id
        payload["dirty_worktree_paths"] = list(self.dirty_worktree_paths)
        payload["next_owner"] = self.next_owner
        payload["completed"] = self.completed
        payload["action"] = self.action
        return payload


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


def parse_increment_plan(
    slice_planning_path: Path,
) -> Tuple[List[str], Dict[str, List[str]]]:
    lines = slice_planning_path.read_text(encoding="utf-8").splitlines()
    try:
        header_map, start_index = _find_markdown_table(
            lines,
            [
                "Increment",
                "Planned Slice IDs",
            ],
        )
    except RuntimeError:
        return [], {}

    increment_order: List[str] = []
    increment_ids_by_planned_slice: Dict[str, List[str]] = {}
    index = start_index
    while index < len(lines):
        row_line = lines[index].strip()
        if not row_line.startswith("|"):
            break
        cells = _split_table_row(row_line)
        if len(cells) <= max(header_map.values()):
            index += 1
            continue
        increment_id = cells[header_map["increment"]].strip()
        if not increment_id:
            index += 1
            continue
        if increment_id not in increment_order:
            increment_order.append(increment_id)
        for planned_slice_id in _split_cell_values(cells[header_map["planned slice ids"]]):
            bucket = increment_ids_by_planned_slice.setdefault(planned_slice_id, [])
            if increment_id not in bucket:
                bucket.append(increment_id)
        index += 1
    return increment_order, increment_ids_by_planned_slice


def parse_traceability_table(
    traceability_path: Path,
) -> Tuple[List[str], int, Dict[str, int], List[List[str]]]:
    lines = traceability_path.read_text(encoding="utf-8").splitlines()
    header_map, start_index = _find_markdown_table(
        lines,
        [
            "Story ID",
            "Planned Slice IDs",
            "Execution Slice IDs",
        ],
    )
    rows: List[List[str]] = []
    index = start_index
    while index < len(lines):
        row_line = lines[index].strip()
        if not row_line.startswith("|"):
            break
        rows.append(_split_table_row(row_line))
        index += 1
    return lines, start_index, header_map, rows


def collect_increment_metadata(
    slice_planning_path: Path, traceability_records
) -> Tuple[List[str], Dict[str, List[str]]]:
    increment_order, increment_ids_by_planned_slice = parse_increment_plan(slice_planning_path)
    for record in traceability_records:
        increment_ids = _split_cell_values(record.increments)
        for increment_id in increment_ids:
            if increment_id not in increment_order:
                increment_order.append(increment_id)
        for planned_slice_id in record.planned_slice_ids:
            bucket = increment_ids_by_planned_slice.setdefault(planned_slice_id, [])
            for increment_id in increment_ids:
                if increment_id not in bucket:
                    bucket.append(increment_id)
    return increment_order, increment_ids_by_planned_slice


def record_execution_slice_id(
    traceability_path: Path, planned_slice_id: str, execution_slice_id: str
) -> None:
    lines, start_index, header_map, rows = parse_traceability_table(traceability_path)
    planned_slice_column = header_map["planned slice ids"]
    execution_slice_column = header_map["execution slice ids"]
    row_index: Optional[int] = None

    for index, row in enumerate(rows):
        if planned_slice_column >= len(row):
            continue
        planned_slice_ids = _split_cell_values(row[planned_slice_column])
        if planned_slice_id not in planned_slice_ids:
            continue
        if len(planned_slice_ids) != 1:
            raise RuntimeError(
                "Batch execution requires one planned slice per traceability row. "
                f"Split the row that contains '{planned_slice_id}' before bootstrapping."
            )
        row_index = index
        execution_slice_ids = (
            _split_cell_values(row[execution_slice_column])
            if execution_slice_column < len(row)
            else []
        )
        if execution_slice_id not in execution_slice_ids:
            execution_slice_ids.append(execution_slice_id)
        while len(row) <= execution_slice_column:
            row.append("")
        row[execution_slice_column] = ", ".join(execution_slice_ids)
        break

    if row_index is None:
        raise RuntimeError(
            f"Could not find a traceability row for planned slice '{planned_slice_id}'."
        )

    for offset, row in enumerate(rows):
        line_index = start_index + offset
        lines[line_index] = "| " + " | ".join(row) + " |"
    traceability_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def resolve_target(planning_module, selector: str, explicit_scope: Optional[str]):
    rows, feature, scope_context = planning_module.resolve_feature_lookup(
        selector, explicit_scope=explicit_scope
    )
    if feature is None:
        raise RuntimeError(f"Planning target not found: {selector}")
    feature_dir = planning_module.feature_dir_for_row(feature, scope_context=scope_context)
    metadata = planning_module.read_metadata(feature_dir)
    status = str(metadata["status"])
    if status not in {"planning_reviewed", "slice_ready", "implemented"}:
        raise RuntimeError(
            f"Planning target '{feature['feature']}' must be in 'planning_reviewed', "
            f"'slice_ready', or 'implemented'. Current status: '{status}'."
        )
    target_type = "subfeature" if "/subfeatures/" in str(feature["path"]) else "feature"
    return feature, feature_dir, metadata, scope_context, target_type


def parse_dependency_selector(dependency: str) -> Optional[Tuple[str, str]]:
    parts = dependency.rsplit(" ", 1)
    if len(parts) != 2:
        return None
    selector, status = (part.strip() for part in parts)
    if not selector or not status:
        return None
    return selector, status


def dependency_is_satisfied(
    dependency: str,
    completed_planned_slices: set,
    planning_module,
    planning_rows: List[Dict[str, object]],
    scope_context: object,
    target_type: str,
    target_dir: Path,
    sibling_subfeature_rows: Optional[List[Dict[str, object]]] = None,
    subfeature_module=None,
) -> bool:
    if dependency in completed_planned_slices:
        return True

    parsed_dependency = parse_dependency_selector(dependency)
    if parsed_dependency is None:
        return False
    selector, required_status = parsed_dependency

    if (
        target_type == "subfeature"
        and sibling_subfeature_rows is not None
        and subfeature_module is not None
    ):
        try:
            required_subfeature_status = subfeature_module.normalize_status(required_status)
        except ValueError:
            required_subfeature_status = None
        if required_subfeature_status is not None:
            sibling_subfeature = subfeature_module.find_subfeature(
                sibling_subfeature_rows, selector
            )
            if sibling_subfeature is not None:
                sibling_metadata = subfeature_module.read_metadata(
                    subfeature_module.subfeature_dir_for_row(
                        sibling_subfeature, scope_context
                    )
                )
                actual_status = str(sibling_metadata["status"])
                return subfeature_module.STATUS_SEQUENCE.index(
                    actual_status
                ) >= subfeature_module.STATUS_SEQUENCE.index(required_subfeature_status)

    try:
        required_planning_status = planning_module.normalize_status(required_status)
    except ValueError:
        return False

    dependency_target = planning_module.find_feature(
        planning_rows, selector, scope_context=scope_context
    )
    if dependency_target is None:
        return False

    dependency_metadata = planning_module.read_metadata(
        planning_module.feature_dir_for_row(dependency_target, scope_context=scope_context)
    )
    actual_planning_status = str(dependency_metadata["status"])
    return planning_module.STATUS_SEQUENCE.index(
        actual_planning_status
    ) >= planning_module.STATUS_SEQUENCE.index(required_planning_status)


def resolve_backlog(selector: str, explicit_scope: Optional[str] = None) -> BacklogResolution:
    planning_module = load_module(GUIDE_PLANNING_SCRIPT, "manage_planning")
    execution_module = load_module(GUIDE_EXECUTION_SCRIPT, "manage_execution")
    subfeature_module = load_module(SUBFEATURES_SCRIPT, "manage_subfeatures")
    artifact_inventory = load_module(ARTIFACT_INVENTORY_SCRIPT, "artifact_inventory")

    feature, target_dir, metadata, scope_context, target_type = resolve_target(
        planning_module, selector, explicit_scope
    )
    target_dir_path = Path(target_dir)

    slice_planning_path = Path(target_dir) / "slice-planning.md"
    traceability_path = Path(target_dir) / "slice-traceability.md"
    if not slice_planning_path.exists():
        raise RuntimeError(f"Missing planning file: {slice_planning_path}")
    if not traceability_path.exists():
        raise RuntimeError(f"Missing traceability file: {traceability_path}")

    planned_slices = parse_planned_slices(slice_planning_path)
    traceability_records = artifact_inventory.parse_traceability_records(
        traceability_path,
        target_type,
        str(feature["feature"]),
        str(feature["path"]),
    )
    increment_order, increment_ids_by_planned_slice = collect_increment_metadata(
        slice_planning_path, traceability_records
    )
    execution_rows = execution_module.parse_registry(scope_context=scope_context)
    execution_status_by_id = {str(row["id"]): str(row["status"]) for row in execution_rows}
    planning_rows = planning_module.parse_registry(scope_context=scope_context)
    sibling_subfeature_rows: Optional[List[Dict[str, object]]] = None
    if target_type == "subfeature":
        sibling_subfeature_rows = subfeature_module.load_registry(
            str(target_dir_path.parent.parent)
        )

    execution_ids_by_planned_slice: Dict[str, List[str]] = {}
    for record in traceability_records:
        if not record.execution_slice_ids:
            continue
        if len(record.planned_slice_ids) == 1:
            bucket = execution_ids_by_planned_slice.setdefault(
                record.planned_slice_ids[0], []
            )
            for execution_slice_id in record.execution_slice_ids:
                if execution_slice_id not in bucket:
                    bucket.append(execution_slice_id)
            continue
        if len(record.planned_slice_ids) == len(record.execution_slice_ids):
            for planned_slice_id, execution_slice_id in zip(
                record.planned_slice_ids, record.execution_slice_ids
            ):
                bucket = execution_ids_by_planned_slice.setdefault(planned_slice_id, [])
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
                increment_ids=list(increment_ids_by_planned_slice.get(planned_slice_id, [])),
                depends_on=list(planned_slice["depends_on"]),
                execution_slice_ids=list(execution_slice_ids),
                closed_execution_slice_ids=list(closed_execution_slice_ids),
                state="pending",
            )
        )

    dependency_ready_next: List[str] = []
    for entry in entries:
        if entry.closed_execution_slice_ids:
            entry.state = "completed"
            continue
        if any(slice_id in active_execution_slices for slice_id in entry.execution_slice_ids):
            entry.state = "active"
            continue
        if all(
            dependency_is_satisfied(
                dep,
                completed_planned_slices,
                planning_module,
                planning_rows,
                scope_context,
                target_type,
                target_dir_path,
                sibling_subfeature_rows=sibling_subfeature_rows,
                subfeature_module=subfeature_module,
            )
            for dep in entry.depends_on
        ):
            entry.state = "ready"
            dependency_ready_next.append(entry.planned_slice_id)
        else:
            entry.state = "blocked"

    active_increment_ids: List[str] = []
    for entry in entries:
        if entry.state != "active":
            continue
        for increment_id in entry.increment_ids:
            if increment_id not in active_increment_ids:
                active_increment_ids.append(increment_id)

    current_increment: Optional[str] = None
    if active_increment_ids:
        current_increment = active_increment_ids[0]
    else:
        for increment_id in increment_order:
            if any(
                increment_id in entry.increment_ids and entry.state != "completed"
                for entry in entries
            ):
                current_increment = increment_id
                break

    ready_next: List[str] = []
    for entry in entries:
        if entry.state != "ready":
            continue
        if current_increment is None or current_increment in entry.increment_ids:
            ready_next.append(entry.planned_slice_id)
            continue
        entry.state = "deferred"

    completed_increments: List[str] = []
    for increment_id in increment_order:
        increment_entries = [
            entry for entry in entries if increment_id in entry.increment_ids
        ]
        if increment_entries and all(entry.state == "completed" for entry in increment_entries):
            completed_increments.append(increment_id)

    return BacklogResolution(
        target_type=target_type,
        target_id=str(feature["feature"]),
        target_path=str(feature["path"]),
        planning_status=str(metadata["status"]),
        increment_order=increment_order,
        current_increment=current_increment,
        completed_increments=completed_increments,
        ready_next=ready_next,
        active_execution_slices=active_execution_slices,
        entries=entries,
    )


def bootstrap_next_slice(
    selector: str, explicit_scope: Optional[str] = None
) -> BootstrapResult:
    backlog = resolve_backlog(selector, explicit_scope=explicit_scope)
    if backlog.active_execution_slices:
        raise RuntimeError(
            "Cannot bootstrap the next planned slice while another mapped execution "
            "slice is still active: "
            + ", ".join(backlog.active_execution_slices)
        )

    if not backlog.ready_next:
        completed = all(entry.state == "completed" for entry in backlog.entries)
        return BootstrapResult(
            backlog=backlog,
            bootstrapped_slice_id=None,
            bootstrapped_slice_path=None,
            slice_status=None,
            checkpoint_slice_id=None,
            dirty_worktree_paths=[],
            next_owner=None,
            completed=completed,
            action="complete" if completed else "blocked",
        )

    planning_module = load_module(GUIDE_PLANNING_SCRIPT, "manage_planning")
    execution_module = load_module(GUIDE_EXECUTION_SCRIPT, "manage_execution")
    _, target_dir, _, scope_context, _ = resolve_target(
        planning_module, selector, explicit_scope
    )
    checkpoint_required = require_commit_checkpoint(backlog, str(scope_context.repo_root))
    if checkpoint_required is not None:
        return checkpoint_required

    next_planned_slice_id = backlog.ready_next[0]
    entry = next(
        item for item in backlog.entries if item.planned_slice_id == next_planned_slice_id
    )
    _, created = execution_module.create_slice(
        next_planned_slice_id,
        entry.title,
        scope_context=scope_context,
    )
    execution_rows = execution_module.parse_registry(scope_context=scope_context)
    slice_row = execution_module.resolve_slice(execution_rows, next_planned_slice_id)
    if slice_row is None:
        raise RuntimeError(
            f"Bootstrapped slice could not be resolved: {next_planned_slice_id}"
        )
    if not created and str(slice_row["status"]) != "closed":
        raise RuntimeError(
            f"Execution slice '{next_planned_slice_id}' already exists with status "
            f"'{slice_row['status']}'."
        )

    record_execution_slice_id(
        Path(target_dir) / "slice-traceability.md",
        next_planned_slice_id,
        next_planned_slice_id,
    )
    refreshed_backlog = resolve_backlog(selector, explicit_scope=explicit_scope)
    return BootstrapResult(
        backlog=refreshed_backlog,
        bootstrapped_slice_id=next_planned_slice_id,
        bootstrapped_slice_path=str(slice_row["path"]),
        slice_status=str(slice_row["status"]),
        checkpoint_slice_id=None,
        dirty_worktree_paths=[],
        next_owner="guide-execution",
        completed=False,
        action="bootstrap_next_slice",
    )


def resume_execution(
    selector: str, explicit_scope: Optional[str] = None
) -> BootstrapResult:
    backlog = resolve_backlog(selector, explicit_scope=explicit_scope)
    if len(backlog.active_execution_slices) > 1:
        raise RuntimeError(
            "Cannot resume while multiple mapped execution slices are active: "
            + ", ".join(backlog.active_execution_slices)
        )

    planning_module = load_module(GUIDE_PLANNING_SCRIPT, "manage_planning")
    execution_module = load_module(GUIDE_EXECUTION_SCRIPT, "manage_execution")
    _, _, _, scope_context, _ = resolve_target(
        planning_module, selector, explicit_scope
    )

    if backlog.active_execution_slices:
        active_slice_id = backlog.active_execution_slices[0]
        execution_rows = execution_module.parse_registry(scope_context=scope_context)
        slice_row = execution_module.resolve_slice(execution_rows, active_slice_id)
        if slice_row is None:
            raise RuntimeError(
                f"Mapped active execution slice could not be resolved: {active_slice_id}"
            )
        return BootstrapResult(
            backlog=backlog,
            bootstrapped_slice_id=active_slice_id,
            bootstrapped_slice_path=str(slice_row["path"]),
            slice_status=str(slice_row["status"]),
            checkpoint_slice_id=None,
            dirty_worktree_paths=[],
            next_owner="guide-execution",
            completed=False,
            action="resume_active_slice",
        )

    checkpoint_required = require_commit_checkpoint(backlog, str(scope_context.repo_root))
    if checkpoint_required is not None:
        return checkpoint_required

    if backlog.ready_next:
        return bootstrap_next_slice(selector, explicit_scope=explicit_scope)

    completed = all(entry.state == "completed" for entry in backlog.entries)
    if completed:
        return BootstrapResult(
            backlog=backlog,
            bootstrapped_slice_id=None,
            bootstrapped_slice_path=None,
            slice_status=None,
            checkpoint_slice_id=None,
            dirty_worktree_paths=[],
            next_owner=None,
            completed=True,
            action="complete",
        )

    blocked = [
        entry.planned_slice_id for entry in backlog.entries if entry.state == "blocked"
    ]
    raise RuntimeError(
        "No ready planned slice remains while unfinished slices are blocked: "
        + ", ".join(blocked)
    )


def read_dirty_worktree_paths(repo_root: str) -> List[str]:
    result = subprocess.run(
        ["git", "-C", repo_root, "status", "--short"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError("Unable to inspect git worktree state for commit checkpoint.")
    return [line.rstrip() for line in result.stdout.splitlines() if line.strip()]


def require_commit_checkpoint(
    backlog: BacklogResolution, repo_root: str
) -> Optional[BootstrapResult]:
    completed_entries = [entry for entry in backlog.entries if entry.state == "completed"]
    if not completed_entries:
        return None
    dirty_worktree_paths = read_dirty_worktree_paths(repo_root)
    if not dirty_worktree_paths:
        return None
    return BootstrapResult(
        backlog=backlog,
        bootstrapped_slice_id=None,
        bootstrapped_slice_path=None,
        slice_status=None,
        checkpoint_slice_id=completed_entries[-1].planned_slice_id,
        dirty_worktree_paths=dirty_worktree_paths,
        next_owner="commit",
        completed=False,
        action="commit_checkpoint_required",
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
    parser.add_argument(
        "--bootstrap-next",
        action="store_true",
        help="Bootstrap the next ready execution slice and record its traceability mapping.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume an active mapped slice or bootstrap the next ready slice.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable output.")
    return parser


def render_text(result: BacklogResolution) -> str:
    lines = [
        f"Target: {result.target_type} {result.target_id}",
        f"Planning status: {result.planning_status}",
        f"Path: {result.target_path}",
        f"Increment order: {', '.join(result.increment_order) if result.increment_order else '-'}",
        f"Current increment: {result.current_increment or '-'}",
        f"Completed increments: {', '.join(result.completed_increments) if result.completed_increments else '-'}",
        f"Ready next: {', '.join(result.ready_next) if result.ready_next else '-'}",
        f"Active execution slices: {', '.join(result.active_execution_slices) if result.active_execution_slices else '-'}",
        "",
        "Planned slices:",
    ]
    for entry in result.entries:
        suffix = ""
        if entry.depends_on:
            suffix = f" (depends on: {', '.join(entry.depends_on)})"
        increment_suffix = (
            f" [increments: {', '.join(entry.increment_ids)}]"
            if entry.increment_ids
            else ""
        )
        lines.append(f"- {entry.planned_slice_id}{increment_suffix}: {entry.state}{suffix}")
    return "\n".join(lines)


def render_bootstrap_text(result: BootstrapResult) -> str:
    lines = [render_text(result.backlog)]
    if result.action == "resume_active_slice" and result.bootstrapped_slice_id:
        lines.extend(
            [
                "",
                f"Resume slice: {result.bootstrapped_slice_id}",
                f"Slice path: {result.bootstrapped_slice_path}",
                f"Slice status: {result.slice_status}",
                f"Next owner: {result.next_owner}",
            ]
        )
    elif result.action == "bootstrap_next_slice" and result.bootstrapped_slice_id:
        lines.extend(
            [
                "",
                f"Bootstrapped slice: {result.bootstrapped_slice_id}",
                f"Slice path: {result.bootstrapped_slice_path}",
                f"Slice status: {result.slice_status}",
                f"Next owner: {result.next_owner}",
            ]
        )
    elif result.action == "commit_checkpoint_required":
        lines.extend(
            [
                "",
                f"Commit checkpoint required for: {result.checkpoint_slice_id}",
                f"Next owner: {result.next_owner}",
                "Dirty worktree paths:",
                *[f"- {path}" for path in result.dirty_worktree_paths],
            ]
        )
    elif result.completed:
        lines.extend(["", "All planned slices are already completed."])
    else:
        lines.extend(["", "No ready slice was bootstrapped."])
    return "\n".join(lines)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.bootstrap_next and args.resume:
        print("Choose either --bootstrap-next or --resume, not both.", file=sys.stderr)
        return 2
    try:
        if args.resume:
            result = resume_execution(args.target, explicit_scope=args.scope)
        elif args.bootstrap_next:
            result = bootstrap_next_slice(args.target, explicit_scope=args.scope)
        else:
            result = resolve_backlog(args.target, explicit_scope=args.scope)
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.json:
        payload = result.to_dict() if hasattr(result, "to_dict") else result
        print(json.dumps(payload, indent=2))
    else:
        if isinstance(result, BootstrapResult):
            print(render_bootstrap_text(result))
        else:
            print(render_text(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
