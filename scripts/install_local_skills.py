#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Iterable, Sequence


DEFAULT_SKILLS_HOME = Path.home() / ".agents" / "skills"


def expected_skill_source(repo_root: Path, skill_name: str) -> Path:
    source = repo_root / "skills" / skill_name
    if not source.is_dir():
        raise RuntimeError(f"Managed skill source is missing: {source}")
    return source


def same_symlink_target(path: Path, expected: Path) -> bool:
    if not path.is_symlink():
        return False
    try:
        return path.resolve(strict=False) == expected.resolve()
    except OSError:
        return False


def ensure_skill_home(skills_home: Path) -> None:
    skills_home.mkdir(parents=True, exist_ok=True)


def install_skills(repo_root: Path, skills_home: Path, skill_names: Sequence[str]) -> None:
    ensure_skill_home(skills_home)
    for skill_name in skill_names:
        source = expected_skill_source(repo_root, skill_name)
        target = skills_home / skill_name

        if same_symlink_target(target, source):
            continue
        if target.is_symlink():
            target.unlink()
        elif target.exists():
            raise RuntimeError(
                f"Refusing to replace non-symlink entry for managed skill '{skill_name}': {target}"
            )

        target.symlink_to(source, target_is_directory=True)


def uninstall_skills(repo_root: Path, skills_home: Path, skill_names: Sequence[str]) -> None:
    del repo_root
    if not skills_home.exists():
        return

    for skill_name in skill_names:
        target = skills_home / skill_name
        if not target.exists() and not target.is_symlink():
            continue
        if not target.is_symlink():
            raise RuntimeError(
                f"Refusing to remove non-symlink entry for managed skill '{skill_name}': {target}"
            )
        target.unlink()


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or remove source-linked local skill symlinks."
    )
    parser.add_argument("mode", choices=("install", "uninstall"))
    parser.add_argument(
        "skills",
        nargs="+",
        help="Managed skill names to link or unlink.",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root containing the managed skills tree.",
    )
    parser.add_argument(
        "--skills-home",
        default=os.environ.get("SKILLS_HOME", str(DEFAULT_SKILLS_HOME)),
        help="Agent skill-home directory to populate.",
    )
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    repo_root = Path(args.repo_root).resolve()
    skills_home = Path(args.skills_home).expanduser().resolve()
    skill_names = list(dict.fromkeys(args.skills))

    try:
        if args.mode == "install":
            install_skills(repo_root, skills_home, skill_names)
        else:
            uninstall_skills(repo_root, skills_home, skill_names)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
