#!/usr/bin/env python3

"""
Quick validation logic for skills.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any


EXCLUDE_DIRS = {".git", "__pycache__", "node_modules"}
ROOT_EXCLUDE_DIRS = {"evals"}


def should_skip_path(directory: Path, path: Path) -> bool:
    relative_parts = path.relative_to(directory).parts
    if not relative_parts:
        return False
    if relative_parts[0] in ROOT_EXCLUDE_DIRS:
        return True
    return any(part in EXCLUDE_DIRS for part in relative_parts[:-1])


def read_text_for_validation(path: Path) -> str:
    return path.read_bytes().decode("utf-8", errors="replace")


def get_all_files(directory: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(directory.rglob("*")):
        if should_skip_path(directory, path):
            continue
        if path.is_file():
            files.append(path)
    return files


def validate_skill(skill_path: str | Path) -> dict[str, Any]:
    skill_dir = Path(skill_path)
    if not skill_dir.exists() or not skill_dir.is_dir():
        return {"valid": False, "message": f"Path is not a directory: {skill_dir}"}

    skill_md_path = skill_dir / "SKILL.md"
    if not skill_md_path.exists():
        return {"valid": False, "message": "SKILL.md not found"}

    content = read_text_for_validation(skill_md_path)
    if not content.startswith("---"):
        return {"valid": False, "message": "No YAML frontmatter found"}

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {"valid": False, "message": "Invalid frontmatter format"}

    frontmatter_text = parts[1]
    frontmatter_lines = [
        line.strip() for line in frontmatter_text.splitlines() if line.strip()
    ]
    allowed_keys = {"name", "description"}
    for line in frontmatter_lines:
        if ":" not in line:
            return {
                "valid": False,
                "message": f"Invalid frontmatter line: {line}",
            }
        key = line.split(":", 1)[0].strip()
        if key not in allowed_keys:
            return {
                "valid": False,
                "message": (
                    f"Unexpected frontmatter key: {key}. "
                    "Only name and description are allowed."
                ),
            }

    name_match = re.search(r"^name:\s*(.+)$", frontmatter_text, re.MULTILINE)
    desc_match = re.search(
        r"""^description:\s*(?:'([^']*)'|"([^"]*)"|(.+))$""",
        frontmatter_text,
        re.MULTILINE,
    )

    if not name_match:
        return {"valid": False, "message": 'Missing "name" in frontmatter'}
    if not desc_match:
        return {
            "valid": False,
            "message": "Description must be a single-line string: description: ...",
        }

    name = name_match.group(1).strip()
    description = next(
        (group for group in desc_match.groups() if group is not None),
        "",
    ).strip()

    if not name:
        return {"valid": False, "message": "Name cannot be empty"}
    if len(name) > 64:
        return {
            "valid": False,
            "message": f"Name is too long ({len(name)} characters). Maximum is 64.",
        }
    if "\n" in description:
        return {
            "valid": False,
            "message": "Description must be a single line (no newlines)",
        }
    if not description:
        return {"valid": False, "message": "Description cannot be empty"}

    if not re.fullmatch(r"[a-z0-9-]+", name):
        return {"valid": False, "message": f'Name "{name}" should be hyphen-case'}
    if name.startswith("-") or name.endswith("-") or "--" in name:
        return {
            "valid": False,
            "message": (
                f'Name "{name}" cannot start or end with a hyphen '
                "or contain consecutive hyphens"
            ),
        }

    if len(description) > 1024:
        return {"valid": False, "message": "Description is too long (max 1024)"}
    if "<" in description or ">" in description:
        return {
            "valid": False,
            "message": "Description cannot contain angle brackets (< or >)",
        }

    for file_path in get_all_files(skill_dir):
        file_content = read_text_for_validation(file_path)
        if "TODO:" in file_content:
            return {
                "valid": True,
                "message": "Skill has unresolved TODOs",
                "warning": f"Found unresolved TODO in {file_path.relative_to(skill_dir)}",
            }

    return {"valid": True, "message": "Skill is valid!"}


def main() -> int:
    args = sys.argv[1:]
    if len(args) != 1:
        print("Usage: python validate_skill.py <skill_directory>")
        return 1

    skill_dir_arg = args[0]
    if ".." in skill_dir_arg:
        print("❌ Error: Path traversal detected in skill directory path.", file=sys.stderr)
        return 1

    result = validate_skill(Path(skill_dir_arg).resolve())
    if result.get("warning"):
        print(f"⚠️  {result['warning']}", file=sys.stderr)
    if result["valid"]:
        print(f"✅ {result['message']}")
        return 0

    print(f"❌ {result['message']}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
