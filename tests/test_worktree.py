from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

import psutil


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from sirius_skills.commands import worktree
from sirius_skills.lib.workflow_runtime import record_worktree, worktree_pool_root


def init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init", "--quiet"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Copilot Test"], cwd=root, check=True)
    subprocess.run(
        ["git", "config", "user.email", "copilot@example.test"],
        cwd=root,
        check=True,
    )


def git_commit_all(root: Path, message: str) -> None:
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "--quiet", "-m", message], cwd=root, check=True)


def test_worktree_get_return_and_reuse(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    init_git_repo(tmp_path)

    config = worktree.load_worktree_config(tmp_path)
    assert config.worktree_root == tmp_path.parent / f"{tmp_path.name}.worktrees"

    (tmp_path / "baseline.txt").write_text("baseline\n", encoding="utf-8")
    git_commit_all(tmp_path, "baseline")

    assert worktree.main(["get"]) == 0
    first_path = Path(capsys.readouterr().out.strip())
    assert first_path.is_dir()
    assert first_path.parent == config.worktree_root
    assert first_path.name == "1"

    assert worktree.main(["status"]) == 0
    status_output = capsys.readouterr().out
    assert "leased" in status_output
    assert str(first_path) in status_output

    assert worktree.main(["return", str(first_path)]) == 0
    return_output = capsys.readouterr().out
    assert "Returned" in return_output

    assert worktree.main(["get"]) == 0
    second_path = Path(capsys.readouterr().out.strip())
    assert second_path == first_path


def test_worktree_pool_anchors_to_the_current_checkout_sibling(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    init_git_repo(tmp_path)

    (tmp_path / "baseline.txt").write_text("baseline\n", encoding="utf-8")
    git_commit_all(tmp_path, "baseline")

    linked = tmp_path.parent / f"{tmp_path.name}-linked"
    subprocess.run(["git", "worktree", "add", "--detach", str(linked), "HEAD"], cwd=tmp_path, check=True)

    config = worktree.load_worktree_config(linked)
    assert config.worktree_root == tmp_path.parent / f"{linked.name}.worktrees"


def test_worktree_pool_does_not_nest_inside_existing_pool() -> None:
    assert worktree_pool_root(Path("/base/main.worktrees/1/main")) == Path(
        "/base/main.worktrees"
    )


def test_worktree_status_marks_in_use_and_blocks_reuse(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    init_git_repo(tmp_path)

    (tmp_path / "baseline.txt").write_text("baseline\n", encoding="utf-8")
    git_commit_all(tmp_path, "baseline")

    assert worktree.main(["get"]) == 0
    first_path = Path(capsys.readouterr().out.strip())
    assert first_path.is_dir()

    assert worktree.main(["return", str(first_path)]) == 0
    capsys.readouterr()

    sleeper = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(10)"],
        cwd=first_path,
    )
    try:
        for _ in range(50):
            if psutil.pid_exists(sleeper.pid):
                break
            time.sleep(0.05)

        assert worktree.main(["status"]) == 0
        status_output = capsys.readouterr().out
        assert "in-use" in status_output or "you're here" in status_output
        assert str(sleeper.pid) in status_output or "python" in status_output.lower()

        assert worktree.main(["get"]) == 0
        second_path = Path(capsys.readouterr().out.strip())
        assert second_path != first_path
    finally:
        sleeper.terminate()
        try:
            sleeper.wait(timeout=5)
        except subprocess.TimeoutExpired:
            sleeper.kill()
            sleeper.wait(timeout=5)


def test_worktree_json_output(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    init_git_repo(tmp_path)

    (tmp_path / "baseline.txt").write_text("baseline\n", encoding="utf-8")
    git_commit_all(tmp_path, "baseline")

    assert worktree.main(["get", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["action"] == "worktree_created"
    assert payload["leased"] is True
    assert Path(payload["worktree_path"]).is_dir()

    assert worktree.main(["status", "--json"]) == 0
    status_payload = json.loads(capsys.readouterr().out)
    assert status_payload["count"] == 1
    assert status_payload["pool"][0]["status"] == "leased"
    assert status_payload["pool"][0]["source"] == "manual"


def test_worktree_status_includes_recorded_entries(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    init_git_repo(tmp_path)

    (tmp_path / "baseline.txt").write_text("baseline\n", encoding="utf-8")
    git_commit_all(tmp_path, "baseline")

    ship_path = worktree_pool_root(tmp_path) / "feature" / "ship-target" / tmp_path.name
    ship_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "worktree", "add", str(ship_path), "HEAD"], cwd=tmp_path, check=True)
    record_worktree(
        tmp_path,
        worktree_root=worktree_pool_root(tmp_path),
        pool_key="shared",
        name="ship-target",
        path=ship_path,
        branch="HEAD",
        source="external",
        lease_holder="target-123",
        leased=True,
    )

    assert worktree.main(["status"]) == 0
    status_output = capsys.readouterr().out
    assert "external" in status_output
    assert "target-123" in status_output
