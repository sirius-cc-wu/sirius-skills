from typing import Sequence

from sirius_skills.legacy import call_legacy_main, load_legacy_module


def _implementation_module():
    return load_legacy_module(
        "close_slice",
        ("skills", "close-slice", "scripts"),
        "close_slice.py",
    )


def dedupe_preserve_order(*args, **kwargs):
    return _implementation_module().dedupe_preserve_order(*args, **kwargs)


def normalize_list_item(*args, **kwargs):
    return _implementation_module().normalize_list_item(*args, **kwargs)


def build_parser(*args, **kwargs):
    return _implementation_module().build_parser(*args, **kwargs)


def main(argv: Sequence[str] | None = None) -> int:
    return call_legacy_main(
        cache_key="close_slice",
        script_parts=("skills", "close-slice", "scripts"),
        script_name="close_slice.py",
        argv0="close-slice",
        argv=argv,
    )
