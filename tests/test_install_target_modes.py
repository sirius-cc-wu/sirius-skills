from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SYNC_RUNTIME = "python3 scripts/sync_shared_skill_runtime.py"
SYNC_REFERENCES = "python3 scripts/sync_shared_skill_references.py"
PACKAGED_ADD = 'npx skills add "'
PACKAGED_REPO_SOURCE = f'{PACKAGED_ADD}{REPO_ROOT}"'


def render_make(target: str) -> str:
    result = subprocess.run(
        ["make", "-n", target],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def test_install_target_keeps_packaged_sync() -> None:
    output = render_make("install")

    assert SYNC_RUNTIME in output
    assert SYNC_REFERENCES in output
    assert PACKAGED_REPO_SOURCE in output
    assert output.count("npx skills add") == 1
    assert "--skill audit-artifacts" in output
    assert "--skill execute-all-slices" in output


def test_install_packaged_alias_matches_install() -> None:
    output = render_make("install-packaged")

    assert SYNC_RUNTIME in output
    assert SYNC_REFERENCES in output
    assert PACKAGED_REPO_SOURCE in output
    assert output.count("npx skills add") == 1
    assert "--skill audit-artifacts" in output
    assert "--skill execute-all-slices" in output


def test_uninstall_alias_still_uses_packaged_flow() -> None:
    output = render_make("uninstall")

    assert "npx skills ls -g --json" in output
    assert "npx skills remove" in output
