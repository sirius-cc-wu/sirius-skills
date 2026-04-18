#!/usr/bin/env python3

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATION_TEST_PATHS = (
    "skills/audit-artifacts/tests/test_audit_artifacts.py",
    "skills/report-artifacts/tests/test_report_artifacts.py",
    "skills/guide-planning/tests/test_manage_planning.py",
    "skills/close-slice/tests/test_close_slice.py",
)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the curated workflow consistency validation suites."
    )
    parser.add_argument(
        "pytest_args",
        nargs=argparse.REMAINDER,
        help="Optional additional pytest arguments. Prefix with -- to separate them.",
    )
    return parser.parse_args(argv)


def build_pytest_command(pytest_args: Optional[Sequence[str]] = None) -> List[str]:
    extra_args = list(pytest_args or [])
    if extra_args and extra_args[0] == "--":
        extra_args = extra_args[1:]
    return [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        *VALIDATION_TEST_PATHS,
        *extra_args,
    ]


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    completed = subprocess.run(
        build_pytest_command(args.pytest_args),
        cwd=REPO_ROOT,
        check=False,
    )
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
