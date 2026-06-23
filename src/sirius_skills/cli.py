from __future__ import annotations

import argparse
import ast
import importlib.util
import inspect
import sys
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Iterable, Sequence

from sirius_skills.paths import package_root


@dataclass(frozen=True)
class CommandSpec:
    name: str
    description: str
    repo_root: Path
    script_path: Path | None = None
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
    "sync-shared-runtime": (
        "sirius_skills.commands.sync_shared_runtime",
        "sirius_skills.commands.sync_shared_runtime",
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


def command_name_for_script(script_path: Path) -> str:
    return script_path.stem.replace("_", "-")


def has_main(script_path: Path) -> bool:
    try:
        tree = ast.parse(script_path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return False
    return any(isinstance(node, ast.FunctionDef) and node.name == "main" for node in tree.body)


def iter_script_paths() -> Iterable[Path]:
    root = package_root()
    root_scripts_dir = root / "scripts"
    skills_dir = root / "skills"
    if root_scripts_dir.is_dir():
        yield from sorted(root_scripts_dir.glob("*.py"))
    if skills_dir.is_dir():
        yield from sorted(skills_dir.glob("*/scripts/*.py"))


def discover_commands() -> dict[str, CommandSpec]:
    specs: dict[str, CommandSpec] = {}
    collisions: dict[str, list[Path]] = {}
    root = package_root()

    for command_name, (module_name, description) in PACKAGE_COMMANDS.items():
        specs[command_name] = CommandSpec(
            name=command_name,
            description=description,
            repo_root=root,
            module_name=module_name,
        )

    for script_path in iter_script_paths():
        if not has_main(script_path):
            continue
        command_name = command_name_for_script(script_path)
        if command_name in specs:
            existing_path = specs[command_name].script_path
            if existing_path is not None:
                collisions.setdefault(command_name, [existing_path]).append(script_path)
            continue
        specs[command_name] = CommandSpec(
            name=command_name,
            script_path=script_path,
            description=str(script_path.relative_to(root)),
            repo_root=root,
        )

    for command_name, paths in collisions.items():
        specs.pop(command_name, None)
        for script_path in paths:
            skill_name = script_path.parents[1].name
            prefixed_name = f"{skill_name}-{command_name}"
            specs[prefixed_name] = CommandSpec(
                name=prefixed_name,
                script_path=script_path,
                description=str(script_path.relative_to(root)),
                repo_root=root,
            )

    return dict(sorted(specs.items()))


def build_parser(commands: dict[str, CommandSpec]) -> argparse.ArgumentParser:
    command_list = "\n".join(
        f"  {name:<30} {spec.description}" for name, spec in commands.items()
    )
    parser = argparse.ArgumentParser(
        prog="sirius-skills",
        description="Run sirius-skills workflow helper commands.",
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


def load_script_module(script_path: Path):
    module_name = f"_sirius_skills_command_{script_path.stem}_{abs(hash(script_path))}"
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load script: {script_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_command_module(spec: CommandSpec):
    if spec.module_name is not None:
        return import_module(spec.module_name)
    if spec.script_path is not None:
        return load_script_module(spec.script_path)
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
    repo_lib_dir = spec.repo_root / "lib"
    if str(repo_lib_dir) not in sys.path:
        sys.path.insert(0, str(repo_lib_dir))
    if spec.script_path is not None:
        script_dir = str(spec.script_path.parent)
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)

    old_argv = sys.argv
    argv0 = str(spec.script_path) if spec.script_path is not None else spec.name
    sys.argv = [argv0, *script_args]
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
            f"unknown command '{command}'. Run 'sirius-skills --help' to list commands."
        )

    return run_command(spec, script_args)


if __name__ == "__main__":
    raise SystemExit(main())
