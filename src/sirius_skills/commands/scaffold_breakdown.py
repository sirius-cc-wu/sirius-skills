#!/usr/bin/env python3

import argparse
import importlib.util
import re
import sys
import json
from pathlib import Path


COMMAND_DIR = Path(__file__).resolve().parent
ASSETS_DIR = Path(__file__).resolve().parents[3] / "skills" / "breakdown" / "assets"
SLICE_PLANNING_TEMPLATE = ASSETS_DIR / "slice-planning-template.md"
SLICE_TRACEABILITY_TEMPLATE = ASSETS_DIR / "slice-traceability-template.md"
DEFAULT_BASE_DIR = Path("docs/features")
PLANNING_CONFIG_FILE = Path(".skills") / "planning.json"
PLANNING_DIR_FIELD = "planning_dir"
FEATURE_SLUG_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
SUBFEATURE_METADATA_FILE = ".subfeature-meta.json"
IMPACT_FILE = "impact-analysis.md"
SUBFEATURE_SCRIPT = (
    COMMAND_DIR / "manage_subfeatures.py"
)


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Scaffold increment-ready breakdown planning files for a canonical "
            "feature folder or a selected subfeature path."
        )
    )
    parser.add_argument(
        "target",
        help=(
            "Feature slug by default, or an explicit planning folder path such as "
            "docs/features/<feature>/subfeatures/<subfeature-id>"
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
    return parser.parse_args(argv)


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


def load_manage_subfeatures_module():
    spec = importlib.util.spec_from_file_location("manage_subfeatures", SUBFEATURE_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def format_code_list(items: list[str], empty: str) -> str:
    if not items:
        return f"- {empty}"
    return "\n".join(f"- `{item}`" for item in items)


def relative_to_cwd(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        text = str(path)
        if text.startswith("./"):
            return text[2:]
        return text


def resolve_subfeature_context(target_dir: Path) -> dict[str, object] | None:
    metadata_path = target_dir / SUBFEATURE_METADATA_FILE
    if not metadata_path.exists():
        return None

    manage_subfeatures = load_manage_subfeatures_module()
    metadata = manage_subfeatures.read_metadata(str(target_dir))
    feature_slug = str(metadata["parent_feature_slug"])
    canonical_feature_path = relative_to_cwd(target_dir.parent.parent)
    subfeature_id = str(metadata["subfeature_id"])
    subfeature_type = str(metadata["subfeature_type"])
    status = str(metadata["status"])
    affected_story_ids = [str(item) for item in metadata.get("affected_story_ids", [])]
    affected_slice_ids = [str(item) for item in metadata.get("affected_slice_ids", [])]
    affected_artifacts = [str(item) for item in metadata.get("affected_artifacts", [])]

    return {
        "feature_slug": feature_slug,
        "subfeature_id": subfeature_id,
        "subfeature_type": subfeature_type,
        "status": status,
        "canonical_feature_path": canonical_feature_path,
        "has_impact_analysis": (target_dir / IMPACT_FILE).exists(),
        "affected_story_ids": affected_story_ids,
        "affected_slice_ids": affected_slice_ids,
        "affected_artifacts": affected_artifacts,
    }


def render_subfeature_context_section(subfeature_context: dict[str, object]) -> str:
    story_lines = format_code_list(
        list(subfeature_context["affected_story_ids"]),
        "No affected story IDs were recorded yet. Refine `impact-analysis.md` before final review.",
    )
    slice_lines = format_code_list(
        list(subfeature_context["affected_slice_ids"]),
        "No affected canonical slice IDs were recorded yet.",
    )
    artifact_lines = format_code_list(
        list(subfeature_context["affected_artifacts"]),
        "No affected baseline artifacts were recorded yet.",
    )
    impact_status = (
        f"`{IMPACT_FILE}` is present and should drive the subfeature-local slice plan."
        if subfeature_context["has_impact_analysis"]
        else f"`{IMPACT_FILE}` is missing; add or regenerate it before planning review."
    )

    return (
        "## 0. Subfeature Context\n\n"
        f"- Parent feature: `{subfeature_context['feature_slug']}`\n"
        f"- Parent feature path: `{subfeature_context['canonical_feature_path']}`\n"
        f"- Subfeature ID: `{subfeature_context['subfeature_id']}`\n"
        f"- Subfeature type: `{subfeature_context['subfeature_type']}`\n"
        f"- Current subfeature status: `{subfeature_context['status']}`\n"
        f"- Impact input: {impact_status}\n\n"
        "### Affected Story IDs\n\n"
        f"{story_lines}\n\n"
        "### Affected Canonical Slice IDs\n\n"
        f"{slice_lines}\n\n"
        "### Affected Baseline Artifacts\n\n"
        f"{artifact_lines}\n"
    )


def render_slice_planning(
    feature_slug: str, subfeature_context: dict[str, object] | None = None
) -> str:
    template = load_template(SLICE_PLANNING_TEMPLATE)
    template = template.replace("- Feature:\n", f"- Feature: {feature_slug}\n", 1)
    if not subfeature_context:
        return template

    template = template.replace(
        "  - `discover.md`\n",
        "  - `discover.md`\n  - `impact-analysis.md`\n",
        1,
    )
    template = template.replace(
        "  - `user-stories.md`\n",
        f"  - parent `{subfeature_context['canonical_feature_path']}/user-stories.md`\n",
        1,
    )
    template = template.replace(
        "- Notes:\n",
        "- Notes:\n"
        f"  - This is subfeature-local breakdown for `{subfeature_context['subfeature_id']}` under parent feature `{subfeature_context['feature_slug']}`.\n"
        "  - Plan only the new or amended slices required by this subfeature.\n"
        "  - Keep this subfeature's `slice-planning.md` and `slice-traceability.md` as the execution-planning source of truth for the child capability.\n"
        "  - When a subfeature supersedes existing parent slices, record the affected baseline slice IDs in dependency or notes fields instead of reusing them as subfeature-local slice IDs.\n",
        1,
    )
    return template.replace(
        "## 1. Planning Scope\n\n",
        render_subfeature_context_section(subfeature_context)
        + "\n\n## 1. Planning Scope\n\n",
        1,
    )


def render_slice_traceability(
    subfeature_context: dict[str, object] | None = None
) -> str:
    template = load_template(SLICE_TRACEABILITY_TEMPLATE)
    if not subfeature_context:
        return template

    notes = (
        "## Subfeature Context\n\n"
        f"- Parent feature: `{subfeature_context['feature_slug']}`\n"
        f"- Subfeature ID: `{subfeature_context['subfeature_id']}`\n"
        f"- Subfeature type: `{subfeature_context['subfeature_type']}`\n"
        "- Use `Planned Slice IDs` for the new or amended slices defined by this subfeature.\n"
        "- Keep subfeature-local traceability in this folder instead of folding it back into parent feature breakdown docs.\n"
        "- Record superseded or narrowed parent slice IDs in `Notes`, not `Execution Slice IDs`.\n"
    )
    return template.replace("## Conventions\n\n", notes + "\n## Conventions\n\n", 1)


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
    subfeature_context = resolve_subfeature_context(target_dir)

    ensure_writable([slice_planning_path, slice_traceability_path], force=force)
    target_dir.mkdir(parents=True, exist_ok=True)

    slice_planning_path.write_text(
        render_slice_planning(label, subfeature_context=subfeature_context),
        encoding="utf-8",
    )
    slice_traceability_path.write_text(
        render_slice_traceability(subfeature_context=subfeature_context),
        encoding="utf-8",
    )
    return target_dir


def main(argv=None) -> int:
    args = parse_args(argv)
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
