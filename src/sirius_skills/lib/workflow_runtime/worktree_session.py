from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional


def _resolve_git_output_path(repo_root: Path, raw_path: str) -> Path:
    path = Path(raw_path.strip())
    if path.is_absolute():
        return path.resolve()
    return (repo_root / path).resolve()


def resolve_git_common_dir(repo_root: Path) -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--git-common-dir"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return _resolve_git_output_path(repo_root, result.stdout)


def worktree_session_dir(repo_root: Path) -> Path:
    return resolve_git_common_dir(repo_root) / "copilot-runtime" / "ship-worktree"


def _sanitize_key_segment(value: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in value.strip())
    collapsed = "-".join(part for part in cleaned.split("-") if part)
    return collapsed or "target"


def build_worktree_target_key(
    repo_root: Path,
    *,
    target_type: str,
    target_path: str,
) -> str:
    target = Path(target_path).resolve()
    try:
        relative = target.relative_to(repo_root.resolve())
        display = "__".join(_sanitize_key_segment(part) for part in relative.parts if part)
        digest_source = str(relative)
    except ValueError:
        display = _sanitize_key_segment(target.name)
        digest_source = str(target)
    digest = hashlib.sha256(digest_source.encode("utf-8")).hexdigest()[:10]
    return f"{_sanitize_key_segment(target_type)}__{display}__{digest}"


def worktree_session_record_path(
    repo_root: Path,
    *,
    target_type: str,
    target_path: str,
) -> Path:
    return worktree_session_dir(repo_root) / (
        build_worktree_target_key(repo_root, target_type=target_type, target_path=target_path)
        + ".json"
    )


@dataclass
class WorktreeSessionRecord:
    target_key: str
    selector: str
    target_type: str
    target_id: str
    target_path: str
    base_branch: str
    worktree_branch: str
    worktree_path: str
    created_at: str
    updated_at: str
    pr_number: Optional[int] = None
    pr_url: Optional[str] = None
    pr_state: Optional[str] = None
    pr_title: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "WorktreeSessionRecord":
        return cls(
            target_key=str(payload["target_key"]),
            selector=str(payload["selector"]),
            target_type=str(payload["target_type"]),
            target_id=str(payload["target_id"]),
            target_path=str(payload["target_path"]),
            base_branch=str(payload["base_branch"]),
            worktree_branch=str(payload["worktree_branch"]),
            worktree_path=str(payload["worktree_path"]),
            created_at=str(payload["created_at"]),
            updated_at=str(payload["updated_at"]),
            pr_number=(
                int(payload["pr_number"])
                if payload.get("pr_number") is not None
                else None
            ),
            pr_url=str(payload["pr_url"]) if payload.get("pr_url") is not None else None,
            pr_state=(
                str(payload["pr_state"]) if payload.get("pr_state") is not None else None
            ),
            pr_title=(
                str(payload["pr_title"]) if payload.get("pr_title") is not None else None
            ),
        )


def write_worktree_session(path: Path, record: WorktreeSessionRecord) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record.to_dict(), indent=2) + "\n", encoding="utf-8")


def read_worktree_session(path: Path) -> WorktreeSessionRecord:
    return WorktreeSessionRecord.from_dict(json.loads(path.read_text(encoding="utf-8")))
