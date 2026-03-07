import os
import json
import argparse
import subprocess
import re
import sys
from datetime import datetime

specs_dir = "specs"
index_file = os.path.join(specs_dir, "README.md")
config_file = ".specs/config.json"


def init():
    if not os.path.exists(specs_dir):
        os.makedirs(specs_dir)
    if not os.path.exists(index_file):
        with open(index_file, "w") as f:
            f.write(
                "# Specification Registry\n\n| ID | Feature | Status | Path |\n|---|---|---|---|\n"
            )
    if not os.path.exists(".specs"):
        os.makedirs(".specs")
    if not os.path.exists(config_file):
        with open(config_file, "w") as f:
            json.dump({"spec_dir": specs_dir, "preferred_workflow": "TDD"}, f)


def add_track(id, name):
    folder_name = f"{id}-{name.lower().replace(' ', '-')}"
    path = os.path.join(specs_dir, folder_name)
    if not os.path.exists(path):
        os.makedirs(path)

    with open(index_file, "a") as f:
        f.write(f"| {id} | {name} | Draft | {path}/ |\n")
    print(f"Created track: {folder_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("init")
    add_p = subparsers.add_parser("add")
    # specific arguments are replaced by a flexible list to support optional ID
    add_p.add_argument("args", nargs="+", help="[ID] Name")

    args = parser.parse_args()
    if args.command == "init":
        init()
    elif args.command == "add":
        # Smart argument parsing
        cmd_args = args.args
        id_to_use = None
        name = None

        if len(cmd_args) == 1:
            name = cmd_args[0]
        elif len(cmd_args) >= 2:
            id_to_use = cmd_args[0]
            name = " ".join(cmd_args[1:])

        # Auto-detect ID if missing
        if not id_to_use:
            # 1. Try Git branch name
            branch = None
            try:
                branch = (
                    subprocess.check_output(
                        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                        stderr=subprocess.DEVNULL,
                    )
                    .decode()
                    .strip()
                )
            except Exception:
                pass

            if branch:
                # Look for numeric ID in branch (e.g. 123-feature, feature/123)
                m = re.search(r"(?:^|/|-)(\d+)(?:-|$)", branch)
                if m:
                    id_to_use = m.group(1)

        # 2. Fallback to specific format or timestamp
        if not id_to_use:
            # Generate a simple timestamp-based ID
            id_to_use = datetime.now().strftime("%Y%m%d")

        add_track(id_to_use, name)
