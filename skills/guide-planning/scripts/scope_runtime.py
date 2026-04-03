from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union


PLANNING_CONFIG_RELATIVE_PATH = Path(".skills") / "planning.json"


@dataclass(frozen=True)
class ScopeContext:
    start_dir: Path
    scope_root: Path
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


def resolve_scope_context(start_path: Optional[Union[str, Path]] = None) -> ScopeContext:
    start_dir = _normalize_start_path(start_path)
    scope_root = find_nearest_planning_config_root(start_dir)
    if scope_root is None:
        scope_root = find_repo_root(start_dir) or start_dir

    return ScopeContext(
        start_dir=start_dir,
        scope_root=scope_root,
        planning_config_path=scope_root / PLANNING_CONFIG_RELATIVE_PATH,
    )


def resolve_scope_path(scope_root: Union[str, Path], value: str) -> str:
    path = Path(value).expanduser()
    if path.is_absolute():
        return str(path)
    return str((Path(scope_root) / path).resolve())
