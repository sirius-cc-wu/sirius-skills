from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Sequence

from sirius_skills.paths import package_root


REFERENCE_RELATIVE_PATH = Path("docs/shared/config-surface-governance.md")
TARGET_RELATIVE_PATHS = (
    Path("skills/behavior-preserving-refactoring/references/config-surface-governance.md"),
)


def sync_one(source: Path, target: Path) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.read_text(encoding="utf-8") == source.read_text(
        encoding="utf-8"
    ):
        return "unchanged"

    shutil.copyfile(source, target)
    return "updated"


def main(argv: Sequence[str] | None = None) -> int:
    if argv:
        print("sync-shared-references does not accept arguments.", file=sys.stderr)
        return 2

    repo_root = package_root()
    source = repo_root / REFERENCE_RELATIVE_PATH
    targets = [repo_root / path for path in TARGET_RELATIVE_PATHS]
    if not source.is_file():
        print(f"Missing shared reference: {source}", file=sys.stderr)
        return 1

    try:
        for target in targets:
            status = sync_one(source, target)
            print(f"{status}: {target.relative_to(repo_root)}")
    except OSError as exc:
        print(f"Failed to sync shared references: {exc}", file=sys.stderr)
        return 1

    return 0
