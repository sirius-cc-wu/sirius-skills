from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Sequence

from sirius_skills.paths import package_root


WORKFLOW_STATE_TARGET_RELATIVE_PATHS = (
    Path("skills/audit-artifacts/lib/workflow_state"),
    Path("skills/trace-artifacts/lib/workflow_state"),
    Path("skills/repair-artifacts/lib/workflow_state"),
    Path("skills/report-artifacts/lib/workflow_state"),
    Path("skills/guide-planning/lib/workflow_state"),
    Path("skills/add-subfeature/lib/workflow_state"),
    Path("skills/guide-execution/lib/workflow_state"),
    Path("skills/close-slice/lib/workflow_state"),
    Path("skills/ship/lib/workflow_state"),
)
WORKFLOW_RUNTIME_TARGET_RELATIVE_PATHS = (
    Path("skills/ship/lib/workflow_runtime"),
    Path("skills/learn/lib/workflow_runtime"),
    Path("skills/ship-slice/lib/workflow_runtime"),
    Path("skills/autoplan/lib/workflow_runtime"),
    Path("skills/ship-worktree/lib/workflow_runtime"),
)
METRICS_STORE_SOURCE_RELATIVE_PATH = Path(
    "skills/measure-artifacts/scripts/metrics_store.py"
)
METRICS_STORE_TARGET_RELATIVE_PATH = Path(
    "skills/report-artifacts/scripts/metrics_store.py"
)
IGNORED_DIR_NAMES = {"__pycache__"}
IGNORED_FILE_SUFFIXES = {".pyc", ".pyo"}


def snapshot_tree(path: Path) -> dict[str, bytes] | None:
    if not path.exists():
        return None
    if not path.is_dir():
        raise RuntimeError(f"Expected directory tree at {path}")

    snapshot: dict[str, bytes] = {}
    for file_path in sorted(path.rglob("*")):
        if file_path.is_dir():
            continue
        if any(part in IGNORED_DIR_NAMES for part in file_path.parts):
            continue
        if file_path.suffix in IGNORED_FILE_SUFFIXES:
            continue
        snapshot[str(file_path.relative_to(path))] = file_path.read_bytes()
    return snapshot


def sync_one(source: Path, target: Path) -> str:
    if snapshot_tree(source) == snapshot_tree(target):
        return "unchanged"

    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
    )
    return "updated"


def sync_file(source: Path, target: Path) -> str:
    if target.exists() and target.read_bytes() == source.read_bytes():
        return "unchanged"

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    return "updated"


def main(argv: Sequence[str] | None = None) -> int:
    if argv:
        print("sync-shared-runtime does not accept arguments.", file=sys.stderr)
        return 2

    repo_root = package_root()
    workflow_state_source = repo_root / "lib" / "workflow_state"
    workflow_runtime_source = repo_root / "lib" / "workflow_runtime"
    metrics_store_source = repo_root / METRICS_STORE_SOURCE_RELATIVE_PATH
    metrics_store_target = repo_root / METRICS_STORE_TARGET_RELATIVE_PATH

    if not workflow_state_source.is_dir():
        print(f"Missing shared runtime source: {workflow_state_source}", file=sys.stderr)
        return 1
    if not workflow_runtime_source.is_dir():
        print(f"Missing shared runtime source: {workflow_runtime_source}", file=sys.stderr)
        return 1
    if not metrics_store_source.is_file():
        print(f"Missing shared runtime source: {metrics_store_source}", file=sys.stderr)
        return 1

    try:
        for target_path in WORKFLOW_STATE_TARGET_RELATIVE_PATHS:
            target = repo_root / target_path
            status = sync_one(workflow_state_source, target)
            print(f"{status}: {target.relative_to(repo_root)}")
        for target_path in WORKFLOW_RUNTIME_TARGET_RELATIVE_PATHS:
            target = repo_root / target_path
            status = sync_one(workflow_runtime_source, target)
            print(f"{status}: {target.relative_to(repo_root)}")
        status = sync_file(metrics_store_source, metrics_store_target)
        print(f"{status}: {metrics_store_target.relative_to(repo_root)}")
    except (OSError, RuntimeError) as exc:
        print(f"Failed to sync shared runtime: {exc}", file=sys.stderr)
        return 1

    return 0
