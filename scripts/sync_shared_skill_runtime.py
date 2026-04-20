#!/usr/bin/env python3

from __future__ import annotations

import shutil
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE = REPO_ROOT / "lib" / "workflow_state"
WORKFLOW_STATE_TARGETS = [
    REPO_ROOT / "skills" / "audit-artifacts" / "lib" / "workflow_state",
    REPO_ROOT / "skills" / "trace-artifacts" / "lib" / "workflow_state",
    REPO_ROOT / "skills" / "repair-artifacts" / "lib" / "workflow_state",
    REPO_ROOT / "skills" / "report-artifacts" / "lib" / "workflow_state",
    REPO_ROOT / "skills" / "guide-planning" / "lib" / "workflow_state",
    REPO_ROOT / "skills" / "add-subfeature" / "lib" / "workflow_state",
    REPO_ROOT / "skills" / "guide-execution" / "lib" / "workflow_state",
    REPO_ROOT / "skills" / "close-slice" / "lib" / "workflow_state",
]
METRICS_STORE_SOURCE = (
    REPO_ROOT / "skills" / "measure-artifacts" / "scripts" / "metrics_store.py"
)
METRICS_STORE_TARGET = (
    REPO_ROOT / "skills" / "report-artifacts" / "scripts" / "metrics_store.py"
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


def main() -> int:
    if not SOURCE.is_dir():
        print(f"Missing shared runtime source: {SOURCE}", file=sys.stderr)
        return 1
    if not METRICS_STORE_SOURCE.is_file():
        print(f"Missing shared runtime source: {METRICS_STORE_SOURCE}", file=sys.stderr)
        return 1

    try:
        for target in WORKFLOW_STATE_TARGETS:
            status = sync_one(SOURCE, target)
            print(f"{status}: {target.relative_to(REPO_ROOT)}")
        status = sync_file(METRICS_STORE_SOURCE, METRICS_STORE_TARGET)
        print(f"{status}: {METRICS_STORE_TARGET.relative_to(REPO_ROOT)}")
    except (OSError, RuntimeError) as exc:
        print(f"Failed to sync shared runtime: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
