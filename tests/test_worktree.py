from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from sirius_skills.commands import worktree


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


def test_worktree_pool_anchors_to_main_repo_root(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    init_git_repo(tmp_path)

    (tmp_path / "baseline.txt").write_text("baseline\n", encoding="utf-8")
    git_commit_all(tmp_path, "baseline")

    linked = tmp_path.parent / f"{tmp_path.name}-linked"
    subprocess.run(["git", "worktree", "add", "--detach", str(linked), "HEAD"], cwd=tmp_path, check=True)

    config = worktree.load_worktree_config(linked)
    assert config.worktree_root == tmp_path.parent / f"{tmp_path.name}.worktrees"


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
