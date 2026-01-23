import os
import json
import argparse
import re
import subprocess
import sys
import shutil
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
    folder_name = f"{id}-{name.lower().replace(' ', '-') }"
    path = os.path.join(specs_dir, folder_name)
    if not os.path.exists(path):
        os.makedirs(path)

    # Copy skill-local templates into the new track folder if present
    templates = [
        (
            os.path.join(
                ".github", "skills", "specify", "templates", "TEMPLATE_spec.md"
            ),
            os.path.join(path, "spec.md"),
        ),
    ]
    for src, dst in templates:
        try:
            if os.path.exists(src) and not os.path.exists(dst):
                shutil.copyfile(src, dst)
                print(f"Created {os.path.basename(dst)} from template")
        except Exception as e:
            print(f"Warning: failed to copy template {src}: {e}", file=sys.stderr)

    with open(index_file, "a") as f:
        f.write(f"| {id} | {name} | Draft | {path}/ |\n")
    print(f"Created track: {folder_name}")


def _current_branch():
    try:
        branch = (
            subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
        )
        return branch
    except Exception:
        ref = os.environ.get("GITHUB_REF", "")
        if ref.startswith("refs/heads/"):
            return ref.split("refs/heads/")[-1]
    return None


def extract_id_from_branch(branch):
    if not branch:
        return None
    # Try JIRA-like pattern first: WORD-NUMBER
    m = re.search(r"([A-Z][A-Z0-9]+-\d+)", branch)
    if m:
        return m.group(1)
    # Try simple numeric ID: 123-description or feature/123-desc
    m = re.search(r"(?:^|/|-)(\d+)(?:-|$)", branch)
    if m:
        return m.group(1)
    return None


def find_track_dir(track_id=None):
    # If track_id provided, try direct lookup
    if track_id:
        candidate = os.path.join(specs_dir, track_id)
        # also allow folders that start with the id
        if os.path.exists(candidate):
            return candidate
        for name in os.listdir(specs_dir):
            if name.startswith(track_id):
                return os.path.join(specs_dir, name)

    # otherwise attempt to derive from branch
    branch = _current_branch()
    jid = extract_id_from_branch(branch)
    if jid:
        for name in os.listdir(specs_dir):
            if name.startswith(jid):
                return os.path.join(specs_dir, name)

    return None


def validate_spec(track_dir):
    spec_path = os.path.join(track_dir, "spec.md")
    if not os.path.exists(spec_path):
        print("spec.md not found", file=sys.stderr)
        return 2
    text = open(spec_path, "r").read()
    ok_interface = "interface spec" in text.lower() or "## Interface Spec" in text
    ok_accept = "acceptance tests" in text.lower() or "## Acceptance Tests" in text
    if not ok_interface:
        print("Missing 'Interface Spec' section in spec.md", file=sys.stderr)
    if not ok_accept:
        print("Missing 'Acceptance Tests' section in spec.md", file=sys.stderr)
    if ok_interface and ok_accept:
        print("spec.md: validation passed")
        return 0
    return 1


def status(track_dir):
    if not track_dir or not os.path.exists(track_dir):
        print("Track not found")
        return 2
    print(f"Track: {track_dir}")
    spec = os.path.exists(os.path.join(track_dir, "spec.md"))
    print(f"  spec.md: {'present' if spec else 'missing'}")
    spec_ret = validate_spec(track_dir) if spec else None
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("init")
    add_p = subparsers.add_parser("add")
    # `id` may be omitted; we'll try to extract an ID from the current branch name
    add_p.add_argument("id", nargs="?", default=None)
    add_p.add_argument("name")
    subparsers.add_parser("validate-spec")
    subparsers.add_parser("status")
    # allow optional track id argument for validations/status
    parser.add_argument("track_id", nargs="?", default=None)

    args = parser.parse_args()
    if args.command == "init":
        init()
    elif args.command == "add":
        id_to_use = args.id
        if not id_to_use:
            branch = _current_branch()
            if branch:
                id_to_use = extract_id_from_branch(branch)

        if not id_to_use:
            # Fallback to timestamp for personal projects
            id_to_use = datetime.now().strftime("%Y%m%d")

        add_track(id_to_use, args.name)
    elif args.command == "validate-spec":
        track_dir = find_track_dir(args.track_id)
        if not track_dir:
            print("Track not found for validation", file=sys.stderr)
            sys.exit(2)
        rc = validate_spec(track_dir)
        sys.exit(rc)
    elif args.command == "status":
        track_dir = find_track_dir(args.track_id)
        rc = status(track_dir)
        sys.exit(rc)
