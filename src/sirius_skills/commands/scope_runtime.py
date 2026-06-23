import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union


SKILLS_DIR = Path(".skills")
PLANNING_CONFIG_RELATIVE_PATH = Path(".skills") / "planning.json"
EXECUTION_CONFIG_RELATIVE_PATH = Path(".skills") / "execution.json"
CONVENTIONS_CONFIG_RELATIVE_PATH = Path(".skills") / "conventions.json"
CONFIG_RELATIVE_PATHS = {
    "planning": PLANNING_CONFIG_RELATIVE_PATH,
    "execution": EXECUTION_CONFIG_RELATIVE_PATH,
    "conventions": CONVENTIONS_CONFIG_RELATIVE_PATH,
}


@dataclass(frozen=True)
class ScopeContext:
    start_dir: Path
    repo_root: Path
    scope_root: Path
    scope_chain: tuple[Path, ...]
    planning_config_path: Path


def _normalize_start_path(start_path: Optional[Union[str, Path]] = None) -> Path:
    if start_path is None:
        path = Path.cwd()
    else:
        path = Path(start_path).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path

    resolved = path.resolve()
    if resolved.is_file():
        return resolved.parent
    return resolved


def _iter_ancestors(start_dir: Path):
    current = start_dir
    while True:
        yield current
        if current.parent == current:
            break
        current = current.parent


def find_nearest_planning_config_root(
    start_path: Optional[Union[str, Path]] = None,
) -> Optional[Path]:
    start_dir = _normalize_start_path(start_path)
    for candidate in _iter_ancestors(start_dir):
        if (candidate / PLANNING_CONFIG_RELATIVE_PATH).exists():
            return candidate
    return None


def find_repo_root(start_path: Optional[Union[str, Path]] = None) -> Optional[Path]:
    start_dir = _normalize_start_path(start_path)
    for candidate in _iter_ancestors(start_dir):
        if (candidate / ".git").exists():
            return candidate
    return None


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def build_scope_chain(repo_root: Path, scope_root: Path) -> tuple[Path, ...]:
    repo_root = repo_root.resolve()
    scope_root = scope_root.resolve()

    candidates = []
    current = scope_root
    while True:
        candidates.append(current)
        if current == repo_root or current.parent == current:
            break
        current = current.parent

    chain = []
    for candidate in reversed(candidates):
        if candidate == repo_root or (candidate / PLANNING_CONFIG_RELATIVE_PATH).exists():
            chain.append(candidate)

    if not chain:
        chain.append(repo_root)
    if chain[-1] != scope_root:
        chain.append(scope_root)
    return tuple(dict.fromkeys(chain))


def resolve_scope_context(
    start_path: Optional[Union[str, Path]] = None,
    explicit_scope: Optional[Union[str, Path]] = None,
) -> ScopeContext:
    start_dir = _normalize_start_path(start_path)
    repo_root = find_repo_root(start_dir) or start_dir
    scope_search_start = (
        _normalize_start_path(explicit_scope) if explicit_scope is not None else start_dir
    )

    if explicit_scope is not None and not _is_within(scope_search_start, repo_root):
        raise ValueError(
            f"Scope path '{scope_search_start}' is outside repository root '{repo_root}'."
        )

    scope_root = find_nearest_planning_config_root(scope_search_start)
    if scope_root is None:
        scope_root = repo_root

    return ScopeContext(
        start_dir=start_dir,
        repo_root=repo_root,
        scope_root=scope_root,
        scope_chain=build_scope_chain(repo_root, scope_root),
        planning_config_path=scope_root / PLANNING_CONFIG_RELATIVE_PATH,
    )


def resolve_scope_path(scope_root: Union[str, Path], value: str) -> str:
    path = Path(value).expanduser()
    if path.is_absolute():
        return str(path)
    return str((Path(scope_root) / path).resolve())


def list_nested_scope_roots(scope_root: Union[str, Path]) -> list[Path]:
    root = Path(scope_root).resolve()
    nested_roots: list[Path] = []
    for config_file in root.rglob("planning.json"):
        if config_file.parent.name != ".skills":
            continue
        candidate = config_file.parent.parent.resolve()
        if candidate == root:
            continue
        nested_roots.append(candidate)

    unique_roots = []
    seen = set()
    for candidate in sorted(nested_roots, key=lambda path: (len(path.parts), str(path))):
        if candidate in seen:
            continue
        seen.add(candidate)
        unique_roots.append(candidate)
    return unique_roots


def config_relative_path(config_name: str) -> Path:
    try:
        return CONFIG_RELATIVE_PATHS[config_name]
    except KeyError as exc:
        raise ValueError(f"Unknown config name '{config_name}'.") from exc


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{label} is not valid JSON: {path}") from exc

    if not isinstance(payload, dict):
        raise RuntimeError(f"{label} must be a JSON object: {path}")
    return payload


def load_merged_config(scope_context: ScopeContext, config_name: str) -> dict[str, Any]:
    relative_path = config_relative_path(config_name)
    label = f"{config_name.title()} config"
    merged: dict[str, Any] = {}
    for scope_root in scope_context.scope_chain:
        config_path = scope_root / relative_path
        if not config_path.exists():
            continue
        merged.update(load_json_object(config_path, label))
    return merged
