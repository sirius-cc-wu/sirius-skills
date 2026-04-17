#!/usr/bin/env python3

import importlib.util
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set, Tuple


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
PROPOSAL_SCRIPT = REPO_ROOT / "skills" / "propose" / "scripts" / "manage_proposals.py"
PLANNING_SCRIPT = (
    REPO_ROOT / "skills" / "guide-planning" / "scripts" / "manage_planning.py"
)
SUBFEATURE_SCRIPT = (
    REPO_ROOT / "skills" / "add-subfeature" / "scripts" / "manage_subfeatures.py"
)
EXECUTION_SCRIPT = (
    REPO_ROOT / "skills" / "guide-execution" / "scripts" / "manage_execution.py"
)


@dataclass
class RegistryStatus:
    artifact_type: str
    owner_id: Optional[str]
    root_path: str
    readme_path: str
    registry_path: str
    root_exists: bool
    readme_exists: bool
    registry_exists: bool
    error: Optional[str] = None


@dataclass
class InventoryContext:
    propose: object
    planning: object
    subfeatures: object
    execution: object
    proposal_root: Path
    proposal_readme: Path
    proposal_registry: Path
    planning_root: Path
    planning_readme: Path
    planning_registry: Path
    slice_root: Path
    slice_readme: Path
    slice_registry: Path


@dataclass
class Inventory:
    context: InventoryContext
    registry_statuses: List[RegistryStatus]
    proposal_rows: List[Dict[str, object]]
    planning_rows: List[Dict[str, object]]
    slice_rows: List[Dict[str, object]]
    proposal_dirs: List[Path]
    feature_dirs: List[Path]
    subfeature_dirs_by_feature: Dict[str, List[Path]]
    slice_dirs: List[Path]
    subfeature_registry_rows: Dict[str, List[Dict[str, object]]]


TRACEABILITY_HEADERS: Set[str] = {
    "story id",
    "increments",
    "planned slice ids",
    "execution slice ids",
    "notes",
}


@dataclass
class TraceabilityRecord:
    owner_type: str
    owner_id: str
    owner_path: str
    story_id: str
    story_size: Optional[str]
    increments: str
    planned_slice_ids: List[str]
    execution_slice_ids: List[str]
    notes: str


def load_module(script_path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def normalize_registry_path(value: str) -> str:
    normalized = value.strip()
    if normalized.startswith("./"):
        normalized = normalized[2:]
    normalized = normalized.rstrip("/")
    return normalized + "/"


def normalize_dir_relpath(path: Path) -> str:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(Path.cwd().resolve())
        return normalize_registry_path(str(relative))
    except ValueError:
        return normalize_registry_path(str(resolved))


def _load_registry_rows(
    registry_path: Path,
    readme_path: Path,
    key: str,
    normalizer: Callable[[Dict[str, object]], Dict[str, object]],
    markdown_parser: Optional[Callable[[str], List[Dict[str, object]]]] = None,
) -> Tuple[List[Dict[str, object]], Optional[str]]:
    if registry_path.exists():
        try:
            payload = json.loads(registry_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return [], f"{registry_path.name} is not valid JSON."
        if isinstance(payload, list):
            raw_rows = payload
        elif isinstance(payload, dict):
            raw_rows = payload.get(key, [])
        else:
            return [], f"{registry_path.name} must be a JSON object or list."
        if raw_rows is None:
            raw_rows = []
        if not isinstance(raw_rows, list):
            return [], f"Registry field '{key}' must be a list."
        try:
            return [normalizer(row) for row in raw_rows], None
        except (RuntimeError, ValueError) as exc:
            return [], str(exc)
    if markdown_parser is not None and readme_path.exists():
        try:
            return markdown_parser(str(readme_path)), None
        except (RuntimeError, ValueError) as exc:
            return [], str(exc)
    return [], None


def _discover_child_dirs(root: Path) -> List[Path]:
    if not root.exists():
        return []
    return sorted(
        [path for path in root.iterdir() if path.is_dir() and not path.name.startswith(".")]
    )


def _discover_subfeature_dirs(feature_dir: Path) -> List[Path]:
    return _discover_child_dirs(feature_dir / "subfeatures")


def planning_row_artifact_type(row: Dict[str, object]) -> str:
    path = str(row.get("path", ""))
    return "subfeature" if "/subfeatures/" in path else "feature"


def iter_subfeature_dirs(inventory: Inventory) -> List[Path]:
    result: List[Path] = []
    for paths in inventory.subfeature_dirs_by_feature.values():
        result.extend(paths)
    return sorted(result)


def _normalize_table_header(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("-", " ").strip().lower())


def _split_table_row(line: str) -> List[str]:
    stripped = line.strip().strip("|")
    return [cell.strip() for cell in stripped.split("|")]


def _split_cell_values(value: str) -> List[str]:
    raw = value.replace("<br/>", "\n").replace("<br />", "\n").replace("<br>", "\n")
    items = [part.strip() for part in re.split(r"[\n,;]+", raw)]
    return [item for item in items if item]


def parse_traceability_records(
    path: Path, owner_type: str, owner_id: str, owner_path: str
) -> List[TraceabilityRecord]:
    if not path.exists():
        return []

    lines = path.read_text(encoding="utf-8").splitlines()
    records: List[TraceabilityRecord] = []
    index = 0
    while index < len(lines) - 1:
        header_line = lines[index].strip()
        divider_line = lines[index + 1].strip()
        if "|" not in header_line or "|" not in divider_line:
            index += 1
            continue

        headers = _split_table_row(header_line)
        normalized_headers = [_normalize_table_header(header) for header in headers]
        if not TRACEABILITY_HEADERS.issubset(set(normalized_headers)):
            index += 1
            continue

        divider_cells = _split_table_row(divider_line)
        if not divider_cells or not all(cell.startswith("---") for cell in divider_cells):
            index += 1
            continue

        header_map = {name: position for position, name in enumerate(normalized_headers)}
        index += 2
        while index < len(lines):
            row_line = lines[index].strip()
            if not row_line.startswith("|"):
                break
            cells = _split_table_row(row_line)
            if len(cells) < len(headers):
                cells.extend([""] * (len(headers) - len(cells)))
            records.append(
                TraceabilityRecord(
                    owner_type=owner_type,
                    owner_id=owner_id,
                    owner_path=owner_path,
                    story_id=cells[header_map["story id"]],
                    story_size=(
                        cells[header_map["story size"]].strip()
                        if "story size" in header_map
                        else None
                    )
                    or None,
                    increments=cells[header_map["increments"]],
                    planned_slice_ids=_split_cell_values(
                        cells[header_map["planned slice ids"]]
                    ),
                    execution_slice_ids=_split_cell_values(
                        cells[header_map["execution slice ids"]]
                    ),
                    notes=cells[header_map["notes"]],
                )
            )
            index += 1
        continue
    return records


def iter_traceability_records(inventory: Inventory) -> List[TraceabilityRecord]:
    records: List[TraceabilityRecord] = []
    for feature_dir in inventory.feature_dirs:
        feature_path = normalize_dir_relpath(feature_dir)
        records.extend(
            parse_traceability_records(
                feature_dir / "slice-traceability.md",
                "feature",
                feature_dir.name,
                feature_path,
            )
        )
    for subfeature_dir in iter_subfeature_dirs(inventory):
        subfeature_path = normalize_dir_relpath(subfeature_dir)
        records.extend(
            parse_traceability_records(
                subfeature_dir / "slice-traceability.md",
                "subfeature",
                subfeature_dir.name,
                subfeature_path,
            )
        )
    return records


def resolve_context() -> InventoryContext:
    propose = load_module(PROPOSAL_SCRIPT, "manage_proposals")
    planning = load_module(PLANNING_SCRIPT, "manage_planning")
    subfeatures = load_module(SUBFEATURE_SCRIPT, "manage_subfeatures")
    execution = load_module(EXECUTION_SCRIPT, "manage_execution")

    proposal_scope = propose.SCOPE_RUNTIME.resolve_scope_context()
    proposal_config = propose.load_config(scope_context=proposal_scope)
    proposal_root = Path(
        propose.SCOPE_RUNTIME.resolve_scope_path(
            proposal_scope.scope_root, proposal_config["proposal_dir"]
        )
    )

    planning_scope = planning.SCOPE_RUNTIME.resolve_scope_context()
    planning_dir, planning_readme, planning_registry = planning.get_registry_paths(
        required_config=False, scope_context=planning_scope
    )

    execution_scope = execution.resolve_execution_scope_context()
    slice_dir, slice_readme, slice_registry = execution.get_registry_paths(
        required_config=False, scope_context=execution_scope
    )

    return InventoryContext(
        propose=propose,
        planning=planning,
        subfeatures=subfeatures,
        execution=execution,
        proposal_root=proposal_root,
        proposal_readme=proposal_root / "README.md",
        proposal_registry=proposal_root / "registry.json",
        planning_root=Path(planning_dir),
        planning_readme=Path(planning_readme),
        planning_registry=Path(planning_registry),
        slice_root=Path(slice_dir),
        slice_readme=Path(slice_readme),
        slice_registry=Path(slice_registry),
    )


def load_inventory() -> Inventory:
    context = resolve_context()

    proposal_rows, proposal_error = _load_registry_rows(
        context.proposal_registry,
        context.proposal_readme,
        "proposals",
        context.propose.normalize_registry_row,
    )
    planning_rows, planning_error = _load_registry_rows(
        context.planning_registry,
        context.planning_readme,
        "features",
        context.planning.normalize_registry_row,
        markdown_parser=context.planning.parse_registry_markdown,
    )
    slice_rows, slice_error = _load_registry_rows(
        context.slice_registry,
        context.slice_readme,
        "slices",
        context.execution.normalize_registry_row,
        markdown_parser=context.execution.parse_registry_markdown,
    )

    proposal_dirs = _discover_child_dirs(context.proposal_root)
    feature_dirs = _discover_child_dirs(context.planning_root)
    subfeature_dirs_by_feature = {
        feature_dir.name: _discover_subfeature_dirs(feature_dir) for feature_dir in feature_dirs
    }
    slice_dirs = _discover_child_dirs(context.slice_root)

    registry_statuses: List[RegistryStatus] = [
        RegistryStatus(
            artifact_type="proposal",
            owner_id=None,
            root_path=normalize_dir_relpath(context.proposal_root),
            readme_path=normalize_dir_relpath(context.proposal_readme),
            registry_path=normalize_dir_relpath(context.proposal_registry),
            root_exists=context.proposal_root.exists(),
            readme_exists=context.proposal_readme.exists(),
            registry_exists=context.proposal_registry.exists(),
            error=proposal_error,
        ),
        RegistryStatus(
            artifact_type="feature",
            owner_id=None,
            root_path=normalize_dir_relpath(context.planning_root),
            readme_path=normalize_dir_relpath(context.planning_readme),
            registry_path=normalize_dir_relpath(context.planning_registry),
            root_exists=context.planning_root.exists(),
            readme_exists=context.planning_readme.exists(),
            registry_exists=context.planning_registry.exists(),
            error=planning_error,
        ),
        RegistryStatus(
            artifact_type="slice",
            owner_id=None,
            root_path=normalize_dir_relpath(context.slice_root),
            readme_path=normalize_dir_relpath(context.slice_readme),
            registry_path=normalize_dir_relpath(context.slice_registry),
            root_exists=context.slice_root.exists(),
            readme_exists=context.slice_readme.exists(),
            registry_exists=context.slice_registry.exists(),
            error=slice_error,
        ),
    ]

    subfeature_registry_rows: Dict[str, List[Dict[str, object]]] = {}
    for feature_dir in feature_dirs:
        feature_slug = feature_dir.name
        subfeatures_dir, readme_path, registry_path = context.subfeatures.subfeature_registry_paths(
            str(feature_dir)
        )
        rows, error = _load_registry_rows(
            Path(registry_path),
            Path(readme_path),
            "subfeatures",
            context.subfeatures.normalize_registry_row,
        )
        subfeature_registry_rows[feature_slug] = rows
        registry_statuses.append(
            RegistryStatus(
                artifact_type="subfeature",
                owner_id=feature_slug,
                root_path=normalize_dir_relpath(Path(subfeatures_dir)),
                readme_path=normalize_dir_relpath(Path(readme_path)),
                registry_path=normalize_dir_relpath(Path(registry_path)),
                root_exists=Path(subfeatures_dir).exists(),
                readme_exists=Path(readme_path).exists(),
                registry_exists=Path(registry_path).exists(),
                error=error,
            )
        )

    return Inventory(
        context=context,
        registry_statuses=registry_statuses,
        proposal_rows=proposal_rows,
        planning_rows=planning_rows,
        slice_rows=slice_rows,
        proposal_dirs=proposal_dirs,
        feature_dirs=feature_dirs,
        subfeature_dirs_by_feature=subfeature_dirs_by_feature,
        slice_dirs=slice_dirs,
        subfeature_registry_rows=subfeature_registry_rows,
    )
