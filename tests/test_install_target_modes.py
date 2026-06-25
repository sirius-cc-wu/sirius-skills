from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SYNC_REFERENCES = "sirius sync-shared-references"
PACKAGED_ADD = 'npx skills add "'
PACKAGED_REPO_SOURCE = f'{PACKAGED_ADD}{REPO_ROOT}"'


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


def test_install_target_keeps_packaged_reference_sync() -> None:
    output = render_just("install")

    assert "python3 -m pip install -e ." in output
    assert SYNC_REFERENCES in output
    assert "sync_shared_skill_runtime.py" not in output
    assert PACKAGED_REPO_SOURCE in output
    assert output.count("npx skills add") == 1
    assert "audit-artifacts" in output
    assert "autoplan" in output
    assert "learn" in output
    assert "ship" in output
    assert "ship-slice" in output


def test_install_packaged_alias_matches_install() -> None:
    output = render_just("install-packaged")

    assert "python3 -m pip install -e ." in output
    assert SYNC_REFERENCES in output
    assert "sync_shared_skill_runtime.py" not in output
    assert PACKAGED_REPO_SOURCE in output
    assert output.count("npx skills add") == 1
    assert "audit-artifacts" in output
    assert "autoplan" in output
    assert "learn" in output
    assert "ship" in output
    assert "ship-slice" in output


def test_uninstall_alias_still_uses_packaged_flow() -> None:
    output = render_just("uninstall")

    assert "npx skills ls -g --json" in output
    assert "npx skills remove" in output
    assert "python3 -m pip uninstall -y sirius-skills" in output
