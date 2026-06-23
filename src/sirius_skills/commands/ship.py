from typing import Sequence

from sirius_skills.legacy import call_legacy_main


def main(argv: Sequence[str] | None = None) -> int:
    return call_legacy_main(
        cache_key="ship",
        script_parts=("skills", "ship", "scripts"),
        script_name="ship.py",
        argv0="ship",
        argv=argv,
    )
