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
        "# Slice Planning\n\nPlan only the replacement checkout slices.\n",
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


def test_reconcile_updates_canonical_docs_and_closes_change(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    reconcile_module, _, feature_dir, change_dir = prepare_reviewed_change(
        tmp_path, monkeypatch
    )

    assert run_cli(
        reconcile_module,
        "reconcile_feature_change.py",
        monkeypatch,
        "checkout",
        "replace-legacy-flow",
    ) == 0

    canonical_design = (feature_dir / "system-design.md").read_text(encoding="utf-8")
    canonical_planning = (feature_dir / "slice-planning.md").read_text(encoding="utf-8")
    reconciliation = (change_dir / "reconciliation.md").read_text(encoding="utf-8")
    history = (feature_dir / "changes" / "history.md").read_text(encoding="utf-8")
    metadata = json.loads((change_dir / ".feature-change-meta.json").read_text(encoding="utf-8"))

    assert "Canonical design baseline." in canonical_design
    assert "## Reconciled Change Packet: replace-legacy-flow" in canonical_design
    assert "Adopt the new checkout design." in canonical_design
    assert "Canonical slice planning baseline." in canonical_planning
    assert "Plan only the replacement checkout slices." in canonical_planning
    assert "## Canonical Files Updated" in reconciliation
    assert "docs/features/checkout/system-design.md" in reconciliation
    assert "## Closed Change: replace-legacy-flow" in history
    assert "docs/features/checkout/changes/replace-legacy-flow/" in history
    assert metadata["status"] == "closed"
    assert metadata["active_change"] is False
    assert "docs/features/checkout/system-design.md" in metadata["reconciled_files"]
    assert "docs/features/checkout/changes/history.md" in metadata["history_targets"]


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
