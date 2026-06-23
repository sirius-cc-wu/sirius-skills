from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
LIB_DIR = REPO_ROOT / "lib"
for path in (SRC_DIR, LIB_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from sirius_skills.commands import learn


def write_learning(repo_root: Path, payload: dict[str, object]) -> None:
    learnings_path = repo_root / ".skills" / "learnings.jsonl"
    learnings_path.parent.mkdir(parents=True, exist_ok=True)
    with learnings_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def test_package_learn_query_outputs_matching_records(tmp_path: Path, capsys) -> None:
    write_learning(
        tmp_path,
        {
            "id": "L001",
            "scope": "checkout-flow",
            "topic": "Prefer small slices",
            "guidance": "Keep each slice independently reviewable.",
            "skill": "ship",
            "state": "active",
            "evidence_refs": [],
            "recorded_at": "2026-04-22T00:00:00+00:00",
            "updated_at": "2026-04-22T00:00:00+00:00",
        },
    )
    write_learning(
        tmp_path,
        {
            "id": "L002",
            "scope": "other-flow",
            "topic": "Ignore me",
            "guidance": "Not in scope.",
            "skill": "ship",
            "state": "active",
            "evidence_refs": [],
            "recorded_at": "2026-04-22T00:00:00+00:00",
            "updated_at": "2026-04-22T00:00:00+00:00",
        },
    )

    result = learn.main(
        [
            "--repo-root",
            str(tmp_path),
            "query",
            "checkout-flow",
            "--skill",
            "ship",
            "--json",
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["count"] == 1
    assert payload["learnings"][0]["id"] == "L001"


def test_package_learn_promote_updates_state(tmp_path: Path, capsys) -> None:
    write_learning(
        tmp_path,
        {
            "id": "L003",
            "scope": "checkout-flow",
            "topic": "Check learnings",
            "guidance": "Load active learnings first.",
            "skill": "autoplan",
            "state": "candidate",
            "evidence_refs": [],
            "recorded_at": "2026-04-22T00:00:00+00:00",
            "updated_at": "2026-04-22T00:00:00+00:00",
        },
    )

    result = learn.main(["--repo-root", str(tmp_path), "promote", "L003", "--json"])

    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["learning"]["state"] == "active"


def test_package_learn_unknown_id_returns_error(tmp_path: Path, capsys) -> None:
    result = learn.main(["--repo-root", str(tmp_path), "promote", "missing"])

    captured = capsys.readouterr()
    assert result == 1
    assert "Unknown learning id: missing" in captured.err
