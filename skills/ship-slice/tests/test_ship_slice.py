from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


SHIP_SLICE_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ship_slice.py"
EXECUTION_SCRIPT = (
    Path(__file__).resolve().parents[2] / "guide-execution" / "scripts" / "manage_execution.py"
)
RUNTIME_HANDOFF = Path(__file__).resolve().parents[3] / "lib" / "workflow_runtime" / "handoff.py"


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


def write_execution_config(root: Path) -> None:
    skills_dir = root / ".skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    (skills_dir / "execution.json").write_text(
        json.dumps(
            {
                "slice_dir": "slices",
                "preferred_workflow": "TDD",
                "auto_start_implementation": True,
            }
        )
        + "\n",
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
    if status in {"blueprint_ready", "execution_ready", "closed"}:
        (slice_dir / "blueprint.md").write_text("# blueprint\n", encoding="utf-8")
    rows = execution.parse_registry()
    row = execution.resolve_slice(rows, slice_id)
    assert row is not None
    if status != "draft":
        ok, message = execution.update_slice_status(rows, row, status, force=(status == "closed"))
        assert ok, message
    return slice_dir


def run_cli(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(SHIP_SLICE_SCRIPT), *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )


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
