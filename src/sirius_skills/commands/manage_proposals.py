from typing import Sequence

from sirius_skills.legacy import call_legacy_main


def main(argv: Sequence[str] | None = None) -> int:
    return call_legacy_main(
        cache_key="manage_proposals",
        script_parts=("skills", "propose", "scripts"),
        script_name="manage_proposals.py",
        argv0="manage-proposals",
        argv=argv,
    )
