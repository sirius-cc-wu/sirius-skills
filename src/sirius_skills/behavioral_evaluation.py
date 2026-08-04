from __future__ import annotations

import fnmatch
import hashlib
import json
import shutil
import subprocess
import tempfile
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence


IGNORED_WORKSPACE_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
}


@dataclass(frozen=True)
class FileChange:
    path: str
    kind: str


@dataclass(frozen=True)
class CheckResult:
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class BehavioralResult:
    skill_name: str
    case_id: str | int
    mechanical_passed: bool
    executor_returncode: int
    changes: tuple[FileChange, ...]
    unauthorized_mutations: list[str]
    missing_required_mutations: list[str]
    checks: tuple[CheckResult, ...]
    workspace: Path
    trace_path: Path
    result_path: Path


def build_codex_command(workspace: Path, *, model: str | None = None) -> list[str]:
    command = [
        "codex",
        "exec",
        "--ephemeral",
        "--json",
        "--sandbox",
        "workspace-write",
        "--ignore-user-config",
        "--cd",
        str(workspace),
    ]
    if model:
        command.extend(["--model", model])
    command.append("-")
    return command


def _resolve_child(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"path escapes its root: {relative}") from exc
    return candidate


def _load_behavioral_case(
    root: Path, skill_name: str, case_id: str | int
) -> dict[str, object]:
    case_path = root / "evals" / "cases" / f"{skill_name}.json"
    try:
        data = json.loads(case_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"no eval case file for {skill_name}") from exc
    for case in data.get("evals", []):
        if isinstance(case, dict) and str(case.get("id")) == str(case_id):
            return case
    raise ValueError(f"no behavioral eval {case_id!r} for {skill_name}")


def _fixture_path(root: Path, case: dict[str, object]) -> Path:
    fixture = case.get("fixture")
    if not isinstance(fixture, str) or not fixture.strip():
        raise ValueError(
            f"behavioral eval {case.get('id')!r} has no disposable fixture"
        )
    path = _resolve_child(root / "evals" / "fixtures", fixture)
    if not path.is_dir():
        raise ValueError(f"behavioral fixture does not exist: {fixture}")
    return path


def _snapshot(workspace: Path) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for path in sorted(workspace.rglob("*")):
        relative_parts = path.relative_to(workspace).parts
        if (
            not path.is_file()
            or any(part in IGNORED_WORKSPACE_PARTS for part in relative_parts)
            or path.suffix == ".pyc"
        ):
            continue
        relative = path.relative_to(workspace).as_posix()
        snapshot[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return snapshot


def _changes(before: dict[str, str], after: dict[str, str]) -> tuple[FileChange, ...]:
    changes: list[FileChange] = []
    for path in sorted(before.keys() | after.keys()):
        if path not in before:
            changes.append(FileChange(path, "created"))
        elif path not in after:
            changes.append(FileChange(path, "deleted"))
        elif before[path] != after[path]:
            changes.append(FileChange(path, "modified"))
    return tuple(changes)


def _string_list(case: dict[str, object], key: str) -> list[str]:
    value = case.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"behavioral eval {case.get('id')!r} has invalid {key}")
    return value


def _check_commands(case: dict[str, object]) -> list[tuple[str, ...]]:
    value = case.get("checks", [])
    if not isinstance(value, list):
        raise ValueError(f"behavioral eval {case.get('id')!r} has invalid checks")
    commands: list[tuple[str, ...]] = []
    for command in value:
        if (
            not isinstance(command, list)
            or not command
            or not all(isinstance(argument, str) and argument for argument in command)
        ):
            raise ValueError(
                f"behavioral eval {case.get('id')!r} has an invalid check command"
            )
        commands.append(tuple(command))
    return commands


def _build_prompt(skill_source: str, case: dict[str, object]) -> str:
    expectations = "\n".join(
        f"- {item}" for item in _string_list(case, "expectations")
    )
    prohibitions = "\n".join(
        f"- {item}" for item in _string_list(case, "prohibitions")
    ) or "- None declared."
    checks = "\n".join(
        f"- {' '.join(command)}" for command in _check_commands(case)
    ) or "- None declared."
    return f"""You are executing a controlled Sirius skill evaluation in a disposable repository.

Follow the supplied skill instructions and complete the task in the current
workspace. Inspect the fixture before editing, make only authorized changes,
run appropriate focused checks, and do not commit or publish anything.

<skill-instructions>
{skill_source}
</skill-instructions>

Task:
{case['prompt']}

Expected outcome:
{case['expected_output']}

Behavioral expectations:
{expectations}

Prohibitions:
{prohibitions}

Declared verification commands:
{checks}
"""


def _run_check(
    command: tuple[str, ...], workspace: Path, timeout_seconds: int
) -> CheckResult:
    try:
        completed = subprocess.run(
            command,
            cwd=workspace,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
        )
        return CheckResult(
            command=command,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
    except subprocess.TimeoutExpired as exc:
        return CheckResult(
            command=command,
            returncode=124,
            stdout=exc.stdout or "",
            stderr=exc.stderr or f"timed out after {timeout_seconds} seconds",
        )


def _git_revision(root: Path) -> str | None:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def _serialize_result(
    *,
    root: Path,
    skill_name: str,
    case: dict[str, object],
    prompt: str,
    command: Sequence[str],
    model: str | None,
    duration_seconds: float,
    executor_returncode: int,
    executor_stderr: str,
    changes: tuple[FileChange, ...],
    unauthorized_mutations: list[str],
    missing_required_mutations: list[str],
    checks: tuple[CheckResult, ...],
    trace_path: Path,
    mechanical_passed: bool,
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "skill_name": skill_name,
        "case_id": case["id"],
        "skill_revision": _git_revision(root),
        "host": "codex" if command[:2] == ["codex", "exec"] else "test-adapter",
        "requested_model": model,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": round(duration_seconds, 3),
        "prompt": prompt,
        "command": list(command),
        "executor_returncode": executor_returncode,
        "executor_stderr": executor_stderr,
        "trace_path": trace_path.name,
        "changes": [asdict(change) for change in changes],
        "unauthorized_mutations": unauthorized_mutations,
        "missing_required_mutations": missing_required_mutations,
        "checks": [
            {
                **asdict(check),
                "command": list(check.command),
            }
            for check in checks
        ],
        "semantic_expectations": {
            "status": "ungraded",
            "expectations": case.get("expectations", []),
            "prohibitions": case.get("prohibitions", []),
        },
        "mechanical_passed": mechanical_passed,
    }


def describe_behavioral_case(
    root: Path,
    skill_name: str,
    case_id: str | int,
    *,
    model: str | None = None,
) -> dict[str, object]:
    case = _load_behavioral_case(root, skill_name, case_id)
    fixture = _fixture_path(root, case)
    return {
        "skill_name": skill_name,
        "case_id": case["id"],
        "fixture": fixture.relative_to(root).as_posix(),
        "allowed_mutations": _string_list(case, "allowed_mutations"),
        "required_mutations": _string_list(case, "required_mutations"),
        "checks": [list(command) for command in _check_commands(case)],
        "model": model,
        "semantic_expectations": "ungraded",
    }


def run_behavioral_case(
    root: Path,
    skill_name: str,
    case_id: str | int,
    *,
    model: str | None = None,
    timeout_seconds: int = 900,
    check_timeout_seconds: int = 120,
    keep_workspace: bool = False,
    executor_command: Sequence[str] | None = None,
    results_directory: Path | None = None,
) -> BehavioralResult:
    case = _load_behavioral_case(root, skill_name, case_id)
    fixture = _fixture_path(root, case)
    skill_path = root / "skills" / skill_name / "SKILL.md"
    if not skill_path.is_file():
        raise ValueError(f"skill instructions do not exist: {skill_name}")
    prompt = _build_prompt(skill_path.read_text(encoding="utf-8"), case)
    allowed = _string_list(case, "allowed_mutations")
    required = _string_list(case, "required_mutations")
    if not allowed:
        raise ValueError(
            f"behavioral eval {case_id!r} must declare allowed_mutations"
        )

    workspace = Path(tempfile.mkdtemp(prefix=f"sirius-eval-{skill_name}-"))
    result_directory = results_directory or root / "evals" / "results"
    result_directory.mkdir(parents=True, exist_ok=True)
    result_base = f"{skill_name}.{case['id']}"
    trace_path = result_directory / f"{result_base}.trace.jsonl"
    result_path = result_directory / f"{result_base}.result.json"

    try:
        shutil.copytree(fixture, workspace, dirs_exist_ok=True)
        subprocess.run(
            ["git", "init", "-q"],
            cwd=workspace,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        before = _snapshot(workspace)
        command = (
            list(executor_command)
            if executor_command is not None
            else build_codex_command(workspace, model=model)
        )
        started = time.monotonic()
        try:
            completed = subprocess.run(
                command,
                cwd=workspace,
                input=prompt,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout_seconds,
            )
            executor_returncode = completed.returncode
            executor_stdout = completed.stdout
            executor_stderr = completed.stderr
        except subprocess.TimeoutExpired as exc:
            executor_returncode = 124
            executor_stdout = exc.stdout or ""
            executor_stderr = exc.stderr or f"timed out after {timeout_seconds} seconds"
        duration_seconds = time.monotonic() - started
        trace_path.write_text(executor_stdout, encoding="utf-8")

        after = _snapshot(workspace)
        changes = _changes(before, after)
        unauthorized = [
            change.path
            for change in changes
            if not any(fnmatch.fnmatchcase(change.path, pattern) for pattern in allowed)
        ]
        missing_required = [
            pattern
            for pattern in required
            if not any(
                fnmatch.fnmatchcase(change.path, pattern) for change in changes
            )
        ]
        checks = tuple(
            _run_check(command_to_run, workspace, check_timeout_seconds)
            for command_to_run in _check_commands(case)
        )
        mechanical_passed = (
            executor_returncode == 0
            and not unauthorized
            and not missing_required
            and all(check.returncode == 0 for check in checks)
        )
        serialized = _serialize_result(
            root=root,
            skill_name=skill_name,
            case=case,
            prompt=prompt,
            command=command,
            model=model,
            duration_seconds=duration_seconds,
            executor_returncode=executor_returncode,
            executor_stderr=executor_stderr,
            changes=changes,
            unauthorized_mutations=unauthorized,
            missing_required_mutations=missing_required,
            checks=checks,
            trace_path=trace_path,
            mechanical_passed=mechanical_passed,
        )
        result_path.write_text(
            json.dumps(serialized, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return BehavioralResult(
            skill_name=skill_name,
            case_id=case["id"],
            mechanical_passed=mechanical_passed,
            executor_returncode=executor_returncode,
            changes=changes,
            unauthorized_mutations=unauthorized,
            missing_required_mutations=missing_required,
            checks=checks,
            workspace=workspace,
            trace_path=trace_path,
            result_path=result_path,
        )
    finally:
        if not keep_workspace:
            shutil.rmtree(workspace, ignore_errors=True)
