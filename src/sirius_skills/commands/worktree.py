"""Manual reusable worktree commands for sirius-skills."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Sequence

from sirius_skills.lib.workflow_runtime import (
    WorktreeAcquireResult,
    acquire_worktree,
    git_repo_root,
    list_worktrees,
    return_worktree,
    worktree_pool_root,
)


@dataclass
class WorktreeCommandConfig:
    """Typed config for the repo-derived manual worktree pool."""

    worktree_root: Path
    branch_prefix: str = "wt"


def load_worktree_config(repo_root: Path) -> WorktreeCommandConfig:
    """Load the manual worktree config from the repository path alone."""
    return WorktreeCommandConfig(worktree_root=worktree_pool_root(repo_root))


def _json_dump(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _human_path(path: str) -> str:
    return str(Path(path))


def _status_payload(statuses) -> Dict[str, Any]:
    return {
        "pool": [status.to_dict() for status in statuses],
        "count": len(statuses),
    }


def _resolve_target_path(args: argparse.Namespace) -> Path:
    if args.path:
        return Path(args.path).expanduser().resolve()
    raise RuntimeError("A worktree path is required.")


def _render_status_lines(statuses) -> list[str]:
    if not statuses:
        return ["🌳 No worktrees in pool."]
    lines = []
    for status in statuses:
        line = f"{status.name:<4}  {status.status:<11}  {_human_path(status.path)}"
        if status.lease_holder:
            line += f"  (held by {status.lease_holder})"
        line += f"  [{status.branch}]"
        lines.append(line)
        if status.processes:
            proc_indent = " " * (4 + 2 + 11 + 2)
            lines.append(
                f"{proc_indent}{', '.join(str(proc) for proc in status.processes)}"
            )
    return lines


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse the manual worktree subcommand arguments."""
    parser = argparse.ArgumentParser(description="Manage a reusable pool of git worktrees.")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    get_parser = subparsers.add_parser("get", help="Acquire a reusable worktree")
    get_parser.add_argument("--json", action="store_true", help="Render machine-readable output.")
    get_parser.add_argument(
        "--lease-holder",
        default=None,
        help="Optional label recorded as the lease holder.",
    )

    return_parser = subparsers.add_parser("return", help="Return a leased worktree")
    return_parser.add_argument("path", help="Path to the worktree to return.")
    return_parser.add_argument("--force", action="store_true", help="Return even if the worktree is dirty.")
    return_parser.add_argument("--json", action="store_true", help="Render machine-readable output.")

    status_parser = subparsers.add_parser("status", help="Show worktree pool status")
    status_parser.add_argument("--json", action="store_true", help="Render machine-readable output.")

    return parser.parse_args(argv)


def run_get(repo_root: Path, config: WorktreeCommandConfig, args: argparse.Namespace) -> int:
    """Acquire a reusable worktree and print the selected path."""
    result: WorktreeAcquireResult = acquire_worktree(
        repo_root,
        worktree_root=config.worktree_root,
        pool_key="manual",
        branch_prefix=config.branch_prefix,
        lease_holder=args.lease_holder,
    )

    payload = {
        "action": "worktree_created" if result.created else "worktree_reused",
        "worktree_path": result.entry.path,
        "worktree_branch": result.entry.branch,
        "worktree_name": result.entry.name,
        "worktree_root": str(config.worktree_root),
        "lease_holder": result.entry.lease_holder,
        "leased": result.entry.leased,
        "state_path": str(result.state_path),
    }

    if args.json:
        _json_dump(payload)
    else:
        print(result.entry.path)
    return 0


def run_return(repo_root: Path, config: WorktreeCommandConfig, args: argparse.Namespace) -> int:
    """Return a reusable worktree to the pool."""
    path = _resolve_target_path(args)
    entry = return_worktree(
        repo_root,
        worktree_root=config.worktree_root,
        pool_key="manual",
        worktree_path=path,
        force=args.force,
    )
    payload = {
        "action": "worktree_returned",
        "worktree_path": entry.path,
        "worktree_branch": entry.branch,
        "worktree_name": entry.name,
        "leased": entry.leased,
    }
    if args.json:
        _json_dump(payload)
    else:
        print(f"Returned {_human_path(entry.path)}")
    return 0


def run_status(repo_root: Path, config: WorktreeCommandConfig, args: argparse.Namespace) -> int:
    """Render the current manual worktree pool status."""
    statuses = list_worktrees(
        repo_root,
        worktree_root=config.worktree_root,
        pool_key="manual",
    )
    payload = _status_payload(statuses)
    if args.json:
        _json_dump(payload)
    else:
        for line in _render_status_lines(statuses):
            print(line)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run the manual worktree command entrypoint."""
    args = parse_args(argv)
    repo_root = git_repo_root()
    config = load_worktree_config(repo_root)

    if args.subcommand == "get":
        return run_get(repo_root, config, args)
    if args.subcommand == "return":
        return run_return(repo_root, config, args)
    if args.subcommand == "status":
        return run_status(repo_root, config, args)

    raise RuntimeError(f"Unknown subcommand: {args.subcommand}")
