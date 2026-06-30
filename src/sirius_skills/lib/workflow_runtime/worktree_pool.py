"""Reusable worktree pool primitives shared by manual and workflow commands."""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Sequence, TypeVar

import psutil

from sirius_skills.lib.workflow_runtime.locking import locked_file
from sirius_skills.lib.workflow_runtime.worktree_scope import git_dirty_paths

T = TypeVar("T")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _run_git(command: Sequence[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )


def _git_output(command: Sequence[str], *, cwd: Path) -> str:
    result = _run_git(command, cwd=cwd)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "git command failed.").strip())
    return result.stdout.strip()


def _resolve_git_output_path(repo_root: Path, raw_path: str) -> Path:
    path = Path(raw_path.strip())
    if path.is_absolute():
        return path.resolve()
    return (repo_root / path).resolve()


def resolve_git_common_dir(repo_root: Path) -> Path:
    """Resolve the repository's common git directory."""
    result = _run_git(["git", "rev-parse", "--git-common-dir"], cwd=repo_root)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "Unable to resolve git common dir.").strip())
    return _resolve_git_output_path(repo_root, result.stdout)


def git_repo_root(start_dir: Path | None = None) -> Path:
    """Resolve the repository root for the given working directory."""
    cwd = start_dir or Path.cwd()
    result = _run_git(["git", "rev-parse", "--show-toplevel"], cwd=cwd)
    if result.returncode != 0:
        raise RuntimeError("Current directory is not inside a git repository.")
    return Path(result.stdout.strip()).resolve()


def git_has_remote(repo_root: Path, name: str = "origin") -> bool:
    """Return True when the repository has the named remote."""
    result = _run_git(["git", "remote"], cwd=repo_root)
    if result.returncode != 0:
        return False
    return any(line.strip() == name for line in result.stdout.splitlines())


def git_ref_exists(repo_root: Path, ref: str) -> bool:
    """Return True when the git ref exists."""
    result = _run_git(["git", "rev-parse", "--verify", ref], cwd=repo_root)
    return result.returncode == 0


def git_fetch(repo_root: Path) -> None:
    """Fetch origin if the repository is configured with that remote."""
    if not git_has_remote(repo_root, "origin"):
        return
    result = _run_git(["git", "fetch", "origin"], cwd=repo_root)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "git fetch failed.").strip())


def get_default_branch(repo_root: Path) -> str:
    """Resolve the repository's default branch."""
    result = _run_git(["git", "symbolic-ref", "HEAD"], cwd=repo_root)
    if result.returncode == 0:
        ref = result.stdout.strip()
        if ref.startswith("refs/heads/"):
            return ref.removeprefix("refs/heads/")

    result = _run_git(["git", "config", "init.defaultBranch"], cwd=repo_root)
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    raise RuntimeError("Cannot determine the default branch.")


def default_branch_ref(repo_root: Path, branch: str) -> str:
    """Return the best ref to use when resetting a worktree to the default branch."""
    remote_ref = f"refs/remotes/origin/{branch}"
    local_ref = f"refs/heads/{branch}"
    if git_has_remote(repo_root, "origin") and git_ref_exists(repo_root, remote_ref):
        return remote_ref
    if git_ref_exists(repo_root, local_ref):
        return local_ref
    return branch


def git_worktree_paths(repo_root: Path) -> set[Path]:
    """List all worktree paths known to git for the repository."""
    result = _run_git(["git", "worktree", "list", "--porcelain"], cwd=repo_root)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "Unable to list worktrees.").strip())

    paths: set[Path] = set()
    for raw_line in result.stdout.splitlines():
        line = raw_line.strip()
        if line.startswith("worktree "):
            paths.add(Path(line.removeprefix("worktree ")).resolve())
    return paths


@dataclass
class ProcessInfo:
    """One running process discovered inside a pooled worktree."""

    pid: int
    name: str

    def __str__(self) -> str:
        return f"{self.name} ({self.pid})"


def _resolve_path(path: str) -> Path:
    return Path(path).expanduser().resolve()


def _path_is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def find_processes_in_worktree(worktree_path: Path) -> list[ProcessInfo]:
    """Return processes whose cwd lives within the given worktree."""
    if not worktree_path.exists():
        return []

    abs_worktree = _resolve_path(str(worktree_path))
    result: list[ProcessInfo] = []
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        try:
            cwd = proc.cwd()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
        if not cwd:
            continue

        abs_cwd = _resolve_path(cwd)
        if not _path_is_within(abs_cwd, abs_worktree):
            continue

        result.append(
            ProcessInfo(
                pid=int(proc.info["pid"]),
                name=str(proc.info.get("name") or ""),
            )
        )
    return result


def is_worktree_in_use(worktree_path: Path) -> bool:
    """Return True when a pooled worktree has running processes inside it."""
    return len(find_processes_in_worktree(worktree_path)) > 0


def is_worktree_dirty(worktree_path: Path) -> bool:
    """Return True when the worktree has uncommitted or unreadable changes."""
    try:
        return bool(git_dirty_paths(worktree_path))
    except Exception:
        return True


def add_worktree(repo_root: Path, path: Path, branch: str, ref: str) -> None:
    """Create a new linked worktree for the given branch."""
    command = ["git", "worktree", "add", str(path), branch]
    if not git_ref_exists(repo_root, f"refs/heads/{branch}"):
        command = ["git", "worktree", "add", "-b", branch, str(path), ref]
    result = _run_git(command, cwd=repo_root)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "Unable to create worktree.").strip())


def reset_worktree(worktree_path: Path, branch: str, ref: str) -> None:
    """Force a worktree back to the supplied branch and ref."""
    result = _run_git(["git", "checkout", "--force", branch], cwd=worktree_path)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "Unable to checkout worktree.").strip())

    result = _run_git(["git", "reset", "--hard", ref], cwd=worktree_path)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "Unable to reset worktree.").strip())

    result = _run_git(["git", "clean", "-fd"], cwd=worktree_path)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "Unable to clean worktree.").strip())


def sanitize_key_segment(value: str) -> str:
    """Normalize a string into a filesystem-safe key segment."""
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in value.strip())
    collapsed = "-".join(part for part in cleaned.split("-") if part)
    return collapsed or "target"


def sanitize_branch_prefix(value: str) -> str:
    """Normalize a branch prefix while preserving nested branch segments."""
    return "/".join(
        segment for segment in (sanitize_key_segment(part) for part in value.split("/")) if segment
    )


def build_pool_key(value: str) -> str:
    """Build the stable pool key used for persisted state."""
    return sanitize_key_segment(value)


def worktree_pool_root(repo_root: Path) -> Path:
    """Return the sibling directory that stores the reusable worktree pool."""
    for parent in (repo_root, *repo_root.parents):
        if parent.name.endswith(".worktrees"):
            return parent.parent / f"{parent.stem}.worktrees"
    return repo_root.parent / f"{repo_root.name}.worktrees"


def worktree_pool_state_path(repo_root: Path, pool_key: str) -> Path:
    """Return the state file path for one worktree pool."""
    return worktree_pool_root(repo_root) / f"{build_pool_key(pool_key)}.json"


@dataclass
class WorktreePoolEntry:
    """One reusable worktree tracked by the shared pool."""

    name: str
    path: str
    branch: str
    created_at: str
    updated_at: str
    leased: bool = False
    lease_holder: Optional[str] = None
    leased_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "WorktreePoolEntry":
        return cls(
            name=str(payload["name"]),
            path=str(payload["path"]),
            branch=str(payload["branch"]),
            created_at=str(payload["created_at"]),
            updated_at=str(payload["updated_at"]),
            leased=bool(payload.get("leased", False)),
            lease_holder=(
                str(payload["lease_holder"]) if payload.get("lease_holder") is not None else None
            ),
            leased_at=str(payload["leased_at"]) if payload.get("leased_at") is not None else None,
        )


@dataclass
class WorktreePoolState:
    """Persisted pool state for one repository and pool key."""

    pool_key: str
    repo_root: str
    worktree_root: str
    default_branch: str
    entries: list[WorktreePoolEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pool_key": self.pool_key,
            "repo_root": self.repo_root,
            "worktree_root": self.worktree_root,
            "default_branch": self.default_branch,
            "entries": [entry.to_dict() for entry in self.entries],
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "WorktreePoolState":
        entries = payload.get("entries", [])
        if not isinstance(entries, list):
            raise RuntimeError("Worktree pool state entries must be a list.")
        return cls(
            pool_key=str(payload["pool_key"]),
            repo_root=str(payload["repo_root"]),
            worktree_root=str(payload["worktree_root"]),
            default_branch=str(payload["default_branch"]),
            entries=[WorktreePoolEntry.from_dict(entry) for entry in entries],
        )


@dataclass
class WorktreePoolStatus:
    """Human-facing status view for a pooled worktree."""

    name: str
    path: str
    branch: str
    status: str
    lease_holder: Optional[str] = None
    processes: list[ProcessInfo] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "branch": self.branch,
            "status": self.status,
            "lease_holder": self.lease_holder,
            "processes": [asdict(proc) for proc in self.processes],
        }


@dataclass
class WorktreeAcquireResult:
    """Result returned when acquiring a reusable worktree."""

    entry: WorktreePoolEntry
    created: bool
    state_path: Path


def _default_state(repo_root: Path, pool_key: str, worktree_root: Path, default_branch: str) -> WorktreePoolState:
    return WorktreePoolState(
        pool_key=build_pool_key(pool_key),
        repo_root=str(repo_root.resolve()),
        worktree_root=str(worktree_root.resolve()),
        default_branch=default_branch,
    )


def _state_lock_path(state_path: Path) -> Path:
    return state_path


def _with_state_lock(state_path: Path, default_state: WorktreePoolState, callback: Callable[[WorktreePoolState], T]) -> T:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with locked_file(_state_lock_path(state_path)) as handle:
        raw = handle.read().strip()
        if raw:
            state = WorktreePoolState.from_dict(json.loads(raw))
        else:
            state = default_state
        result = callback(state)
        handle.seek(0)
        handle.truncate()
        handle.write(json.dumps(state.to_dict(), indent=2, sort_keys=True) + "\n")
        return result


def _next_entry_name(state: WorktreePoolState) -> str:
    numeric_names = [int(entry.name) for entry in state.entries if entry.name.isdigit()]
    if numeric_names:
        return str(max(numeric_names) + 1)
    return "1"


def _entry_path(worktree_root: Path, pool_key: str, name: str, repo_root: Path) -> Path:
    return worktree_root / build_pool_key(pool_key) / name / repo_root.name


def _branch_name(branch_prefix: str, name: str) -> str:
    prefix = sanitize_branch_prefix(branch_prefix)
    return f"{prefix}/{name}" if prefix else name


def _heal_state(state: WorktreePoolState, repo_root: Path) -> bool:
    active_paths = git_worktree_paths(repo_root)
    before = len(state.entries)
    state.entries = [
        entry
        for entry in state.entries
        if Path(entry.path).resolve() in active_paths and Path(entry.path).exists()
    ]
    return len(state.entries) != before


def acquire_worktree(
    repo_root: Path,
    *,
    worktree_root: Path,
    pool_key: str,
    branch_prefix: str = "wt",
    max_trees: int = 16,
    lease_holder: Optional[str] = None,
) -> WorktreeAcquireResult:
    """Acquire a reusable worktree, creating one if the pool has capacity."""
    git_fetch(repo_root)
    default_branch = get_default_branch(repo_root)
    default_ref = default_branch_ref(repo_root, default_branch)
    state_path = worktree_pool_state_path(repo_root, pool_key)
    default_state = _default_state(repo_root, pool_key, worktree_root, default_branch)

    def _acquire(state: WorktreePoolState) -> WorktreeAcquireResult:
        _heal_state(state, repo_root)

        for index, entry in enumerate(state.entries):
            entry_path = Path(entry.path)
            if entry.leased:
                continue
            if find_processes_in_worktree(entry_path):
                continue
            if is_worktree_dirty(entry_path):
                continue

            reset_worktree(entry_path, entry.branch, default_ref)
            state.entries[index].leased = True
            state.entries[index].lease_holder = lease_holder
            state.entries[index].leased_at = _utc_now()
            state.entries[index].updated_at = _utc_now()
            return WorktreeAcquireResult(entry=state.entries[index], created=False, state_path=state_path)

        if len(state.entries) >= max_trees:
            raise RuntimeError(
                f"All {len(state.entries)} worktrees are already in use or dirty (max_trees = {max_trees})."
            )

        name = _next_entry_name(state)
        branch = _branch_name(branch_prefix, name)
        path = _entry_path(worktree_root, pool_key, name, repo_root)
        path.parent.mkdir(parents=True, exist_ok=True)
        add_worktree(repo_root, path, branch, default_ref)
        entry = WorktreePoolEntry(
            name=name,
            path=str(path),
            branch=branch,
            created_at=_utc_now(),
            updated_at=_utc_now(),
            leased=True,
            lease_holder=lease_holder,
            leased_at=_utc_now(),
        )
        state.entries.append(entry)
        return WorktreeAcquireResult(entry=entry, created=True, state_path=state_path)

    return _with_state_lock(state_path, default_state, _acquire)


def list_worktrees(
    repo_root: Path,
    *,
    worktree_root: Path,
    pool_key: str,
) -> list[WorktreePoolStatus]:
    """List the current status of all pooled worktrees."""
    state_path = worktree_pool_state_path(repo_root, pool_key)
    default_state = _default_state(repo_root, pool_key, worktree_root, get_default_branch(repo_root))
    cwd = Path.cwd().resolve()

    def _list(state: WorktreePoolState) -> list[WorktreePoolStatus]:
        _heal_state(state, repo_root)
        statuses: list[WorktreePoolStatus] = []
        cwd = Path.cwd().resolve()
        for entry in state.entries:
            path = Path(entry.path)
            processes = find_processes_in_worktree(path)
            if entry.leased:
                status = "leased"
            elif processes:
                status = "you're here" if _path_is_within(cwd, path.resolve()) else "in-use"
            elif is_worktree_dirty(path):
                status = "dirty"
            else:
                status = "available"
            statuses.append(
                WorktreePoolStatus(
                    name=entry.name,
                    path=entry.path,
                    branch=entry.branch,
                    status=status,
                    lease_holder=entry.lease_holder if entry.leased else None,
                    processes=processes,
                )
            )
        return statuses

    return _with_state_lock(state_path, default_state, _list)


def return_worktree(
    repo_root: Path,
    *,
    worktree_root: Path,
    pool_key: str,
    worktree_path: Path,
    force: bool = False,
) -> WorktreePoolEntry:
    """Return a worktree to the pool after resetting it to the default branch."""
    default_branch = get_default_branch(repo_root)
    default_ref = default_branch_ref(repo_root, default_branch)
    state_path = worktree_pool_state_path(repo_root, pool_key)
    default_state = _default_state(repo_root, pool_key, worktree_root, default_branch)
    normalized = worktree_path.resolve()

    def _return(state: WorktreePoolState) -> WorktreePoolEntry:
        _heal_state(state, repo_root)
        for index, entry in enumerate(state.entries):
            entry_path = Path(entry.path).resolve()
            if entry_path != normalized:
                continue
            if is_worktree_dirty(entry_path) and not force:
                raise RuntimeError(f"Worktree {normalized} has uncommitted changes; use --force to return it.")
            reset_worktree(entry_path, entry.branch, default_ref)
            state.entries[index].leased = False
            state.entries[index].lease_holder = None
            state.entries[index].leased_at = None
            state.entries[index].updated_at = _utc_now()
            return state.entries[index]
        raise RuntimeError(f"Worktree {normalized} is not managed by this pool.")

    return _with_state_lock(state_path, default_state, _return)
