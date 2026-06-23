from typing import Sequence

from sirius_skills.legacy import call_legacy_main, load_legacy_module


def _implementation_module():
    return load_legacy_module(
        "bootstrap_slice",
        ("skills", "slice", "scripts"),
        "bootstrap_slice.py",
    )


def parse_bootstrap_args(*args, **kwargs):
    return _implementation_module().parse_bootstrap_args(*args, **kwargs)


def resolve_slice_id(*args, **kwargs):
    return _implementation_module().resolve_slice_id(*args, **kwargs)


def build_parser(*args, **kwargs):
    return _implementation_module().build_parser(*args, **kwargs)


def main(argv: Sequence[str] | None = None) -> int:
    return call_legacy_main(
        cache_key="bootstrap_slice",
        script_parts=("skills", "slice", "scripts"),
        script_name="bootstrap_slice.py",
        argv0="bootstrap-slice",
        argv=argv,
    )
