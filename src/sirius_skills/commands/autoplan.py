from typing import Sequence

from sirius_skills.legacy import call_legacy_main


def main(argv: Sequence[str] | None = None) -> int:
    return call_legacy_main(
        cache_key="autoplan",
        script_parts=("skills", "autoplan", "scripts"),
        script_name="autoplan.py",
        argv0="autoplan",
        argv=argv,
    )
