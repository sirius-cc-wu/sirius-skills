#!/usr/bin/env python3

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from sirius_skills.commands.sync_shared_references import *  # noqa: F403,E402


SOURCE = REPO_ROOT / REFERENCE_RELATIVE_PATH  # noqa: F405
TARGETS = [REPO_ROOT / path for path in TARGET_RELATIVE_PATHS]  # noqa: F405


if __name__ == "__main__":
    raise SystemExit(main())
