from typing import Sequence

from sirius_skills.legacy import call_legacy_main, load_legacy_module


def _implementation_module():
    return load_legacy_module(
        "bootstrap",
        ("skills", "bootstrap", "scripts"),
        "bootstrap.py",
    )


def derive_wiki_dir(*args, **kwargs):
    return _implementation_module().derive_wiki_dir(*args, **kwargs)


def build_planning_config(*args, **kwargs):
    return _implementation_module().build_planning_config(*args, **kwargs)


def build_execution_config(*args, **kwargs):
    return _implementation_module().build_execution_config(*args, **kwargs)


def build_conventions_config(*args, **kwargs):
    return _implementation_module().build_conventions_config(*args, **kwargs)


def main(argv: Sequence[str] | None = None) -> int:
    return call_legacy_main(
        cache_key="bootstrap",
        script_parts=("skills", "bootstrap", "scripts"),
        script_name="bootstrap.py",
        argv0="bootstrap",
        argv=argv,
    )
