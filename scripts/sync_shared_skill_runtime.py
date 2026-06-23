#!/usr/bin/env python3

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from sirius_skills.commands.sync_shared_runtime import *  # noqa: F403,E402


WORKFLOW_STATE_SOURCE = REPO_ROOT / "lib" / "workflow_state"
WORKFLOW_STATE_TARGETS = [
    REPO_ROOT / path for path in WORKFLOW_STATE_TARGET_RELATIVE_PATHS  # noqa: F405
]
WORKFLOW_RUNTIME_SOURCE = REPO_ROOT / "lib" / "workflow_runtime"
WORKFLOW_RUNTIME_TARGETS = [
    REPO_ROOT / path for path in WORKFLOW_RUNTIME_TARGET_RELATIVE_PATHS  # noqa: F405
]
SOURCE = WORKFLOW_STATE_SOURCE
METRICS_STORE_SOURCE = REPO_ROOT / METRICS_STORE_SOURCE_RELATIVE_PATH  # noqa: F405
METRICS_STORE_TARGET = REPO_ROOT / METRICS_STORE_TARGET_RELATIVE_PATH  # noqa: F405


if __name__ == "__main__":
    raise SystemExit(main())
