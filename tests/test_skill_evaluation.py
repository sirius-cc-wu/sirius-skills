from __future__ import annotations

import json
from pathlib import Path

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
    assert report.case_files == 6
    assert report.routing_checks >= 30
