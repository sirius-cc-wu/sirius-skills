#!/usr/bin/env python3

import argparse
import re
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ASSETS_DIR = SKILL_DIR / "assets"
TASK_PLANNING_TEMPLATE = ASSETS_DIR / "task-planning-template.md"
TASK_TRACEABILITY_TEMPLATE = ASSETS_DIR / "task-traceability-template.md"
DEFAULT_BASE_DIR = Path("doc/specs/projects")
PROJECT_SLUG_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Scaffold increment-ready breakdown planning files for a project under "
            "doc/specs/projects/<project-slug>/ by default."
        )
    )
    parser.add_argument("project_slug", help="Project slug, for example: pm-tool")
    parser.add_argument(
        "--base-dir",
        default=str(DEFAULT_BASE_DIR),
        help=(
            "Base directory for project planning folders. Relative paths are "
            "resolved from the current working directory."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing task-planning.md and task-traceability.md files.",
    )
    return parser.parse_args()


def validate_project_slug(value: str) -> str:
    slug = value.strip()
    if not slug:
        raise ValueError("Project slug cannot be empty.")
    if "/" in slug or "\\" in slug:
        raise ValueError("Project slug must not contain path separators.")
    if not PROJECT_SLUG_PATTERN.fullmatch(slug):
        raise ValueError(
            "Project slug may contain only letters, numbers, dot, underscore, and hyphen."
        )
    return slug


def resolve_base_dir(value: str) -> Path:
    base_dir = Path(value).expanduser()
    if not str(base_dir).strip():
        raise ValueError("Base directory cannot be empty.")
    if base_dir.is_absolute():
        return base_dir
    return Path.cwd() / base_dir


def load_template(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    return path.read_text(encoding="utf-8")


def render_task_planning(project_slug: str) -> str:
    template = load_template(TASK_PLANNING_TEMPLATE)
    return template.replace("- Project:\n", f"- Project: {project_slug}\n", 1)


def render_task_traceability() -> str:
    return load_template(TASK_TRACEABILITY_TEMPLATE)


def ensure_writable(paths: list[Path], force: bool) -> None:
    if force:
        return
    existing = [str(path) for path in paths if path.exists()]
    if existing:
        raise FileExistsError(
            "Refusing to overwrite existing files: " + ", ".join(existing)
        )


def scaffold(project_slug: str, base_dir: Path, force: bool) -> Path:
    target_dir = base_dir / project_slug
    task_planning_path = target_dir / "task-planning.md"
    task_traceability_path = target_dir / "task-traceability.md"

    ensure_writable([task_planning_path, task_traceability_path], force=force)
    target_dir.mkdir(parents=True, exist_ok=True)

    task_planning_path.write_text(render_task_planning(project_slug), encoding="utf-8")
    task_traceability_path.write_text(render_task_traceability(), encoding="utf-8")
    return target_dir


def main() -> int:
    args = parse_args()
    try:
        project_slug = validate_project_slug(args.project_slug)
        base_dir = resolve_base_dir(args.base_dir)
        target_dir = scaffold(project_slug, base_dir, force=args.force)
    except (FileExistsError, FileNotFoundError, OSError, ValueError) as exc:
        print(f"Failure: {exc}", file=sys.stderr)
        return 1

    print(f"Success: scaffolded increment-ready breakdown files in {target_dir}")
    print(f"- {target_dir / 'task-planning.md'}")
    print(f"- {target_dir / 'task-traceability.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
