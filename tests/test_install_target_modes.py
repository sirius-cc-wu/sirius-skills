from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SYNC_REFERENCES = "sirius_skills.commands.sync_shared_references"
PACKAGED_ADD = 'npx skills add "'
PACKAGED_REPO_SOURCE = f'{PACKAGED_ADD}{REPO_ROOT}"'
MANAGED_SKILLS = "simplify create-pr commit governance-update"


def render_just(target: str) -> str:
    result = subprocess.run(
        ["just", "-n", target],
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return result.stdout


def assert_only_supported_skills_are_managed(output: str) -> None:
    assert f'"{MANAGED_SKILLS}".split()' in output


def test_install_target_keeps_packaged_reference_sync() -> None:
    output = render_just("install")

    assert "pip install" not in output
    assert SYNC_REFERENCES in output
    assert "sync_shared_skill_runtime.py" not in output
    assert PACKAGED_REPO_SOURCE in output
    assert output.count("npx skills add") == 1
    assert_only_supported_skills_are_managed(output)


def test_install_packaged_alias_matches_install() -> None:
    output = render_just("install-packaged")

    assert "pip install" not in output
    assert SYNC_REFERENCES in output
    assert "sync_shared_skill_runtime.py" not in output
    assert PACKAGED_REPO_SOURCE in output
    assert output.count("npx skills add") == 1
    assert_only_supported_skills_are_managed(output)


def test_uninstall_alias_still_uses_packaged_flow() -> None:
    output = render_just("uninstall")

    assert "npx skills ls -g --json" in output
    assert "npx skills remove" in output
    assert "pip uninstall" not in output
    assert_only_supported_skills_are_managed(output)
