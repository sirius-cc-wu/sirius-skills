from typing import Sequence

from sirius_skills.legacy import call_legacy_main


def main(argv: Sequence[str] | None = None) -> int:
    return call_legacy_main(
        cache_key="manage_subfeatures",
        script_parts=("skills", "add-subfeature", "scripts"),
        script_name="manage_subfeatures.py",
        argv0="manage-subfeatures",
        argv=argv,
    )
