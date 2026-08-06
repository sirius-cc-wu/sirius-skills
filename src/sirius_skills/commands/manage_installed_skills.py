from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
REVISION_PATTERN = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True)
class Retirement:
    name: str
    revision: str


def default_state_path() -> Path:
    override = os.environ.get("SIRIUS_SKILLS_STATE_FILE")
    if override:
        return Path(override).expanduser()

    state_home = os.environ.get("XDG_STATE_HOME")
    base = Path(state_home).expanduser() if state_home else Path.home() / ".local/state"
    return base / "sirius-skills/managed-skills.txt"


def read_name_file(path: Path) -> set[str]:
    if not path.exists():
        return set()

    names: set[str] = set()
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if not SKILL_NAME_PATTERN.fullmatch(line):
            raise ValueError(f"{path.name}:{line_number}: invalid skill name {line!r}")
        names.add(line)
    return names


def read_retirements(path: Path) -> list[Retirement]:
    retirements: list[Retirement] = []
    seen: set[str] = set()
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        fields = line.split("\t")
        if (
            len(fields) != 2
            or not SKILL_NAME_PATTERN.fullmatch(fields[0])
            or not REVISION_PATTERN.fullmatch(fields[1])
        ):
            raise ValueError(
                f"{path.name}:{line_number}: expected skill<TAB>40-character "
                "evidence revision"
            )

        name, revision = fields
        if name in seen:
            raise ValueError(
                f"{path.name}:{line_number}: duplicate retired skill {name}"
            )
        seen.add(name)
        retirements.append(Retirement(name=name, revision=revision))
    return retirements


def parse_installed_skills(payload: str) -> set[str]:
    data = json.loads(payload)
    if not isinstance(data, list):
        raise ValueError("installed skill data must be a JSON list")

    names: set[str] = set()
    for item in data:
        if not isinstance(item, dict):
            raise ValueError("each installed skill entry must be an object")
        name = item.get("name")
        if not isinstance(name, str) or not name:
            raise ValueError("each installed skill entry must have a non-empty name")
        names.add(name)
    return names


def select_retired_skills(
    installed_json: str,
    *,
    ledger_path: Path,
    state_path: Path,
    include_unowned: bool = False,
) -> tuple[list[str], list[str]]:
    installed = parse_installed_skills(installed_json)
    retired = {entry.name for entry in read_retirements(ledger_path)}
    owned = read_name_file(state_path)
    candidates = installed & retired
    selected = candidates if include_unowned else candidates & owned
    return sorted(selected), sorted(candidates - selected)


def write_names(path: Path, names: Iterable[str]) -> None:
    normalized = sorted(set(names))
    invalid = [name for name in normalized if not SKILL_NAME_PATTERN.fullmatch(name)]
    if invalid:
        raise ValueError(f"invalid skill name {invalid[0]!r}")

    path.parent.mkdir(parents=True, exist_ok=True)
    content = "".join(f"{name}\n" for name in normalized)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            delete=False,
        ) as temporary:
            temporary.write(content)
            temporary_path = Path(temporary.name)
        temporary_path.replace(path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def record_names(names: Iterable[str], state_path: Path) -> None:
    write_names(state_path, read_name_file(state_path) | set(names))


def forget_names(names: Iterable[str], state_path: Path) -> None:
    write_names(state_path, read_name_file(state_path) - set(names))


def record_installed(profile_path: Path, state_path: Path) -> None:
    record_names(read_name_file(profile_path), state_path)


def forget_profile(profile_path: Path, state_path: Path) -> None:
    forget_names(read_name_file(profile_path), state_path)


def forget_retired(ledger_path: Path, state_path: Path) -> None:
    forget_names((entry.name for entry in read_retirements(ledger_path)), state_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Track Sirius-installed skills and select retired installations safely."
    )
    parser.add_argument(
        "--state",
        type=Path,
        default=default_state_path(),
        help="host-local ownership state (default: %(default)s)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    select_parser = subparsers.add_parser(
        "select-retired", help="read installed-skill JSON and print removable names"
    )
    select_parser.add_argument("--ledger", type=Path, required=True)
    select_parser.add_argument("--include-unowned", action="store_true")

    record_parser = subparsers.add_parser(
        "record-installed", help="record a successfully installed profile"
    )
    record_parser.add_argument("--profile", type=Path, required=True)

    forget_profile_parser = subparsers.add_parser(
        "forget-profile", help="forget ownership for an uninstalled profile"
    )
    forget_profile_parser.add_argument("--profile", type=Path, required=True)

    forget_retired_parser = subparsers.add_parser(
        "forget-retired", help="remove retired names from ownership state"
    )
    forget_retired_parser.add_argument("--ledger", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "select-retired":
            selected, unowned = select_retired_skills(
                sys.stdin.read(),
                ledger_path=args.ledger,
                state_path=args.state,
                include_unowned=args.include_unowned,
            )
            if selected:
                print("\n".join(selected))
            if unowned:
                print(
                    "Retired skill names are installed but ownership is unknown: "
                    + ", ".join(unowned),
                    file=sys.stderr,
                )
                print(
                    "Review them, then run `just prune-retired-legacy` to remove "
                    "those names explicitly.",
                    file=sys.stderr,
                )
        elif args.command == "record-installed":
            record_installed(args.profile, args.state)
        elif args.command == "forget-profile":
            forget_profile(args.profile, args.state)
        elif args.command == "forget-retired":
            forget_retired(args.ledger, args.state)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Failed to manage installed skills: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
