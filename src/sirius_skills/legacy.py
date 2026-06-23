from __future__ import annotations

import importlib.util
import sys
from functools import lru_cache
from pathlib import Path
from typing import Sequence

from sirius_skills.paths import package_root


@lru_cache(maxsize=None)
def load_legacy_module(cache_key: str, script_parts: tuple[str, ...], script_name: str):
    root = package_root()
    script_dir = root.joinpath(*script_parts)
    script_path = script_dir / script_name
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))

    module_name = f"_sirius_skills_{cache_key}_impl"
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {cache_key} implementation: {script_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def call_legacy_main(
    *,
    cache_key: str,
    script_parts: tuple[str, ...],
    script_name: str,
    argv0: str,
    argv: Sequence[str] | None,
) -> int:
    module = load_legacy_module(cache_key, script_parts, script_name)
    old_argv = sys.argv
    sys.argv = [argv0, *(argv or [])]
    try:
        result = module.main()
    finally:
        sys.argv = old_argv
    return 0 if result is None else result
