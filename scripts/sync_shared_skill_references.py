#!/usr/bin/env python3

from __future__ import annotations

import shutil
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE = REPO_ROOT / "docs/shared/config-surface-governance.md"
TARGETS = [
    REPO_ROOT / "skills/assess/references/config-surface-governance.md",
    REPO_ROOT / "skills/design/references/config-surface-governance.md",
    REPO_ROOT / "skills/governance-update/references/config-surface-governance.md",
    REPO_ROOT / "skills/review-planning/references/config-surface-governance.md",
    REPO_ROOT / "skills/simplify/references/config-surface-governance.md",
]


def sync_one(source: Path, target: Path) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.read_text(encoding="utf-8") == source.read_text(
        encoding="utf-8"
    ):
        return "unchanged"

    shutil.copyfile(source, target)
    return "updated"


def main() -> int:
    if not SOURCE.is_file():
        print(f"Missing shared reference: {SOURCE}", file=sys.stderr)
        return 1

    try:
        for target in TARGETS:
            status = sync_one(SOURCE, target)
            print(f"{status}: {target.relative_to(REPO_ROOT)}")
    except OSError as exc:
        print(f"Failed to sync shared references: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
