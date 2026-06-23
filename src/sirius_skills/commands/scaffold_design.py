from typing import Sequence

from sirius_skills.legacy import call_legacy_main, load_legacy_module


def _implementation_module():
    return load_legacy_module(
        "scaffold_design",
        ("skills", "design", "scripts"),
        "scaffold_design.py",
    )


def title_from_slug(*args, **kwargs):
    return _implementation_module().title_from_slug(*args, **kwargs)


def render_story_list(*args, **kwargs):
    return _implementation_module().render_story_list(*args, **kwargs)


def collect_story_ids(*args, **kwargs):
    return _implementation_module().collect_story_ids(*args, **kwargs)


def build_scaffold(*args, **kwargs):
    return _implementation_module().build_scaffold(*args, **kwargs)


def main(argv: Sequence[str] | None = None) -> int:
    return call_legacy_main(
        cache_key="scaffold_design",
        script_parts=("skills", "design", "scripts"),
        script_name="scaffold_design.py",
        argv0="scaffold-design",
        argv=argv,
    )
