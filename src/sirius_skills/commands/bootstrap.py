#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any


DEFAULT_PLANNING_DIR = "docs/features"
DEFAULT_PROPOSAL_DIR = "docs/proposals"
DEFAULT_DESIGN_DIAGRAM_MODE = "embedded"
DEFAULT_SLICE_DIR = "slices"
DEFAULT_WORKFLOW = "TDD"
DEFAULT_AUTO_START_IMPLEMENTATION = True
DEFAULT_WIKI_DIR_NAME = "wiki"
BOOTSTRAP_AGENTS_START = "<!-- sirius-skills bootstrap wiki architecture start -->"
BOOTSTRAP_AGENTS_END = "<!-- sirius-skills bootstrap wiki architecture end -->"
VALID_DESIGN_DIAGRAM_MODES = ("embedded", "linked_svg")

DEFAULT_JIRA_CONVENTIONS = {
    "issue_sliceer": "jira",
    "id_pattern": r"^[A-Z][A-Z0-9]*-[0-9]+$",
    "branch_extract_pattern": r"^([A-Z][A-Z0-9]*-[0-9]+)-(.+)$",
    "commit_format": "{ID}: {summary}",
    "pr_title_format": "{ID}: {summary}",
    "issue_url_template": "https://jira.example.com/browse/{ID}",
}
DEFAULT_SLICE_NAMING_CONVENTIONS = {
    "slice_id_style": "scope_prefix",
    "slice_id_format": "{scope_prefix}-{capability_slug}",
    "slice_id_scope_precedence": "subfeature_then_feature",
    "slice_id_prefix_source": "slug_alias",
    "slice_id_prefix_guidance": (
        "Use a short lowercase alias derived from the feature or subfeature slug "
        "and avoid bare 'slice-*' IDs."
    ),
}


def load_scope_runtime_module():
    from sirius_skills.commands import scope_runtime
    return scope_runtime


SCOPE_RUNTIME = load_scope_runtime_module()


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or update sirius-skills project configuration files."
    )
    parser.add_argument(
        "--mode",
        choices=("default", "jira"),
        required=True,
        help="Configuration preset to apply.",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root where the .skills directory should be written.",
    )
    parser.add_argument(
        "--planning-dir",
        default=None,
        help=(
            "Planning directory for .skills/planning.json "
            f"(default: {DEFAULT_PLANNING_DIR})."
        ),
    )
    parser.add_argument(
        "--proposal-dir",
        default=None,
        help=(
            "Proposal directory for .skills/planning.json "
            f"(default: {DEFAULT_PROPOSAL_DIR})."
        ),
    )
    parser.add_argument(
        "--design-diagram-mode",
        choices=VALID_DESIGN_DIAGRAM_MODES,
        default=None,
        help=(
            "Diagram output mode for design artifacts in .skills/planning.json "
            f"(default: {DEFAULT_DESIGN_DIAGRAM_MODE})."
        ),
    )
    parser.add_argument(
        "--slice-dir",
        default=None,
        help=f"Slice directory for .skills/execution.json (default: {DEFAULT_SLICE_DIR}).",
    )
    parser.add_argument(
        "--workflow",
        default=None,
        help=f"Preferred workflow for .skills/execution.json (default: {DEFAULT_WORKFLOW}).",
    )
    parser.add_argument(
        "--auto-start-implementation",
        action=argparse.BooleanOptionalAction,
        default=None,
        help=(
            "Whether guide-execution should auto-advance from blueprint_ready into "
            "execution_ready and begin implementation."
        ),
    )
    parser.add_argument(
        "--issue-url-template",
        default=None,
        help="Issue URL template for jira mode.",
    )
    parser.add_argument(
        "--wiki",
        action=argparse.BooleanOptionalAction,
        default=False,
        help=(
            "Create a lightweight wiki scaffold next to the planning feature "
            "directory, with features, concepts, concepts/architecture, index.md, "
            "and log.md."
        ),
    )
    return parser.parse_args(argv)


def load_json_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc.msg}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object in {path}.")
    return data


def write_json_file(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def write_text_file_if_missing(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def derive_wiki_dir(planning_dir: str) -> str:
    planning_path = PurePosixPath(planning_dir)
    parent = planning_path.parent
    if str(parent) in {"", "."}:
        return DEFAULT_WIKI_DIR_NAME
    return str(parent / DEFAULT_WIKI_DIR_NAME)


def inherited_or_default(
    existing: dict[str, Any], key: str, override: Any, default: Any
) -> Any:
    if override is not None:
        return override
    return existing.get(key, default)


def iter_scope_chain_for_target(target_root: Path) -> list[Path]:
    target_root = target_root.resolve()
    repo_root = SCOPE_RUNTIME.find_repo_root(target_root) or target_root
    chain: list[Path] = []

    current = target_root
    while True:
        chain.append(current)
        if current == repo_root or current.parent == current:
            break
        current = current.parent

    ordered = list(reversed(chain))
    scope_chain: list[Path] = []
    for candidate in ordered:
        if (
            candidate == repo_root
            or candidate == target_root
            or (candidate / ".skills" / "planning.json").exists()
        ):
            scope_chain.append(candidate)
    return scope_chain


def load_merged_config_for_target(target_root: Path, filename: str) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for scope_root in iter_scope_chain_for_target(target_root):
        config_path = scope_root / ".skills" / filename
        merged.update(load_json_file(config_path))
    return merged


def build_planning_config(
    existing: dict[str, Any],
    planning_dir: str | None,
    proposal_dir: str | None,
    design_diagram_mode: str | None,
) -> dict[str, Any]:
    updated = dict(existing)
    updated["planning_dir"] = inherited_or_default(
        existing, "planning_dir", planning_dir, DEFAULT_PLANNING_DIR
    )
    updated["proposal_dir"] = inherited_or_default(
        existing, "proposal_dir", proposal_dir, DEFAULT_PROPOSAL_DIR
    )
    updated["design_diagram_mode"] = inherited_or_default(
        existing,
        "design_diagram_mode",
        design_diagram_mode,
        DEFAULT_DESIGN_DIAGRAM_MODE,
    )
    return updated


def build_execution_config(
    existing: dict[str, Any],
    slice_dir: str | None,
    workflow: str | None,
    auto_start_implementation: bool | None,
) -> dict[str, Any]:
    updated = dict(existing)
    updated["slice_dir"] = inherited_or_default(
        existing, "slice_dir", slice_dir, DEFAULT_SLICE_DIR
    )
    updated["preferred_workflow"] = inherited_or_default(
        existing, "preferred_workflow", workflow, DEFAULT_WORKFLOW
    )
    updated["auto_start_implementation"] = inherited_or_default(
        existing,
        "auto_start_implementation",
        auto_start_implementation,
        DEFAULT_AUTO_START_IMPLEMENTATION,
    )
    return updated


def build_conventions_config(
    existing: dict[str, Any], mode: str, issue_url_template: str | None
) -> dict[str, Any]:
    updated = dict(existing)
    for key, value in DEFAULT_SLICE_NAMING_CONVENTIONS.items():
        updated.setdefault(key, value)
    if mode == "jira":
        updated.update(DEFAULT_JIRA_CONVENTIONS)
        updated["issue_url_template"] = (
            issue_url_template or updated["issue_url_template"]
        )
    return updated


def scaffold_wiki(
    repo_root: Path, planning_dir: str, proposal_dir: str, slice_dir: str
) -> None:
    wiki_dir = repo_root / Path(derive_wiki_dir(planning_dir))
    (wiki_dir / "features").mkdir(parents=True, exist_ok=True)
    (wiki_dir / "concepts").mkdir(parents=True, exist_ok=True)
    (wiki_dir / "concepts" / "architecture").mkdir(parents=True, exist_ok=True)

    index_content = f"""# Wiki Index

This wiki is the repository's synthesized knowledge layer. Read it before
re-deriving answers from raw planning artifacts or upstream references.

It is intentionally separate from `{planning_dir}/`, `{proposal_dir}/`, and
`{slice_dir}/`, which remain the canonical planning and execution sources of
truth.

## Architecture

| Page | Summary | Main sources |
|---|---|---|

## Features

| Page | Summary | Main sources |
|---|---|---|

## Concepts

| Page | Summary | Main sources |
|---|---|---|

## Notes

- Add feature pages as understanding changes or implementation completes.
- Add concept pages only when multiple feature pages need the same
  cross-cutting synthesis.
"""
    log_content = """# Wiki Log

Append-only record of wiki maintenance.

Use entries like `## [YYYY-MM-DD] operation | subject` so the log stays
grep-friendly.
"""

    write_text_file_if_missing(wiki_dir / "index.md", index_content)
    write_text_file_if_missing(wiki_dir / "log.md", log_content)


def render_agents_wiki_section(wiki_dir: str) -> str:
    architecture_dir = f"{wiki_dir}/concepts/architecture/"
    concepts_dir = f"{wiki_dir}/concepts/"
    return f"""{BOOTSTRAP_AGENTS_START}
## Wiki architecture pages

When this repository uses the wiki scaffold, keep implementation-sourced or
code-only architecture/design pages under `{architecture_dir}`.

Use `{concepts_dir}` for broader cross-cutting concept pages, pattern surveys,
or reference-informed synthesis. Keep `index.md` clear about the distinction so
readers can tell whether a page is code-only architecture or broader concept
material.
{BOOTSTRAP_AGENTS_END}
"""


def patch_agents_for_wiki(repo_root: Path, planning_dir: str) -> bool:
    agents_path = repo_root / "AGENTS.md"
    if not agents_path.exists():
        return False

    contents = agents_path.read_text(encoding="utf-8")
    section = render_agents_wiki_section(derive_wiki_dir(planning_dir)).strip()
    pattern = re.compile(
        rf"{re.escape(BOOTSTRAP_AGENTS_START)}.*?{re.escape(BOOTSTRAP_AGENTS_END)}",
        re.DOTALL,
    )

    if pattern.search(contents):
        updated = pattern.sub(section, contents)
    else:
        separator = "" if contents.endswith("\n\n") else "\n\n"
        updated = f"{contents.rstrip()}{separator}{section}\n"

    if updated == contents:
        return False

    agents_path.write_text(updated, encoding="utf-8")
    return True


def main(argv=None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).expanduser().resolve()
    skills_dir = repo_root / ".skills"

    planning_path = skills_dir / "planning.json"
    execution_path = skills_dir / "execution.json"
    conventions_path = skills_dir / "conventions.json"

    try:
        planning_existing = load_merged_config_for_target(repo_root, "planning.json")
        execution_existing = load_merged_config_for_target(repo_root, "execution.json")
        conventions_existing = load_merged_config_for_target(
            repo_root, "conventions.json"
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    planning_config = build_planning_config(
        planning_existing,
        args.planning_dir,
        args.proposal_dir,
        args.design_diagram_mode,
    )
    execution_config = build_execution_config(
        execution_existing,
        args.slice_dir,
        args.workflow,
        args.auto_start_implementation,
    )
    conventions_config = build_conventions_config(
        conventions_existing, args.mode, args.issue_url_template
    )

    write_json_file(planning_path, planning_config)
    write_json_file(execution_path, execution_config)
    write_json_file(conventions_path, conventions_config)

    if args.wiki:
        wiki_dir = derive_wiki_dir(planning_config["planning_dir"])
        scaffold_wiki(
            repo_root,
            planning_config["planning_dir"],
            planning_config["proposal_dir"],
            execution_config["slice_dir"],
        )
        agents_updated = patch_agents_for_wiki(repo_root, planning_config["planning_dir"])

    message = (
        "Configured .skills/planning.json, .skills/execution.json, and "
        f".skills/conventions.json using '{args.mode}' mode."
    )
    if args.wiki:
        message += f" Created {wiki_dir}/ scaffold."
        if agents_updated:
            message += " Updated AGENTS.md wiki guidance."

    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
