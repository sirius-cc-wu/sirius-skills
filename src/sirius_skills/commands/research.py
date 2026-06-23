from __future__ import annotations

from typing import Sequence

from sirius_skills.legacy import call_legacy_main, load_legacy_module


def _implementation_module():
    return load_legacy_module(
        "research",
        ("skills", "research", "scripts"),
        "research.py",
    )


def derive_wiki_dir_name(*args, **kwargs):
    return _implementation_module().derive_wiki_dir_name(*args, **kwargs)


def format_title(*args, **kwargs):
    return _implementation_module().format_title(*args, **kwargs)


def default_wiki_status(*args, **kwargs):
    return _implementation_module().default_wiki_status(*args, **kwargs)


def parse_args(*args, **kwargs):
    return _implementation_module().parse_args(*args, **kwargs)


def main(argv: Sequence[str] | None = None) -> int:
    return call_legacy_main(
        cache_key="research",
        script_parts=("skills", "research", "scripts"),
        script_name="research.py",
        argv0="research",
        argv=argv,
    )
