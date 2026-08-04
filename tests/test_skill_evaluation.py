from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from sirius_skills import behavioral_evaluation
from sirius_skills.behavioral_evaluation import (
    build_codex_command,
    run_behavioral_case,
)
from sirius_skills.commands import run_evals
from sirius_skills.evaluation import evaluate_repository, rank_skills


REPO_ROOT = Path(__file__).resolve().parents[1]


def write_skill(root: Path, name: str, description: str) -> None:
    skill = root / "skills" / name / "SKILL.md"
    skill.parent.mkdir(parents=True, exist_ok=True)
    skill.write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n",
        encoding="utf-8",
    )


def write_case(root: Path, name: str, data: dict[str, object]) -> None:
    case = root / "evals" / "cases" / f"{name}.json"
    case.parent.mkdir(parents=True, exist_ok=True)
    case.write_text(json.dumps(data), encoding="utf-8")


def test_rank_skills_uses_names_and_descriptions() -> None:
    ranking = rank_skills(
        "Reconstruct the deployed components and runtime dependencies",
        {
            "commit": "Commit changes with scoped staging.",
            "reconstruct-software-architecture": (
                "Recover components, runtime collaborations, deployment, and dependencies."
            ),
        },
    )

    assert ranking[0].name == "reconstruct-software-architecture"
    assert ranking[0].score > 0


def test_evaluator_checks_positive_and_owned_negative_routes(tmp_path: Path) -> None:
    write_skill(tmp_path, "behavior", "Recover observable commands and API behavior.")
    write_skill(tmp_path, "architecture", "Recover modules and architecture dependencies.")
    write_case(
        tmp_path,
        "behavior",
        {
            "skill_name": "behavior",
            "trigger": {
                "positive": [
                    {"prompt": "Recover the observable API behavior", "top_k": 1}
                ],
                "negative": [
                    {
                        "prompt": "Map the architecture modules and dependencies",
                        "owner": "architecture",
                    }
                ],
            },
            "evals": [
                {
                    "id": "recover-api",
                    "prompt": "Recover this API's behavior.",
                    "expected_output": "An evidence-backed behavior model.",
                    "expectations": ["Observable behavior is separated from inference."],
                }
            ],
        },
    )

    report = evaluate_repository(tmp_path)

    assert report.errors == []
    assert report.routing_checks == 2
    assert report.routing_passed == 2


def test_evaluator_rejects_unknown_negative_owner(tmp_path: Path) -> None:
    write_skill(tmp_path, "behavior", "Recover observable behavior.")
    write_case(
        tmp_path,
        "behavior",
        {
            "skill_name": "behavior",
            "trigger": {
                "positive": [],
                "negative": [
                    {"prompt": "Commit this change", "owner": "missing-skill"}
                ],
            },
            "evals": [],
        },
    )

    report = evaluate_repository(tmp_path)

    assert any("unknown owner 'missing-skill'" in error for error in report.errors)


def test_evaluator_detects_description_collisions(tmp_path: Path) -> None:
    description = "Recover architecture modules dependencies runtime deployment."
    write_skill(tmp_path, "architecture-one", description)
    write_skill(tmp_path, "architecture-two", description)

    report = evaluate_repository(tmp_path)

    assert any("description collision" in error for error in report.errors)


def test_evaluator_rejects_unknown_file_assertion_scope(tmp_path: Path) -> None:
    write_skill(tmp_path, "visualize", "Create focused architecture diagrams.")
    write_case(
        tmp_path,
        "visualize",
        {
            "skill_name": "visualize",
            "trigger": {"positive": [], "negative": []},
            "evals": [
                {
                    "id": "component-view",
                    "prompt": "Create a component view.",
                    "expected_output": "A focused component diagram.",
                    "expectations": ["The component boundary is visible."],
                    "file_assertions": [
                        {
                            "path": "docs/architecture.md",
                            "scope": "diagram",
                            "contains": ["component"],
                        }
                    ],
                }
            ],
        },
    )

    report = evaluate_repository(tmp_path)

    assert any("invalid 'file_assertions'" in error for error in report.errors)


def test_pilot_routing_cases_pass() -> None:
    report = evaluate_repository(REPO_ROOT)

    assert report.errors == []
    assert report.case_files == 8
    assert report.routing_checks >= 40


def write_behavior_fixture(
    root: Path,
    *,
    allowed_mutations: list[str],
    trace_assertions: list[dict[str, object]] | None = None,
) -> None:
    write_skill(root, "implementation", "Implement behavior with executable tests.")
    fixture = root / "evals" / "fixtures" / "example"
    (fixture / "src").mkdir(parents=True)
    (fixture / "tests").mkdir()
    (fixture / "src" / "value.txt").write_text("broken\n", encoding="utf-8")
    (fixture / "tests" / "verify.py").write_text(
        "from pathlib import Path\n"
        "raise SystemExit(Path('src/value.txt').read_text() != 'fixed\\n')\n",
        encoding="utf-8",
    )
    behavioral_case: dict[str, object] = {
        "id": "fix-value",
        "prompt": "Fix the value.",
        "expected_output": "The verifier passes.",
        "expectations": ["The broken value is corrected."],
        "prohibitions": ["Do not change unrelated files."],
        "fixture": "example",
        "allowed_mutations": allowed_mutations,
        "required_mutations": ["src/**"],
        "checks": [[sys.executable, "tests/verify.py"]],
    }
    if trace_assertions is not None:
        behavioral_case["trace_assertions"] = trace_assertions
    write_case(
        root,
        "implementation",
        {
            "skill_name": "implementation",
            "trigger": {"positive": [], "negative": []},
            "evals": [behavioral_case],
        },
    )


def write_fake_executor(tmp_path: Path, mutation: str) -> list[str]:
    executor = tmp_path / "fake_executor.py"
    executor.write_text(
        "import json\n"
        "from pathlib import Path\n"
        f"path = Path({mutation!r})\n"
        "path.parent.mkdir(parents=True, exist_ok=True)\n"
        "path.write_text('fixed\\n', encoding='utf-8')\n"
        "print(json.dumps({'type': 'turn.completed', 'usage': {'input_tokens': 1}}))\n",
        encoding="utf-8",
    )
    return [sys.executable, str(executor)]


def write_alternating_executor(tmp_path: Path) -> list[str]:
    executor = tmp_path / "alternating_executor.py"
    counter = tmp_path / "alternating_executor.count"
    executor.write_text(
        "import json\n"
        "from pathlib import Path\n"
        f"counter = Path({str(counter)!r})\n"
        "run = int(counter.read_text()) if counter.exists() else 0\n"
        "counter.write_text(str(run + 1), encoding='utf-8')\n"
        "Path('src/value.txt').write_text('fixed\\n', encoding='utf-8')\n"
        "if run % 2:\n"
        "    Path('notes.md').write_text('unexpected\\n', encoding='utf-8')\n"
        "print(json.dumps({'type': 'turn.completed'}))\n",
        encoding="utf-8",
    )
    return [sys.executable, str(executor)]


def write_codex_metadata_executor(tmp_path: Path) -> list[str]:
    executable = tmp_path / "bin" / "codex"
    executable.parent.mkdir()
    executable.write_text(
        "#!/usr/bin/env python3\n"
        "import json\n"
        "import sys\n"
        "from pathlib import Path\n"
        "if sys.argv[1:] == ['--version']:\n"
        "    print('codex-cli test-version')\n"
        "    raise SystemExit\n"
        "Path('src/value.txt').write_text('fixed\\n', encoding='utf-8')\n"
        "print(json.dumps({'type': 'turn.started', 'model': 'resolved-test-model'}))\n"
        "print(json.dumps({'type': 'turn.completed', 'usage': {\n"
        "    'input_tokens': 10,\n"
        "    'cached_input_tokens': 4,\n"
        "    'cache_write_input_tokens': 2,\n"
        "    'output_tokens': 3,\n"
        "    'reasoning_output_tokens': 1,\n"
        "}}))\n",
        encoding="utf-8",
    )
    executable.chmod(0o755)
    return [str(executable), "exec"]


def write_trace_executor(tmp_path: Path, *, include_red: bool) -> list[str]:
    executor = tmp_path / "trace_executor.py"
    red_event = (
        "event('command_execution', command='python3 -m pytest -q', exit_code=1)\n"
        if include_red
        else ""
    )
    executor.write_text(
        "import json\n"
        "from pathlib import Path\n"
        "def event(item_type, **details):\n"
        "    print(json.dumps({\n"
        "        'type': 'item.completed',\n"
        "        'item': {'type': item_type, **details},\n"
        "    }))\n"
        f"{red_event}"
        "path = Path('src/value.txt')\n"
        "path.write_text('fixed\\n', encoding='utf-8')\n"
        "event('file_change', changes=[{'path': str(path.resolve()), 'kind': 'update'}])\n"
        "event('command_execution', command='python3 -m pytest -q', exit_code=0)\n",
        encoding="utf-8",
    )
    return [sys.executable, str(executor)]


def red_green_trace_assertion() -> dict[str, object]:
    return {
        "type": "red_green",
        "command_contains": ["pytest"],
        "mutation_patterns": ["src/**"],
    }


def test_behavioral_runner_captures_authorized_mutations_and_checks(
    tmp_path: Path,
) -> None:
    write_behavior_fixture(tmp_path, allowed_mutations=["src/**"])

    result = run_behavioral_case(
        tmp_path,
        "implementation",
        "fix-value",
        executor_command=write_fake_executor(tmp_path, "src/value.txt"),
        results_directory=tmp_path / "results",
    )

    assert result.mechanical_passed is True
    assert [change.path for change in result.changes] == ["src/value.txt"]
    assert result.unauthorized_mutations == []
    assert result.checks[0].returncode == 0
    assert result.trace_path.read_text(encoding="utf-8").startswith(
        '{"type": "turn.completed"'
    )
    assert result.result_path.is_file()
    assert not result.workspace.exists()
    assert result.host == "test-adapter"
    assert result.host_version is None
    assert result.usage is not None
    assert result.usage.input_tokens == 1


def test_behavioral_runner_records_reported_model_host_version_and_usage(
    tmp_path: Path,
) -> None:
    write_behavior_fixture(tmp_path, allowed_mutations=["src/**"])

    result = run_behavioral_case(
        tmp_path,
        "implementation",
        "fix-value",
        model="requested-test-model",
        executor_command=write_codex_metadata_executor(tmp_path),
        results_directory=tmp_path / "results",
    )

    assert result.host == "codex"
    assert result.host_version == "codex-cli test-version"
    assert result.requested_model == "requested-test-model"
    assert result.observed_model == "resolved-test-model"
    assert result.usage is not None
    assert result.usage.input_tokens == 10
    assert result.usage.cached_input_tokens == 4
    assert result.usage.uncached_input_tokens == 6
    serialized = json.loads(result.result_path.read_text(encoding="utf-8"))
    assert serialized["host_version"] == "codex-cli test-version"
    assert serialized["observed_model"] == "resolved-test-model"
    assert serialized["usage"]["output_tokens"] == 3


def test_behavioral_runner_preserves_prior_run_results(tmp_path: Path) -> None:
    write_behavior_fixture(tmp_path, allowed_mutations=["src/**"])
    results_directory = tmp_path / "results"

    first = run_behavioral_case(
        tmp_path,
        "implementation",
        "fix-value",
        executor_command=write_fake_executor(tmp_path, "src/value.txt"),
        results_directory=results_directory,
    )
    second = run_behavioral_case(
        tmp_path,
        "implementation",
        "fix-value",
        executor_command=write_fake_executor(tmp_path, "src/value.txt"),
        results_directory=results_directory,
    )

    assert first.result_path != second.result_path
    assert first.result_path.is_file()
    assert second.result_path.is_file()


def test_behavioral_repetitions_summarize_stable_runs(tmp_path: Path) -> None:
    write_behavior_fixture(tmp_path, allowed_mutations=["src/**"])

    batch = behavioral_evaluation.run_behavioral_repetitions(
        tmp_path,
        "implementation",
        "fix-value",
        repeat_count=3,
        executor_command=write_fake_executor(tmp_path, "src/value.txt"),
        results_directory=tmp_path / "results",
    )

    assert len(batch.runs) == 3
    assert batch.mechanical_passes == 3
    assert batch.mechanically_stable is True
    assert batch.mutations_stable is True
    assert len({run.result_path for run in batch.runs}) == 3
    summary = json.loads(batch.summary_path.read_text(encoding="utf-8"))
    assert summary["mechanical_pass_rate"] == 1.0
    assert summary["mechanically_stable"] is True
    assert summary["mutations_stable"] is True
    assert summary["execution_environments_stable"] is True
    assert summary["usage"]["reported_runs"] == 3
    assert summary["usage"]["input_tokens"] == 3
    assert summary["usage"]["missing_runs"] == 0
    assert len(summary["runs"]) == 3


def test_behavioral_repetitions_report_variable_outcomes(tmp_path: Path) -> None:
    write_behavior_fixture(tmp_path, allowed_mutations=["src/**"])

    batch = behavioral_evaluation.run_behavioral_repetitions(
        tmp_path,
        "implementation",
        "fix-value",
        repeat_count=2,
        executor_command=write_alternating_executor(tmp_path),
        results_directory=tmp_path / "results",
    )

    assert batch.mechanical_passes == 1
    assert batch.mechanically_stable is False
    assert batch.mutations_stable is False
    summary = json.loads(batch.summary_path.read_text(encoding="utf-8"))
    assert summary["mechanical_pass_rate"] == 0.5
    assert [run["mechanical_passed"] for run in summary["runs"]] == [True, False]
    assert summary["usage"] == {"reported_runs": 0, "missing_runs": 2}


def test_behavioral_runner_accepts_red_green_trace_around_mutation(
    tmp_path: Path,
) -> None:
    write_behavior_fixture(
        tmp_path,
        allowed_mutations=["src/**"],
        trace_assertions=[red_green_trace_assertion()],
    )

    result = run_behavioral_case(
        tmp_path,
        "implementation",
        "fix-value",
        executor_command=write_trace_executor(tmp_path, include_red=True),
        results_directory=tmp_path / "results",
    )

    assert result.mechanical_passed is True
    assert result.trace_assertions[0].passed is True
    serialized = json.loads(result.result_path.read_text(encoding="utf-8"))
    assert serialized["trace_assertions"][0]["passed"] is True


def test_behavioral_runner_rejects_green_only_trace(tmp_path: Path) -> None:
    write_behavior_fixture(
        tmp_path,
        allowed_mutations=["src/**"],
        trace_assertions=[red_green_trace_assertion()],
    )

    result = run_behavioral_case(
        tmp_path,
        "implementation",
        "fix-value",
        executor_command=write_trace_executor(tmp_path, include_red=False),
        results_directory=tmp_path / "results",
    )

    assert result.mechanical_passed is False
    assert result.trace_assertions[0].error == (
        "no matching failing command completed before the first mutation"
    )


def test_evaluator_rejects_invalid_trace_assertion(tmp_path: Path) -> None:
    write_behavior_fixture(
        tmp_path,
        allowed_mutations=["src/**"],
        trace_assertions=[
            {
                "type": "green_only",
                "command_contains": ["pytest"],
                "mutation_patterns": ["src/**"],
            }
        ],
    )

    report = evaluate_repository(tmp_path)

    assert any("invalid 'trace_assertions'" in error for error in report.errors)


def test_behavioral_runner_commits_a_clean_fixture_baseline(tmp_path: Path) -> None:
    write_behavior_fixture(tmp_path, allowed_mutations=["src/**"])
    executor = tmp_path / "git_aware_executor.py"
    executor.write_text(
        "import json\n"
        "import subprocess\n"
        "from pathlib import Path\n"
        "subprocess.run(['git', 'rev-parse', '--verify', 'HEAD'], check=True)\n"
        "status = subprocess.run(\n"
        "    ['git', 'status', '--short'], check=True, text=True, capture_output=True\n"
        ").stdout\n"
        "if status:\n"
        "    raise SystemExit(f'fixture baseline is dirty: {status}')\n"
        "Path('src/value.txt').write_text('fixed\\n', encoding='utf-8')\n"
        "diff = subprocess.run(\n"
        "    ['git', 'diff', '--', 'src/value.txt'],\n"
        "    check=True, text=True, capture_output=True,\n"
        ").stdout\n"
        "if '-broken' not in diff or '+fixed' not in diff:\n"
        "    raise SystemExit('fixture mutation is not visible in git diff')\n"
        "print(json.dumps({'type': 'turn.completed'}))\n",
        encoding="utf-8",
    )

    result = run_behavioral_case(
        tmp_path,
        "implementation",
        "fix-value",
        executor_command=[sys.executable, str(executor)],
        results_directory=tmp_path / "results",
    )

    assert result.mechanical_passed is True


def test_behavioral_runner_rejects_mutations_outside_allowlist(
    tmp_path: Path,
) -> None:
    write_behavior_fixture(tmp_path, allowed_mutations=["src/**"])

    result = run_behavioral_case(
        tmp_path,
        "implementation",
        "fix-value",
        executor_command=write_fake_executor(tmp_path, "notes.md"),
        results_directory=tmp_path / "results",
    )

    assert result.mechanical_passed is False
    assert result.unauthorized_mutations == ["notes.md"]


def test_codex_command_is_ephemeral_json_and_workspace_scoped(
    tmp_path: Path,
) -> None:
    command = build_codex_command(tmp_path, model="test-model")

    assert command[:2] == ["codex", "exec"]
    assert "--ephemeral" in command
    assert "--json" in command
    assert command[command.index("--sandbox") + 1] == "workspace-write"
    assert command[command.index("--cd") + 1] == str(tmp_path)
    assert command[command.index("--model") + 1] == "test-model"
    assert command[-1] == "-"


def test_behavioral_cli_dry_run_does_not_execute(
    tmp_path: Path, capsys
) -> None:
    write_behavior_fixture(tmp_path, allowed_mutations=["src/**"])

    exit_code = run_evals.main(
        [
            "--root",
            str(tmp_path),
            "--behavioral",
            "implementation",
            "--case",
            "fix-value",
            "--repeat",
            "3",
            "--dry-run",
        ]
    )

    assert exit_code == 0
    output = capsys.readouterr().out
    assert '"repeat_count": 3' in output
    assert '"semantic_expectations": "ungraded"' in output
    assert not (tmp_path / "evals" / "results").exists()


def test_invoice_fixture_seeds_the_expected_rounding_failure() -> None:
    fixture = REPO_ROOT / "evals" / "fixtures" / "invoice-rounding"

    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=fixture,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    assert completed.returncode == 1
    assert "assert '2.67' == '2.68'" in completed.stdout


def test_order_cancellation_fixture_starts_green_without_approved_policy() -> None:
    fixture = REPO_ROOT / "evals" / "fixtures" / "order-cancellation-feedback"

    regression = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=fixture,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    missing_policy = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from src.order import Order; "
                "order = Order('order-1'); "
                "order.cancel(); "
                "assert order.cancellation_reason is None"
            ),
        ],
        cwd=fixture,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    independent_oracle = subprocess.run(
        [sys.executable, "-m", "verification.verify_cancellation_policy"],
        cwd=fixture,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    assert regression.returncode == 0, regression.stdout
    assert missing_policy.returncode == 0, missing_policy.stdout
    assert independent_oracle.returncode != 0
    assert "cancel" in independent_oracle.stdout


def test_behavioral_runner_checks_required_file_content(tmp_path: Path) -> None:
    write_skill(tmp_path, "visualize", "Create focused PlantUML architecture views.")
    fixture = tmp_path / "evals" / "fixtures" / "visual"
    fixture.mkdir(parents=True)
    write_case(
        tmp_path,
        "visualize",
        {
            "skill_name": "visualize",
            "trigger": {"positive": [], "negative": []},
            "evals": [
                {
                    "id": "component-view",
                    "prompt": "Explain the components.",
                    "expected_output": "A focused component diagram.",
                    "expectations": ["The component boundary is visible."],
                    "fixture": "visual",
                    "allowed_mutations": ["docs/**"],
                    "required_mutations": ["docs/architecture.md"],
                    "file_assertions": [
                        {
                            "path": "docs/architecture.md",
                            "scope": "plantuml",
                            "contains": ["@startuml", "component", "@enduml"],
                            "not_contains": ["class "],
                        }
                    ],
                }
            ],
        },
    )
    executor = tmp_path / "visual_executor.py"
    executor.write_text(
        "from pathlib import Path\n"
        "path = Path('docs/architecture.md')\n"
        "path.parent.mkdir(parents=True)\n"
        "path.write_text(\n"
        "    'No class diagram is included.\\n\\n'\n"
        "    '```plantuml\\n@startuml\\ncomponent API\\n@enduml\\n```\\n'\n"
        ")\n",
        encoding="utf-8",
    )

    result = run_behavioral_case(
        tmp_path,
        "visualize",
        "component-view",
        executor_command=[sys.executable, str(executor)],
        results_directory=tmp_path / "results",
    )

    assert result.mechanical_passed is True
    assert result.file_assertions[0].passed is True


def test_behavioral_runner_rejects_forbidden_file_content(tmp_path: Path) -> None:
    write_skill(tmp_path, "visualize", "Create focused PlantUML architecture views.")
    fixture = tmp_path / "evals" / "fixtures" / "visual"
    fixture.mkdir(parents=True)
    write_case(
        tmp_path,
        "visualize",
        {
            "skill_name": "visualize",
            "trigger": {"positive": [], "negative": []},
            "evals": [
                {
                    "id": "component-view",
                    "prompt": "Explain the components.",
                    "expected_output": "A focused component diagram.",
                    "expectations": ["The component boundary is visible."],
                    "fixture": "visual",
                    "allowed_mutations": ["docs/**"],
                    "required_mutations": ["docs/architecture.md"],
                    "file_assertions": [
                        {
                            "path": "docs/architecture.md",
                            "scope": "plantuml",
                            "contains": ["@startuml", "component", "@enduml"],
                            "not_contains": ["class "],
                        }
                    ],
                }
            ],
        },
    )
    executor = tmp_path / "visual_executor.py"
    executor.write_text(
        "from pathlib import Path\n"
        "path = Path('docs/architecture.md')\n"
        "path.parent.mkdir(parents=True)\n"
        "path.write_text(\n"
        "    'No class diagram should be needed.\\n\\n'\n"
        "    '```plantuml\\n@startuml\\ncomponent API\\nclass Order\\n@enduml\\n```\\n'\n"
        ")\n",
        encoding="utf-8",
    )

    result = run_behavioral_case(
        tmp_path,
        "visualize",
        "component-view",
        executor_command=[sys.executable, str(executor)],
        results_directory=tmp_path / "results",
    )

    assert result.mechanical_passed is False
    assert result.file_assertions[0].unexpected_fragments == ("class ",)
