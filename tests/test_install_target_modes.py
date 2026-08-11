from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SYNC_REFERENCES = "sirius_skills.commands.sync_shared_references"
NPX_SKILLS = "npx --yes skills"
PACKAGED_ADD = f'{NPX_SKILLS} add "'
PACKAGED_REPO_SOURCE = f'{PACKAGED_ADD}{REPO_ROOT}"'
PROFILE_NAMES = (
    "workflow",
    "iterative-design",
    "applying-uml-and-patterns",
    "reverse-engineering",
    "all",
)
WORKFLOW_SKILLS = {
    "simplify",
    "create-pr",
    "commit",
    "governance-update",
}
ITERATIVE_DESIGN_SKILLS = {
    "assess-development-input",
    "author-software-proposal",
    "iterative-up-analysis-design",
    "rewrite-technical-artifacts",
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
    "test-driven-implementation",
    "behavior-preserving-refactoring",
}
REVERSE_ENGINEERING_SKILLS = {
    "reverse-engineer-software-system",
    "survey-existing-system",
    "recover-system-behavior",
    "reconstruct-software-architecture",
    "reconcile-recovered-design",
    "rewrite-technical-artifacts",
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


def test_install_defaults_to_workflow_profile_and_keeps_reference_sync() -> None:
    output = render_just("install")

    assert "pip install" not in output
    assert SYNC_REFERENCES in output
    assert "sync_shared_skill_runtime.py" not in output
    assert PACKAGED_REPO_SOURCE in output
    assert output.count(f"{NPX_SKILLS} add") == 1
    assert "prune-retired" in output
    assert "link-profile" in output
    assert "record-installed" in output
    assert "set -euo pipefail" in output
    assert "skill_set='workflow'" in output
    assert 'skill-sets/${skill_set}.txt' in output


@pytest.mark.parametrize("profile", PROFILE_NAMES)
def test_install_accepts_each_named_profile(profile: str) -> None:
    output = render_just("install", profile)

    assert f"skill_set='{profile}'" in output
    assert PACKAGED_REPO_SOURCE in output


def test_install_rejects_an_unknown_profile_before_invoking_npx() -> None:
    result = subprocess.run(
        ["just", "install", "not-a-profile"],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    assert result.returncode != 0
    assert "Unknown skill set: not-a-profile" in result.stdout
    assert "workflow" in result.stdout
    assert "npx skills" not in result.stdout


def test_profiles_partition_the_active_catalog() -> None:
    assert read_profile("workflow") == WORKFLOW_SKILLS
    assert read_profile("iterative-design") == ITERATIVE_DESIGN_SKILLS
    assert read_profile("applying-uml-and-patterns") == ITERATIVE_DESIGN_SKILLS
    assert read_profile("reverse-engineering") == REVERSE_ENGINEERING_SKILLS
    assert read_profile("all") == (
        WORKFLOW_SKILLS | ITERATIVE_DESIGN_SKILLS | REVERSE_ENGINEERING_SKILLS
    )


def test_install_packaged_alias_matches_install() -> None:
    output = render_just("install-packaged")

    assert "pip install" not in output
    assert SYNC_REFERENCES in output
    assert "sync_shared_skill_runtime.py" not in output
    assert PACKAGED_REPO_SOURCE in output
    assert output.count(f"{NPX_SKILLS} add") == 1
    assert "skill_set='workflow'" in output


@pytest.mark.parametrize(
    "target", ("install", "uninstall", "prune-retired", "prune-retired-legacy")
)
def test_npx_can_bootstrap_skills_without_an_interactive_prompt(target: str) -> None:
    output = render_just(target)

    assert "npx skills" not in output
    assert NPX_SKILLS in output


def test_uninstall_defaults_to_workflow_profile() -> None:
    output = render_just("uninstall")

    assert f"{NPX_SKILLS} ls -g --json" in output
    assert f"{NPX_SKILLS} remove" in output
    assert f'{NPX_SKILLS} remove "${{installed_skills[@]}}" --global' in output
    assert f"xargs {NPX_SKILLS} remove" not in output
    remove_command = next(
        line.strip() for line in output.splitlines() if f"{NPX_SKILLS} remove" in line
    )
    assert "--agent" not in remove_command
    assert "pip uninstall" not in output
    assert "skill_set='workflow'" in output
    assert 'skill-sets/${skill_set}.txt' in output
    assert "prune-retired" in output
    assert "unlink-profile" in output
    assert "forget-profile" in output
    assert "set -euo pipefail" in output


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


@pytest.mark.parametrize("profile", PROFILE_NAMES)
def test_uninstall_accepts_each_named_profile(profile: str) -> None:
    output = render_just("uninstall", profile)

    assert f"skill_set='{profile}'" in output
    assert f"{NPX_SKILLS} ls -g --json" in output


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
