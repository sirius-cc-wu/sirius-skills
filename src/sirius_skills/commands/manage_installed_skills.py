from __future__ import annotations

import argparse
import json
import os
import re
import shutil
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


def default_canonical_skills_dir() -> Path:
    return Path.home() / ".agents/skills"


def default_antigravity_skills_dir() -> Path:
    return Path.home() / ".gemini/config/skills"


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


def remove_locked_profile(
    profile_path: Path,
    *,
    lock_path: Path,
    skills_dir: Path,
    source: str,
) -> None:
    if not lock_path.exists():
        return
    if lock_path.is_symlink():
        raise ValueError(f"project skill lock must not be a symlink: {lock_path}")

    lock_data = json.loads(lock_path.read_text(encoding="utf-8"))
    if not isinstance(lock_data, dict) or not isinstance(
        lock_data.get("skills"), dict
    ):
        raise ValueError("project skill lock must contain a skills object")

    entries = lock_data["skills"]
    selected: list[tuple[str, Path]] = []
    for name in sorted(read_name_file(profile_path)):
        entry = entries.get(name)
        if entry is None:
            continue
        if not isinstance(entry, dict):
            raise ValueError(f"project skill lock entry must be an object: {name}")
        if entry.get("source") != source:
            continue

        target = skills_dir / name
        if target.is_symlink() or target.is_dir() or not target.exists():
            selected.append((name, target))
            continue
        raise ValueError(
            f"locked target skill is not a directory or symlink: {target}"
        )

    if not selected:
        return

    for name, _target in selected:
        entries.pop(name)

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=lock_path.parent,
            prefix=f".{lock_path.name}.",
            delete=False,
        ) as temporary:
            temporary.write(json.dumps(lock_data, indent=2) + "\n")
            temporary_path = Path(temporary.name)

        for _name, target in selected:
            if target.is_symlink():
                target.unlink()
            elif target.is_dir():
                shutil.rmtree(target)
        temporary_path.replace(lock_path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def link_points_to(path: Path, expected_target: Path) -> bool:
    if not path.is_symlink():
        return False

    link_target = Path(os.readlink(path))
    if not link_target.is_absolute():
        link_target = path.parent / link_target
    return link_target.resolve(strict=False) == expected_target.resolve(strict=False)


def skill_roots_are_equivalent(source_dir: Path, target_dir: Path) -> bool:
    return source_dir.resolve(strict=False) == target_dir.resolve(strict=False)


def link_names(
    names: Iterable[str],
    *,
    source_dir: Path,
    target_dir: Path,
) -> None:
    normalized = sorted(set(names))
    if skill_roots_are_equivalent(source_dir, target_dir):
        return
    if target_dir.is_symlink() and not target_dir.is_dir():
        raise ValueError(f"target skill directory is a broken link: {target_dir}")
    if target_dir.exists() and not target_dir.is_dir():
        raise ValueError(f"target skill directory is not a directory: {target_dir}")

    links_to_create: list[tuple[Path, Path]] = []
    for name in normalized:
        source = source_dir / name
        target = target_dir / name
        if not source.is_dir():
            raise ValueError(f"source skill directory is missing: {source}")
        if target.is_symlink():
            if link_points_to(target, source):
                continue
            raise ValueError(f"refusing to replace existing target skill: {target}")
        if target.exists():
            raise ValueError(f"refusing to replace existing target skill: {target}")
        links_to_create.append((source, target))

    target_dir.mkdir(parents=True, exist_ok=True)
    for source, target in links_to_create:
        relative_source = os.path.relpath(source, start=target.parent)
        target.symlink_to(relative_source, target_is_directory=True)


def unlink_names(
    names: Iterable[str],
    *,
    source_dir: Path,
    target_dir: Path,
) -> None:
    if skill_roots_are_equivalent(source_dir, target_dir):
        return

    for name in sorted(set(names)):
        source = source_dir / name
        target = target_dir / name
        if link_points_to(target, source):
            target.unlink()


def link_profile(
    profile_path: Path,
    *,
    source_dir: Path,
    target_dir: Path,
) -> None:
    link_names(
        read_name_file(profile_path),
        source_dir=source_dir,
        target_dir=target_dir,
    )


def unlink_profile(
    profile_path: Path,
    *,
    source_dir: Path,
    target_dir: Path,
) -> None:
    unlink_names(
        read_name_file(profile_path),
        source_dir=source_dir,
        target_dir=target_dir,
    )


def unlink_retired(
    ledger_path: Path,
    *,
    state_path: Path,
    source_dir: Path,
    target_dir: Path,
    include_unowned: bool = False,
) -> None:
    retired = {entry.name for entry in read_retirements(ledger_path)}
    names = retired if include_unowned else retired & read_name_file(state_path)
    unlink_names(names, source_dir=source_dir, target_dir=target_dir)


def add_skill_dir_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=default_canonical_skills_dir(),
        help="source skill directory (default: %(default)s)",
    )
    parser.add_argument(
        "--target-dir",
        type=Path,
        default=default_antigravity_skills_dir(),
        help="target skill directory (default: %(default)s)",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Track Sirius-installed skills, manage skill-directory links, and "
            "select retired installations safely."
        )
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

    remove_locked_parser = subparsers.add_parser(
        "remove-locked-profile",
        help="remove project skills owned by one lock-file source",
    )
    remove_locked_parser.add_argument("--profile", type=Path, required=True)
    remove_locked_parser.add_argument("--lock", type=Path, required=True)
    remove_locked_parser.add_argument("--skills-dir", type=Path, required=True)
    remove_locked_parser.add_argument("--source", required=True)

    link_profile_parser = subparsers.add_parser(
        "link-profile", help="link a profile into a target skill directory"
    )
    link_profile_parser.add_argument("--profile", type=Path, required=True)
    add_skill_dir_arguments(link_profile_parser)

    unlink_profile_parser = subparsers.add_parser(
        "unlink-profile", help="remove a profile's managed target links"
    )
    unlink_profile_parser.add_argument("--profile", type=Path, required=True)
    add_skill_dir_arguments(unlink_profile_parser)

    unlink_retired_parser = subparsers.add_parser(
        "unlink-retired", help="remove retired managed target links"
    )
    unlink_retired_parser.add_argument("--ledger", type=Path, required=True)
    unlink_retired_parser.add_argument("--include-unowned", action="store_true")
    add_skill_dir_arguments(unlink_retired_parser)

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
        elif args.command == "remove-locked-profile":
            remove_locked_profile(
                args.profile,
                lock_path=args.lock,
                skills_dir=args.skills_dir,
                source=args.source,
            )
        elif args.command == "link-profile":
            link_profile(
                args.profile,
                source_dir=args.source_dir,
                target_dir=args.target_dir,
            )
        elif args.command == "unlink-profile":
            unlink_profile(
                args.profile,
                source_dir=args.source_dir,
                target_dir=args.target_dir,
            )
        elif args.command == "unlink-retired":
            unlink_retired(
                args.ledger,
                state_path=args.state,
                source_dir=args.source_dir,
                target_dir=args.target_dir,
                include_unowned=args.include_unowned,
            )
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
