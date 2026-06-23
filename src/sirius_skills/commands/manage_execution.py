from typing import Sequence

from sirius_skills.legacy import call_legacy_main


def main(argv: Sequence[str] | None = None) -> int:
    return call_legacy_main(
        cache_key="manage_execution",
        script_parts=("skills", "guide-execution", "scripts"),
        script_name="manage_execution.py",
        argv0="manage-execution",
        argv=argv,
    )
