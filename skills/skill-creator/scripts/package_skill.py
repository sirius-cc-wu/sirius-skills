#!/usr/bin/env python3

"""
Skill packager - creates a distributable .skill file from a skill folder.

Usage:
    python package_skill.py <path/to/skill-folder> [output-directory]
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

from validate_skill import validate_skill


EXCLUDE_DIRS = {".git", "__pycache__", "node_modules"}
ROOT_EXCLUDE_DIRS = {"evals"}
EXCLUDE_FILE_NAMES = {".DS_Store"}
EXCLUDE_FILE_SUFFIXES = {".pyc"}


def should_exclude(skill_path: Path, path: Path, output_file: Path) -> bool:
    if path == output_file:
        return True
    relative_parts = path.relative_to(skill_path).parts
    if relative_parts and relative_parts[0] in ROOT_EXCLUDE_DIRS:
        return True
    if any(part in EXCLUDE_DIRS for part in relative_parts):
        return True
    if path.name in EXCLUDE_FILE_NAMES:
        return True
    if path.is_file() and path.suffix in EXCLUDE_FILE_SUFFIXES:
        return True
    return False


def write_package(skill_path: Path, output_file: Path) -> None:
    with zipfile.ZipFile(output_file, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(skill_path.rglob("*")):
            if should_exclude(skill_path, path, output_file):
                continue
            archive.write(path, arcname=path.relative_to(skill_path).as_posix())


def main() -> int:
    args = sys.argv[1:]
    if len(args) < 1:
        print("Usage: python package_skill.py <path/to/skill-folder> [output-directory]")
        return 1

    skill_path_arg = args[0]
    output_dir_arg = args[1] if len(args) > 1 else None

    if ".." in skill_path_arg or (output_dir_arg and ".." in output_dir_arg):
        print("❌ Error: Path traversal detected in arguments.", file=sys.stderr)
        return 1

    skill_path = Path(skill_path_arg).resolve()
    output_dir = Path(output_dir_arg).resolve() if output_dir_arg else Path.cwd()
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"❌ Error packaging: {exc}", file=sys.stderr)
        return 1
    if not output_dir.is_dir():
        print(
            f"❌ Error packaging: Output directory is not a directory: {output_dir}",
            file=sys.stderr,
        )
        return 1

    skill_name = skill_path.name

    print("🔍 Validating skill...")
    result = validate_skill(skill_path)
    if not result["valid"]:
        print(f"❌ Validation failed: {result['message']}", file=sys.stderr)
        return 1

    if result.get("warning"):
        print(f"⚠️  {result['warning']}", file=sys.stderr)
        print("Please resolve all TODOs before packaging.")
        return 1

    print("✅ Skill is valid!")
    output_file = output_dir / f"{skill_name}.skill"

    try:
        write_package(skill_path, output_file)
    except (OSError, zipfile.BadZipFile) as exc:
        print(f"❌ Error packaging: {exc}", file=sys.stderr)
        return 1

    print(f"✅ Successfully packaged skill to: {output_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
