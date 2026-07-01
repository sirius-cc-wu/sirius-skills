from __future__ import annotations

import argparse
import inspect
import sys
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Sequence

from sirius_skills.paths import package_root


CLI_NAME = "sirius"


@dataclass(frozen=True)
class CommandSpec:
    name: str
    description: str
    repo_root: Path
    module_name: str | None = None


PACKAGE_COMMANDS = {
    "analyze-impact": (
        "sirius_skills.commands.analyze_impact",
        "sirius_skills.commands.analyze_impact",
    ),
    "archive-artifacts": (
        "sirius_skills.commands.archive_artifacts",
        "sirius_skills.commands.archive_artifacts",
    ),
    "audit-artifacts": (
        "sirius_skills.commands.audit_artifacts",
        "sirius_skills.commands.audit_artifacts",
    ),
    "autoplan": (
        "sirius_skills.commands.autoplan",
        "sirius_skills.commands.autoplan",
    ),
    "bootstrap": (
        "sirius_skills.commands.bootstrap",
        "sirius_skills.commands.bootstrap",
    ),
    "bootstrap-slice": (
        "sirius_skills.commands.bootstrap_slice",
        "sirius_skills.commands.bootstrap_slice",
    ),
    "close-slice": (
        "sirius_skills.commands.close_slice",
        "sirius_skills.commands.close_slice",
    ),
    "learn": (
        "sirius_skills.commands.learn",
        "sirius_skills.commands.learn",
    ),
    "manage-execution": (
        "sirius_skills.commands.manage_execution",
        "sirius_skills.commands.manage_execution",
    ),
    "manage-planning": (
        "sirius_skills.commands.manage_planning",
        "sirius_skills.commands.manage_planning",
    ),
    "manage-proposals": (
        "sirius_skills.commands.manage_proposals",
        "sirius_skills.commands.manage_proposals",
    ),
    "manage-subfeatures": (
        "sirius_skills.commands.manage_subfeatures",
        "sirius_skills.commands.manage_subfeatures",
    ),
    "measure-artifacts": (
        "sirius_skills.commands.measure_artifacts",
        "sirius_skills.commands.measure_artifacts",
    ),
    "migrate-subfeatures": (
        "sirius_skills.commands.migrate_subfeatures",
        "sirius_skills.commands.migrate_subfeatures",
    ),
    "migrate-slices": (
        "sirius_skills.commands.migrate_slices",
        "sirius_skills.commands.migrate_slices",
    ),
    "record-review": (
        "sirius_skills.commands.record_review",
        "sirius_skills.commands.record_review",
    ),
    "repair-artifacts": (
        "sirius_skills.commands.repair_artifacts",
        "sirius_skills.commands.repair_artifacts",
    ),
    "report-artifacts": (
        "sirius_skills.commands.report_artifacts",
        "sirius_skills.commands.report_artifacts",
    ),
    "research": (
        "sirius_skills.commands.research",
        "sirius_skills.commands.research",
    ),
    "scaffold-breakdown": (
        "sirius_skills.commands.scaffold_breakdown",
        "sirius_skills.commands.scaffold_breakdown",
    ),
    "scaffold-design": (
        "sirius_skills.commands.scaffold_design",
        "sirius_skills.commands.scaffold_design",
    ),
    "ship": (
        "sirius_skills.commands.ship",
        "sirius_skills.commands.ship",
    ),
    "ship-slice": (
        "sirius_skills.commands.ship_slice",
        "sirius_skills.commands.ship_slice",
    ),
    "ship-worktree": (
        "sirius_skills.commands.ship_worktree",
        "sirius_skills.commands.ship_worktree",
    ),
    "sync-shared-references": (
        "sirius_skills.commands.sync_shared_references",
        "sirius_skills.commands.sync_shared_references",
    ),
    "trace-artifacts": (
        "sirius_skills.commands.trace_artifacts",
        "sirius_skills.commands.trace_artifacts",
    ),
    "validate-workflow-state": (
        "sirius_skills.commands.validate_workflow_state",
        "sirius_skills.commands.validate_workflow_state",
    ),
}


def discover_commands() -> dict[str, CommandSpec]:
    specs: dict[str, CommandSpec] = {}
    root = package_root()

    for command_name, (module_name, description) in PACKAGE_COMMANDS.items():
        specs[command_name] = CommandSpec(
            name=command_name,
            description=description,
            repo_root=root,
            module_name=module_name,
        )

    return dict(sorted(specs.items()))


def build_parser(commands: dict[str, CommandSpec]) -> argparse.ArgumentParser:
    command_list = "\n".join(
        f"  {name:<30} {spec.description}" for name, spec in commands.items()
    )
    parser = argparse.ArgumentParser(
        prog=CLI_NAME,
        description="Run sirius workflow helper commands.",
        epilog=f"Available commands:\n{command_list}" if command_list else None,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("command", nargs="?", help="Command to run.")
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Arguments passed through to the selected command.",
    )
    return parser


def load_command_module(spec: CommandSpec):
    if spec.module_name is not None:
        return import_module(spec.module_name)
    raise RuntimeError(f"Command '{spec.name}' has no implementation.")


def call_main(module, script_args: Sequence[str]) -> int:
    main_func = getattr(module, "main", None)
    if main_func is None:
        raise RuntimeError("Selected script does not define main().")

    signature = inspect.signature(main_func)
    if len(signature.parameters) == 0:
        result = main_func()
    else:
        result = main_func(script_args)

    if result is None:
        return 0
    if isinstance(result, int):
        return result
    raise RuntimeError(f"main() returned unsupported value: {result!r}")


def run_command(spec: CommandSpec, script_args: Sequence[str]) -> int:
    old_argv = sys.argv
    sys.argv = [spec.name, *script_args]
    try:
        module = load_command_module(spec)
        return call_main(module, script_args)
    except SystemExit as exc:
        if exc.code is None:
            return 0
        if isinstance(exc.code, int):
            return exc.code
        print(exc.code, file=sys.stderr)
        return 1
    finally:
        sys.argv = old_argv


def main(argv: Sequence[str] | None = None) -> int:
    raw_args = list(sys.argv[1:] if argv is None else argv)
    commands = discover_commands()
    parser = build_parser(commands)

    if not raw_args:
        parser.print_help()
        return 0
    if raw_args[0] in {"-h", "--help"}:
        parser.parse_args(raw_args)
        return 0

    command, script_args = raw_args[0], raw_args[1:]
    spec = commands.get(command)
    if spec is None:
        parser.error(
            f"unknown command '{command}'. Run '{CLI_NAME} --help' to list commands."
        )

    return run_command(spec, script_args)


if __name__ == "__main__":
    raise SystemExit(main())
