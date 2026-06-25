#!/usr/bin/env python3

import importlib.util
import json
import re
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set, Tuple

from sirius_skills.lib.workflow_state.models import (
    Inventory,
    InventoryContext,
    RegistryStatus,
    TraceabilityRecord,
)
from sirius_skills.lib.workflow_state import markdown_repository


def _resolve_runtime_roots() -> Tuple[Path, Path]:
    current = Path(__file__).resolve()
    command_paths = (
        Path("src") / "sirius_skills" / "commands" / "manage_planning.py",
        Path("src") / "sirius_skills" / "commands" / "manage_proposals.py",
        Path("src") / "sirius_skills" / "commands" / "manage_execution.py",
        Path("src") / "sirius_skills" / "commands" / "manage_subfeatures.py",
    )
    for candidate in current.parents:
        if all((candidate / relpath).is_file() for relpath in command_paths):
            return candidate, candidate / "src" / "sirius_skills" / "commands"
    raise RuntimeError(
        "Unable to resolve workflow-state repository root from shared runtime location."
    )


REPO_ROOT, COMMANDS_ROOT = _resolve_runtime_roots()
PROPOSAL_SCRIPT = COMMANDS_ROOT / "manage_proposals.py"
PLANNING_SCRIPT = COMMANDS_ROOT / "manage_planning.py"
SUBFEATURE_SCRIPT = COMMANDS_ROOT / "manage_subfeatures.py"
EXECUTION_SCRIPT = COMMANDS_ROOT / "manage_execution.py"

TRACEABILITY_HEADERS: Set[str] = markdown_repository.TRACEABILITY_HEADERS
ARCHIVE_SUMMARIES_START = markdown_repository.ARCHIVE_SUMMARIES_START
ARCHIVE_SUMMARIES_END = markdown_repository.ARCHIVE_SUMMARIES_END
SLICE_SUMMARY_BLOCK_PATTERN = markdown_repository.SLICE_SUMMARY_BLOCK_PATTERN


# load_module function is no longer used, standard imports are used instead.


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
        except json.JSONDecodeError:
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


def archive_slice_root(inventory: Inventory) -> str:
    return normalize_registry_path(
        inventory.context.execution.default_archive_dir(str(inventory.context.slice_root))
    )


def is_archived_slice_row(inventory: Inventory, row: Dict[str, object]) -> bool:
    archived_at = row.get("archived_at")
    if isinstance(archived_at, str) and archived_at.strip():
        return True
    return normalize_registry_path(str(row.get("path", ""))).startswith(archive_slice_root(inventory))


def iter_all_slice_dirs(inventory: Inventory) -> List[Path]:
    archive_root = Path(archive_slice_root(inventory).rstrip("/"))
    discovered = list(inventory.slice_dirs)
    discovered.extend(_discover_child_dirs(archive_root))
    dirs_by_relpath = {normalize_dir_relpath(path): path for path in discovered}
    return [dirs_by_relpath[relpath] for relpath in sorted(dirs_by_relpath)]


def iter_active_slice_rows(inventory: Inventory) -> List[Dict[str, object]]:
    return [dict(row) for row in inventory.slice_rows if not is_archived_slice_row(inventory, row)]


def load_archived_slice_summary_index(
    inventory: Inventory,
) -> Dict[str, List[Dict[str, str]]]:
    index: Dict[str, List[Dict[str, str]]] = {}
    owner_specs = [
        ("feature", feature_dir.name, normalize_dir_relpath(feature_dir), feature_dir / "system-design.md")
        for feature_dir in inventory.feature_dirs
    ]
    owner_specs.extend(
        (
            "subfeature",
            subfeature_dir.name,
            normalize_dir_relpath(subfeature_dir),
            subfeature_dir / "system-design.md",
        )
        for subfeature_dir in iter_subfeature_dirs(inventory)
    )
    for owner_type, owner_id, owner_path, design_path in owner_specs:
        if not design_path.exists():
            continue
        try:
            design_text = design_path.read_text(encoding="utf-8")
        except OSError:
            continue
        managed_blocks = markdown_repository.load_existing_summary_blocks(design_text)
        for slice_id, _block in managed_blocks.items():
            slice_id = slice_id.strip()
            if not slice_id:
                continue
            index.setdefault(slice_id, []).append(
                {
                    "owner_type": owner_type,
                    "owner_id": owner_id,
                    "owner_path": owner_path,
                    "design_path": normalize_dir_relpath(design_path),
                }
            )
    return index


def is_retained_pruned_slice_row(
    inventory: Inventory,
    row: Dict[str, object],
    summary_index: Optional[Dict[str, List[Dict[str, str]]]] = None,
) -> bool:
    if not is_archived_slice_row(inventory, row):
        return False
    slice_dir = Path(inventory.context.execution.slice_path_for_row(row))
    if slice_dir.is_dir():
        return False
    summaries = summary_index if summary_index is not None else load_archived_slice_summary_index(inventory)
    return str(row.get("id", "")).strip() in summaries


def _normalize_table_header(value: str) -> str:
    return markdown_repository.normalize_table_header(value)


def _split_table_row(line: str) -> List[str]:
    return markdown_repository.split_table_row(line)


def _split_cell_values(value: str) -> List[str]:
    return markdown_repository.split_cell_values(value)


def parse_traceability_records(
    path: Path, owner_type: str, owner_id: str, owner_path: str
) -> List[TraceabilityRecord]:
    return markdown_repository.parse_traceability_records(path, owner_type, owner_id, owner_path)


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
    from sirius_skills.commands import manage_proposals as propose
    from sirius_skills.commands import manage_planning as planning
    from sirius_skills.commands import manage_subfeatures as subfeatures
    from sirius_skills.commands import manage_execution as execution

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
