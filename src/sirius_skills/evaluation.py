from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping


COLLISION_WARNING = 0.60
COLLISION_ERROR = 0.90
MIN_POSITIVE = 3
MIN_NEGATIVE = 2
MIN_BEHAVIORAL = 1

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "before",
    "by",
    "for",
    "from",
    "help",
    "i",
    "in",
    "into",
    "is",
    "it",
    "its",
    "me",
    "my",
    "need",
    "needs",
    "of",
    "on",
    "or",
    "our",
    "so",
    "that",
    "the",
    "them",
    "this",
    "to",
    "use",
    "want",
    "we",
    "when",
    "with",
    "you",
    "your",
}


@dataclass(frozen=True)
class RankedSkill:
    name: str
    score: float


@dataclass
class EvaluationReport:
    skill_count: int = 0
    case_files: int = 0
    routing_checks: int = 0
    routing_passed: int = 0
    positive_checks: int = 0
    rank_one_positives: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def rank_one_rate(self) -> float | None:
        if not self.positive_checks:
            return None
        return self.rank_one_positives / self.positive_checks


def _stem(token: str) -> str:
    for suffix in ("ally", "ing", "ed", "es", "al"):
        if len(token) > len(suffix) + 3 and token.endswith(suffix):
            token = token[: -len(suffix)]
            break
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        token = token[:-1]
    if len(token) > 4 and token.endswith("e"):
        token = token[:-1]
    if (
        len(token) > 4
        and token[-1] == token[-2]
        and token[-1] not in "aeiou"
    ):
        token = token[:-1]
    if len(token) > 3 and token.endswith("y"):
        token = f"{token[:-1]}i"
    return token


def _tokenize(text: str) -> list[str]:
    raw = re.sub(r"[^a-z0-9\s-]", " ", text.lower())
    return [
        _stem(token)
        for token in re.split(r"[\s-]+", raw)
        if len(token) > 2 and token not in STOP_WORDS
    ]


def _skill_terms(name: str, description: str) -> Counter[str]:
    name_tokens = _tokenize(name.replace("-", " "))
    return Counter([*name_tokens, *name_tokens, *_tokenize(description)])


def _idf(term: str, documents: Iterable[Counter[str]]) -> float:
    documents = tuple(documents)
    frequency = sum(term in document for document in documents)
    return math.log(1 + len(documents) / (1 + frequency))


def _vector(
    terms: Counter[str], documents: tuple[Counter[str], ...]
) -> dict[str, float]:
    return {term: count * _idf(term, documents) for term, count in terms.items()}


def _cosine(left: Mapping[str, float], right: Mapping[str, float]) -> float:
    dot = sum(weight * right.get(term, 0.0) for term, weight in left.items())
    left_norm = math.sqrt(sum(weight * weight for weight in left.values()))
    right_norm = math.sqrt(sum(weight * weight for weight in right.values()))
    if not left_norm or not right_norm:
        return 0.0
    return dot / (left_norm * right_norm)


def rank_skills(prompt: str, descriptions: Mapping[str, str]) -> list[RankedSkill]:
    names = sorted(descriptions)
    term_counts = {
        name: _skill_terms(name, descriptions[name]) for name in names
    }
    documents = tuple(term_counts.values())
    prompt_vector = _vector(Counter(_tokenize(prompt)), documents)
    ranking = [
        RankedSkill(
            name=name,
            score=_cosine(prompt_vector, _vector(term_counts[name], documents)),
        )
        for name in names
    ]
    return sorted(ranking, key=lambda item: (-item.score, item.name))


def _frontmatter_value(source: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", source, re.MULTILINE)
    if match is None:
        return None
    value = match.group(1).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def load_skill_descriptions(root: Path) -> dict[str, str]:
    descriptions: dict[str, str] = {}
    for path in sorted((root / "skills").glob("*/SKILL.md")):
        source = path.read_text(encoding="utf-8")
        name = _frontmatter_value(source, "name")
        description = _frontmatter_value(source, "description")
        if name and description:
            descriptions[name] = description
    return descriptions


def _valid_string_list(value: object, *, allow_empty: bool = True) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(isinstance(item, str) and bool(item.strip()) for item in value)
    )


def _validate_behavioral_cases(
    filename: str, cases: object, report: EvaluationReport
) -> None:
    if not isinstance(cases, list):
        report.errors.append(f"{filename}: 'evals' must be a list")
        return
    seen_ids: set[str | int] = set()
    for case in cases:
        if not isinstance(case, dict):
            report.errors.append(f"{filename}: each behavioral eval must be an object")
            continue
        case_id = case.get("id")
        valid_id = (
            isinstance(case_id, str) and bool(case_id.strip())
        ) or (isinstance(case_id, int) and not isinstance(case_id, bool))
        if not valid_id:
            report.errors.append(f"{filename}: behavioral eval has an invalid id")
        elif case_id in seen_ids:
            report.errors.append(f"{filename}: duplicate behavioral eval id {case_id!r}")
        else:
            seen_ids.add(case_id)
        for key in ("prompt", "expected_output"):
            value = case.get(key)
            if not isinstance(value, str) or not value.strip():
                report.errors.append(
                    f"{filename}: behavioral eval {case_id!r} needs non-empty '{key}'"
                )
        if not _valid_string_list(case.get("expectations"), allow_empty=False):
            report.errors.append(
                f"{filename}: behavioral eval {case_id!r} needs expectations"
            )
        for key in ("prohibitions", "allowed_mutations"):
            if key in case and not _valid_string_list(case[key]):
                report.errors.append(
                    f"{filename}: behavioral eval {case_id!r} has invalid '{key}'"
                )
        if "required_mutations" in case and not _valid_string_list(
            case["required_mutations"]
        ):
            report.errors.append(
                f"{filename}: behavioral eval {case_id!r} has invalid "
                "'required_mutations'"
            )
        fixture = case.get("fixture")
        workspace_mode = case.get("workspace_mode", "mutable")
        if workspace_mode not in {"mutable", "read-only"}:
            report.errors.append(
                f"{filename}: behavioral eval {case_id!r} has invalid "
                "'workspace_mode'"
            )
        if fixture is not None and (
            not isinstance(fixture, str) or not fixture.strip()
        ):
            report.errors.append(
                f"{filename}: behavioral eval {case_id!r} has invalid 'fixture'"
            )
        if fixture is not None:
            allowed_mutations = case.get("allowed_mutations")
            if not _valid_string_list(allowed_mutations):
                report.errors.append(
                    f"{filename}: fixture-backed eval {case_id!r} needs "
                    "allowed_mutations"
                )
            elif workspace_mode == "mutable" and not allowed_mutations:
                report.errors.append(
                    f"{filename}: mutable eval {case_id!r} needs allowed mutations"
                )
            elif workspace_mode == "read-only" and allowed_mutations:
                report.errors.append(
                    f"{filename}: read-only eval {case_id!r} must not allow "
                    "mutations"
                )
            if (
                workspace_mode == "read-only"
                and case.get("required_mutations") != []
            ):
                report.errors.append(
                    f"{filename}: read-only eval {case_id!r} must declare empty "
                    "required_mutations"
                )
        checks = case.get("checks", [])
        if not isinstance(checks, list) or any(
            not isinstance(command, list)
            or not command
            or any(not isinstance(argument, str) or not argument for argument in command)
            for command in checks
        ):
            report.errors.append(
                f"{filename}: behavioral eval {case_id!r} has invalid 'checks'"
            )
        file_assertions = case.get("file_assertions", [])
        if not isinstance(file_assertions, list) or any(
            not isinstance(assertion, dict)
            or not isinstance(assertion.get("path"), str)
            or not assertion.get("path")
            or assertion.get("scope", "file") not in {"file", "plantuml"}
            or not _valid_string_list(assertion.get("contains", []))
            or not _valid_string_list(assertion.get("not_contains", []))
            for assertion in file_assertions
        ):
            report.errors.append(
                f"{filename}: behavioral eval {case_id!r} has invalid "
                "'file_assertions'"
            )
        trace_assertions = case.get("trace_assertions", [])
        if not isinstance(trace_assertions, list) or any(
            not isinstance(assertion, dict)
            or assertion.get("type") != "red_green"
            or not _valid_string_list(
                assertion.get("command_contains"), allow_empty=False
            )
            or not _valid_string_list(
                assertion.get("mutation_patterns"), allow_empty=False
            )
            for assertion in trace_assertions
        ):
            report.errors.append(
                f"{filename}: behavioral eval {case_id!r} has invalid "
                "'trace_assertions'"
            )
        semantic_rubric = case.get("semantic_rubric", [])
        rubric_ids: set[str | int] = set()
        ordered_rubric_ids: list[str | int] = []
        if not isinstance(semantic_rubric, list):
            report.errors.append(
                f"{filename}: behavioral eval {case_id!r} has invalid "
                "'semantic_rubric'"
            )
        else:
            for criterion in semantic_rubric:
                criterion_id = (
                    criterion.get("id") if isinstance(criterion, dict) else None
                )
                description = (
                    criterion.get("criterion")
                    if isinstance(criterion, dict)
                    else None
                )
                valid_id = (
                    isinstance(criterion_id, str) and bool(criterion_id.strip())
                ) or (
                    isinstance(criterion_id, int)
                    and not isinstance(criterion_id, bool)
                )
                if (
                    not valid_id
                    or not isinstance(description, str)
                    or not description.strip()
                ):
                    report.errors.append(
                        f"{filename}: behavioral eval {case_id!r} has invalid "
                        "semantic rubric criterion"
                    )
                    continue
                if criterion_id in rubric_ids:
                    report.errors.append(
                        f"{filename}: behavioral eval {case_id!r} has duplicate "
                        f"semantic rubric id {criterion_id!r}"
                    )
                rubric_ids.add(criterion_id)
                ordered_rubric_ids.append(criterion_id)
        semantic_controls = case.get("semantic_controls", [])
        if not isinstance(semantic_controls, list):
            report.errors.append(
                f"{filename}: behavioral eval {case_id!r} has invalid "
                "'semantic_controls'"
            )
        else:
            control_ids: set[str | int] = set()
            polarities = {
                criterion_id: set() for criterion_id in ordered_rubric_ids
            }
            controls_valid = True
            if semantic_controls and not ordered_rubric_ids:
                controls_valid = False
                report.errors.append(
                    f"{filename}: behavioral eval {case_id!r} has semantic "
                    "controls without a semantic rubric"
                )
            for control in semantic_controls:
                control_id = (
                    control.get("id") if isinstance(control, dict) else None
                )
                response = (
                    control.get("response")
                    if isinstance(control, dict)
                    else None
                )
                expected = (
                    control.get("expected_criteria")
                    if isinstance(control, dict)
                    else None
                )
                valid_control_id = (
                    isinstance(control_id, str) and bool(control_id.strip())
                ) or (
                    isinstance(control_id, int)
                    and not isinstance(control_id, bool)
                )
                if (
                    not valid_control_id
                    or control_id in control_ids
                    or not isinstance(response, str)
                    or not response.strip()
                    or not isinstance(expected, list)
                ):
                    controls_valid = False
                    report.errors.append(
                        f"{filename}: behavioral eval {case_id!r} has invalid "
                        "semantic control"
                    )
                    continue
                control_ids.add(control_id)
                expected_ids: list[str | int] = []
                valid_expectations = True
                for criterion in expected:
                    expected_id = (
                        criterion.get("id")
                        if isinstance(criterion, dict)
                        else None
                    )
                    passed = (
                        criterion.get("passed")
                        if isinstance(criterion, dict)
                        else None
                    )
                    if (
                        expected_id not in rubric_ids
                        or expected_id in expected_ids
                        or not isinstance(passed, bool)
                    ):
                        valid_expectations = False
                        break
                    expected_ids.append(expected_id)
                if not valid_expectations:
                    controls_valid = False
                    report.errors.append(
                        f"{filename}: semantic control {control_id!r} has "
                        "invalid expectations"
                    )
                elif expected_ids != ordered_rubric_ids:
                    controls_valid = False
                    report.errors.append(
                        f"{filename}: semantic control {control_id!r} must cover "
                        "semantic rubric ids in rubric order"
                    )
                else:
                    for criterion in expected:
                        polarities[criterion["id"]].add(criterion["passed"])
            missing_polarities = [
                criterion_id
                for criterion_id, values in polarities.items()
                if values != {False, True}
            ]
            if semantic_controls and controls_valid and missing_polarities:
                report.errors.append(
                    f"{filename}: semantic controls must exercise true and "
                    f"false for rubric ids {missing_polarities!r}"
                )
        trust_level = case.get("trust_level")
        if trust_level not in (None, "provisional", "fixture-backed"):
            report.errors.append(
                f"{filename}: behavioral eval {case_id!r} has invalid "
                "'trust_level'"
            )


def _load_case_files(root: Path, report: EvaluationReport) -> list[tuple[Path, object]]:
    loaded: list[tuple[Path, object]] = []
    case_directory = root / "evals" / "cases"
    for path in sorted(case_directory.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            report.errors.append(f"{path.name}: invalid JSON: {exc}")
            continue
        loaded.append((path, data))
    report.case_files = len(loaded)
    return loaded


def _check_collisions(
    descriptions: Mapping[str, str], report: EvaluationReport
) -> None:
    names = sorted(descriptions)
    terms = {name: Counter(_tokenize(descriptions[name])) for name in names}
    documents = tuple(terms.values())
    vectors = {name: _vector(terms[name], documents) for name in names}
    for index, left in enumerate(names):
        for right in names[index + 1 :]:
            similarity = _cosine(vectors[left], vectors[right])
            message = (
                f"description collision: {left} and {right} are "
                f"{similarity:.0%} similar"
            )
            if similarity >= COLLISION_ERROR:
                report.errors.append(message)
            elif similarity >= COLLISION_WARNING:
                report.warnings.append(message.replace("collision", "overlap"))


def _check_positive(
    filename: str,
    expected: str,
    trigger: object,
    descriptions: Mapping[str, str],
    report: EvaluationReport,
) -> None:
    report.routing_checks += 1
    report.positive_checks += 1
    if not isinstance(trigger, dict):
        report.errors.append(f"{filename}: positive trigger must be an object")
        return
    prompt = trigger.get("prompt")
    top_k = trigger.get("top_k", 3)
    if not isinstance(prompt, str) or not prompt.strip():
        report.errors.append(f"{filename}: positive trigger needs a prompt")
        return
    if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k < 1:
        report.errors.append(f"{filename}: positive trigger has invalid top_k")
        return
    ranking = rank_skills(prompt, descriptions)
    index = next(i for i, item in enumerate(ranking) if item.name == expected)
    hit = ranking[index]
    if index == 0 and hit.score > 0:
        report.rank_one_positives += 1
    if index < top_k and hit.score > 0:
        report.routing_passed += 1
        return
    if hit.score == 0:
        report.errors.append(
            f"{expected}: positive prompt shares no vocabulary with its description: "
            f"{prompt!r}"
        )
        return
    leaders = ", ".join(
        f"{item.name} ({item.score:.2f})" for item in ranking[:3] if item.score > 0
    )
    report.errors.append(
        f"{expected}: positive prompt ranked {index + 1}, expected top {top_k}: "
        f"{prompt!r}; leaders: {leaders}"
    )


def _check_negative(
    filename: str,
    expected: str,
    trigger: object,
    descriptions: Mapping[str, str],
    report: EvaluationReport,
) -> None:
    report.routing_checks += 1
    if not isinstance(trigger, dict):
        report.errors.append(f"{filename}: negative trigger must be an object")
        return
    prompt = trigger.get("prompt")
    owner = trigger.get("owner")
    if not isinstance(prompt, str) or not prompt.strip():
        report.errors.append(f"{filename}: negative trigger needs a prompt")
        return
    if not isinstance(owner, str) or owner not in descriptions:
        report.errors.append(f"{filename}: negative trigger declares unknown owner {owner!r}")
        return
    ranking = rank_skills(prompt, descriptions)
    self_index = next(i for i, item in enumerate(ranking) if item.name == expected)
    owner_index = next(i for i, item in enumerate(ranking) if item.name == owner)
    if ranking[0].name == expected and ranking[0].score > 0:
        report.errors.append(
            f"{expected}: ranked first for negative prompt owned by {owner}: {prompt!r}"
        )
        return
    if ranking[owner_index].score == 0 or owner_index > self_index:
        report.errors.append(
            f"{expected}: owner {owner} did not outrank it for negative prompt: "
            f"{prompt!r}"
        )
        return
    report.routing_passed += 1


def evaluate_repository(root: Path) -> EvaluationReport:
    report = EvaluationReport()
    descriptions = load_skill_descriptions(root)
    report.skill_count = len(descriptions)
    loaded_cases = _load_case_files(root, report)
    case_names = {path.stem for path, _ in loaded_cases}
    for name in sorted(descriptions):
        if name not in case_names:
            report.warnings.append(f"{name}: no routing case file")

    for path, data in loaded_cases:
        if not isinstance(data, dict):
            report.errors.append(f"{path.name}: case file must contain an object")
            continue
        expected = path.stem
        if data.get("skill_name") != expected:
            report.errors.append(
                f"{path.name}: skill_name {data.get('skill_name')!r} does not match filename"
            )
        if expected not in descriptions:
            report.errors.append(f"{path.name}: no matching skill directory")
            continue
        trigger = data.get("trigger")
        if not isinstance(trigger, dict):
            report.errors.append(f"{path.name}: 'trigger' must be an object")
            continue
        positives = trigger.get("positive", [])
        negatives = trigger.get("negative", [])
        if not isinstance(positives, list) or not isinstance(negatives, list):
            report.errors.append(
                f"{path.name}: positive and negative triggers must be lists"
            )
            continue
        for positive in positives:
            _check_positive(path.name, expected, positive, descriptions, report)
        for negative in negatives:
            _check_negative(path.name, expected, negative, descriptions, report)
        _validate_behavioral_cases(path.name, data.get("evals", []), report)
        behavioral = data.get("evals", [])
        behavioral_count = len(behavioral) if isinstance(behavioral, list) else 0
        if (
            len(positives) < MIN_POSITIVE
            or len(negatives) < MIN_NEGATIVE
            or behavioral_count < MIN_BEHAVIORAL
        ):
            report.warnings.append(
                f"{expected}: below pilot minimums "
                f"({len(positives)} positive/{len(negatives)} negative/"
                f"{behavioral_count} behavioral)"
            )

    _check_collisions(descriptions, report)
    return report
