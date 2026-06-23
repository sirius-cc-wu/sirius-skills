from __future__ import annotations

from typing import Sequence

from sirius_skills.legacy import call_legacy_main, load_legacy_module


def _implementation_module():
    return load_legacy_module(
        "migrate_subfeatures",
        ("skills", "migrate-subfeatures", "scripts"),
        "migrate_subfeatures.py",
    )


def normalize_optional_string(*args, **kwargs):
    return _implementation_module().normalize_optional_string(*args, **kwargs)


def normalize_string_list(*args, **kwargs):
    return _implementation_module().normalize_string_list(*args, **kwargs)


def normalize_legacy_status(*args, **kwargs):
    return _implementation_module().normalize_legacy_status(*args, **kwargs)


def map_legacy_status(*args, **kwargs):
    return _implementation_module().map_legacy_status(*args, **kwargs)


def build_parser(*args, **kwargs):
    return _implementation_module().build_parser(*args, **kwargs)


def main(argv: Sequence[str] | None = None) -> int:
    return call_legacy_main(
        cache_key="migrate_subfeatures",
        script_parts=("skills", "migrate-subfeatures", "scripts"),
        script_name="migrate_subfeatures.py",
        argv0="migrate-subfeatures",
        argv=argv,
    )
