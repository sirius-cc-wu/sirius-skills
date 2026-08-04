from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from sirius_skills.behavioral_evaluation import (
    BehavioralResult,
    SemanticCalibrationResult,
    describe_behavioral_case,
    describe_semantic_calibration,
    run_behavioral_repetitions,
    run_semantic_calibration,
)
from sirius_skills.evaluation import evaluate_repository
from sirius_skills.paths import package_root


def _print_behavioral_result(
    result: BehavioralResult, *, index: int, total: int, keep_workspace: bool
) -> None:
    print(
        f"Behavioral eval {result.skill_name}/{result.case_id} "
        f"run {index}/{total}: "
        f"{'MECHANICAL PASS' if result.mechanical_passed else 'MECHANICAL FAIL'}"
    )
    print(f"Changes: {len(result.changes)}")
    if result.unauthorized_mutations:
        print(
            "Unauthorized mutations: " + ", ".join(result.unauthorized_mutations)
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
    failed_trace_assertions = [
        assertion for assertion in result.trace_assertions if not assertion.passed
    ]
    if failed_trace_assertions:
        print(
            "Failed trace assertions: "
            + ", ".join(
                f"{assertion.assertion_type}: {assertion.error}"
                for assertion in failed_trace_assertions
            )
        )
    judgment = result.semantic_judgment
    if judgment.status == "completed":
        print(
            "Semantic judge: "
            f"{'PASS' if judgment.passed else 'FAIL'} (non-gating)"
        )
    elif judgment.status == "error":
        print(f"Semantic judge: ERROR (non-gating): {judgment.error}")
    print(f"Trace: {result.trace_path}")
    print(f"Result: {result.result_path}")
    if keep_workspace:
        print(f"Workspace: {result.workspace}")


def _print_semantic_calibration(result: SemanticCalibrationResult) -> None:
    print(
        f"Semantic judge calibration {result.skill_name}/{result.case_id}: "
        f"{'PASS' if result.passed else 'FAIL'}"
    )
    for control in result.controls:
        status = "MATCH" if control.matched else "MISMATCH"
        print(f"Control {control.control_id!r}: {status}")
        if control.judgment.error:
            print(f"  Judge error: {control.judgment.error}")
    print(f"Summary: {result.summary_path}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run Sirius routing and opt-in behavioral evaluations."
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
        "--judge",
        action="store_true",
        help="Run the case's semantic rubric through a non-gating Codex judge.",
    )
    parser.add_argument(
        "--judge-model",
        help="Optional judge or calibration model; defaults to --model.",
    )
    parser.add_argument(
        "--calibrate-judge",
        action="store_true",
        help="Run declared semantic controls without running the coding agent.",
    )
    parser.add_argument(
        "--keep-workspace",
        action="store_true",
        help="Keep the disposable behavioral workspace for diagnosis.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=900,
        help="Per-executor timeout in seconds (default: 900).",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Behavioral repetitions to run and summarize (default: 1).",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve() if args.root is not None else package_root()

    if args.behavioral:
        if not args.case_id:
            parser.error("--case is required with --behavioral")
        if args.judge and args.calibrate_judge:
            parser.error("--judge and --calibrate-judge cannot be combined")
        if args.judge_model and not (args.judge or args.calibrate_judge):
            parser.error("--judge-model requires --judge or --calibrate-judge")
        if args.calibrate_judge and args.keep_workspace:
            parser.error("--keep-workspace does not apply to --calibrate-judge")
        if args.calibrate_judge and args.repeat != 1:
            parser.error("--repeat does not apply to --calibrate-judge")
        if args.timeout < 1:
            parser.error("--timeout must be positive")
        if args.repeat < 1:
            parser.error("--repeat must be positive")
        try:
            if args.calibrate_judge:
                judge_model = args.judge_model or args.model
                if args.dry_run:
                    plan = describe_semantic_calibration(
                        root,
                        args.behavioral,
                        args.case_id,
                        judge_model=judge_model,
                    )
                    print(json.dumps(plan, indent=2, sort_keys=True))
                    return 0
                calibration = run_semantic_calibration(
                    root,
                    args.behavioral,
                    args.case_id,
                    judge_model=judge_model,
                    timeout_seconds=args.timeout,
                )
                _print_semantic_calibration(calibration)
                return 0 if calibration.passed else 1
            if args.dry_run:
                plan = describe_behavioral_case(
                    root,
                    args.behavioral,
                    args.case_id,
                    model=args.model,
                    semantic_judge=args.judge,
                    judge_model=args.judge_model,
                )
                plan["repeat_count"] = args.repeat
                print(json.dumps(plan, indent=2, sort_keys=True))
                return 0
            batch = run_behavioral_repetitions(
                root,
                args.behavioral,
                args.case_id,
                repeat_count=args.repeat,
                model=args.model,
                semantic_judge=args.judge,
                judge_model=args.judge_model,
                timeout_seconds=args.timeout,
                keep_workspace=args.keep_workspace,
            )
        except (OSError, ValueError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        for index, result in enumerate(batch.runs, start=1):
            _print_behavioral_result(
                result,
                index=index,
                total=len(batch.runs),
                keep_workspace=args.keep_workspace,
            )
        print(f"Summary: {batch.summary_path}")
        print(
            "Stability: "
            f"mechanical={'stable' if batch.mechanically_stable else 'variable'}, "
            f"mutations={'stable' if batch.mutations_stable else 'variable'}, "
            "environment="
            f"{'stable' if batch.execution_environments_stable else 'variable'}"
        )
        if batch.usage is None:
            print(f"Usage: unavailable for all {len(batch.runs)} runs")
        else:
            print(
                f"Usage ({batch.usage_runs}/{len(batch.runs)} runs): "
                f"input={batch.usage.input_tokens}, "
                f"cached={batch.usage.cached_input_tokens}, "
                f"uncached={batch.usage.uncached_input_tokens}, "
                f"output={batch.usage.output_tokens}, "
                f"reasoning={batch.usage.reasoning_output_tokens}"
            )
        if args.judge:
            print("Semantic judge: NON-GATING; see per-run results")
        else:
            print("Semantic expectations: UNGRADED")
        return 0 if batch.mechanical_passes == len(batch.runs) else 1

    if (
        args.case_id
        or args.dry_run
        or args.model
        or args.judge
        or args.judge_model
        or args.calibrate_judge
        or args.keep_workspace
        or args.repeat != 1
    ):
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
