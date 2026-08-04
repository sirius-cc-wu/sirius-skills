from __future__ import annotations

import fnmatch
import hashlib
import json
import shutil
import subprocess
import tempfile
import time
import uuid
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
class FileAssertionResult:
    path: str
    passed: bool
    missing_fragments: tuple[str, ...] = ()
    unexpected_fragments: tuple[str, ...] = ()
    error: str | None = None


@dataclass(frozen=True)
class TraceAssertionResult:
    assertion_type: str
    passed: bool
    command_contains: tuple[str, ...]
    mutation_patterns: tuple[str, ...]
    error: str | None = None


@dataclass(frozen=True)
class BehavioralResult:
    skill_name: str
    case_id: str | int
    mechanical_passed: bool
    duration_seconds: float
    executor_returncode: int
    changes: tuple[FileChange, ...]
    unauthorized_mutations: list[str]
    missing_required_mutations: list[str]
    checks: tuple[CheckResult, ...]
    file_assertions: tuple[FileAssertionResult, ...]
    trace_assertions: tuple[TraceAssertionResult, ...]
    workspace: Path
    trace_path: Path
    result_path: Path


@dataclass(frozen=True)
class BehavioralBatchResult:
    skill_name: str
    case_id: str | int
    runs: tuple[BehavioralResult, ...]
    mechanical_passes: int
    mechanically_stable: bool
    mutations_stable: bool
    summary_path: Path


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


def _new_result_id(prefix: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return f"{prefix}-{timestamp}-{uuid.uuid4().hex[:8]}"


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


def _file_assertion_specs(case: dict[str, object]) -> list[dict[str, object]]:
    value = case.get("file_assertions", [])
    if not isinstance(value, list):
        raise ValueError(
            f"behavioral eval {case.get('id')!r} has invalid file_assertions"
        )
    specifications: list[dict[str, object]] = []
    for specification in value:
        if not isinstance(specification, dict):
            raise ValueError(
                f"behavioral eval {case.get('id')!r} has an invalid file assertion"
            )
        path = specification.get("path")
        scope = specification.get("scope", "file")
        contains = specification.get("contains", [])
        not_contains = specification.get("not_contains", [])
        if (
            not isinstance(path, str)
            or not path
            or scope not in {"file", "plantuml"}
            or not isinstance(contains, list)
            or not isinstance(not_contains, list)
            or not all(isinstance(item, str) and item for item in contains)
            or not all(isinstance(item, str) and item for item in not_contains)
        ):
            raise ValueError(
                f"behavioral eval {case.get('id')!r} has an invalid file assertion"
            )
        specifications.append(specification)
    return specifications


def _trace_assertion_specs(case: dict[str, object]) -> list[dict[str, object]]:
    value = case.get("trace_assertions", [])
    if not isinstance(value, list):
        raise ValueError(
            f"behavioral eval {case.get('id')!r} has invalid trace_assertions"
        )
    specifications: list[dict[str, object]] = []
    for specification in value:
        if not isinstance(specification, dict):
            raise ValueError(
                f"behavioral eval {case.get('id')!r} has an invalid trace assertion"
            )
        command_contains = specification.get("command_contains")
        mutation_patterns = specification.get("mutation_patterns")
        if (
            specification.get("type") != "red_green"
            or not isinstance(command_contains, list)
            or not command_contains
            or not all(
                isinstance(fragment, str) and fragment for fragment in command_contains
            )
            or not isinstance(mutation_patterns, list)
            or not mutation_patterns
            or not all(
                isinstance(pattern, str) and pattern for pattern in mutation_patterns
            )
        ):
            raise ValueError(
                f"behavioral eval {case.get('id')!r} has an invalid trace assertion"
            )
        specifications.append(specification)
    return specifications


def _trace_events(trace: str) -> tuple[list[dict[str, object]], str | None]:
    events: list[dict[str, object]] = []
    for line_number, line in enumerate(trace.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            return [], f"invalid JSONL trace at line {line_number}: {exc.msg}"
        if not isinstance(event, dict):
            return [], f"invalid JSONL trace object at line {line_number}"
        events.append(event)
    return events, None


def _relative_trace_path(path: str, workspace: Path) -> str | None:
    candidate = Path(path)
    if not candidate.is_absolute():
        return candidate.as_posix().removeprefix("./")
    try:
        return candidate.resolve().relative_to(workspace.resolve()).as_posix()
    except ValueError:
        return None


def _red_green_trace_assertion(
    specification: dict[str, object],
    events: list[dict[str, object]],
    workspace: Path,
) -> TraceAssertionResult:
    command_contains = tuple(
        str(fragment) for fragment in specification["command_contains"]
    )
    mutation_patterns = tuple(
        str(pattern) for pattern in specification["mutation_patterns"]
    )
    command_events: list[tuple[int, int]] = []
    mutation_indices: list[int] = []
    for index, event in enumerate(events):
        if event.get("type") != "item.completed":
            continue
        item = event.get("item")
        if not isinstance(item, dict):
            continue
        if item.get("type") == "command_execution":
            command = item.get("command")
            exit_code = item.get("exit_code")
            if (
                isinstance(command, str)
                and isinstance(exit_code, int)
                and all(fragment in command for fragment in command_contains)
            ):
                command_events.append((index, exit_code))
        if item.get("type") != "file_change":
            continue
        changes = item.get("changes")
        if not isinstance(changes, list):
            continue
        for change in changes:
            if not isinstance(change, dict) or not isinstance(change.get("path"), str):
                continue
            relative = _relative_trace_path(str(change["path"]), workspace)
            if relative is not None and any(
                fnmatch.fnmatchcase(relative, pattern) for pattern in mutation_patterns
            ):
                mutation_indices.append(index)
                break

    error = None
    if not mutation_indices:
        error = "no trace file change matched the mutation patterns"
    elif not any(
        exit_code != 0 and index < mutation_indices[0]
        for index, exit_code in command_events
    ):
        error = "no matching failing command completed before the first mutation"
    elif not any(
        exit_code == 0 and index > mutation_indices[-1]
        for index, exit_code in command_events
    ):
        error = "no matching passing command completed after the last mutation"
    return TraceAssertionResult(
        assertion_type="red_green",
        passed=error is None,
        command_contains=command_contains,
        mutation_patterns=mutation_patterns,
        error=error,
    )


def _evaluate_trace_assertions(
    case: dict[str, object], trace: str, workspace: Path
) -> tuple[TraceAssertionResult, ...]:
    specifications = _trace_assertion_specs(case)
    if not specifications:
        return ()
    events, trace_error = _trace_events(trace)
    if trace_error is not None:
        return tuple(
            TraceAssertionResult(
                assertion_type=str(specification["type"]),
                passed=False,
                command_contains=tuple(
                    str(item) for item in specification["command_contains"]
                ),
                mutation_patterns=tuple(
                    str(item) for item in specification["mutation_patterns"]
                ),
                error=trace_error,
            )
            for specification in specifications
        )
    return tuple(
        _red_green_trace_assertion(specification, events, workspace)
        for specification in specifications
    )


def _plantuml_fenced_content(content: str) -> tuple[str, str | None]:
    blocks: list[str] = []
    current: list[str] = []
    for line in content.splitlines(keepends=True):
        marker = line.strip().casefold()
        if not current:
            if marker == "```plantuml":
                current.append(line)
            continue
        current.append(line)
        if marker == "```":
            blocks.append("".join(current))
            current = []
    if current:
        return "", "unterminated PlantUML fenced block"
    if not blocks:
        return "", "no PlantUML fenced block found"
    return "\n".join(blocks), None


def _evaluate_file_assertions(
    case: dict[str, object], workspace: Path
) -> tuple[FileAssertionResult, ...]:
    results: list[FileAssertionResult] = []
    for specification in _file_assertion_specs(case):
        relative = str(specification["path"])
        path = _resolve_child(workspace, relative)
        contains = tuple(str(item) for item in specification.get("contains", []))
        not_contains = tuple(
            str(item) for item in specification.get("not_contains", [])
        )
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            results.append(
                FileAssertionResult(
                    path=relative,
                    passed=False,
                    missing_fragments=contains,
                    error=str(exc),
                )
            )
            continue
        assertion_content = content
        scope_error = None
        if specification.get("scope", "file") == "plantuml":
            assertion_content, scope_error = _plantuml_fenced_content(content)
        missing = tuple(
            fragment for fragment in contains if fragment not in assertion_content
        )
        unexpected = tuple(
            fragment for fragment in not_contains if fragment in assertion_content
        )
        results.append(
            FileAssertionResult(
                path=relative,
                passed=scope_error is None and not missing and not unexpected,
                missing_fragments=missing,
                unexpected_fragments=unexpected,
                error=scope_error,
            )
        )
    return tuple(results)


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


def _initialize_git_baseline(workspace: Path) -> None:
    subprocess.run(
        ["git", "init", "-q"],
        cwd=workspace,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        ["git", "add", "--all"],
        cwd=workspace,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Sirius Eval",
            "-c",
            "user.email=sirius-eval@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "-c",
            "core.hooksPath=/dev/null",
            "commit",
            "-q",
            "--allow-empty",
            "-m",
            "Initialize evaluation fixture",
        ],
        cwd=workspace,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _serialize_result(
    *,
    root: Path,
    skill_name: str,
    case: dict[str, object],
    prompt: str,
    command: Sequence[str],
    model: str | None,
    started_at: datetime,
    duration_seconds: float,
    executor_returncode: int,
    executor_stderr: str,
    changes: tuple[FileChange, ...],
    unauthorized_mutations: list[str],
    missing_required_mutations: list[str],
    checks: tuple[CheckResult, ...],
    file_assertions: tuple[FileAssertionResult, ...],
    trace_assertions: tuple[TraceAssertionResult, ...],
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
        "started_at": started_at.isoformat(),
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
        "file_assertions": [asdict(assertion) for assertion in file_assertions],
        "trace_assertions": [asdict(assertion) for assertion in trace_assertions],
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
        "file_assertions": _file_assertion_specs(case),
        "trace_assertions": _trace_assertion_specs(case),
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
    result_id: str | None = None,
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

    result_directory = results_directory or root / "evals" / "results"
    result_directory.mkdir(parents=True, exist_ok=True)
    run_directory = _resolve_child(
        result_directory, result_id or _new_result_id("run")
    )
    run_directory.mkdir(parents=True, exist_ok=False)
    trace_path = run_directory / "trace.jsonl"
    result_path = run_directory / "result.json"
    workspace = Path(tempfile.mkdtemp(prefix=f"sirius-eval-{skill_name}-"))

    try:
        shutil.copytree(
            fixture,
            workspace,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(*IGNORED_WORKSPACE_PARTS, "*.pyc"),
        )
        _initialize_git_baseline(workspace)
        before = _snapshot(workspace)
        command = (
            list(executor_command)
            if executor_command is not None
            else build_codex_command(workspace, model=model)
        )
        execution_started_at = datetime.now(timezone.utc)
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
        file_assertions = _evaluate_file_assertions(case, workspace)
        trace_assertions = _evaluate_trace_assertions(
            case, executor_stdout, workspace
        )
        mechanical_passed = (
            executor_returncode == 0
            and not unauthorized
            and not missing_required
            and all(check.returncode == 0 for check in checks)
            and all(assertion.passed for assertion in file_assertions)
            and all(assertion.passed for assertion in trace_assertions)
        )
        serialized = _serialize_result(
            root=root,
            skill_name=skill_name,
            case=case,
            prompt=prompt,
            command=command,
            model=model,
            started_at=execution_started_at,
            duration_seconds=duration_seconds,
            executor_returncode=executor_returncode,
            executor_stderr=executor_stderr,
            changes=changes,
            unauthorized_mutations=unauthorized,
            missing_required_mutations=missing_required,
            checks=checks,
            file_assertions=file_assertions,
            trace_assertions=trace_assertions,
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
            duration_seconds=duration_seconds,
            executor_returncode=executor_returncode,
            changes=changes,
            unauthorized_mutations=unauthorized,
            missing_required_mutations=missing_required,
            checks=checks,
            file_assertions=file_assertions,
            trace_assertions=trace_assertions,
            workspace=workspace,
            trace_path=trace_path,
            result_path=result_path,
        )
    finally:
        if not keep_workspace:
            shutil.rmtree(workspace, ignore_errors=True)


def _mutation_signature(result: BehavioralResult) -> tuple[tuple[str, str], ...]:
    return tuple((change.path, change.kind) for change in result.changes)


def run_behavioral_repetitions(
    root: Path,
    skill_name: str,
    case_id: str | int,
    *,
    repeat_count: int,
    model: str | None = None,
    timeout_seconds: int = 900,
    check_timeout_seconds: int = 120,
    keep_workspace: bool = False,
    executor_command: Sequence[str] | None = None,
    results_directory: Path | None = None,
) -> BehavioralBatchResult:
    if repeat_count < 1:
        raise ValueError("behavioral repeat count must be positive")
    result_directory = results_directory or root / "evals" / "results"
    result_directory.mkdir(parents=True, exist_ok=True)
    batch_id = _new_result_id("batch")
    batch_directory = _resolve_child(result_directory, batch_id)
    started_at = datetime.now(timezone.utc)
    runs = tuple(
        run_behavioral_case(
            root,
            skill_name,
            case_id,
            model=model,
            timeout_seconds=timeout_seconds,
            check_timeout_seconds=check_timeout_seconds,
            keep_workspace=keep_workspace,
            executor_command=executor_command,
            results_directory=result_directory,
            result_id=f"{batch_id}/run-{index:03d}",
        )
        for index in range(1, repeat_count + 1)
    )
    mechanical_passes = sum(result.mechanical_passed for result in runs)
    mechanically_stable = len({result.mechanical_passed for result in runs}) == 1
    mutations_stable = len({_mutation_signature(result) for result in runs}) == 1
    durations = [result.duration_seconds for result in runs]
    summary_path = batch_directory / "summary.json"
    summary = {
        "schema_version": 1,
        "batch_id": batch_id,
        "skill_name": skill_name,
        "case_id": case_id,
        "requested_model": model,
        "started_at": started_at.isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "repeat_count": repeat_count,
        "mechanical_passes": mechanical_passes,
        "mechanical_failures": repeat_count - mechanical_passes,
        "mechanical_pass_rate": mechanical_passes / repeat_count,
        "mechanically_stable": mechanically_stable,
        "mutations_stable": mutations_stable,
        "duration_seconds": {
            "minimum": round(min(durations), 3),
            "mean": round(sum(durations) / repeat_count, 3),
            "maximum": round(max(durations), 3),
            "total": round(sum(durations), 3),
        },
        "runs": [
            {
                "index": index,
                "mechanical_passed": result.mechanical_passed,
                "duration_seconds": round(result.duration_seconds, 3),
                "changes": [asdict(change) for change in result.changes],
                "trace_path": result.trace_path.relative_to(
                    batch_directory
                ).as_posix(),
                "result_path": result.result_path.relative_to(
                    batch_directory
                ).as_posix(),
            }
            for index, result in enumerate(runs, start=1)
        ],
    }
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return BehavioralBatchResult(
        skill_name=skill_name,
        case_id=case_id,
        runs=runs,
        mechanical_passes=mechanical_passes,
        mechanically_stable=mechanically_stable,
        mutations_stable=mutations_stable,
        summary_path=summary_path,
    )
