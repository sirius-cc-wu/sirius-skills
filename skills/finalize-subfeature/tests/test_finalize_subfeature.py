import importlib.util
import json
import sys
from pathlib import Path


FINALIZE_SCRIPT = (
    Path(__file__).resolve().parents[1] / "scripts" / "finalize_subfeature.py"
)
SUBFEATURE_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "add-subfeature"
    / "scripts"
    / "manage_subfeatures.py"
)
EXECUTION_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "guide-execution"
    / "scripts"
    / "manage_execution.py"
)
PLANNING_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "guide-planning"
    / "scripts"
    / "manage_planning.py"
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
    planning_module = load_module(PLANNING_SCRIPT, "manage_planning")
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
    planning_module.sync_registry()
    write_file(feature_dir / "discover.md", "# Discover\n\nCanonical discovery baseline.\n")
    write_file(feature_dir / "system-design.md", "# System Design\n\nCanonical design baseline.\n")
    write_file(feature_dir / "slice-planning.md", "# Slice Planning\n\nCanonical slice planning baseline.\n")
    write_file(feature_dir / "slice-traceability.md", "# Slice Traceability\n\nCanonical traceability baseline.\n")
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


def prepare_reviewed_subfeature(tmp_path: Path, monkeypatch):
    finalize_module = load_module(FINALIZE_SCRIPT, "finalize_subfeature")
    subfeature_module = load_module(SUBFEATURE_SCRIPT, "manage_subfeatures")
    feature_dir = setup_feature(tmp_path)

    assert run_cli(
        subfeature_module,
        "manage_subfeatures.py",
        monkeypatch,
        "add",
        "checkout",
        "replace-legacy-flow",
        "--type",
        "superseding",
        "--summary",
        "Replace the legacy checkout path",
    ) == 0

    subfeature_dir = feature_dir / "subfeatures" / "replace-legacy-flow"
    write_file(subfeature_dir / "discover.md", "# Discover\n\nShip a durable new checkout path.\n")
    write_file(subfeature_dir / "impact-analysis.md", "# Impact Analysis\n\nSubfeature impacts checkout.\n")
    write_file(subfeature_dir / "system-design.md", "# System Design\n\nAdopt the new checkout design.\n")
    write_file(
        subfeature_dir / "slice-planning.md",
        "# Slice Planning\n\n"
        "## 4. Execution Slice Backlog\n\n"
        "| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        "| CHK-101 | CHK-01 | Replace legacy flow | Implement the new checkout path. | `checkout/` | primary | `pytest -q` | create slice |  | yes |\n",
    )
    write_file(
        subfeature_dir / "slice-traceability.md",
        "# Slice Traceability\n\nTrack durable replacement checkout slices.\n",
    )

    metadata = json.loads((subfeature_dir / ".subfeature-meta.json").read_text(encoding="utf-8"))
    metadata["affected_story_ids"] = ["CHK-01"]
    metadata["affected_slice_ids"] = ["CHK-101"]
    (subfeature_dir / ".subfeature-meta.json").write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )

    assert run_cli(
        subfeature_module,
        "manage_subfeatures.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "impact_ready",
    ) == 0
    assert run_cli(
        subfeature_module,
        "manage_subfeatures.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "design_ready",
    ) == 0
    assert run_cli(
        subfeature_module,
        "manage_subfeatures.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "breakdown_ready",
    ) == 0
    assert run_cli(
        subfeature_module,
        "manage_subfeatures.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "reviewed",
        "--review-note",
        "Approved for durable subfeature finalization.",
    ) == 0

    return finalize_module, feature_dir, subfeature_dir


def test_finalize_removes_closed_slices_and_keeps_subfeature_artifacts(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    finalize_module, feature_dir, subfeature_dir = prepare_reviewed_subfeature(
        tmp_path, monkeypatch
    )
    manage_execution = ensure_execution_registry(tmp_path, monkeypatch)
    add_slice_with_status(manage_execution, monkeypatch, "CHK-101", "Checkout Flow", "closed")

    assert run_cli(
        finalize_module,
        "finalize_subfeature.py",
        monkeypatch,
        "checkout",
        "replace-legacy-flow",
    ) == 0

    slice_dir = tmp_path / "slices" / "CHK-101-checkout-flow"
    registry = json.loads((tmp_path / "slices" / "registry.json").read_text(encoding="utf-8"))
    subfeature_meta = json.loads((subfeature_dir / ".subfeature-meta.json").read_text(encoding="utf-8"))
    planning_meta = json.loads((subfeature_dir / ".planning-meta.json").read_text(encoding="utf-8"))
    planning_registry = json.loads(
        (tmp_path / "docs" / "features" / "registry.json").read_text(encoding="utf-8")
    )

    assert subfeature_dir.exists()
    assert not slice_dir.exists()
    assert registry["slices"] == []
    assert subfeature_meta["status"] == "finalized"
    assert subfeature_meta["finalized_at"]
    assert planning_meta["status"] == "implemented"
    assert planning_meta["ready_slice_ids"] == []
    assert any(
        row["path"] == "docs/features/checkout/subfeatures/replace-legacy-flow/"
        and row["status"] == "implemented"
        for row in planning_registry["features"]
    )
    assert (feature_dir / "discover.md").read_text(encoding="utf-8") == "# Discover\n\nCanonical discovery baseline.\n"


def test_finalize_requires_planned_slices_to_be_closed(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    finalize_module, _, _ = prepare_reviewed_subfeature(tmp_path, monkeypatch)
    manage_execution = ensure_execution_registry(tmp_path, monkeypatch)
    add_slice_with_status(manage_execution, monkeypatch, "CHK-101", "Checkout Flow", "execution_ready")

    assert run_cli(
        finalize_module,
        "finalize_subfeature.py",
        monkeypatch,
        "checkout",
        "replace-legacy-flow",
    ) == 2

    captured = capsys.readouterr()
    assert "all planned slices" in captured.err
    assert "open slices: CHK-101" in captured.err
