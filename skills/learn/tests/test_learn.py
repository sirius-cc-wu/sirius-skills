from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "skills" / "learn" / "scripts" / "learn.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module("learn", SCRIPT_PATH)


def write_learning(repo_root: Path, payload: dict[str, object]) -> None:
    learnings_path = repo_root / ".skills" / "learnings.jsonl"
    learnings_path.parent.mkdir(parents=True, exist_ok=True)
    with learnings_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def run_cli(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(SCRIPT_PATH), "--repo-root", str(repo_root), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def test_query_returns_matching_scope_and_filters(tmp_path: Path) -> None:
    write_learning(
        tmp_path,
        {
            "id": "L001",
            "scope": "throughput-acceleration-workflow",
            "topic": "Prefer explicit commit checkpoints",
            "guidance": "Keep one commit per closed slice.",
            "skill": "ship",
            "state": "active",
            "evidence_refs": ["slices/taw-runtime-foundation-add-shared-accelerator-runtime-support/"],
            "recorded_at": "2026-04-22T00:00:00+00:00",
            "updated_at": "2026-04-22T00:00:00+00:00",
        },
    )
    write_learning(
        tmp_path,
        {
            "id": "L002",
            "scope": "other-feature",
            "topic": "Ignore me",
            "guidance": "Not in scope.",
            "skill": "ship",
            "state": "candidate",
            "evidence_refs": [],
            "recorded_at": "2026-04-22T00:00:00+00:00",
            "updated_at": "2026-04-22T00:00:00+00:00",
        },
    )

    result = run_cli(
        tmp_path,
        "query",
        "throughput-acceleration-workflow",
        "--skill",
        "ship",
        "--state",
        "active",
        "--json",
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["count"] == 1
    assert payload["learnings"][0]["id"] == "L001"


def test_promote_and_prune_update_state(tmp_path: Path) -> None:
    write_learning(
        tmp_path,
        {
            "id": "L003",
            "scope": "throughput-acceleration-workflow",
            "topic": "Check active learnings before automation runs",
            "guidance": "Load active repo learnings first.",
            "skill": "autoplan",
            "state": "candidate",
            "evidence_refs": [],
            "recorded_at": "2026-04-22T00:00:00+00:00",
            "updated_at": "2026-04-22T00:00:00+00:00",
        },
    )

    promoted = run_cli(tmp_path, "promote", "L003", "--json")
    assert promoted.returncode == 0
    promoted_payload = json.loads(promoted.stdout)
    assert promoted_payload["learning"]["state"] == "active"

    pruned = run_cli(tmp_path, "prune", "L003", "--json")
    assert pruned.returncode == 0
    pruned_payload = json.loads(pruned.stdout)
    assert pruned_payload["learning"]["state"] == "pruned"


def test_unknown_learning_id_returns_error(tmp_path: Path) -> None:
    result = run_cli(tmp_path, "promote", "missing")

    assert result.returncode == 1
    assert "Unknown learning id: missing" in result.stderr


def test_resolve_learnings_path_uses_repo_relative_default() -> None:
    repo_root = Path("/tmp/example-repo")

    resolved = MODULE.resolve_learnings_path(repo_root, None)

    assert resolved == repo_root / ".skills" / "learnings.jsonl"
