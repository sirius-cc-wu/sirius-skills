from typing import Sequence

from sirius_skills.legacy import call_legacy_main


def main(argv: Sequence[str] | None = None) -> int:
    return call_legacy_main(
        cache_key="ship_slice",
        script_parts=("skills", "ship-slice", "scripts"),
        script_name="ship_slice.py",
        argv0="ship-slice",
        argv=argv,
    )
