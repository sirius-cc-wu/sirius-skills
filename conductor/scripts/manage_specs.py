import os
import json
import argparse
from datetime import datetime

specs_dir = "specs"
index_file = os.path.join(specs_dir, "README.md")
config_file = ".specs/config.json"

def init():
    if not os.path.exists(specs_dir):
        os.makedirs(specs_dir)
    if not os.path.exists(index_file):
        with open(index_file, "w") as f:
            f.write("# Specification Registry\n\n| ID | Feature | Status | Path |\n|---|---|---|---|\n")
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
    add_p.add_argument("id")
    add_p.add_argument("name")
    
    args = parser.parse_args()
    if args.command == "init":
        init()
    elif args.command == "add":
        add_track(args.id, args.name)
