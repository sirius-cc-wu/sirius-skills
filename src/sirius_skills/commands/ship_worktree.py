from typing import Sequence

from sirius_skills.legacy import call_legacy_main


def main(argv: Sequence[str] | None = None) -> int:
    return call_legacy_main(
        cache_key="ship_worktree",
        script_parts=("skills", "ship-worktree", "scripts"),
        script_name="ship_worktree.py",
        argv0="ship-worktree",
        argv=argv,
    )
