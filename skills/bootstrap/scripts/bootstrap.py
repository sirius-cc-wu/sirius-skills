#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


DEFAULT_PLANNING_DIR = "docs/features"
DEFAULT_PROPOSAL_DIR = "docs/proposals"
DEFAULT_DESIGN_DIAGRAM_MODE = "embedded"
DEFAULT_SLICE_DIR = "slices"
DEFAULT_WORKFLOW = "TDD"
DEFAULT_AUTO_START_IMPLEMENTATION = True
VALID_DESIGN_DIAGRAM_MODES = ("embedded", "linked_svg")

DEFAULT_JIRA_CONVENTIONS = {
    "issue_sliceer": "jira",
    "id_pattern": r"^[A-Z][A-Z0-9]*-[0-9]+$",
    "branch_extract_pattern": r"^([A-Z][A-Z0-9]*-[0-9]+)-(.+)$",
    "commit_format": "{ID}: {summary}",
    "pr_title_format": "{ID}: {summary}",
    "issue_url_template": "https://jira.example.com/browse/{ID}",
}


def parse_args() -> argparse.Namespace:
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
        default=DEFAULT_PLANNING_DIR,
        help=f"Planning directory for .skills/planning.json (default: {DEFAULT_PLANNING_DIR}).",
    )
    parser.add_argument(
        "--proposal-dir",
        default=DEFAULT_PROPOSAL_DIR,
        help=f"Proposal directory for .skills/planning.json (default: {DEFAULT_PROPOSAL_DIR}).",
    )
    parser.add_argument(
        "--design-diagram-mode",
        choices=VALID_DESIGN_DIAGRAM_MODES,
        default=DEFAULT_DESIGN_DIAGRAM_MODE,
        help=(
            "Diagram output mode for design artifacts in .skills/planning.json "
            f"(default: {DEFAULT_DESIGN_DIAGRAM_MODE})."
        ),
    )
    parser.add_argument(
        "--slice-dir",
        default=DEFAULT_SLICE_DIR,
        help=f"Slice directory for .skills/execution.json (default: {DEFAULT_SLICE_DIR}).",
    )
    parser.add_argument(
        "--workflow",
        default=DEFAULT_WORKFLOW,
        help=f"Preferred workflow for .skills/execution.json (default: {DEFAULT_WORKFLOW}).",
    )
    parser.add_argument(
        "--auto-start-implementation",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_AUTO_START_IMPLEMENTATION,
        help=(
            "Whether guide-execution should auto-advance from blueprint_ready into "
            "execution_ready and begin implementation."
        ),
    )
    parser.add_argument(
        "--issue-url-template",
        default=DEFAULT_JIRA_CONVENTIONS["issue_url_template"],
        help="Issue URL template for jira mode.",
    )
    return parser.parse_args()


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


def build_planning_config(
    existing: dict[str, Any],
    planning_dir: str,
    proposal_dir: str,
    design_diagram_mode: str,
) -> dict[str, Any]:
    updated = dict(existing)
    updated["planning_dir"] = planning_dir
    updated["proposal_dir"] = proposal_dir
    updated["design_diagram_mode"] = design_diagram_mode
    return updated


def build_execution_config(
    existing: dict[str, Any],
    slice_dir: str,
    workflow: str,
    auto_start_implementation: bool,
) -> dict[str, Any]:
    updated = dict(existing)
    updated["slice_dir"] = slice_dir
    updated["preferred_workflow"] = workflow
    updated["auto_start_implementation"] = auto_start_implementation
    return updated


def build_conventions_config(
    existing: dict[str, Any], mode: str, issue_url_template: str
) -> dict[str, Any]:
    updated = dict(existing)
    if mode == "jira":
        updated.update(DEFAULT_JIRA_CONVENTIONS)
        updated["issue_url_template"] = issue_url_template
    return updated


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).expanduser().resolve()
    skills_dir = repo_root / ".skills"

    planning_path = skills_dir / "planning.json"
    execution_path = skills_dir / "execution.json"
    conventions_path = skills_dir / "conventions.json"

    try:
        planning_existing = load_json_file(planning_path)
        execution_existing = load_json_file(execution_path)
        conventions_existing = load_json_file(conventions_path)
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

    print(
        "Configured .skills/planning.json, .skills/execution.json, and "
        f".skills/conventions.json using '{args.mode}' mode."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
