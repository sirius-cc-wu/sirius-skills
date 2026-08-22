from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SYNC_REFERENCES = "sirius_skills.commands.sync_shared_references"
NPX_SKILLS = "npx --yes skills"
PACKAGED_ADD = f'{NPX_SKILLS} add "'
PACKAGED_REPO_SOURCE = f'{PACKAGED_ADD}{REPO_ROOT}"'
SOURCE_SKILLS_DIR = REPO_ROOT / "skills"
TARGET_PROJECT = Path("/tmp/sirius-say")
ADDY_EXTERNAL_PROFILE = REPO_ROOT / "catalog/external-skill-sets/addy-osmani.txt"
ADDY_SOURCE = (
    "https://github.com/addyosmani/agent-skills/archive/"
    "5a1b82d6445d1e2f0abeea1072851419a50c0e5c.tar.gz"
)
ADDY_SKILLS = {
    "interview-me",
    "idea-refine",
    "code-review-and-quality",
    "code-simplification",
    "git-workflow-and-versioning",
}
PROFILE_NAMES = (
    "workflow",
    "iterative-design",
    "applying-uml-and-patterns",
    "reverse-engineering",
    "all",
)
WORKFLOW_SKILLS = {
    "create-pr",
    "walkthrough-me",
}
ITERATIVE_DESIGN_SKILLS = {
    "assess-development-input",
    "select-technical-artifacts",
    "design-repository-artifact-layout",
    "record-architecture-decision",
    "iterative-risk-driven-development",
    "stakeholder-requirements-elicitation",
    "requirements-synthesis-validation",
    "implementation-slice-briefing",
    "inception",
    "use-case-modeling",
    "behavior-driven-specification",
    "domain-modeling",
    "system-sequence-diagrams",
    "operation-contracts",
    "grasp-responsibility-design",
    "use-case-realization",
    "uml-class-diagram-design",
    "design-pattern-application",
    "software-design-language-adaptation",
    "design-rust-lifecycles",
    "test-driven-implementation",
    "behavior-preserving-refactoring",
}
REVERSE_ENGINEERING_SKILLS = {
    "reverse-engineer-software-system",
    "select-technical-artifacts",
    "design-repository-artifact-layout",
    "record-architecture-decision",
    "survey-existing-system",
    "recover-system-behavior",
    "reconstruct-software-architecture",
    "reconcile-recovered-design",
}


def render_just(target: str, *args: str) -> str:
    result = subprocess.run(
        ["just", "-n", target, *args],
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return result.stdout


def read_profile(name: str) -> set[str]:
    return {
        line.strip()
        for line in (REPO_ROOT / "skill-sets" / f"{name}.txt").read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def read_external_profile(path: Path) -> set[str]:
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def assert_addy_install_is_guarded_to_all(output: str) -> None:
    guard = 'if [[ "$skill_set" == "all" ]]'
    source_position = output.index(ADDY_SOURCE)
    guard_start = output.rfind(guard, 0, source_position)
    guard_end = output.index("\nfi", guard_start)
    assert guard_start < source_position < guard_end


def npx_commands(output: str, operation: str) -> list[str]:
    return [
        line.strip()
        for line in output.splitlines()
        if f"{NPX_SKILLS} {operation}" in line
    ]


def test_install_targets_a_consumer_project_with_the_workflow_profile() -> None:
    output = render_just("install", str(TARGET_PROJECT))

    assert "pip install" not in output
    assert SYNC_REFERENCES in output
    assert "sync_shared_skill_runtime.py" not in output
    assert PACKAGED_REPO_SOURCE not in output
    assert len(npx_commands(output, "add")) == 1
    assert ADDY_SOURCE in npx_commands(output, "add")[0]
    assert_addy_install_is_guarded_to_all(output)
    assert 'if [[ "$skill_set" == "all" ]]' in output
    assert "prune-retired-local" in output
    assert "link-profile" in output
    assert f'--source-dir "{SOURCE_SKILLS_DIR}"' in output
    assert f"target_dir='{TARGET_PROJECT}'" in output
    assert 'target_skills_dir="$target_dir/.agents/skills"' in output
    assert '--target-dir "$target_skills_dir"' in output
    assert 'cd "$target_dir"' in output
    assert "record-installed" not in output
    assert "--global" not in output
    assert "set -euo pipefail" in output
    assert "skill_set='workflow'" in output
    assert 'skill-sets/${skill_set}.txt' in output


@pytest.mark.parametrize("profile", PROFILE_NAMES)
def test_install_accepts_each_named_profile(profile: str) -> None:
    output = render_just("install", str(TARGET_PROJECT), profile)

    assert f"target_dir='{TARGET_PROJECT}'" in output
    assert f"skill_set='{profile}'" in output
    assert "link-profile" in output
    assert PACKAGED_REPO_SOURCE not in output


def test_install_global_preserves_the_packaged_global_workflow() -> None:
    output = render_just("install-global")

    assert SYNC_REFERENCES in output
    assert PACKAGED_REPO_SOURCE in output
    assert "prune-retired" in output
    assert "link-profile" in output
    assert "record-installed" in output
    assert npx_commands(output, "add")
    assert all("--global" in command for command in npx_commands(output, "add"))


def test_install_all_adds_only_the_pinned_external_addy_profile_locally() -> None:
    output = render_just("install", str(TARGET_PROJECT), "all")

    assert read_external_profile(ADDY_EXTERNAL_PROFILE) == ADDY_SKILLS
    assert not read_profile("all") & ADDY_SKILLS
    assert ADDY_SOURCE in output
    assert str(ADDY_EXTERNAL_PROFILE) in output
    assert_addy_install_is_guarded_to_all(output)
    assert output.count(f"{NPX_SKILLS} add") == 1
    assert "external_skills" in output
    assert "combined_profile" not in output
    assert "--global" not in npx_commands(output, "add")[0]


def test_named_profiles_guard_external_addy_install_to_all() -> None:
    output = render_just("install", str(TARGET_PROJECT), "iterative-design")

    assert ADDY_SOURCE in output
    assert str(ADDY_EXTERNAL_PROFILE) in output
    assert_addy_install_is_guarded_to_all(output)
    assert output.count(f"{NPX_SKILLS} add") == 1


def test_uninstall_all_manages_the_external_addy_profile() -> None:
    output = render_just("uninstall", str(TARGET_PROJECT), "all")

    assert str(ADDY_EXTERNAL_PROFILE) in output
    assert "remove-locked-profile" in output
    assert '--lock "$target_dir/skills-lock.json"' in output
    assert "addyosmani/agent-skills" in output
    assert npx_commands(output, "ls") == []
    assert npx_commands(output, "remove") == []
    assert "--global" not in output


def test_install_rejects_an_unknown_profile_before_invoking_npx(
    tmp_path: Path,
) -> None:
    result = subprocess.run(
        ["just", "install", str(tmp_path), "not-a-profile"],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    assert result.returncode != 0
    assert "Unknown skill set: not-a-profile" in result.stdout
    assert "workflow" in result.stdout
    assert "npx skills" not in result.stdout


def test_install_requires_a_target_project() -> None:
    result = subprocess.run(
        ["just", "-n", "install"],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    assert result.returncode != 0
    assert "TARGET_DIR" in result.stdout.upper()


def test_install_rejects_a_missing_target_project(tmp_path: Path) -> None:
    missing_target = tmp_path / "missing-project"
    result = subprocess.run(
        ["just", "install", str(missing_target)],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    assert result.returncode != 0
    assert f"Target project is not a directory: {missing_target}" in result.stdout
    assert not missing_target.exists()


def test_profiles_partition_the_active_catalog() -> None:
    assert read_profile("workflow") == WORKFLOW_SKILLS
    assert read_profile("iterative-design") == ITERATIVE_DESIGN_SKILLS
    assert read_profile("applying-uml-and-patterns") == ITERATIVE_DESIGN_SKILLS
    assert read_profile("reverse-engineering") == REVERSE_ENGINEERING_SKILLS
    assert read_profile("all") == (
        WORKFLOW_SKILLS | ITERATIVE_DESIGN_SKILLS | REVERSE_ENGINEERING_SKILLS
    )


def test_install_packaged_alias_preserves_the_global_install() -> None:
    output = render_just("install-packaged")

    assert "pip install" not in output
    assert SYNC_REFERENCES in output
    assert "sync_shared_skill_runtime.py" not in output
    assert PACKAGED_REPO_SOURCE in output
    assert 'if [[ "$skill_set" == "all" ]]' in output
    assert "skill_set='workflow'" in output
    assert all("--global" in command for command in npx_commands(output, "add"))


def test_install_local_alias_matches_the_default_install() -> None:
    assert render_just("install-local", str(TARGET_PROJECT)) == render_just(
        "install", str(TARGET_PROJECT)
    )


@pytest.mark.parametrize(
    ("target", "args"),
    (
        ("install", (str(TARGET_PROJECT),)),
        ("install-global", ()),
        ("uninstall-global", ()),
        ("prune-retired", ()),
        ("prune-retired-legacy", ()),
    ),
)
def test_npx_can_bootstrap_skills_without_an_interactive_prompt(
    target: str, args: tuple[str, ...]
) -> None:
    output = render_just(target, *args)

    assert "npx skills" not in output
    assert NPX_SKILLS in output


def test_uninstall_targets_the_consumer_project_workflow_profile() -> None:
    output = render_just("uninstall", str(TARGET_PROJECT))

    assert npx_commands(output, "ls") == []
    assert npx_commands(output, "remove") == []
    assert "pip uninstall" not in output
    assert "skill_set='workflow'" in output
    assert 'skill-sets/${skill_set}.txt' in output
    assert "prune-retired-local" in output
    assert "unlink-profile" in output
    assert f'--source-dir "{SOURCE_SKILLS_DIR}"' in output
    assert f"target_dir='{TARGET_PROJECT}'" in output
    assert 'target_skills_dir="$target_dir/.agents/skills"' in output
    assert '--target-dir "$target_skills_dir"' in output
    assert "remove-locked-profile" in output
    assert "forget-profile" not in output
    assert "--global" not in output
    assert "set -euo pipefail" in output


def test_uninstall_global_preserves_owned_global_removal() -> None:
    output = render_just("uninstall-global")

    assert f"{NPX_SKILLS} ls -g --json" in output
    assert f'{NPX_SKILLS} remove "${{installed_skills[@]}}" --global' in output
    assert "prune-retired" in output
    assert "unlink-profile" in output
    assert "forget-profile" in output


def test_uninstall_local_alias_matches_the_default_uninstall() -> None:
    assert render_just("uninstall-local", str(TARGET_PROJECT)) == render_just(
        "uninstall", str(TARGET_PROJECT)
    )


def test_prune_retired_defaults_to_owned_skills_only() -> None:
    output = render_just("prune-retired")

    assert "select-retired" in output
    assert "--include-unowned" not in output
    assert f"{NPX_SKILLS} remove" in output
    assert "unlink-retired" in output
    assert "forget-retired" in output


def test_prune_retired_legacy_requires_the_explicit_alias() -> None:
    output = render_just("prune-retired-legacy")

    assert "select-retired" in output
    assert "unlink-retired" in output
    assert "--include-unowned" in output


def test_prune_retired_local_removes_only_source_linked_entries() -> None:
    output = render_just("prune-retired-local", str(TARGET_PROJECT))

    assert "unlink-retired" in output
    assert "--include-unowned" in output
    assert f'--source-dir "{SOURCE_SKILLS_DIR}"' in output
    assert f"target_dir='{TARGET_PROJECT}'" in output
    assert '--target-dir "$target_skills_dir"' in output
    assert npx_commands(output, "ls") == []
    assert npx_commands(output, "remove") == []


@pytest.mark.parametrize("profile", PROFILE_NAMES)
def test_uninstall_accepts_each_named_profile(profile: str) -> None:
    output = render_just("uninstall", str(TARGET_PROJECT), profile)

    assert f"target_dir='{TARGET_PROJECT}'" in output
    assert f"skill_set='{profile}'" in output
    assert "unlink-profile" in output


def test_skill_descriptions_with_yaml_indicator_text_are_quoted() -> None:
    for skill_file in (REPO_ROOT / "skills").glob("*/SKILL.md"):
        description_line = next(
            line
            for line in skill_file.read_text(encoding="utf-8").splitlines()
            if line.startswith("description: ")
        )
        value = description_line.removeprefix("description: ")
        assert ": " not in value or (
            len(value) >= 2
            and value[0] == value[-1]
            and value[0] in "\"'"
        ), skill_file


def test_validation_covers_the_consolidated_catalog() -> None:
    result = subprocess.run(
        ["just", "validate"],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    assert result.returncode == 0, result.stdout
    assert "Validated 29 skills" in result.stdout
