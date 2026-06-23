from typing import Sequence

from sirius_skills.legacy import call_legacy_main


def main(argv: Sequence[str] | None = None) -> int:
    return call_legacy_main(
        cache_key="manage_planning",
        script_parts=("skills", "guide-planning", "scripts"),
        script_name="manage_planning.py",
        argv0="manage-planning",
        argv=argv,
    )
