from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional


SHIP_SLICE_SCRIPT = Path(__file__).resolve().parents[3] / "src" / "sirius_skills" / "commands" / "ship_slice.py"
EXECUTION_SCRIPT = (
    Path(__file__).resolve().parents[3] / "src" / "sirius_skills" / "commands" / "manage_execution.py"
)
RUNTIME_HANDOFF = Path(__file__).resolve().parents[3] / "src" / "sirius_skills" / "lib" / "workflow_runtime" / "handoff.py"


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


def commit_all(root: Path, message: str = "baseline") -> None:
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=root, check=True)


def write_execution_config(
    root: Path,
    *,
    accelerators_overrides: Optional[Dict[str, Any]] = None,
    auto_start_implementation: bool = True,
) -> None:
    skills_dir = root / ".skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    payload: Dict[str, Any] = {
        "slice_dir": "slices",
        "preferred_workflow": "TDD",
        "auto_start_implementation": auto_start_implementation,
    }
    if accelerators_overrides is not None:
        payload["accelerators"] = accelerators_overrides

    (skills_dir / "execution.json").write_text(
        json.dumps(payload) + "\n",
        encoding="utf-8",
    )


def create_slice(tmp_path: Path, monkeypatch, slice_id: str, feature: str, status: str) -> Path:
    monkeypatch.chdir(tmp_path)
    execution = load_module("manage_execution_for_ship_slice_test", EXECUTION_SCRIPT)
    _, created = execution.create_slice(slice_id, feature)
    assert created
    rows = execution.parse_registry()
    row = execution.resolve_slice(rows, slice_id)
    assert row is not None
    slice_dir = tmp_path / str(row["path"])
    if status in {"brief_ready", "blueprint_ready", "execution_ready", "closed"}:
        (slice_dir / "brief.md").write_text("# brief\n", encoding="utf-8")
        (slice_dir / "checklists").mkdir(parents=True, exist_ok=True)
        (slice_dir / "checklists" / "requirements.md").write_text(
            "- [x] requirements complete\n",
            encoding="utf-8",
        )
    rows = execution.parse_registry()
    row = execution.resolve_slice(rows, slice_id)
    assert row is not None
    if status in {"brief_ready", "blueprint_ready", "execution_ready", "closed"}:
        ok, message = execution.update_slice_status(rows, row, "brief_ready")
        assert ok, message
    if status in {"blueprint_ready", "execution_ready", "closed"}:
        (slice_dir / "blueprint.md").write_text("# blueprint\n", encoding="utf-8")
        ok, message = execution.update_slice_status(rows, row, "blueprint_ready")
        assert ok, message
    if status in {"execution_ready", "closed"} and str(row["status"]) != "execution_ready":
        ok, message = execution.update_slice_status(rows, row, "execution_ready")
        assert ok, message
    if status == "closed":
        ok, message = execution.update_slice_status(rows, row, "closed", force=True)
        assert ok, message
    assert str(row["status"]) == status
    return slice_dir


def run_cli(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "sirius_skills.cli", "ship-slice", *args],
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


def read_git_status(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.rstrip() for line in result.stdout.splitlines() if line.strip()]


def test_finish_or_resume_from_handoff_routes_draft_slice_and_writes_runtime_files(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_execution_config(tmp_path)
    create_slice(
        tmp_path,
        monkeypatch,
        "taw-ship-slice-loop",
        "Add one-slice finishing and resume orchestration",
        "draft",
    )
    handoff_module = load_module("handoff_runtime_for_ship_slice_test", RUNTIME_HANDOFF)
    handoff_path = tmp_path / "handoff.json"
    handoff_module.write_handoff_payload(
        handoff_path,
        handoff_module.HandoffPayload(
            target_type="feature",
            target_id="throughput-acceleration-workflow",
            planned_slice_id="taw-ship-slice-loop",
            execution_slice_id="taw-ship-slice-loop",
            execution_slice_path="slices/taw-ship-slice-loop-add-one-slice-finishing-and-resume-orchestration/",
            slice_status="draft",
            next_owner="brief",
            action="resume_active_slice",
        ),
    )

    result = run_cli(tmp_path, "--handoff", str(handoff_path), "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["next_owner"] == "brief"
    assert payload["action"] == "create_or_update_brief"
    assert Path(payload["checkpoint_path"]).is_file()
    assert Path(payload["event_log_path"]).is_file()
    assert payload["readiness"]["can_proceed"] is True
    assert payload["readiness"]["blocked_by"] == []


def test_finish_or_resume_uses_checkpoint_on_resume(tmp_path: Path, monkeypatch) -> None:
    init_git_repo(tmp_path)
    write_execution_config(tmp_path)
    create_slice(
        tmp_path,
        monkeypatch,
        "taw-ship-slice-loop",
        "Add one-slice finishing and resume orchestration",
        "brief_ready",
    )

    first = run_cli(tmp_path, "taw-ship-slice-loop", "--json")
    assert first.returncode == 0

    resumed = run_cli(tmp_path, "--resume", "--json")

    assert resumed.returncode == 0
    payload = json.loads(resumed.stdout)
    assert payload["slice_id"] == "taw-ship-slice-loop"
    assert payload["next_owner"] == "blueprint"


def test_finish_or_resume_routes_closed_dirty_slice_to_commit(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_execution_config(tmp_path)
    create_slice(
        tmp_path,
        monkeypatch,
        "taw-ship-slice-loop",
        "Add one-slice finishing and resume orchestration",
        "closed",
    )
    (tmp_path / "scratch.txt").write_text("dirty\n", encoding="utf-8")

    result = run_cli(tmp_path, "taw-ship-slice-loop", "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["next_owner"] == "commit"
    assert payload["action"] == "commit_completed_slice"
    assert payload["readiness"]["can_proceed"] is False
    assert payload["readiness"]["blocked_by"] == ["commit_checkpoint"]


def test_ship_slice_owner_chain_advances_to_review_boundary(tmp_path: Path, monkeypatch) -> None:
    init_git_repo(tmp_path)
    write_execution_config(
        tmp_path,
        accelerators_overrides={
            "ship_slice": {
                "execute_owner_chain": True,
            }
        },
        auto_start_implementation=False,
    )
    create_slice(
        tmp_path,
        monkeypatch,
        "taw-ship-slice-loop",
        "Add one-slice finishing and resume orchestration",
        "blueprint_ready",
    )

    result = run_cli(tmp_path, "taw-ship-slice-loop", "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["execute_owner_chain"] is True
    assert payload["slice_status"] == "execution_ready"
    assert payload["next_owner"] == "review-execution"
    assert payload["action"] == "run_review_execution"
    assert payload["owner_chain"]["stop_reason"]["kind"] == "review_boundary"
    assert payload["owner_chain"]["stop_reason"]["policy_action"] == "stop"
    assert payload["owner_chain"]["stop_reason"]["policy_source"] == "default"
    assert payload["readiness"]["can_proceed"] is False
    assert payload["readiness"]["blocked_by"] == ["review_boundary"]
    assert payload["readiness"]["stop_reason"]["kind"] == "review_boundary"
    assert payload["readiness"]["policy_action"] == "stop"
    assert payload["readiness"]["policy_source"] == "default"
    assert [step["owner"] for step in payload["owner_chain"]["steps"]] == [
        "implementation"
    ]


def test_ship_slice_owner_chain_respects_stop_owner_boundary(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_execution_config(
        tmp_path,
        accelerators_overrides={
            "ship_slice": {
                "execute_owner_chain": True,
                "stop_on_owner": ["implementation"],
            }
        },
        auto_start_implementation=False,
    )
    create_slice(
        tmp_path,
        monkeypatch,
        "taw-ship-slice-loop",
        "Add one-slice finishing and resume orchestration",
        "blueprint_ready",
    )

    result = run_cli(tmp_path, "taw-ship-slice-loop", "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["slice_status"] == "blueprint_ready"
    assert payload["next_owner"] == "implementation"
    assert payload["owner_chain"]["stop_reason"]["kind"] == "owner_stop"
    assert payload["readiness"]["can_proceed"] is False
    assert payload["readiness"]["blocked_by"] == ["owner_stop"]
    assert payload["owner_chain"]["steps"] == []


def test_ship_slice_owner_chain_reports_missing_required_input(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_execution_config(
        tmp_path,
        accelerators_overrides={
            "ship_slice": {
                "execute_owner_chain": True,
            }
        },
    )
    create_slice(
        tmp_path,
        monkeypatch,
        "taw-ship-slice-loop",
        "Add one-slice finishing and resume orchestration",
        "brief_ready",
    )
    slice_dir = tmp_path / "slices" / "taw-ship-slice-loop-add-one-slice-finishing-and-resume-orchestration"
    blueprint_path = slice_dir / "blueprint.md"
    if blueprint_path.exists():
        blueprint_path.unlink()

    result = run_cli(tmp_path, "taw-ship-slice-loop", "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["slice_status"] == "brief_ready"
    assert payload["next_owner"] == "blueprint"
    assert payload["owner_chain"]["stop_reason"]["kind"] == "missing_required_input"
    assert payload["failure_context"]["reason_code"] == "missing_required_input"
    assert payload["failure_context"]["recovery_suggestions"]
    assert payload["readiness"]["can_proceed"] is False
    assert payload["readiness"]["blocked_by"] == ["missing_required_input"]
    events = read_jsonl(Path(payload["event_log_path"]))
    assert events[-1]["event"] == "failure"
    assert events[-1]["reason_code"] == "missing_required_input"
    assert events[-1]["slice_id"] == "taw-ship-slice-loop"


def test_ship_slice_owner_chain_reports_commit_checkpoint(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_execution_config(
        tmp_path,
        accelerators_overrides={
            "ship_slice": {
                "execute_owner_chain": True,
            }
        },
    )
    create_slice(
        tmp_path,
        monkeypatch,
        "taw-ship-slice-loop",
        "Add one-slice finishing and resume orchestration",
        "closed",
    )
    (tmp_path / "scratch.txt").write_text("dirty\n", encoding="utf-8")

    result = run_cli(tmp_path, "taw-ship-slice-loop", "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["next_owner"] == "commit"
    assert payload["action"] == "commit_completed_slice"
    assert payload["owner_chain"]["stop_reason"]["kind"] == "commit_checkpoint"
    assert payload["owner_chain"]["stop_reason"]["policy_action"] == "stop"
    assert payload["owner_chain"]["stop_reason"]["policy_source"] == "default"
    assert payload["readiness"]["can_proceed"] is False
    assert payload["readiness"]["blocked_by"] == ["commit_checkpoint"]
    assert payload["readiness"]["policy_action"] == "stop"
    assert payload["readiness"]["policy_source"] == "default"


def test_ship_slice_owner_chain_reports_review_policy_continue(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_execution_config(
        tmp_path,
        accelerators_overrides={
            "ship_slice": {
                "execute_owner_chain": True,
                "continuation_policy": {"review_boundary": "continue"},
            }
        },
        auto_start_implementation=False,
    )
    create_slice(
        tmp_path,
        monkeypatch,
        "taw-ship-slice-loop",
        "Add one-slice finishing and resume orchestration",
        "blueprint_ready",
    )

    result = run_cli(tmp_path, "taw-ship-slice-loop", "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["next_owner"] == "review-execution"
    assert payload["owner_chain"]["stop_reason"]["kind"] == "review_boundary"
    assert payload["owner_chain"]["stop_reason"]["policy_action"] == "continue"
    assert payload["owner_chain"]["stop_reason"]["policy_source"] == "config"
    assert payload["readiness"]["blocked_by"] == ["review_boundary"]
    assert payload["readiness"]["policy_action"] == "continue"
    assert payload["readiness"]["policy_source"] == "config"


def test_ship_slice_policy_stop_prevents_terminal_auto_close(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_execution_config(
        tmp_path,
        accelerators_overrides={
            "ship_slice": {
                "execute_owner_chain": True,
                "auto_close": True,
                "continuation_policy": {"review_boundary": "stop"},
            }
        },
        auto_start_implementation=False,
    )
    create_slice(
        tmp_path,
        monkeypatch,
        "taw-ship-slice-loop",
        "Add one-slice finishing and resume orchestration",
        "execution_ready",
    )

    result = run_cli(tmp_path, "taw-ship-slice-loop", "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["next_owner"] == "review-execution"
    assert payload["terminal_automation"]["close_applied"] is False
    assert payload["readiness"]["policy_action"] == "stop"
    assert payload["readiness"]["policy_source"] == "config"


def test_ship_slice_tracks_owned_dirty_paths_separately_from_baseline(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_execution_config(tmp_path)
    create_slice(
        tmp_path,
        monkeypatch,
        "taw-ship-slice-loop",
        "Add one-slice finishing and resume orchestration",
        "execution_ready",
    )
    commit_all(tmp_path)
    (tmp_path / "notes.txt").write_text("baseline\n", encoding="utf-8")

    first = run_cli(tmp_path, "taw-ship-slice-loop", "--json")

    assert first.returncode == 0
    first_payload = json.loads(first.stdout)
    assert first_payload["next_owner"] == "implementation"
    assert first_payload["readiness"]["blocked_by"] == []
    assert first_payload["worktree_ownership"]["owned_dirty_paths"] == []
    assert first_payload["worktree_ownership"]["unowned_dirty_paths"] == ["notes.txt"]

    execution = load_module("manage_execution_state_test", EXECUTION_SCRIPT)
    rows = execution.parse_registry()
    row = execution.resolve_slice(rows, "taw-ship-slice-loop")
    assert row is not None
    ok, message = execution.update_slice_status(rows, row, "closed", force=True)
    assert ok, message

    (tmp_path / "owned.txt").write_text("owned\n", encoding="utf-8")

    resumed = run_cli(tmp_path, "--resume", "--json")

    assert resumed.returncode == 0
    payload = json.loads(resumed.stdout)
    assert payload["next_owner"] == "commit"
    assert payload["action"] == "commit_completed_slice"
    owned_paths = payload["worktree_ownership"]["owned_dirty_paths"]
    assert "owned.txt" in owned_paths
    assert "notes.txt" not in owned_paths
    assert payload["worktree_ownership"]["unowned_dirty_paths"] == ["notes.txt"]
    assert payload["readiness"]["blocked_by"] == ["commit_checkpoint"]


def test_ship_slice_reports_owned_file_conflict_when_baseline_file_changes(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_execution_config(
        tmp_path,
        accelerators_overrides={
            "ship_slice": {
                "continuation_policy": {
                    "review_boundary": "continue",
                    "commit_checkpoint": "continue",
                },
            }
        },
    )
    create_slice(
        tmp_path,
        monkeypatch,
        "taw-ship-slice-loop",
        "Add one-slice finishing and resume orchestration",
        "execution_ready",
    )
    commit_all(tmp_path)
    shared = tmp_path / "shared.txt"
    shared.write_text("before\n", encoding="utf-8")

    first = run_cli(tmp_path, "taw-ship-slice-loop", "--json")

    assert first.returncode == 0
    first_payload = json.loads(first.stdout)
    assert first_payload["next_owner"] == "implementation"
    shared.write_text("after\n", encoding="utf-8")

    resumed = run_cli(tmp_path, "--resume", "--json")

    assert resumed.returncode == 0
    payload = json.loads(resumed.stdout)
    assert payload["next_owner"] == "guide-execution"
    assert payload["action"] == "resolve_owned_file_conflict"
    assert payload["worktree_ownership"]["owned_file_conflict_paths"] == ["shared.txt"]
    assert payload["readiness"]["can_proceed"] is False
    assert payload["readiness"]["blocked_by"] == ["owned_file_conflict"]
    assert payload["readiness"]["stop_reason"] == {
        "kind": "owned_file_conflict",
        "paths": ["shared.txt"],
    }
    assert payload["readiness"]["policy_action"] is None
    assert payload["readiness"]["policy_source"] is None


def test_detect_scope_spillover_flags_changes_outside_owned_paths() -> None:
    module = load_module("ship_slice_scope_test", SHIP_SLICE_SCRIPT)

    spillover = module.detect_scope_spillover(
        {
            "owned.txt": "before-owned",
            "baseline.txt": "before-baseline",
        },
        {
            "owned.txt": "after-owned",
            "baseline.txt": "before-baseline",
            "spill.txt": "after-spill",
        },
        allowed_paths=["owned.txt"],
    )

    assert spillover == ["spill.txt"]


def test_ship_slice_rejects_auto_commit_without_auto_close(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_execution_config(
        tmp_path,
        accelerators_overrides={"ship_slice": {"auto_commit": True}},
    )
    create_slice(
        tmp_path,
        monkeypatch,
        "taw-ship-slice-loop",
        "Add one-slice finishing and resume orchestration",
        "closed",
    )

    result = run_cli(tmp_path, "taw-ship-slice-loop", "--json")

    assert result.returncode == 2
    assert "auto_commit requires auto_close" in result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["failure_context"]["reason_code"] == "invalid_configuration"
    events = read_jsonl(Path(payload["event_log_path"]))
    assert events[-1]["event"] == "failure"
    assert events[-1]["reason_code"] == "invalid_configuration"


def test_ship_slice_terminal_automation_formats_closes_and_commits_owned_changes(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_execution_config(
        tmp_path,
        accelerators_overrides={
            "ship_slice": {
                "execute_owner_chain": True,
                "auto_format": True,
                "auto_close": True,
                "auto_commit": True,
                "format_command": [str(tmp_path / "formatter.sh")],
                "continuation_policy": {
                    "review_boundary": "continue",
                    "commit_checkpoint": "continue",
                },
            }
        },
        auto_start_implementation=False,
    )
    create_slice(
        tmp_path,
        monkeypatch,
        "taw-ship-slice-loop",
        "Add one-slice finishing and resume orchestration",
        "execution_ready",
    )
    commit_all(tmp_path)
    (tmp_path / "notes.txt").write_text("baseline\n", encoding="utf-8")

    formatter = tmp_path / "formatter.sh"
    formatter.write_text(
        "#!/bin/sh\n"
        "for path in \"$@\"; do\n"
        "  printf '# formatted\\n' >> \"$path\"\n"
        "done\n",
        encoding="utf-8",
    )
    formatter.chmod(0o755)

    first = run_cli(tmp_path, "taw-ship-slice-loop", "--no-execute-owner-chain", "--json")

    assert first.returncode == 0
    assert json.loads(first.stdout)["next_owner"] == "implementation"
    (tmp_path / "owned.py").write_text("print('hi')\n", encoding="utf-8")

    resumed = run_cli(tmp_path, "--resume", "--execute-owner-chain", "--json")

    assert resumed.returncode == 0
    payload = json.loads(resumed.stdout)
    assert payload["slice_status"] == "closed"
    assert payload["next_owner"] == "none"
    assert payload["terminal_automation"]["format_applied"] is True
    assert payload["terminal_automation"]["close_applied"] is True
    assert payload["terminal_automation"]["commit_applied"] is True
    assert payload["readiness"]["blocked_by"] == ["review_boundary", "completed"]
    assert payload["readiness"]["policy_action"] == "continue"
    assert payload["readiness"]["policy_source"] == "config"
    assert "owned.py" in payload["terminal_automation"]["committed_paths"]

    status = read_git_status(tmp_path)
    assert any("notes.txt" in line for line in status)
    assert not any("owned.py" in line for line in status)
    assert not any("slices/" in line for line in status)

    last_subject = subprocess.run(
        ["git", "log", "-1", "--pretty=%s"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert last_subject == "ship-slice: Complete taw-ship-slice-loop"


def test_ship_slice_terminal_automation_reports_formatter_spillover(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_execution_config(
        tmp_path,
        accelerators_overrides={
            "ship_slice": {
                "execute_owner_chain": True,
                "auto_format": True,
                "auto_close": True,
                "format_command": [str(tmp_path / "formatter-spill.sh")],
                "continuation_policy": {
                    "review_boundary": "continue",
                },
            }
        },
        auto_start_implementation=False,
    )
    create_slice(
        tmp_path,
        monkeypatch,
        "taw-ship-slice-loop",
        "Add one-slice finishing and resume orchestration",
        "execution_ready",
    )
    commit_all(tmp_path)

    formatter = tmp_path / "formatter-spill.sh"
    formatter.write_text(
        "#!/bin/sh\n"
        "printf '# formatted\\n' >> \"$1\"\n"
        "printf 'spill\\n' > spill.txt\n",
        encoding="utf-8",
    )
    formatter.chmod(0o755)

    first = run_cli(tmp_path, "taw-ship-slice-loop", "--no-execute-owner-chain", "--json")

    assert first.returncode == 0
    (tmp_path / "owned.py").write_text("print('hi')\n", encoding="utf-8")

    resumed = run_cli(tmp_path, "--resume", "--execute-owner-chain", "--json")

    assert resumed.returncode == 0
    payload = json.loads(resumed.stdout)
    assert payload["next_owner"] == "guide-execution"
    assert payload["terminal_automation"]["close_applied"] is False
    assert payload["terminal_automation"]["stop_reason"] == {
        "kind": "formatter_spillover",
        "paths": ["spill.txt"],
    }
    assert payload["readiness"]["stop_reason"] == {
        "kind": "formatter_spillover",
        "paths": ["spill.txt"],
    }
    assert payload["readiness"]["policy_action"] == "continue"
    assert payload["readiness"]["policy_source"] == "config"


def test_ship_slice_terminal_automation_reports_partial_success_when_commit_fails(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    write_execution_config(
        tmp_path,
        accelerators_overrides={
            "ship_slice": {
                "execute_owner_chain": True,
                "auto_close": True,
                "auto_commit": True,
                "continuation_policy": {
                    "review_boundary": "continue",
                    "commit_checkpoint": "continue",
                },
            }
        },
        auto_start_implementation=False,
    )
    create_slice(
        tmp_path,
        monkeypatch,
        "taw-ship-slice-loop",
        "Add one-slice finishing and resume orchestration",
        "execution_ready",
    )
    commit_all(tmp_path)

    first = run_cli(tmp_path, "taw-ship-slice-loop", "--no-execute-owner-chain", "--json")

    assert first.returncode == 0

    hook = tmp_path / ".git" / "hooks" / "pre-commit"
    hook.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    hook.chmod(0o755)
    (tmp_path / "owned.py").write_text("print('hi')\n", encoding="utf-8")

    resumed = run_cli(tmp_path, "--resume", "--execute-owner-chain", "--json")

    assert resumed.returncode == 0
    payload = json.loads(resumed.stdout)
    assert payload["slice_status"] == "closed"
    assert payload["next_owner"] == "commit"
    assert payload["terminal_automation"]["close_applied"] is True
    assert payload["terminal_automation"]["commit_applied"] is False
    assert payload["terminal_automation"]["stop_reason"]["kind"] == "commit_failed"
    assert payload["readiness"]["stop_reason"]["kind"] == "commit_failed"
    assert payload["readiness"]["policy_action"] == "continue"
    assert payload["readiness"]["policy_source"] == "config"
    assert "commit_checkpoint" in payload["readiness"]["blocked_by"]
    assert "commit_failed" in payload["readiness"]["blocked_by"]
