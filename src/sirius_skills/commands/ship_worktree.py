#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Sequence


COMMAND_DIR = Path(__file__).resolve().parent

SHIP_SCRIPT = COMMAND_DIR / "ship.py"
GUIDE_EXECUTION_SCRIPT = COMMAND_DIR / "manage_execution.py"


from sirius_skills.lib.workflow_runtime import (  # noqa: E402
    WorktreeSessionRecord,
    read_worktree_session,
    worktree_session_record_path,
    write_worktree_session,
)


@dataclass
class ShipWorktreeConfig:
    worktree_root: Path
    branch_prefix: str = "wt"
    draft_pr: bool = True


@dataclass
class PullRequestInfo:
    number: Optional[int] = None
    url: Optional[str] = None
    state: Optional[str] = None
    title: Optional[str] = None
    is_draft: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ShipWorktreeResult:
    target_type: str
    target_id: str
    target_path: str
    base_branch: str
    worktree_branch: str
    worktree_path: str
    record_path: str
    worktree_created: bool
    action: str
    next_owner: str
    ship_result: Optional[Dict[str, Any]] = None
    pull_request: Optional[PullRequestInfo] = None
    blocked_reason: Optional[str] = None
    dirty_worktree_paths: list[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "target_type": self.target_type,
            "target_id": self.target_id,
            "target_path": self.target_path,
            "base_branch": self.base_branch,
            "worktree_branch": self.worktree_branch,
            "worktree_path": self.worktree_path,
            "record_path": self.record_path,
            "worktree_created": self.worktree_created,
            "action": self.action,
            "next_owner": self.next_owner,
            "ship_result": dict(self.ship_result) if self.ship_result is not None else None,
            "pull_request": (
                self.pull_request.to_dict() if self.pull_request is not None else None
            ),
            "blocked_reason": self.blocked_reason,
            "dirty_worktree_paths": list(self.dirty_worktree_paths),
        }
        return payload


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create or resume a dedicated git worktree for one feature or subfeature "
            "and optionally run ship or open a pull request from that worktree."
        )
    )
    parser.add_argument("target", help="Feature slug, subfeature slug, or planning packet path.")
    parser.add_argument(
        "--scope",
        default=None,
        help="Optional explicit scope path forwarded to ship.",
    )
    parser.add_argument("--json", action="store_true", help="Render machine-readable output.")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Run ship --resume in the dedicated worktree after ensuring it exists.",
    )
    parser.add_argument(
        "--finalize",
        action="store_true",
        help="Run ship --finalize in the dedicated worktree after ensuring it exists.",
    )
    parser.add_argument(
        "--create-pr",
        action="store_true",
        help="Push the worktree branch and create or reuse a pull request to the base branch.",
    )
    parser.add_argument(
        "--pr-title",
        default=None,
        help="Optional pull request title override.",
    )
    parser.add_argument(
        "--pr-body-file",
        default=None,
        help="Optional file containing the pull request body.",
    )
    parser.set_defaults(draft_pr=None)
    parser.add_argument(
        "--draft-pr",
        dest="draft_pr",
        action="store_true",
        help="Create the PR as a draft.",
    )
    parser.add_argument(
        "--no-draft-pr",
        dest="draft_pr",
        action="store_false",
        help="Create the PR as ready for review.",
    )
    return parser.parse_args(argv)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_module(script_path: Path, name: str):
    if script_path.name == "manage_execution.py":
        from sirius_skills.commands import manage_execution
        return manage_execution
    raise RuntimeError(f"Unknown script path: {script_path}")


def run_command(command: Sequence[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )


def _command_error(result: subprocess.CompletedProcess[str]) -> str:
    message = (result.stderr or result.stdout or "Command failed.").strip()
    return message or "Command failed."


def run_json_command(command: Sequence[str], *, cwd: Path) -> Dict[str, Any]:
    result = run_command(command, cwd=cwd)
    if result.returncode != 0:
        raise RuntimeError(_command_error(result))
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Command did not return valid JSON output.") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("Expected JSON object output from delegated command.")
    return payload


def git_repo_root(start_dir: Optional[Path] = None) -> Path:
    result = run_command(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=(start_dir or Path.cwd()),
    )
    if result.returncode != 0:
        raise RuntimeError("Current directory is not inside a git repository.")
    return Path(result.stdout.strip()).resolve()


def current_branch(cwd: Path) -> str:
    result = run_command(["git", "branch", "--show-current"], cwd=cwd)
    branch = result.stdout.strip()
    if result.returncode != 0 or not branch or branch == "HEAD":
        raise RuntimeError("A checked-out branch is required to start a ship-worktree session.")
    return branch


def git_status_paths(cwd: Path) -> list[str]:
    result = run_command(["git", "status", "--short", "--untracked-files=all"], cwd=cwd)
    if result.returncode != 0:
        raise RuntimeError("Unable to inspect git status for the target worktree.")
    return [line.rstrip() for line in result.stdout.splitlines() if line.strip()]


def git_branch_exists(repo_root: Path, branch: str) -> bool:
    result = run_command(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
        cwd=repo_root,
    )
    return result.returncode == 0


def sanitize_segment(value: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in value.strip())
    collapsed = "-".join(part for part in cleaned.split("-") if part)
    return collapsed or "target"


def sanitize_branch_prefix(value: str) -> str:
    parts = [sanitize_segment(part) for part in value.split("/") if part.strip()]
    return "/".join(parts)


def load_ship_worktree_config(
    repo_root: Path,
    *,
    explicit_scope: Optional[str],
) -> tuple[ShipWorktreeConfig, Dict[str, str]]:
    execution_module = load_module(GUIDE_EXECUTION_SCRIPT, "ship_worktree_manage_execution")
    scope_context = execution_module.SCOPE_RUNTIME.resolve_scope_context(
        start_path=repo_root,
        explicit_scope=explicit_scope,
    )
    raw_execution = execution_module.load_raw_config(required=False, scope_context=scope_context)
    conventions = execution_module.load_conventions_config(
        required=False, scope_context=scope_context
    )

    accelerators = raw_execution.get("accelerators", {})
    if accelerators is None:
        accelerators = {}
    if not isinstance(accelerators, dict):
        raise RuntimeError("Execution config field 'accelerators' must be a JSON object.")

    raw_config = accelerators.get("ship_worktree", {})
    if raw_config is None:
        raw_config = {}
    if not isinstance(raw_config, dict):
        raise RuntimeError(
            "Execution config field 'accelerators.ship_worktree' must be a JSON object."
        )

    raw_root = raw_config.get("worktree_root")
    if raw_root is None:
        worktree_root = repo_root.parent / f".{repo_root.name}-worktrees"
    else:
        if not isinstance(raw_root, str) or not raw_root.strip():
            raise RuntimeError(
                "Execution config field 'accelerators.ship_worktree.worktree_root' "
                "must be a non-empty string."
            )
        worktree_root = Path(raw_root).expanduser()
        if not worktree_root.is_absolute():
            worktree_root = (repo_root / worktree_root).resolve()

    raw_prefix = raw_config.get("branch_prefix", "wt")
    if not isinstance(raw_prefix, str) or not raw_prefix.strip():
        raise RuntimeError(
            "Execution config field 'accelerators.ship_worktree.branch_prefix' "
            "must be a non-empty string."
        )
    raw_draft = raw_config.get("draft_pr", True)
    if not isinstance(raw_draft, bool):
        raise RuntimeError(
            "Execution config field 'accelerators.ship_worktree.draft_pr' must be a boolean."
        )

    return (
        ShipWorktreeConfig(
            worktree_root=worktree_root,
            branch_prefix=sanitize_branch_prefix(raw_prefix),
            draft_pr=raw_draft,
        ),
        conventions,
    )


def resolve_target(repo_root: Path, selector: str, *, explicit_scope: Optional[str]) -> Dict[str, Any]:
    command = [sys.executable, "-m", "sirius_skills.cli", "ship", selector, "--json"]
    if explicit_scope:
        command.extend(["--scope", explicit_scope])
    return run_json_command(command, cwd=repo_root)


def target_segments(target_type: str, target_path: str) -> list[str]:
    path = Path(target_path).resolve()
    if target_type == "feature":
        return [sanitize_segment(path.name)]

    parts = list(path.parts)
    if "subfeatures" in parts:
        index = len(parts) - 1 - parts[::-1].index("subfeatures")
        if index >= 1 and index + 1 < len(parts):
            return [sanitize_segment(parts[index - 1]), sanitize_segment(parts[index + 1])]

    return [sanitize_segment(path.parent.name), sanitize_segment(path.name)]


def list_worktrees(repo_root: Path) -> list[dict[str, str]]:
    result = run_command(["git", "worktree", "list", "--porcelain"], cwd=repo_root)
    if result.returncode != 0:
        raise RuntimeError("Unable to inspect git worktree list.")

    entries: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for raw_line in result.stdout.splitlines():
        line = raw_line.strip()
        if not line:
            if current:
                entries.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        current[key] = value.strip()
    if current:
        entries.append(current)
    return entries


def find_worktree_path_for_branch(repo_root: Path, branch: str) -> Optional[Path]:
    expected_ref = f"refs/heads/{branch}"
    for entry in list_worktrees(repo_root):
        raw_branch = entry.get("branch")
        raw_worktree = entry.get("worktree")
        if not raw_branch or not raw_worktree:
            continue
        if raw_branch == expected_ref or raw_branch == branch:
            return Path(raw_worktree).resolve()
    return None


def load_or_create_session(
    repo_root: Path,
    *,
    selector: str,
    target_payload: Dict[str, Any],
    config: ShipWorktreeConfig,
) -> tuple[WorktreeSessionRecord, Path]:
    target_type = str(target_payload["target_type"])
    target_id = str(target_payload["target_id"])
    target_path = str(target_payload["target_path"])
    record_path = worktree_session_record_path(
        repo_root,
        target_type=target_type,
        target_path=target_path,
    )
    now = utc_now()
    if record_path.exists():
        record = read_worktree_session(record_path)
        record.selector = selector
        record.target_id = target_id
        record.target_path = target_path
        record.updated_at = now
        return record, record_path

    base_branch = current_branch(repo_root)
    segments = target_segments(target_type, target_path)
    branch_suffix = "/".join(segments)
    worktree_branch = (
        f"{config.branch_prefix}/{branch_suffix}" if config.branch_prefix else branch_suffix
    )
    worktree_path = config.worktree_root / target_type / Path(*segments)

    record = WorktreeSessionRecord(
        target_key=record_path.stem,
        selector=selector,
        target_type=target_type,
        target_id=target_id,
        target_path=target_path,
        base_branch=base_branch,
        worktree_branch=worktree_branch,
        worktree_path=str(worktree_path),
        created_at=now,
        updated_at=now,
    )
    return record, record_path


def ensure_worktree(repo_root: Path, record: WorktreeSessionRecord) -> bool:
    existing_path = find_worktree_path_for_branch(repo_root, record.worktree_branch)
    if existing_path is not None:
        record.worktree_path = str(existing_path)
        record.updated_at = utc_now()
        return False

    target_path = Path(record.worktree_path).resolve()
    if target_path.exists():
        branch = current_branch(target_path)
        if branch != record.worktree_branch:
            raise RuntimeError(
                f"Worktree path already exists at '{target_path}' but is checked out on "
                f"'{branch}', not '{record.worktree_branch}'."
            )
        record.worktree_path = str(target_path)
        record.updated_at = utc_now()
        return False

    target_path.parent.mkdir(parents=True, exist_ok=True)
    if git_branch_exists(repo_root, record.worktree_branch):
        command = ["git", "worktree", "add", str(target_path), record.worktree_branch]
    else:
        command = [
            "git",
            "worktree",
            "add",
            "-b",
            record.worktree_branch,
            str(target_path),
            record.base_branch,
        ]
    result = run_command(command, cwd=repo_root)
    if result.returncode != 0:
        raise RuntimeError(_command_error(result))
    record.worktree_path = str(target_path)
    record.updated_at = utc_now()
    return True


def run_ship_operation(
    record: WorktreeSessionRecord,
    selector: str,
    *,
    explicit_scope: Optional[str],
    operation: str,
) -> Dict[str, Any]:
    command = [
        sys.executable,
        "-m",
        "sirius_skills.cli",
        "ship",
        selector,
        f"--{operation}",
        "--json",
    ]
    if explicit_scope:
        command.extend(["--scope", explicit_scope])
    return run_json_command(command, cwd=Path(record.worktree_path))


def infer_id_from_branch_name(branch: str, conventions: Dict[str, str]) -> Optional[str]:
    pattern = conventions.get("branch_extract_pattern")
    if not pattern:
        return None
    try:
        match = re.search(pattern, branch)
    except re.error as exc:
        raise RuntimeError(
            "Conventions config field 'branch_extract_pattern' is not a valid regex."
        ) from exc
    if not match:
        return None
    named_id = match.groupdict().get("id")
    if named_id:
        return named_id
    if match.lastindex:
        return match.group(1)
    return match.group(0)


def format_pr_title(
    record: WorktreeSessionRecord,
    conventions: Dict[str, str],
    *,
    override: Optional[str],
) -> str:
    if override is not None:
        title = override.strip()
        if not title:
            raise RuntimeError("PR title override cannot be empty.")
        return title

    summary = f"Implement {record.target_id}"
    issue_id = infer_id_from_branch_name(record.base_branch, conventions) or infer_id_from_branch_name(
        record.worktree_branch, conventions
    )
    template = conventions.get("pr_title_format")
    if template:
        requires_id = "{ID}" in template or "{id}" in template
        if not requires_id or issue_id:
            return template.format_map(
                {
                    "ID": issue_id or "",
                    "id": issue_id or "",
                    "scope": record.target_type,
                    "summary": summary,
                }
            )
    return f"{record.target_type}: {summary}"


def load_pr_body(record: WorktreeSessionRecord, body_file: Optional[str]) -> str:
    if body_file is not None:
        body_path = Path(body_file).expanduser()
        if not body_path.is_absolute():
            body_path = (Path.cwd() / body_path).resolve()
        return body_path.read_text(encoding="utf-8")

    return (
        "## Description\n\n"
        f"Implement `{record.target_type}` `{record.target_id}` in the dedicated "
        f"`{record.worktree_branch}` worktree branch.\n\n"
        "## Worktree Context\n\n"
        f"- Base branch: `{record.base_branch}`\n"
        f"- Worktree branch: `{record.worktree_branch}`\n"
        f"- Target path: `{record.target_path}`\n"
    )


def branch_ahead_count(worktree_path: Path, base_branch: str) -> int:
    result = run_command(["git", "rev-list", "--count", f"{base_branch}..HEAD"], cwd=worktree_path)
    if result.returncode != 0:
        raise RuntimeError(_command_error(result))
    return int(result.stdout.strip() or "0")


def list_open_pull_requests(
    worktree_path: Path,
    *,
    base_branch: str,
    head_branch: str,
) -> list[PullRequestInfo]:
    result = run_command(
        [
            "gh",
            "pr",
            "list",
            "--state",
            "open",
            "--base",
            base_branch,
            "--head",
            head_branch,
            "--json",
            "number,url,state,title,isDraft",
        ],
        cwd=worktree_path,
    )
    if result.returncode != 0:
        raise RuntimeError(_command_error(result))
    payload = json.loads(result.stdout or "[]")
    if not isinstance(payload, list):
        raise RuntimeError("Unexpected gh pr list output.")
    prs: list[PullRequestInfo] = []
    for entry in payload:
        if not isinstance(entry, dict):
            continue
        prs.append(
            PullRequestInfo(
                number=int(entry["number"]) if entry.get("number") is not None else None,
                url=str(entry["url"]) if entry.get("url") is not None else None,
                state=str(entry["state"]) if entry.get("state") is not None else None,
                title=str(entry["title"]) if entry.get("title") is not None else None,
                is_draft=(
                    bool(entry["isDraft"]) if entry.get("isDraft") is not None else None
                ),
            )
        )
    return prs


def create_or_reuse_pull_request(
    record: WorktreeSessionRecord,
    *,
    selector: str,
    explicit_scope: Optional[str],
    conventions: Dict[str, str],
    draft_pr: bool,
    pr_title: Optional[str],
    pr_body_file: Optional[str],
) -> tuple[Optional[PullRequestInfo], Optional[str], str, list[str], bool]:
    worktree_path = Path(record.worktree_path)
    dirty_paths = git_status_paths(worktree_path)
    if dirty_paths:
        return None, "commit_checkpoint", "commit", dirty_paths, False

    target_payload = resolve_target(worktree_path, selector, explicit_scope=explicit_scope)
    entries = target_payload.get("entries")
    if not isinstance(entries, list):
        raise RuntimeError("ship JSON output did not contain backlog entries.")
    active_slices = target_payload.get("active_execution_slices")
    if not isinstance(active_slices, list):
        raise RuntimeError("ship JSON output did not contain active_execution_slices.")
    if str(target_payload.get("planning_status")) != "implemented" or active_slices or any(
        not isinstance(entry, dict) or str(entry.get("state")) != "completed" for entry in entries
    ):
        readiness = target_payload.get("readiness")
        next_owner = "ship"
        if isinstance(readiness, dict):
            raw_owner = readiness.get("next_owner")
            if isinstance(raw_owner, str) and raw_owner.strip():
                next_owner = raw_owner
        return None, "target_not_ready", next_owner, [], False

    if branch_ahead_count(worktree_path, record.base_branch) <= 0:
        return None, "no_commits_to_review", "ship", [], False

    push_result = run_command(
        ["git", "push", "-u", "origin", record.worktree_branch],
        cwd=worktree_path,
    )
    if push_result.returncode != 0:
        raise RuntimeError(_command_error(push_result))

    existing = list_open_pull_requests(
        worktree_path,
        base_branch=record.base_branch,
        head_branch=record.worktree_branch,
    )
    if existing:
        return existing[0], None, "none", [], True

    title = format_pr_title(record, conventions, override=pr_title)
    body = load_pr_body(record, pr_body_file)
    command = [
        "gh",
        "pr",
        "create",
        "--base",
        record.base_branch,
        "--head",
        record.worktree_branch,
        "--title",
        title,
        "--body",
        body,
    ]
    if draft_pr:
        command.insert(3, "--draft")
    result = run_command(command, cwd=worktree_path)
    if result.returncode != 0:
        raise RuntimeError(_command_error(result))

    prs = list_open_pull_requests(
        worktree_path,
        base_branch=record.base_branch,
        head_branch=record.worktree_branch,
    )
    if prs:
        return prs[0], None, "none", [], False

    url = (result.stdout or "").strip() or None
    return (
        PullRequestInfo(url=url, title=title, state="OPEN", is_draft=draft_pr),
        None,
        "none",
        [],
        False,
    )


def render_result(result: ShipWorktreeResult, *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
        return

    lines = [
        f"Target: {result.target_type} {result.target_id}",
        f"Base branch: {result.base_branch}",
        f"Worktree branch: {result.worktree_branch}",
        f"Worktree path: {result.worktree_path}",
        f"Action: {result.action}",
        f"Next owner: {result.next_owner}",
    ]
    if result.pull_request is not None and result.pull_request.url:
        lines.append(f"Pull request: {result.pull_request.url}")
    if result.dirty_worktree_paths:
        lines.append("Dirty worktree paths:")
        lines.extend(f"- {path}" for path in result.dirty_worktree_paths)
    print("\n".join(lines))


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.resume and args.finalize:
        raise SystemExit("Choose at most one of --resume or --finalize.")

    repo_root = git_repo_root()
    config, conventions = load_ship_worktree_config(repo_root, explicit_scope=args.scope)
    target_payload = resolve_target(repo_root, args.target, explicit_scope=args.scope)
    record, record_path = load_or_create_session(
        repo_root,
        selector=args.target,
        target_payload=target_payload,
        config=config,
    )
    worktree_created = ensure_worktree(repo_root, record)

    ship_result: Optional[Dict[str, Any]] = None
    action = "worktree_ready"
    next_owner = "ship"
    blocked_reason: Optional[str] = None
    dirty_paths: list[str] = []

    if args.resume:
        ship_result = run_ship_operation(
            record,
            args.target,
            explicit_scope=args.scope,
            operation="resume",
        )
        action = str(ship_result.get("action") or "ship_resume")
        next_owner = str(ship_result.get("next_owner") or "guide-execution")
        if action == "commit_checkpoint_required":
            dirty_paths = [str(path) for path in ship_result.get("dirty_worktree_paths", [])]
            blocked_reason = "commit_checkpoint"
    elif args.finalize:
        ship_result = run_ship_operation(
            record,
            args.target,
            explicit_scope=args.scope,
            operation="finalize",
        )
        action = str(ship_result.get("action") or "ship_finalize")
        next_owner = str(ship_result.get("next_owner") or "none")
        if action == "commit_checkpoint_required":
            dirty_paths = [str(path) for path in ship_result.get("dirty_worktree_paths", [])]
            blocked_reason = "commit_checkpoint"

    pull_request: Optional[PullRequestInfo] = None
    if args.create_pr:
        draft_pr = config.draft_pr if args.draft_pr is None else bool(args.draft_pr)
        (
            pull_request,
            pr_block_reason,
            pr_next_owner,
            pr_dirty_paths,
            reused_existing_pr,
        ) = create_or_reuse_pull_request(
            record,
            selector=args.target,
            explicit_scope=args.scope,
            conventions=conventions,
            draft_pr=draft_pr,
            pr_title=args.pr_title,
            pr_body_file=args.pr_body_file,
        )
        if pull_request is None:
            action = "pull_request_blocked"
            next_owner = pr_next_owner
            blocked_reason = pr_block_reason
            dirty_paths = pr_dirty_paths
        else:
            action = "pull_request_exists" if reused_existing_pr else "pull_request_created"
            next_owner = "none"
            blocked_reason = None
            dirty_paths = []
            record.pr_number = pull_request.number
            record.pr_url = pull_request.url
            record.pr_state = pull_request.state
            record.pr_title = pull_request.title

    record.updated_at = utc_now()
    write_worktree_session(record_path, record)

    result = ShipWorktreeResult(
        target_type=record.target_type,
        target_id=record.target_id,
        target_path=record.target_path,
        base_branch=record.base_branch,
        worktree_branch=record.worktree_branch,
        worktree_path=record.worktree_path,
        record_path=str(record_path),
        worktree_created=worktree_created,
        action=action,
        next_owner=next_owner,
        ship_result=ship_result,
        pull_request=pull_request,
        blocked_reason=blocked_reason,
        dirty_worktree_paths=dirty_paths,
    )
    render_result(result, as_json=args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
