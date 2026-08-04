from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

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


def test_pilot_routing_cases_pass() -> None:
    report = evaluate_repository(REPO_ROOT)

    assert report.errors == []
    assert report.case_files == 8
    assert report.routing_checks >= 40


def write_behavior_fixture(root: Path, *, allowed_mutations: list[str]) -> None:
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
    write_case(
        root,
        "implementation",
        {
            "skill_name": "implementation",
            "trigger": {"positive": [], "negative": []},
            "evals": [
                {
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
            ],
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
            "--dry-run",
        ]
    )

    assert exit_code == 0
    assert '"semantic_expectations": "ungraded"' in capsys.readouterr().out
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
        "path.write_text('```plantuml\\n@startuml\\ncomponent API\\n@enduml\\n```\\n')\n",
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
        "path.write_text('@startuml\\ncomponent API\\nclass Order\\n@enduml\\n')\n",
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
