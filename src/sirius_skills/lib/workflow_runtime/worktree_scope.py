from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Dict, Sequence


def git_dirty_paths(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--short", "--untracked-files=all"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.rstrip() for line in result.stdout.splitlines() if line.strip()]


def dirty_line_to_path(line: str) -> str:
    raw_path = line[3:].strip()
    if " -> " in raw_path:
        raw_path = raw_path.split(" -> ", 1)[1]
    return raw_path.strip('"')


def hash_worktree_path(repo_root: Path, relative_path: str) -> str:
    target = repo_root / relative_path
    if not target.exists():
        return "missing"
    if target.is_dir():
        digest = hashlib.sha256()
        for child in sorted(
            path for path in target.rglob("*") if path.is_file() and not path.is_symlink()
        ):
            digest.update(str(child.relative_to(repo_root)).encode("utf-8"))
            digest.update(b"\0")
            digest.update(child.read_bytes())
            digest.update(b"\0")
        return f"dir:{digest.hexdigest()}"
    return f"file:{hashlib.sha256(target.read_bytes()).hexdigest()}"


def snapshot_dirty_worktree(
    repo_root: Path,
    *,
    ignored_prefixes: Sequence[str] = (),
) -> tuple[list[str], Dict[str, str]]:
    lines: list[str] = []
    snapshot: Dict[str, str] = {}
    ignored = tuple(prefix for prefix in ignored_prefixes if prefix)
    for line in git_dirty_paths(repo_root):
        relative_path = dirty_line_to_path(line)
        if ignored and relative_path.startswith(ignored):
            continue
        lines.append(line)
        snapshot[relative_path] = hash_worktree_path(repo_root, relative_path)
    return lines, snapshot


def detect_scope_spillover(
    before_snapshot: Dict[str, str],
    after_snapshot: Dict[str, str],
    *,
    allowed_paths: Sequence[str],
) -> list[str]:
    allowed = {path for path in allowed_paths if path}
    spillover: list[str] = []
    for path, digest in sorted(after_snapshot.items()):
        if before_snapshot.get(path) == digest:
            continue
        if path not in allowed:
            spillover.append(path)
    return spillover
