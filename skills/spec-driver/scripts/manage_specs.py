import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

SPECS_DIR = "specs"
INDEX_FILE = os.path.join(SPECS_DIR, "README.md")
CONFIG_DIR = ".specs"
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
REGISTRY_HEADER = (
    "# Specification Registry\n\n| ID | Feature | Status | Path |\n|---|---|---|---|\n"
)
TRACK_METADATA_FILE = ".track-meta.json"
TRACK_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
VALID_STATUSES = {
    "draft_spec",
    "spec_ready",
    "plan_ready",
    "implementation_ready",
    "implementing",
    "done",
}


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "feature"


def normalize_feature_name(value: str) -> str:
    normalized = re.sub(r"\s+", " ", value.strip())
    return normalized.replace("|", "/")


def validate_track_id(value: str) -> str:
    track_id = value.strip()
    if not track_id:
        raise ValueError("Track ID cannot be empty.")
    if not TRACK_ID_PATTERN.fullmatch(track_id):
        raise ValueError(
            "Invalid track ID. Use only letters, numbers, dot, underscore, and hyphen."
        )
    return track_id


def ensure_registry() -> None:
    os.makedirs(SPECS_DIR, exist_ok=True)
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            f.write(REGISTRY_HEADER)
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"spec_dir": SPECS_DIR, "preferred_workflow": "TDD"}, f, indent=2)


def parse_registry() -> List[Dict[str, str]]:
    ensure_registry()
    rows: List[Dict[str, str]] = []
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("|"):
                continue
            if line.startswith("| ID |") or line.startswith("|---"):
                continue
            cols = [c.strip() for c in line.strip("|").split("|")]
            if len(cols) != 4:
                continue
            rows.append(
                {"id": cols[0], "feature": cols[1], "status": cols[2], "path": cols[3]}
            )
    return rows


def write_registry(rows: List[Dict[str, str]]) -> None:
    ensure_registry()
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(REGISTRY_HEADER)
        for row in rows:
            f.write(
                f"| {row['id']} | {row['feature']} | {row['status']} | {row['path']} |\n"
            )


def normalize_track_path(path: str) -> str:
    normalized = path.rstrip("/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized + "/"


def infer_id_from_branch() -> Optional[str]:
    try:
        branch = (
            subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    match = re.search(r"(?:^|/|-)(\d+)(?:-|$)", branch)
    if match:
        return match.group(1)
    return None


def resolve_track(rows: List[Dict[str, str]], selector: str) -> Optional[Dict[str, str]]:
    selector = selector.strip().rstrip("/")
    for row in rows:
        row_path = row["path"].rstrip("/")
        if row["id"] == selector or row_path.endswith(selector):
            return row
        if os.path.basename(row_path) == selector:
            return row
    return None


def find_active_track(rows: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
    priority = ["implementing", "implementation_ready", "plan_ready", "spec_ready", "draft_spec"]
    for wanted in priority:
        matches = [r for r in rows if r["status"] == wanted]
        if matches:
            return matches[-1]
    return rows[-1] if rows else None


def expected_status_for_files(spec_exists: bool, plan_exists: bool, tasks_exists: bool) -> str:
    if not spec_exists:
        return "draft_spec"
    if spec_exists and not plan_exists:
        return "spec_ready"
    if plan_exists and not tasks_exists:
        return "plan_ready"
    return "implementation_ready"


def validate_track(row: Dict[str, str]) -> Tuple[bool, List[str], Dict[str, bool]]:
    issues: List[str] = []
    path = row["path"].rstrip("/")
    spec = os.path.join(path, "spec.md")
    plan = os.path.join(path, "plan.md")
    tasks = os.path.join(path, "tasks.md")
    checks = {
        "track_dir_exists": os.path.isdir(path),
        "spec_exists": os.path.isfile(spec),
        "plan_exists": os.path.isfile(plan),
        "tasks_exists": os.path.isfile(tasks),
    }

    if row["status"] not in VALID_STATUSES:
        issues.append(f"invalid_status:{row['status']}")

    if not checks["track_dir_exists"]:
        issues.append("missing_track_directory")
        return False, issues, checks

    expected = expected_status_for_files(
        checks["spec_exists"], checks["plan_exists"], checks["tasks_exists"]
    )
    if row["status"] in {"draft_spec", "spec_ready", "plan_ready", "implementation_ready"}:
        if row["status"] != expected:
            issues.append(
                f"status_mismatch:status={row['status']} expected={expected} based_on_files"
            )
    if row["status"] == "implementing" and not checks["plan_exists"]:
        issues.append("implementing_without_plan")
    if row["status"] == "done" and not (checks["spec_exists"] and checks["plan_exists"]):
        issues.append("done_without_core_artifacts")

    return len(issues) == 0, issues, checks


def write_track_metadata(track_path: str, metadata: Dict[str, object]) -> None:
    metadata_path = os.path.join(track_path, TRACK_METADATA_FILE)
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        f.write("\n")


def create_track(
    track_id: str, name: str, metadata: Optional[Dict[str, object]] = None
) -> Tuple[str, bool]:
    ensure_registry()
    normalized_id = validate_track_id(track_id)
    normalized_name = normalize_feature_name(name)
    if not normalized_name:
        raise ValueError("Feature name cannot be empty.")

    slug = slugify(normalized_name)
    folder = f"{normalized_id}-{slug}"
    track_path = os.path.join(SPECS_DIR, folder)

    rows = parse_registry()
    if any(r["id"] == normalized_id or r["path"].rstrip("/").endswith(folder) for r in rows):
        return folder, False

    os.makedirs(track_path, exist_ok=True)
    if metadata is not None:
        write_track_metadata(track_path, metadata)

    rows.append(
        {
            "id": normalized_id,
            "feature": normalized_name,
            "status": "draft_spec",
            "path": normalize_track_path(track_path),
        }
    )
    write_registry(rows)
    return folder, True


def get_sb_issue(issue_id: str) -> Dict[str, object]:
    requested_id = validate_track_id(issue_id)
    try:
        result = subprocess.run(
            ["sb", "show", requested_id, "--json"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("The 'sb' CLI was not found on PATH.") from exc

    if result.returncode != 0:
        details = result.stderr.strip() or result.stdout.strip()
        if not details:
            details = f"sb show exited with code {result.returncode}"
        raise RuntimeError(f"Failed to resolve sb issue '{requested_id}': {details}")

    try:
        issue = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("The 'sb show --json' output was not valid JSON.") from exc

    if not isinstance(issue, dict):
        raise RuntimeError("The 'sb show --json' output must be a JSON object.")

    resolved_id = issue.get("id")
    title = issue.get("title")
    if not isinstance(resolved_id, str):
        raise RuntimeError("The 'sb show --json' output did not include a string 'id'.")
    if not isinstance(title, str):
        raise RuntimeError("The 'sb show --json' output did not include a string 'title'.")

    issue["id"] = validate_track_id(resolved_id)
    issue["title"] = normalize_feature_name(title)
    if not issue["title"]:
        raise RuntimeError("The 'sb' issue title cannot be empty.")
    return issue


def build_sb_metadata(issue: Dict[str, object]) -> Dict[str, object]:
    tracked_fields = [
        "id",
        "title",
        "description",
        "status",
        "priority",
        "repo",
        "repo_branch",
        "repo_commit",
        "worktree_path",
        "created_at",
    ]
    issue_metadata = {field: issue[field] for field in tracked_fields if field in issue}
    return {
        "source": "sb",
        "imported_at": datetime.now().isoformat(timespec="seconds"),
        "issue": issue_metadata,
    }


def cmd_init(_: argparse.Namespace) -> int:
    ensure_registry()
    print("Initialized specs registry and config.")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    cmd_args = args.args
    if len(cmd_args) == 1:
        id_to_use = None
        name = cmd_args[0]
    else:
        id_to_use = cmd_args[0]
        name = " ".join(cmd_args[1:])

    if not id_to_use:
        id_to_use = infer_id_from_branch() or datetime.now().strftime("%Y%m%d")

    try:
        folder, created = create_track(id_to_use, name)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not created:
        print(f"Track already exists: {folder}")
        return 0

    print(f"Created track: {folder}")
    return 0


def cmd_add_from_sb(args: argparse.Namespace) -> int:
    try:
        issue = get_sb_issue(args.issue_id)
        folder, created = create_track(
            issue["id"], issue["title"], metadata=build_sb_metadata(issue)
        )
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not created:
        print(f"Track already exists: {folder}")
        return 0

    print(f"Created track from sb issue: {folder}")
    return 0


def cmd_set_status(args: argparse.Namespace) -> int:
    status = args.status.strip()
    if status not in VALID_STATUSES:
        print(f"Invalid status '{status}'. Valid: {sorted(VALID_STATUSES)}", file=sys.stderr)
        return 2

    rows = parse_registry()
    track = resolve_track(rows, args.track)
    if not track:
        print(f"Track not found: {args.track}", file=sys.stderr)
        return 2

    track["status"] = status
    write_registry(rows)
    print(f"Updated {track['id']} to status '{status}'")
    return 0


def cmd_get_active(_: argparse.Namespace) -> int:
    rows = parse_registry()
    track = find_active_track(rows)
    if not track:
        print("No tracks found.", file=sys.stderr)
        return 1
    print(json.dumps(track, indent=2))
    return 0


def cmd_validate_track(args: argparse.Namespace) -> int:
    rows = parse_registry()
    track = resolve_track(rows, args.track)
    if not track:
        print(f"Track not found: {args.track}", file=sys.stderr)
        return 2

    ok, issues, checks = validate_track(track)
    result = {"track": track, "ok": ok, "checks": checks, "issues": issues}
    print(json.dumps(result, indent=2))
    return 0 if ok else 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Initialize the specs registry and config")

    add_p = subparsers.add_parser("add", help="Create a track from a name or explicit opaque ID")
    add_p.add_argument("args", nargs="+", help="[ID] Name")

    add_from_sb_p = subparsers.add_parser(
        "add-from-sb", help="Create a track from an sb issue ID"
    )
    add_from_sb_p.add_argument("issue_id", help="sb issue ID, for example BNC-lg2fwe")

    set_p = subparsers.add_parser("set-status", help="Update a track status")
    set_p.add_argument("track", help="Track ID, folder name, or path")
    set_p.add_argument("status", help="New status")

    subparsers.add_parser("get-active", help="Return the active track as JSON")

    validate_p = subparsers.add_parser("validate-track", help="Validate track/file consistency")
    validate_p.add_argument("track", help="Track ID, folder name, or path")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "init":
        return cmd_init(args)
    if args.command == "add":
        return cmd_add(args)
    if args.command == "add-from-sb":
        return cmd_add_from_sb(args)
    if args.command == "set-status":
        return cmd_set_status(args)
    if args.command == "get-active":
        return cmd_get_active(args)
    if args.command == "validate-track":
        return cmd_validate_track(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
