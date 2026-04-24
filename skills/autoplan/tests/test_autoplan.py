from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional


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


def write_planning_config(
    root: Path,
    *,
    autoplan_overrides: Optional[Dict[str, Any]] = None,
) -> None:
    skills_dir = root / ".skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    autoplan_config: Dict[str, Any] = {
        "auto_decision_policy": "conservative",
    }
    if autoplan_overrides:
        autoplan_config.update(autoplan_overrides)

    (skills_dir / "planning.json").write_text(
        json.dumps(
            {
                "planning_dir": "docs/features",
                "proposal_dir": "docs/proposals",
                "design_diagram_mode": "embedded",
                "accelerators": {
                    "autoplan": autoplan_config,
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
    assert payload["readiness"]["can_proceed"] is True
    assert payload["readiness"]["blocked_by"] == []
    assert payload["readiness"]["approval_gate"]["required"] is False


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
    assert payload["owner_handoff"] is None
    assert payload["readiness"]["can_proceed"] is False
    assert payload["readiness"]["blocked_by"] == ["approval_boundary"]
    assert payload["readiness"]["approval_gate"]["required"] is True


def test_autoplan_owner_chain_advances_to_review_boundary(tmp_path: Path, monkeypatch) -> None:
    init_git_repo(tmp_path)
    write_planning_config(tmp_path)
    feature_path = create_feature(tmp_path, monkeypatch, "discovery_pending")
    (feature_path / "discover.md").write_text("# Discover\n", encoding="utf-8")
    (feature_path / "system-design.md").write_text("# Design\n", encoding="utf-8")
    (feature_path / "slice-planning.md").write_text("# Slice Planning\n", encoding="utf-8")
    (feature_path / "slice-traceability.md").write_text("# Slice Traceability\n", encoding="utf-8")

    result = run_cli(
        tmp_path,
        "throughput-acceleration-workflow",
        "--execute-owner-chain",
        "--review-note",
        "Autoplan review pass",
        "--json",
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["planning_status"] == "planning_reviewed"
    assert payload["next_owner"] == "approval"
    assert payload["action"] == "approval_required"
    assert payload["execute_owner_chain"] is True
    assert payload["owner_chain"]["stop_reason"]["kind"] == "approval_boundary"
    assert payload["readiness"]["can_proceed"] is False
    assert payload["readiness"]["blocked_by"] == ["approval_boundary"]
    assert payload["readiness"]["stop_reason"]["kind"] == "approval_boundary"
    assert [step["owner"] for step in payload["owner_chain"]["steps"]] == [
        "discover",
        "design",
        "breakdown",
        "review-planning",
    ]


def test_autoplan_owner_chain_respects_stop_owner_boundary(tmp_path: Path, monkeypatch) -> None:
    init_git_repo(tmp_path)
    write_planning_config(
        tmp_path,
        autoplan_overrides={
            "execute_owner_chain": True,
            "stop_on_owner": ["design"],
        },
    )
    feature_path = create_feature(tmp_path, monkeypatch, "discovery_pending")
    (feature_path / "discover.md").write_text("# Discover\n", encoding="utf-8")

    result = run_cli(tmp_path, "throughput-acceleration-workflow", "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["planning_status"] == "discovery_ready"
    assert payload["next_owner"] == "design"
    assert payload["action"] == "run_design"
    assert payload["owner_handoff"] is None
    assert payload["owner_chain"]["stop_reason"]["kind"] == "owner_stop"
    assert payload["readiness"]["can_proceed"] is False
    assert payload["readiness"]["blocked_by"] == ["owner_stop"]
    assert [step["owner"] for step in payload["owner_chain"]["steps"]] == ["discover"]


def test_autoplan_owner_chain_reports_missing_required_input(tmp_path: Path, monkeypatch) -> None:
    init_git_repo(tmp_path)
    write_planning_config(
        tmp_path,
        autoplan_overrides={
            "execute_owner_chain": True,
        },
    )
    create_feature(tmp_path, monkeypatch, "discovery_pending")

    result = run_cli(tmp_path, "throughput-acceleration-workflow", "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["planning_status"] == "discovery_pending"
    assert payload["next_owner"] == "discover"
    assert payload["action"] == "run_discover"
    assert payload["owner_chain"]["stop_reason"]["kind"] == "missing_required_input"
    assert payload["owner_handoff"] == {
        "should_invoke_skill": True,
        "owner": "discover",
        "target_id": "throughput-acceleration-workflow",
        "target_path": "docs/features/throughput-acceleration-workflow/",
        "stop_reason": payload["owner_chain"]["stop_reason"],
        "missing_files": ["discover.md"],
        "bootstrap_commands": [],
    }
    assert payload["readiness"]["can_proceed"] is False
    assert payload["readiness"]["blocked_by"] == ["missing_required_input"]
    assert payload["owner_chain"]["steps"][0]["advanced"] is False


def test_autoplan_owner_chain_suggests_breakdown_scaffold_handoff(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_planning_config(
        tmp_path,
        autoplan_overrides={
            "execute_owner_chain": True,
        },
    )
    create_feature(tmp_path, monkeypatch, "design_ready")

    result = run_cli(tmp_path, "throughput-acceleration-workflow", "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["planning_status"] == "design_ready"
    assert payload["next_owner"] == "breakdown"
    assert payload["owner_chain"]["stop_reason"]["kind"] == "missing_required_input"
    assert payload["owner_handoff"]["should_invoke_skill"] is True
    assert payload["owner_handoff"]["owner"] == "breakdown"
    assert payload["owner_handoff"]["missing_files"] == [
        "slice-planning.md",
        "slice-traceability.md",
    ]
    assert payload["owner_handoff"]["bootstrap_commands"] == [
        "python3 skills/breakdown/scripts/scaffold_breakdown.py "
        "docs/features/throughput-acceleration-workflow/"
    ]


def test_autoplan_owner_chain_reports_approval_when_already_reviewed(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_planning_config(
        tmp_path,
        autoplan_overrides={
            "execute_owner_chain": True,
        },
    )
    create_feature(tmp_path, monkeypatch, "planning_reviewed")

    result = run_cli(tmp_path, "throughput-acceleration-workflow", "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["planning_status"] == "planning_reviewed"
    assert payload["next_owner"] == "approval"
    assert payload["owner_chain"]["steps"] == []
    assert payload["owner_chain"]["stop_reason"]["kind"] == "approval_boundary"
    assert payload["owner_handoff"] is None
    assert payload["readiness"]["can_proceed"] is False
    assert payload["readiness"]["blocked_by"] == ["approval_boundary"]
