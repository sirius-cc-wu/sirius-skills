from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


AUTOPLAN_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "autoplan.py"
PLANNING_SCRIPT = (
    Path(__file__).resolve().parents[2] / "guide-planning" / "scripts" / "manage_planning.py"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init", "--quiet"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Copilot Test"], cwd=root, check=True)
    subprocess.run(
        ["git", "config", "user.email", "copilot@example.test"],
        cwd=root,
        check=True,
    )


def write_planning_config(root: Path) -> None:
    skills_dir = root / ".skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    (skills_dir / "planning.json").write_text(
        json.dumps(
            {
                "planning_dir": "docs/features",
                "proposal_dir": "docs/proposals",
                "design_diagram_mode": "embedded",
                "accelerators": {
                    "autoplan": {
                        "auto_decision_policy": "conservative",
                    }
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )


def create_feature(tmp_path: Path, monkeypatch, status: str) -> Path:
    monkeypatch.chdir(tmp_path)
    planning = load_module("manage_planning_for_autoplan_test", PLANNING_SCRIPT)
    feature_dir, _ = planning.create_feature("throughput-acceleration-workflow")
    feature_path = Path(feature_dir)
    (feature_path / "user-stories.md").write_text("# Stories\n", encoding="utf-8")
    if status in {"discovery_ready", "design_ready", "breakdown_ready", "planning_reviewed"}:
        (feature_path / "discover.md").write_text("# Discover\n", encoding="utf-8")
    if status in {"design_ready", "breakdown_ready", "planning_reviewed"}:
        (feature_path / "system-design.md").write_text("# Design\n", encoding="utf-8")
    if status in {"breakdown_ready", "planning_reviewed"}:
        (feature_path / "slice-planning.md").write_text("# Slice Planning\n", encoding="utf-8")
        (feature_path / "slice-traceability.md").write_text("# Slice Traceability\n", encoding="utf-8")
    rows = planning.parse_registry()
    feature = planning.find_feature(rows, "throughput-acceleration-workflow")
    assert feature is not None
    for target_status in (
        "discovery_ready",
        "design_ready",
        "breakdown_ready",
        "planning_reviewed",
    ):
        if status == "discovery_pending":
            break
        ok, message = planning.update_feature_status(
            rows,
            feature,
            target_status,
            force=(target_status == "planning_reviewed"),
            review_note="ready" if target_status == "planning_reviewed" else None,
        )
        assert ok, message
        if target_status == status:
            break
    return feature_path


def run_cli(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(AUTOPLAN_SCRIPT), *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )


def test_autoplan_routes_discovery_pending_to_discover(tmp_path: Path, monkeypatch) -> None:
    init_git_repo(tmp_path)
    write_planning_config(tmp_path)
    create_feature(tmp_path, monkeypatch, "discovery_pending")

    result = run_cli(tmp_path, "throughput-acceleration-workflow", "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["next_owner"] == "discover"
    assert Path(payload["checkpoint_path"]).is_file()


def test_autoplan_resume_uses_checkpoint(tmp_path: Path, monkeypatch) -> None:
    init_git_repo(tmp_path)
    write_planning_config(tmp_path)
    create_feature(tmp_path, monkeypatch, "design_ready")

    first = run_cli(tmp_path, "throughput-acceleration-workflow", "--json")
    assert first.returncode == 0

    resumed = run_cli(tmp_path, "--resume", "--json")

    assert resumed.returncode == 0
    payload = json.loads(resumed.stdout)
    assert payload["target_id"] == "throughput-acceleration-workflow"
    assert payload["next_owner"] == "breakdown"


def test_autoplan_stops_at_planning_reviewed_boundary(tmp_path: Path, monkeypatch) -> None:
    init_git_repo(tmp_path)
    write_planning_config(tmp_path)
    create_feature(tmp_path, monkeypatch, "planning_reviewed")

    result = run_cli(tmp_path, "throughput-acceleration-workflow", "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["next_owner"] == "approval"
    assert payload["action"] == "approval_required"
