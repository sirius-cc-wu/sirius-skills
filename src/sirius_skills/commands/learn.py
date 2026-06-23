#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable, Sequence


from sirius_skills.paths import package_root
from sirius_skills.lib.workflow_runtime.learnings import query_learnings, update_learning_state  # noqa: E402


REPO_ROOT = package_root()
DEFAULT_LEARNINGS_PATH = Path(".skills/learnings.jsonl")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query and curate durable repo-scoped workflow learnings."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    query_parser = subparsers.add_parser("query", help="Query learnings for one scope.")
    query_parser.add_argument("scope", help="Scope identifier to match exactly.")
    query_parser.add_argument(
        "--skill",
        default=None,
        help="Optional skill name filter.",
    )
    query_parser.add_argument(
        "--state",
        action="append",
        dest="states",
        default=None,
        help="Repeatable learning state filter.",
    )
    query_parser.add_argument(
        "--json",
        action="store_true",
        help="Render machine-readable output.",
    )

    export_parser = subparsers.add_parser(
        "export",
        help="Export filtered learnings for one scope.",
    )
    export_parser.add_argument("scope", help="Scope identifier to match exactly.")
    export_parser.add_argument(
        "--skill",
        default=None,
        help="Optional skill name filter.",
    )
    export_parser.add_argument(
        "--state",
        action="append",
        dest="states",
        default=None,
        help="Repeatable learning state filter.",
    )
    export_parser.add_argument(
        "--json",
        action="store_true",
        help="Render machine-readable output.",
    )

    for name, help_text in (
        ("promote", "Promote one learning to the active set."),
        ("prune", "Mark one learning as pruned."),
    ):
        state_parser = subparsers.add_parser(name, help=help_text)
        state_parser.add_argument("learning_id", help="Learning record identifier.")
        state_parser.add_argument(
            "--json",
            action="store_true",
            help="Render machine-readable output.",
        )

    parser.add_argument(
        "--repo-root",
        default=str(REPO_ROOT),
        help="Repository root used to resolve the learnings path.",
    )
    parser.add_argument(
        "--learnings-path",
        default=None,
        help="Optional override for the learnings file path.",
    )
    return parser.parse_args(argv)


def resolve_learnings_path(repo_root: Path, explicit_path: str | None) -> Path:
    relative = Path(explicit_path) if explicit_path else DEFAULT_LEARNINGS_PATH
    return relative if relative.is_absolute() else repo_root / relative


def normalize_states(values: Iterable[str] | None) -> list[str] | None:
    if values is None:
        return None
    result: list[str] = []
    for value in values:
        normalized = value.strip().lower()
        if normalized and normalized not in result:
            result.append(normalized)
    return result or None


def render_learning_rows(records: list[dict[str, object]]) -> str:
    if not records:
        return "No learnings matched."
    lines = []
    for record in records:
        lines.append(
            f"{record['id']} [{record['state']}] {record['scope']} / {record['skill']}: {record['topic']}"
        )
        lines.append(f"  {record['guidance']}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    learnings_path = resolve_learnings_path(repo_root, args.learnings_path)

    if args.command in {"query", "export"}:
        records = [
            record.to_dict()
            for record in query_learnings(
                learnings_path,
                scope=args.scope,
                skill=args.skill,
                states=normalize_states(args.states),
            )
        ]
        if args.json:
            print(
                json.dumps(
                    {
                        "scope": args.scope,
                        "path": str(learnings_path),
                        "count": len(records),
                        "learnings": records,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
        else:
            print(render_learning_rows(records))
        return 0

    try:
        next_state = "active" if args.command == "promote" else "pruned"
        record = update_learning_state(learnings_path, args.learning_id, next_state).to_dict()
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.json:
        print(
            json.dumps(
                {
                    "path": str(learnings_path),
                    "learning": record,
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print(f"{record['id']} -> {record['state']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
