from __future__ import annotations

import sys
from pathlib import Path

import pytest


def _is_pytest_temp_path(path: str) -> bool:
    try:
        resolved = Path(path).resolve()
    except (OSError, RuntimeError):
        return False
    return any(part.startswith("pytest-") for part in resolved.parts)


def _purge_temp_workflow_modules() -> None:
    for name, module in list(sys.modules.items()):
        if not (name == "workflow_state" or name.startswith("workflow_state.")):
            continue
        module_file = getattr(module, "__file__", None)
        if isinstance(module_file, str) and _is_pytest_temp_path(module_file):
            del sys.modules[name]


def _purge_temp_import_paths() -> None:
    sys.path[:] = [
        path
        for path in sys.path
        if not (
            _is_pytest_temp_path(path)
            and (
                path.endswith("/lib")
                or path.endswith("/scripts")
                or "/lib/workflow_state" in path
                or "/lib/workflow_runtime" in path
            )
        )
    ]


@pytest.fixture(autouse=True)
def isolate_self_contained_skill_imports():
    _purge_temp_import_paths()
    _purge_temp_workflow_modules()
    yield
    _purge_temp_import_paths()
    _purge_temp_workflow_modules()
