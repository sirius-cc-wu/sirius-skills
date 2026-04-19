from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "install_local_skills.py"
SPEC = importlib.util.spec_from_file_location("install_local_skills", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def create_repo(tmp_path: Path, skills: list[str]) -> Path:
    repo_root = tmp_path / "repo"
    for skill in skills:
        skill_dir = repo_root / "skills" / skill
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(f"# {skill}\n", encoding="utf-8")
    return repo_root


def test_install_creates_symlinks_and_is_idempotent(tmp_path: Path) -> None:
    repo_root = create_repo(tmp_path, ["audit-artifacts", "guide-planning"])
    skills_home = tmp_path / "skills-home"

    MODULE.install_skills(repo_root, skills_home, ["audit-artifacts", "guide-planning"])
    MODULE.install_skills(repo_root, skills_home, ["audit-artifacts", "guide-planning"])

    audit_target = skills_home / "audit-artifacts"
    planning_target = skills_home / "guide-planning"
    assert audit_target.is_symlink()
    assert planning_target.is_symlink()
    assert audit_target.resolve() == repo_root / "skills" / "audit-artifacts"
    assert planning_target.resolve() == repo_root / "skills" / "guide-planning"


def test_install_refreshes_managed_symlink_target(tmp_path: Path) -> None:
    repo_root = create_repo(tmp_path, ["audit-artifacts"])
    skills_home = tmp_path / "skills-home"
    skills_home.mkdir()
    old_root = create_repo(tmp_path / "stale", ["audit-artifacts"])
    (skills_home / "audit-artifacts").symlink_to(
        old_root / "skills" / "audit-artifacts",
        target_is_directory=True,
    )

    MODULE.install_skills(repo_root, skills_home, ["audit-artifacts"])

    assert (skills_home / "audit-artifacts").resolve() == (
        repo_root / "skills" / "audit-artifacts"
    )


def test_install_rejects_non_symlink_collision(tmp_path: Path) -> None:
    repo_root = create_repo(tmp_path, ["audit-artifacts"])
    skills_home = tmp_path / "skills-home"
    (skills_home / "audit-artifacts").mkdir(parents=True)

    with pytest.raises(RuntimeError, match="Refusing to replace non-symlink entry"):
        MODULE.install_skills(repo_root, skills_home, ["audit-artifacts"])


def test_uninstall_removes_only_managed_symlinks(tmp_path: Path) -> None:
    repo_root = create_repo(tmp_path, ["audit-artifacts"])
    skills_home = tmp_path / "skills-home"
    MODULE.install_skills(repo_root, skills_home, ["audit-artifacts"])
    unrelated = skills_home / "personal-skill"
    unrelated.mkdir()

    MODULE.uninstall_skills(repo_root, skills_home, ["audit-artifacts"])

    assert not (skills_home / "audit-artifacts").exists()
    assert unrelated.is_dir()
