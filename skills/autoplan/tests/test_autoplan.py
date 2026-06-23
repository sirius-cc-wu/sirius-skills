from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional


AUTOPLAN_SCRIPT = Path(__file__).resolve().parents[3] / "src" / "sirius_skills" / "commands" / "autoplan.py"
PLANNING_SCRIPT = (
    Path(__file__).resolve().parents[3] / "src" / "sirius_skills" / "commands" / "manage_planning.py"
)
ADD_SUBFEATURE_SCRIPT = (
    Path(__file__).resolve().parents[3] / "src" / "sirius_skills" / "commands" / "manage_subfeatures.py"
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
        [sys.executable, "-m", "sirius_skills.cli", "autoplan", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )


def run_add_subfeature_cli(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "sirius_skills.cli", "manage-subfeatures", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def commit_all(repo_root: Path, message: str = "checkpoint") -> None:
    subprocess.run(["git", "add", "-A"], cwd=repo_root, check=True)
    subprocess.run(["git", "commit", "--quiet", "-m", message], cwd=repo_root, check=True)


def create_subfeature(
    tmp_path: Path,
    monkeypatch,
    *,
    subfeature_id: str = "transcript-copy-simplification",
    authored_discover: bool = False,
) -> Path:
    feature_path = create_feature(tmp_path, monkeypatch, "planning_reviewed")
    result = run_add_subfeature_cli(
        tmp_path,
        "add",
        "throughput-acceleration-workflow",
        subfeature_id,
        "--type",
        "narrowing",
        "--summary",
        "Simplify transcript copy behavior",
    )
    assert result.returncode == 0, result.stderr
    subfeature_path = feature_path / "subfeatures" / subfeature_id
    if authored_discover:
        (subfeature_path / "discover.md").write_text(
            "# Discover: Transcript Copy Simplification\n\n"
            "## Problem\n\n"
            "Ctrl-S forces users through an awkward toggle.\n\n"
            "## Next Step\n\n"
            "Assess the impact of retiring the toggle.\n",
            encoding="utf-8",
        )
        (subfeature_path / "user-stories.md").write_text(
            "# User Stories\n\n- TUI-001 Simplify transcript copy.\n",
            encoding="utf-8",
        )
    return subfeature_path


def prepare_approved_subfeature(
    tmp_path: Path,
    monkeypatch,
    *,
    ready_slice_ids: Optional[list[str]] = None,
) -> Path:
    subfeature_path = create_subfeature(tmp_path, monkeypatch, authored_discover=True)
    (subfeature_path / "impact-analysis.md").write_text("# Impact Analysis\n", encoding="utf-8")
    (subfeature_path / "system-design.md").write_text("# Design\n", encoding="utf-8")
    (subfeature_path / "slice-planning.md").write_text("# Slice Planning\n", encoding="utf-8")
    (subfeature_path / "slice-traceability.md").write_text(
        "# Slice Traceability\n", encoding="utf-8"
    )
    metadata_path = subfeature_path / ".subfeature-meta.json"
    metadata = read_json(metadata_path)
    metadata.update(
        {
            "status": "reviewed",
            "approval_status": "approved",
            "review_note": "Ready for approval.",
            "approved_at": "2026-01-03T00:00:00",
            "approved_by": "maintainer",
            "approval_note": "Approved for execution bootstrap.",
            "ready_slice_ids": ready_slice_ids or ["TCS-001"],
        }
    )
    metadata_path.write_text(json.dumps(metadata) + "\n", encoding="utf-8")
    return subfeature_path


def test_autoplan_routes_discovery_pending_to_discover(tmp_path: Path, monkeypatch) -> None:
    init_git_repo(tmp_path)
    write_planning_config(tmp_path)
    create_feature(tmp_path, monkeypatch, "discovery_pending")

    result = run_cli(tmp_path, "throughput-acceleration-workflow", "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["next_owner"] == "discover"
    assert Path(payload["checkpoint_path"]).is_file()
    request_handoff = Path(payload["request_handoff_path"])
    assert request_handoff.is_file()
    handoff_payload = read_json(request_handoff)
    assert handoff_payload["route_decision"] == "invoke_discover"
    assert handoff_payload["classification"] == "request_route"
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
    assert payload["approval_gate"]["decision"] == "waiting_approval"
    handoff_payload = read_json(Path(payload["request_handoff_path"]))
    assert handoff_payload["classification"] == "approval_boundary"
    assert handoff_payload["route_decision"] == "record_approval"
    assert payload["approval_gate"]["reason"] == "approval_not_recorded"
    assert payload["readiness"]["can_proceed"] is False
    assert payload["readiness"]["blocked_by"] == ["approval_required"]
    assert payload["readiness"]["approval_gate"]["required"] is True
    assert payload["readiness"]["approval_gate"]["state"] == "waiting_approval"
    assert payload["readiness"]["stop_reason"]["kind"] == "approval_required"


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
    assert payload["approval_gate"]["decision"] == "waiting_approval"
    assert payload["readiness"]["can_proceed"] is False
    assert payload["readiness"]["blocked_by"] == ["approval_required"]
    assert payload["readiness"]["stop_reason"]["kind"] == "approval_required"
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
        "bootstrap_commands_executed": [],
    }
    assert payload["failure_context"]["reason_code"] == "missing_required_input"
    handoff_payload = read_json(Path(payload["request_handoff_path"]))
    assert handoff_payload["classification"] == "owner_handoff"
    assert handoff_payload["route_decision"] == "invoke_discover"
    assert handoff_payload["evidence_refs"] == ["discover.md"]
    assert payload["failure_context"]["recovery_suggestions"]
    assert payload["readiness"]["can_proceed"] is False
    assert payload["readiness"]["blocked_by"] == ["missing_required_input"]
    assert payload["owner_chain"]["steps"][0]["advanced"] is False
    events = read_jsonl(Path(payload["event_log_path"]))
    assert events[-1]["event"] == "failure"
    assert events[-1]["reason_code"] == "missing_required_input"
    assert events[-1]["target_id"] == "throughput-acceleration-workflow"


def test_autoplan_owner_chain_suggests_design_scaffold_handoff(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_planning_config(
        tmp_path,
        autoplan_overrides={
            "execute_owner_chain": True,
        },
    )
    feature_path = create_feature(tmp_path, monkeypatch, "discovery_pending")
    (feature_path / "discover.md").write_text("# Discover\n", encoding="utf-8")

    result = run_cli(tmp_path, "throughput-acceleration-workflow", "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert (feature_path / "system-design.md").is_file()
    assert payload["planning_status"] == "discovery_ready"
    assert payload["next_owner"] == "design"
    assert payload["owner_chain"]["stop_reason"]["kind"] == "bootstrap_applied"
    assert payload["owner_handoff"]["should_invoke_skill"] is True
    assert payload["owner_handoff"]["owner"] == "design"
    assert payload["owner_handoff"]["missing_files"] == ["system-design.md"]
    assert payload["owner_handoff"]["bootstrap_commands"] == []
    assert payload["owner_handoff"]["bootstrap_commands_executed"] == [
        "sirius scaffold-design "
        "docs/features/throughput-acceleration-workflow/"
    ]
    assert payload["failure_context"] is None
    assert payload["readiness"]["can_proceed"] is True


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
    assert (tmp_path / "docs" / "features" / "throughput-acceleration-workflow" / "slice-planning.md").is_file()
    assert (tmp_path / "docs" / "features" / "throughput-acceleration-workflow" / "slice-traceability.md").is_file()
    assert payload["planning_status"] == "design_ready"
    assert payload["next_owner"] == "breakdown"
    assert payload["owner_chain"]["stop_reason"]["kind"] == "bootstrap_applied"
    assert payload["owner_handoff"]["should_invoke_skill"] is True
    assert payload["owner_handoff"]["owner"] == "breakdown"
    assert payload["owner_handoff"]["missing_files"] == [
        "slice-planning.md",
        "slice-traceability.md",
    ]
    assert payload["owner_handoff"]["bootstrap_commands"] == []
    assert payload["owner_handoff"]["bootstrap_commands_executed"] == [
        "sirius scaffold-breakdown "
        "docs/features/throughput-acceleration-workflow/"
    ]
    assert payload["failure_context"] is None
    assert payload["readiness"]["can_proceed"] is True


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
    assert payload["approval_gate"]["decision"] == "waiting_approval"
    assert payload["readiness"]["can_proceed"] is False
    assert payload["readiness"]["blocked_by"] == ["approval_required"]


def test_autoplan_routes_implemented_target_back_to_follow_on_delta_resolution(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_planning_config(tmp_path)
    create_feature(tmp_path, monkeypatch, "planning_reviewed")

    planning = load_module("manage_planning_for_implemented_autoplan_test", PLANNING_SCRIPT)
    rows = planning.parse_registry()
    feature = planning.find_feature(rows, "throughput-acceleration-workflow")
    assert feature is not None
    ok, message = planning.update_feature_status(
        rows,
        feature,
        "implemented",
        force=True,
    )
    assert ok, message

    result = run_cli(tmp_path, "throughput-acceleration-workflow", "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["planning_status"] == "implemented"
    assert payload["next_owner"] == "guide-planning"
    assert payload["action"] == "resolve_follow_on_delta"
    assert payload["readiness"]["blocked_by"] == ["planning_resolution_required"]
    handoff_payload = read_json(Path(payload["request_handoff_path"]))
    assert handoff_payload["classification"] == "follow_on_delta"
    assert handoff_payload["route_decision"] == "open_or_continue_subfeature"
    assert handoff_payload["next_owner"] == "guide-planning"
    assert handoff_payload["open_questions"] == [
        "Which subfeature should own this follow-on change?"
    ]


def test_autoplan_approve_records_gate_and_requires_commit(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_planning_config(tmp_path)
    create_feature(tmp_path, monkeypatch, "planning_reviewed")
    commit_all(tmp_path, "Initial planning packet")

    result = run_cli(
        tmp_path,
        "throughput-acceleration-workflow",
        "--approve",
        "--approval-note",
        "approved for execution",
        "--json",
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["next_owner"] == "commit"
    assert payload["action"] == "commit_planning"
    assert payload["approval_gate"]["decision"] == "approved"
    assert payload["approval_gate"]["approval_note"] == "approved for execution"
    assert payload["readiness"]["blocked_by"] == ["commit_checkpoint"]
    assert payload["readiness"]["stop_reason"]["kind"] == "commit_checkpoint"
    assert payload["readiness"]["commit_checkpoint"]["required"] is True
    assert any(".approval-gate.json" in line for line in payload["dirty_worktree_paths"])


def test_autoplan_approve_auto_chains_to_commit_handoff_even_without_dirty_worktree(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_planning_config(tmp_path)
    create_feature(tmp_path, monkeypatch, "planning_reviewed")
    commit_all(tmp_path, "Initial planning packet")

    result = run_cli(
        tmp_path,
        "throughput-acceleration-workflow",
        "--approve",
        "--approval-note",
        "approved for execution",
        "--json",
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["next_owner"] == "commit"
    assert payload["action"] == "commit_planning"
    assert payload["approval_gate"]["decision"] == "approved"
    assert payload["action"] == "commit_planning"
    assert payload["approval_gate"]["decision"] == "approved"


def test_autoplan_hands_off_to_slice_after_approved_planning_is_committed(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_planning_config(tmp_path)
    create_feature(tmp_path, monkeypatch, "planning_reviewed")
    commit_all(tmp_path, "Initial planning packet")

    approved = run_cli(tmp_path, "throughput-acceleration-workflow", "--approve", "--json")
    assert approved.returncode == 0
    commit_all(tmp_path, "Approve planning packet")

    result = run_cli(tmp_path, "throughput-acceleration-workflow", "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["next_owner"] == "slice"
    assert payload["action"] == "bootstrap_slice"
    assert payload["approval_gate"]["decision"] == "approved"
    assert payload["readiness"]["blocked_by"] == []
    assert payload["readiness"]["commit_checkpoint"]["required"] is False
    assert payload["readiness"]["approval_gate"]["state"] == "approved"


def test_autoplan_invalidates_stale_approval_after_planning_changes(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_planning_config(tmp_path)
    feature_path = create_feature(tmp_path, monkeypatch, "planning_reviewed")
    commit_all(tmp_path, "Initial planning packet")

    approved = run_cli(tmp_path, "throughput-acceleration-workflow", "--approve", "--json")
    assert approved.returncode == 0
    commit_all(tmp_path, "Approve planning packet")
    (feature_path / "discover.md").write_text("# Discover\nChanged after approval\n", encoding="utf-8")

    result = run_cli(tmp_path, "throughput-acceleration-workflow", "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["next_owner"] == "approval"
    assert payload["action"] == "approval_required"
    assert payload["approval_gate"]["decision"] == "invalidated"
    assert payload["approval_gate"]["reason"] == "planning_artifacts_changed"
    assert payload["readiness"]["blocked_by"] == ["approval_required"]
    assert payload["readiness"]["approval_gate"]["state"] == "invalidated"


def test_autoplan_invalid_configuration_logs_failure_context(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_planning_config(tmp_path, autoplan_overrides={"stop_on_owner": [123]})
    create_feature(tmp_path, monkeypatch, "discovery_pending")

    result = run_cli(tmp_path, "throughput-acceleration-workflow", "--json")

    assert result.returncode == 2
    assert "stop_on_owner entries must be strings" in result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["failure_context"]["reason_code"] == "invalid_configuration"
    assert payload["failure_context"]["improvement_suggestions"]
    events = read_jsonl(Path(payload["event_log_path"]))
    assert events[-1]["event"] == "failure"
    assert events[-1]["reason_code"] == "invalid_configuration"


def test_autoplan_routes_subfeature_stub_back_to_discover(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_planning_config(tmp_path)
    subfeature_path = create_subfeature(tmp_path, monkeypatch)

    result = run_cli(tmp_path, str(subfeature_path.relative_to(tmp_path)), "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["target_kind"] == "subfeature"
    assert payload["planning_status"] == "discovery_pending"
    assert payload["subfeature_status"] == "draft"
    assert payload["subfeature_discover_stub"] is True
    assert payload["next_owner"] == "discover"
    assert payload["action"] == "run_discover"


def test_autoplan_routes_authored_subfeature_discovery_to_assess(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_planning_config(tmp_path)
    subfeature_path = create_subfeature(tmp_path, monkeypatch, authored_discover=True)

    result = run_cli(tmp_path, str(subfeature_path.relative_to(tmp_path)), "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["target_kind"] == "subfeature"
    assert payload["planning_status"] == "discovery_pending"
    assert payload["subfeature_status"] == "draft"
    assert payload["subfeature_discover_stub"] is False
    assert payload["next_owner"] == "assess"
    assert payload["action"] == "run_assess"


def test_autoplan_owner_chain_hands_off_authored_subfeature_to_assess(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_planning_config(
        tmp_path,
        autoplan_overrides={
            "execute_owner_chain": True,
        },
    )
    subfeature_path = create_subfeature(tmp_path, monkeypatch, authored_discover=True)

    result = run_cli(tmp_path, str(subfeature_path.relative_to(tmp_path)), "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["next_owner"] == "assess"
    assert payload["action"] == "run_assess"
    assert payload["owner_chain"]["stop_reason"]["kind"] == "missing_required_input"
    assert payload["owner_handoff"]["should_invoke_skill"] is True
    assert payload["owner_handoff"]["owner"] == "assess"
    assert payload["owner_handoff"]["missing_files"] == ["impact-analysis.md"]


def test_autoplan_requires_commit_for_approved_subfeature_before_slice(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_planning_config(tmp_path)
    subfeature_path = prepare_approved_subfeature(tmp_path, monkeypatch, ready_slice_ids=["TCS-001"])
    commit_all(tmp_path, "Initial subfeature packet")

    metadata_path = subfeature_path / ".subfeature-meta.json"
    metadata = read_json(metadata_path)
    metadata["approval_note"] = "Approved and waiting for planning commit."
    metadata_path.write_text(json.dumps(metadata) + "\n", encoding="utf-8")

    result = run_cli(tmp_path, str(subfeature_path.relative_to(tmp_path)), "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["planning_status"] == "slice_ready"
    assert payload["next_owner"] == "commit"
    assert payload["action"] == "commit_planning"
    assert payload["approval_gate"]["decision"] == "approved"
    assert payload["readiness"]["blocked_by"] == ["commit_checkpoint"]
    assert payload["readiness"]["stop_reason"]["kind"] == "commit_checkpoint"
    assert payload["readiness"]["commit_checkpoint"]["required"] is True
    assert any(".subfeature-meta.json" in line for line in payload["dirty_worktree_paths"])


def test_autoplan_hands_off_to_slice_after_approved_subfeature_is_committed(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_planning_config(tmp_path)
    subfeature_path = prepare_approved_subfeature(tmp_path, monkeypatch, ready_slice_ids=["TCS-001"])
    commit_all(tmp_path, "Approve subfeature planning packet")

    result = run_cli(tmp_path, str(subfeature_path.relative_to(tmp_path)), "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["planning_status"] == "slice_ready"
    assert payload["next_owner"] == "slice"
    assert payload["action"] == "bootstrap_slice"
    assert payload["approval_gate"]["decision"] == "approved"
    assert payload["readiness"]["blocked_by"] == []
    assert payload["readiness"]["commit_checkpoint"]["required"] is False
