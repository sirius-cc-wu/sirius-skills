from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SYNC_RUNTIME = "python3 scripts/sync_shared_skill_runtime.py"
SYNC_REFERENCES = "python3 scripts/sync_shared_skill_references.py"
LOCAL_HELPER = "python3 scripts/install_local_skills.py install"
PACKAGED_ADD = 'npx skills add "'


def render_make(target: str) -> str:
    result = subprocess.run(
        ["make", "-n", target],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def test_install_local_skips_packaged_sync() -> None:
    output = render_make("install-local")

    assert LOCAL_HELPER in output
    assert SYNC_RUNTIME not in output
    assert SYNC_REFERENCES not in output


def test_install_packaged_keeps_packaged_sync() -> None:
    output = render_make("install-packaged")

    assert SYNC_RUNTIME in output
    assert SYNC_REFERENCES in output
    assert PACKAGED_ADD in output


def test_install_alias_still_uses_packaged_flow() -> None:
    output = render_make("install")

    assert SYNC_RUNTIME in output
    assert SYNC_REFERENCES in output
    assert PACKAGED_ADD in output
