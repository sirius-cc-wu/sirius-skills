from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LIB_DIR = REPO_ROOT / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from workflow_runtime import (
    CheckpointRecord,
    HandoffPayload,
    LearningRecord,
    append_event,
    append_learning,
    detect_scope_spillover,
    load_checkpoint,
    mark_checkpoint_stale,
    query_learnings,
    read_events,
    read_handoff_payload,
    snapshot_dirty_worktree,
    update_learning_state,
    write_checkpoint,
    write_handoff_payload,
)


def test_handoff_payload_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "handoff.json"
    payload = HandoffPayload(
        target_type="feature",
        target_id="throughput-acceleration-workflow",
        planned_slice_id="taw-runtime-foundation",
        execution_slice_id="taw-runtime-foundation",
        execution_slice_path="slices/taw-runtime-foundation/",
        slice_status="brief_ready",
        next_owner="blueprint",
        action="resume_active_slice",
    )

    write_handoff_payload(path, payload)

    loaded = read_handoff_payload(path)
    assert loaded == payload


def test_checkpoint_round_trip_and_stale_marker(tmp_path: Path) -> None:
    path = tmp_path / "checkpoints" / "run.json"
    record = CheckpointRecord(run_id="run-1", state="blocked", payload={"slice": "taw-runtime"})

    write_checkpoint(path, record)
    loaded = load_checkpoint(path)
    assert loaded == record

    stale = mark_checkpoint_stale(path, "repo_artifacts_changed")
    assert stale.stale_reason == "repo_artifacts_changed"
    assert load_checkpoint(path).stale_reason == "repo_artifacts_changed"


def test_event_log_append_and_read(tmp_path: Path) -> None:
    path = tmp_path / "execution-log.jsonl"

    append_event(path, {"event": "checkpoint_written", "slice_id": "taw-runtime-foundation"})
    append_event(path, {"event": "resume", "slice_id": "taw-runtime-foundation"})

    assert [entry["event"] for entry in read_events(path)] == [
        "checkpoint_written",
        "resume",
    ]


def test_learning_queries_and_state_updates(tmp_path: Path) -> None:
    path = tmp_path / "learnings.jsonl"
    append_learning(
        path,
        LearningRecord(
            id="L001",
            scope="throughput-acceleration-workflow",
            topic="runtime",
            guidance="keep runtime supplemental",
            skill="ship",
            state="candidate",
            evidence_refs=["system-design.md"],
            recorded_at="2026-04-22T10:00:00",
            updated_at="2026-04-22T10:00:00",
        ),
    )

    matches = query_learnings(path, scope="throughput-acceleration-workflow", states=["candidate"])
    assert [record.id for record in matches] == ["L001"]

    updated = update_learning_state(path, "L001", "active")
    assert updated.state == "active"
    assert [record.state for record in query_learnings(path, states=["active"])] == ["active"]


def test_detect_scope_spillover_reports_changes_outside_allowed_paths() -> None:
    before_snapshot = {
        "owned.py": "file:before-owned",
        "baseline.txt": "file:before-baseline",
    }
    after_snapshot = {
        "owned.py": "file:after-owned",
        "baseline.txt": "file:before-baseline",
        "spill.txt": "file:new-spill",
    }

    assert detect_scope_spillover(
        before_snapshot,
        after_snapshot,
        allowed_paths=["owned.py"],
    ) == ["spill.txt"]


def test_snapshot_dirty_worktree_respects_ignored_prefixes(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    tracked = tmp_path / "tracked.txt"
    tracked.write_text("baseline\n", encoding="utf-8")
    subprocess.run(
        ["git", "add", "tracked.txt"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "baseline"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    (tmp_path / ".skills" / "runtime").mkdir(parents=True)
    (tmp_path / ".skills" / "runtime" / "checkpoint.json").write_text("{}", encoding="utf-8")
    tracked.write_text("changed\n", encoding="utf-8")

    dirty_lines, snapshot = snapshot_dirty_worktree(
        tmp_path,
        ignored_prefixes=(".skills/runtime/",),
    )

    assert all(".skills/runtime/" not in line for line in dirty_lines)
    assert sorted(snapshot) == ["tracked.txt"]
