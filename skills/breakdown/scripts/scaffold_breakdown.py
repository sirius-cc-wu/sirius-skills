#!/usr/bin/env python3

import argparse
import re
import sys
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ASSETS_DIR = SKILL_DIR / "assets"
SLICE_PLANNING_TEMPLATE = ASSETS_DIR / "slice-planning-template.md"
SLICE_TRACEABILITY_TEMPLATE = ASSETS_DIR / "slice-traceability-template.md"
DEFAULT_BASE_DIR = Path("docs/features")
PLANNING_CONFIG_FILE = Path(".skills") / "planning.json"
PLANNING_DIR_FIELD = "planning_dir"
FEATURE_SLUG_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Scaffold increment-ready breakdown planning files for a canonical "
            "feature folder or a selected change packet path."
        )
    )
    parser.add_argument(
        "target",
        help=(
            "Feature slug by default, or an explicit planning folder path such as "
            "docs/features/<feature>/changes/<change-id>"
        ),
    )
    parser.add_argument(
        "--base-dir",
        help=(
            "Base directory for feature planning folders. Defaults to the "
            f"'{PLANNING_DIR_FIELD}' value in .skills/planning.json when present, "
            f"otherwise {DEFAULT_BASE_DIR}. Relative paths are resolved from the "
            "current working directory."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing slice-planning.md and slice-traceability.md files.",
    )
    return parser.parse_args()


def validate_feature_slug(value: str) -> str:
    slug = value.strip()
    if not slug:
        raise ValueError("Feature slug cannot be empty.")
    if "/" in slug or "\\" in slug:
        raise ValueError("Feature slug must not contain path separators.")
    if not FEATURE_SLUG_PATTERN.fullmatch(slug):
        raise ValueError(
            "Feature slug may contain only letters, numbers, dot, underscore, and hyphen."
        )
    return slug


def resolve_base_dir(value: str) -> Path:
    base_dir = Path(value).expanduser()
    if not str(base_dir).strip():
        raise ValueError("Base directory cannot be empty.")
    normalized = str(base_dir).rstrip("/")
    if normalized in {".", "./"}:
        raise ValueError("Base directory cannot be the repository root.")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    base_dir = Path(normalized)
    if base_dir.is_absolute():
        return base_dir
    return Path.cwd() / base_dir


def load_planning_config() -> dict[str, str]:
    if not PLANNING_CONFIG_FILE.exists():
        return {}

    try:
        config = json.loads(PLANNING_CONFIG_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("Planning config is not valid JSON.") from exc

    if not isinstance(config, dict):
        raise ValueError("Planning config must be a JSON object.")

    value = config.get(PLANNING_DIR_FIELD)
    if value is None:
        return {}
    if not isinstance(value, str):
        raise ValueError(
            f"Planning config field '{PLANNING_DIR_FIELD}' must be a string."
        )
    return {PLANNING_DIR_FIELD: value}


def resolve_default_base_dir() -> Path:
    config = load_planning_config()
    configured_dir = config.get(PLANNING_DIR_FIELD, str(DEFAULT_BASE_DIR))
    return resolve_base_dir(configured_dir)


def resolve_target_dir(target: str, base_dir: Path) -> Path:
    stripped = target.strip()
    if not stripped:
        raise ValueError("Target cannot be empty.")
    if "/" in stripped or "\\" in stripped:
        return resolve_base_dir(stripped)
    return base_dir / validate_feature_slug(stripped)


def load_template(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    return path.read_text(encoding="utf-8")


def render_slice_planning(feature_slug: str) -> str:
    template = load_template(SLICE_PLANNING_TEMPLATE)
    return template.replace("- Feature:\n", f"- Feature: {feature_slug}\n", 1)


def render_slice_traceability() -> str:
    return load_template(SLICE_TRACEABILITY_TEMPLATE)


def ensure_writable(paths: list[Path], force: bool) -> None:
    if force:
        return
    existing = [str(path) for path in paths if path.exists()]
    if existing:
        raise FileExistsError(
            "Refusing to overwrite existing files: " + ", ".join(existing)
        )


def scaffold(target_dir: Path, label: str, force: bool) -> Path:
    slice_planning_path = target_dir / "slice-planning.md"
    slice_traceability_path = target_dir / "slice-traceability.md"

    ensure_writable([slice_planning_path, slice_traceability_path], force=force)
    target_dir.mkdir(parents=True, exist_ok=True)

    slice_planning_path.write_text(render_slice_planning(label), encoding="utf-8")
    slice_traceability_path.write_text(render_slice_traceability(), encoding="utf-8")
    return target_dir


def main() -> int:
    args = parse_args()
    try:
        base_dir = (
            resolve_base_dir(args.base_dir)
            if args.base_dir is not None
            else resolve_default_base_dir()
        )
        target_dir = resolve_target_dir(args.target, base_dir)
        label = target_dir.name if ("/" in args.target or "\\" in args.target) else validate_feature_slug(args.target)
        target_dir = scaffold(target_dir, label, force=args.force)
    except (FileExistsError, FileNotFoundError, OSError, ValueError) as exc:
        print(f"Failure: {exc}", file=sys.stderr)
        return 1

    print(f"Success: scaffolded increment-ready breakdown files in {target_dir}")
    print(f"- {target_dir / 'slice-planning.md'}")
    print(f"- {target_dir / 'slice-traceability.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
