from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "sync_shared_skill_runtime.py"
SPEC = importlib.util.spec_from_file_location("sync_shared_skill_runtime", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_close_slice_receives_workflow_state_runtime() -> None:
    targets = {
        str(path.relative_to(REPO_ROOT))
        for path in MODULE.WORKFLOW_STATE_TARGETS
    }

    assert "skills/close-slice/lib/workflow_state" in targets
