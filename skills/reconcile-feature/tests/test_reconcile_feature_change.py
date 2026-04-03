import importlib.util
import json
import sys
from pathlib import Path


RECONCILE_SCRIPT = (
    Path(__file__).resolve().parents[1] / "scripts" / "reconcile_feature_change.py"
)
CHANGE_SCRIPT = (
    Path(__file__).resolve().parents[2] / "evolve-feature" / "scripts" / "manage_feature_changes.py"
)
EXECUTION_SCRIPT = (
    Path(__file__).resolve().parents[2] / "guide-execution" / "scripts" / "manage_execution.py"
)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_cli(module, script_name: str, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", [script_name, *args])
    return module.main()


def write_file(path: Path, content: str = "# doc\n"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def setup_feature(tmp_path: Path) -> Path:
    feature_dir = tmp_path / "docs" / "features" / "checkout"
    feature_dir.mkdir(parents=True, exist_ok=True)
    (tmp_path / ".skills").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".skills" / "planning.json").write_text(
        json.dumps({"planning_dir": "docs/features"}) + "\n", encoding="utf-8"
    )
    (feature_dir / ".planning-meta.json").write_text(
        json.dumps(
            {
                "feature_slug": "checkout",
                "status": "planning_reviewed",
                "created_at": "2026-01-01T00:00:00",
                "updated_at": "2026-01-01T00:00:00",
                "requires_ui_flow": False,
                "review_note": "ready",
                "ready_slice_ids": ["CHK-101"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    write_file(feature_dir / "discover.md", "# Discover\n\nCanonical discovery baseline.\n")
    write_file(feature_dir / "system-design.md", "# System Design\n\nCanonical design baseline.\n")
    write_file(feature_dir / "slice-planning.md", "# Slice Planning\n\nCanonical slice planning baseline.\n")
    write_file(
        feature_dir / "slice-traceability.md",
        "# Slice Traceability\n\nCanonical traceability baseline.\n",
    )
    return feature_dir


def ensure_execution_registry(tmp_path: Path, monkeypatch):
    manage_execution = load_module(EXECUTION_SCRIPT, "manage_execution")
    monkeypatch.chdir(tmp_path)
    assert run_cli(manage_execution, "manage_execution.py", monkeypatch, "init", "slices") == 0
    return manage_execution


def add_slice_with_status(
    manage_execution, monkeypatch, slice_id: str, feature_name: str, status: str
) -> None:
    assert (
        run_cli(manage_execution, "manage_execution.py", monkeypatch, "add", slice_id, feature_name)
        == 0
    )
    slice_dir = Path("slices") / f"{slice_id}-{feature_name.lower().replace(' ', '-')}"
    write_file(slice_dir / "brief.md", "# Slice Brief\n\n## 3. Functional Requirements\n\n- FR\n")
    (slice_dir / "checklists").mkdir()
    write_file(
        slice_dir / "checklists" / "requirements.md",
        "- [x] FR requirements captured\n",
    )
    assert (
        run_cli(manage_execution, "manage_execution.py", monkeypatch, "set-status", slice_id, "brief_ready")
        == 0
    )
    write_file(slice_dir / "blueprint.md", "# Implementation Plan\n\n- Validation:\n  - [ ] V001\n")
    assert (
        run_cli(
            manage_execution, "manage_execution.py", monkeypatch, "set-status", slice_id, "blueprint_ready"
        )
        == 0
    )
    if status in {"execution_ready", "closed"}:
        assert (
            run_cli(
                manage_execution,
                "manage_execution.py",
                monkeypatch,
                "set-status",
                slice_id,
                "execution_ready",
            )
            == 0
        )
    if status == "closed":
        assert (
            run_cli(manage_execution, "manage_execution.py", monkeypatch, "set-status", slice_id, "closed")
            == 0
        )


def prepare_reviewed_change(tmp_path: Path, monkeypatch):
    reconcile_module = load_module(RECONCILE_SCRIPT, "reconcile_feature_change")
    change_module = load_module(CHANGE_SCRIPT, "manage_feature_changes")
    feature_dir = setup_feature(tmp_path)

    assert run_cli(
        change_module,
        "manage_feature_changes.py",
        monkeypatch,
        "add",
        "checkout",
        "replace-legacy-flow",
        "--type",
        "superseding",
        "--summary",
        "Replace the legacy checkout path",
    ) == 0

    change_dir = feature_dir / "changes" / "replace-legacy-flow"
    write_file(change_dir / "impact-analysis.md", "# Impact Analysis\n\nChange impacts checkout.\n")
    write_file(change_dir / "system-design.md", "# System Design\n\nAdopt the new checkout design.\n")
    write_file(
        change_dir / "slice-planning.md",
        "# Slice Planning\n\n"
        "## 4. Execution Slice Backlog\n\n"
        "| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        "| CHK-101 | CHK-01 | Replace legacy flow | Implement the new checkout path. | `checkout/` | primary | `pytest -q` | create slice |  | yes |\n",
    )
    write_file(
        change_dir / "slice-traceability.md",
        "# Slice Traceability\n\nTrack replacement checkout slices.\n",
    )

    metadata = json.loads((change_dir / ".feature-change-meta.json").read_text(encoding="utf-8"))
    metadata["affected_story_ids"] = ["CHK-01"]
    metadata["affected_slice_ids"] = ["CHK-101"]
    (change_dir / ".feature-change-meta.json").write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )

    assert run_cli(
        change_module,
        "manage_feature_changes.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "impact_ready",
    ) == 0
    assert run_cli(
        change_module,
        "manage_feature_changes.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "design_ready",
    ) == 0
    assert run_cli(
        change_module,
        "manage_feature_changes.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "breakdown_ready",
    ) == 0
    assert run_cli(
        change_module,
        "manage_feature_changes.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "reviewed",
        "--review-note",
        "Approved for reconciliation into the canonical checkout docs.",
    ) == 0

    return reconcile_module, change_module, feature_dir, change_dir


def test_reconcile_archives_completed_feature_artifacts_and_closes_change(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    reconcile_module, _, feature_dir, change_dir = prepare_reviewed_change(
        tmp_path, monkeypatch
    )
    manage_execution = ensure_execution_registry(tmp_path, monkeypatch)
    add_slice_with_status(manage_execution, monkeypatch, "CHK-101", "Checkout Flow", "closed")

    assert run_cli(
        reconcile_module,
        "reconcile_feature_change.py",
        monkeypatch,
        "checkout",
        "replace-legacy-flow",
    ) == 0

    canonical_design = (feature_dir / "system-design.md").read_text(encoding="utf-8")
    canonical_planning = (feature_dir / "slice-planning.md").read_text(encoding="utf-8")
    archived_planning = next((feature_dir / ".archived" / "planning").glob("*/slice-planning.md"))
    archived_traceability = next(
        (feature_dir / ".archived" / "planning").glob("*/slice-traceability.md")
    )
    archived_slice_dir = tmp_path / "slices" / ".archived" / "CHK-101-checkout-flow"
    reconciliation = (change_dir / "reconciliation.md").read_text(encoding="utf-8")
    history = (feature_dir / "changes" / "history.md").read_text(encoding="utf-8")
    change_meta = json.loads((change_dir / ".feature-change-meta.json").read_text(encoding="utf-8"))
    planning_meta = json.loads((feature_dir / ".planning-meta.json").read_text(encoding="utf-8"))

    assert "## Reconciled Change Packet: replace-legacy-flow" in canonical_design
    assert "Detailed execution planning was archived after feature completion." in canonical_planning
    assert "## Reconciled Change Packet: replace-legacy-flow" in archived_planning.read_text(
        encoding="utf-8"
    )
    assert "| CHK-101 | CHK-01 | Replace legacy flow |" in archived_planning.read_text(
        encoding="utf-8"
    )
    assert "Track replacement checkout slices." in archived_traceability.read_text(encoding="utf-8")
    assert archived_slice_dir.exists()
    assert "### Feature Completion" in history
    assert "`CHK-101`" in history
    assert "slices/.archived/CHK-101-checkout-flow/" in history
    assert "## Archived Planning Files" in reconciliation
    assert change_meta["status"] == "closed"
    assert change_meta["planning_archive_targets"]
    assert change_meta["archived_slice_paths"] == ["slices/.archived/CHK-101-checkout-flow/"]
    assert planning_meta["feature_completed_at"]
    assert planning_meta["archived_slice_paths"] == ["slices/.archived/CHK-101-checkout-flow/"]


def test_reconcile_requires_planned_slices_to_be_closed(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    reconcile_module, _, _, _ = prepare_reviewed_change(tmp_path, monkeypatch)
    manage_execution = ensure_execution_registry(tmp_path, monkeypatch)
    add_slice_with_status(
        manage_execution, monkeypatch, "CHK-101", "Checkout Flow", "execution_ready"
    )

    assert run_cli(
        reconcile_module,
        "reconcile_feature_change.py",
        monkeypatch,
        "checkout",
        "replace-legacy-flow",
    ) == 2

    captured = capsys.readouterr()
    assert "all planned slices" in captured.err
    assert "open slices: CHK-101" in captured.err


def test_reconcile_requires_reviewed_state(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    reconcile_module = load_module(RECONCILE_SCRIPT, "reconcile_feature_change")
    change_module = load_module(CHANGE_SCRIPT, "manage_feature_changes")
    feature_dir = setup_feature(tmp_path)

    assert run_cli(
        change_module,
        "manage_feature_changes.py",
        monkeypatch,
        "add",
        "checkout",
        "replace-legacy-flow",
    ) == 0
    change_dir = feature_dir / "changes" / "replace-legacy-flow"
    write_file(change_dir / "system-design.md", "# System Design\n\nChanged design.\n")

    assert run_cli(
        reconcile_module,
        "reconcile_feature_change.py",
        monkeypatch,
        "checkout",
        "replace-legacy-flow",
    ) == 2

    captured = capsys.readouterr()
    assert "must be in 'reviewed' status" in captured.err
