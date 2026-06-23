from __future__ import annotations

from typing import Sequence

from sirius_skills.legacy import call_legacy_main, load_legacy_module


def _implementation_module():
    return load_legacy_module(
        "audit_artifacts",
        ("skills", "audit-artifacts", "scripts"),
        "audit_artifacts.py",
    )


def run_audit(*args, **kwargs):
    return _implementation_module().run_audit(*args, **kwargs)


def render_text(*args, **kwargs):
    return _implementation_module().render_text(*args, **kwargs)


def parse_args(*args, **kwargs):
    return _implementation_module().parse_args(*args, **kwargs)


def main(argv: Sequence[str] | None = None) -> int:
    return call_legacy_main(
        cache_key="audit_artifacts",
        script_parts=("skills", "audit-artifacts", "scripts"),
        script_name="audit_artifacts.py",
        argv0="audit-artifacts",
        argv=argv,
    )
