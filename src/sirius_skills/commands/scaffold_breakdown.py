from __future__ import annotations

from typing import Sequence

from sirius_skills.legacy import call_legacy_main, load_legacy_module


def _implementation_module():
    return load_legacy_module(
        "scaffold_breakdown",
        ("skills", "breakdown", "scripts"),
        "scaffold_breakdown.py",
    )


def validate_feature_slug(*args, **kwargs):
    return _implementation_module().validate_feature_slug(*args, **kwargs)


def resolve_base_dir(*args, **kwargs):
    return _implementation_module().resolve_base_dir(*args, **kwargs)


def format_code_list(*args, **kwargs):
    return _implementation_module().format_code_list(*args, **kwargs)


def render_slice_planning(*args, **kwargs):
    return _implementation_module().render_slice_planning(*args, **kwargs)


def render_slice_traceability(*args, **kwargs):
    return _implementation_module().render_slice_traceability(*args, **kwargs)


def main(argv: Sequence[str] | None = None) -> int:
    return call_legacy_main(
        cache_key="scaffold_breakdown",
        script_parts=("skills", "breakdown", "scripts"),
        script_name="scaffold_breakdown.py",
        argv0="scaffold-breakdown",
        argv=argv,
    )
