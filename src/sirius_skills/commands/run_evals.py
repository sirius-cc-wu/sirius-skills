from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from sirius_skills.behavioral_evaluation import (
    describe_behavioral_case,
    run_behavioral_case,
)
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
    parser.add_argument(
        "--behavioral",
        metavar="SKILL",
        help="Run one opt-in behavioral eval instead of deterministic routing.",
    )
    parser.add_argument(
        "--case",
        dest="case_id",
        help="Opaque behavioral case ID; required with --behavioral.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print a behavioral execution plan without running Codex.",
    )
    parser.add_argument("--model", help="Optional Codex model override to record and use.")
    parser.add_argument(
        "--keep-workspace",
        action="store_true",
        help="Keep the disposable behavioral workspace for diagnosis.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=900,
        help="Behavioral executor timeout in seconds (default: 900).",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve() if args.root is not None else package_root()

    if args.behavioral:
        if not args.case_id:
            parser.error("--case is required with --behavioral")
        if args.timeout < 1:
            parser.error("--timeout must be positive")
        try:
            if args.dry_run:
                plan = describe_behavioral_case(
                    root, args.behavioral, args.case_id, model=args.model
                )
                print(json.dumps(plan, indent=2, sort_keys=True))
                return 0
            result = run_behavioral_case(
                root,
                args.behavioral,
                args.case_id,
                model=args.model,
                timeout_seconds=args.timeout,
                keep_workspace=args.keep_workspace,
            )
        except (OSError, ValueError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        print(
            f"Behavioral eval {result.skill_name}/{result.case_id}: "
            f"{'MECHANICAL PASS' if result.mechanical_passed else 'MECHANICAL FAIL'}"
        )
        print(f"Changes: {len(result.changes)}")
        if result.unauthorized_mutations:
            print(
                "Unauthorized mutations: "
                + ", ".join(result.unauthorized_mutations)
            )
        if result.missing_required_mutations:
            print(
                "Missing required mutations: "
                + ", ".join(result.missing_required_mutations)
            )
        failed_assertions = [
            assertion for assertion in result.file_assertions if not assertion.passed
        ]
        if failed_assertions:
            print(
                "Failed file assertions: "
                + ", ".join(assertion.path for assertion in failed_assertions)
            )
        print(f"Trace: {result.trace_path}")
        print(f"Result: {result.result_path}")
        print("Semantic expectations: UNGRADED")
        if args.keep_workspace:
            print(f"Workspace: {result.workspace}")
        return 0 if result.mechanical_passed else 1

    if args.case_id or args.dry_run or args.model or args.keep_workspace:
        parser.error("behavioral options require --behavioral")
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
