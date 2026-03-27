#!/usr/bin/env python3

import importlib.util
import sys
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "planning-driver"
    / "scripts"
    / "manage_planning.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("manage_planning_legacy", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise RuntimeError(f"Unable to load legacy planning tooling from {SCRIPT_PATH}")
    spec.loader.exec_module(module)
    return module


LEGACY_MODULE = load_module()


def __getattr__(name):
    return getattr(LEGACY_MODULE, name)


def main() -> int:
    return LEGACY_MODULE.main()


if __name__ == "__main__":
    sys.exit(main())
