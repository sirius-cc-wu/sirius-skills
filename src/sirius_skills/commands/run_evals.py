from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from sirius_skills.evaluation import evaluate_repository
from sirius_skills.paths import package_root


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run deterministic Sirius skill routing evaluations."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root; defaults to the installed or source package root.",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve() if args.root is not None else package_root()
    report = evaluate_repository(root)

    print(
        f"Evaluated {report.skill_count} skills across "
        f"{report.case_files} routing case files."
    )
    for warning in report.warnings:
        print(f"WARN: {warning}")
    for error in report.errors:
        print(f"ERROR: {error}")
    rate = (
        "n/a"
        if report.rank_one_rate is None
        else f"{report.rank_one_rate:.0%}"
    )
    print(
        f"Routing checks: {report.routing_passed}/{report.routing_checks} passed; "
        f"positive rank-one rate: {rate}."
    )
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
