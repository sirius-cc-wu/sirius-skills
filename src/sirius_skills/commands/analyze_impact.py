from __future__ import annotations

from typing import Sequence

from sirius_skills.legacy import call_legacy_main, load_legacy_module


def _implementation_module():
    return load_legacy_module(
        "analyze_impact",
        ("skills", "assess", "scripts"),
        "analyze_impact.py",
    )


def normalize_relpath(*args, **kwargs):
    return _implementation_module().normalize_relpath(*args, **kwargs)


def dedupe(*args, **kwargs):
    return _implementation_module().dedupe(*args, **kwargs)


def format_bullets(*args, **kwargs):
    return _implementation_module().format_bullets(*args, **kwargs)


def parse_args(*args, **kwargs):
    return _implementation_module().parse_args(*args, **kwargs)


def main(argv: Sequence[str] | None = None) -> int:
    return call_legacy_main(
        cache_key="analyze_impact",
        script_parts=("skills", "assess", "scripts"),
        script_name="analyze_impact.py",
        argv0="analyze-impact",
        argv=argv,
    )
