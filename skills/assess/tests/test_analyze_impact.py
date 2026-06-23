import importlib.util
import json
import sys
from pathlib import Path


IMPACT_SCRIPT = Path(__file__).resolve().parents[3] / "src" / "sirius_skills" / "commands" / "analyze_impact.py"
SUBFEATURE_SCRIPT = (
    Path(__file__).resolve().parents[3] / "src" / "sirius_skills" / "commands" / "manage_subfeatures.py"
)
PLANNING_SCRIPT = (
    Path(__file__).resolve().parents[3] / "src" / "sirius_skills" / "commands" / "manage_planning.py"
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


def setup_feature(tmp_path: Path):
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
    write_file(feature_dir / "discover.md", "# Discover\n")
    write_file(feature_dir / "system-design.md", "# Design\n")
    write_file(
        feature_dir / "user-stories.md",
        "# Stories\n\n- **CHK-01 (M)**: Update checkout flow.\n- **CHK-02 (S)**: Preserve guest checkout.\n",
    )
    write_file(
        feature_dir / "slice-planning.md",
        "# Slice Planning\n\n## 2. Story Decisions\n\n| Story ID | Story Size | Story Risk | Decision | Reason | Output Slice Count |\n| --- | --- | --- | --- | --- | --- |\n| CHK-01 | M | medium | keep | Coherent | 1 |\n| CHK-02 | S | low | keep | Small | 1 |\n\n## 3. Increment Plan\n\n| Increment | Goal / User-Visible Value | Included Story IDs | Planned Slice IDs | Demo / Verification Outcome | Notes |\n| --- | --- | --- | --- | --- | --- |\n| I1 | Baseline checkout | CHK-01 | CHK-101 | Flow works |  |\n\n## 4. Execution Slice Backlog\n\n| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n| CHK-101 | CHK-01 | Update checkout | Summary | checkout | primary | pytest | create slice |  | yes |\n| CHK-102 | CHK-02 | Guest checkout | Summary | checkout | primary | pytest | create slice | CHK-101 | yes |\n",
    )
    write_file(
        feature_dir / "slice-traceability.md",
        "# Traceability\n\n| Story ID | Story Title | Planned Slice IDs | Notes |\n| --- | --- | --- | --- |\n| CHK-01 | Update checkout flow | CHK-101 | Note |\n| CHK-02 | Preserve guest checkout | CHK-102 | Note |\n",
    )
    planning_module.sync_registry()
    return feature_dir


def add_subfeature(tmp_path: Path, monkeypatch):
    subfeature_module = load_module(SUBFEATURE_SCRIPT, "manage_subfeatures")
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
    return subfeature_module


def test_analyze_generates_impact_analysis_and_updates_metadata(tmp_path, monkeypatch):
    impact_module = load_module(IMPACT_SCRIPT, "analyze_impact")
    monkeypatch.chdir(tmp_path)
    feature_dir = setup_feature(tmp_path)
    add_subfeature(tmp_path, monkeypatch)

    assert run_cli(
        impact_module,
        "analyze_impact.py",
        monkeypatch,
        "checkout",
        "replace-legacy-flow",
    ) == 0

    subfeature_dir = feature_dir / "subfeatures" / "replace-legacy-flow"
    impact_text = (subfeature_dir / "impact-analysis.md").read_text(encoding="utf-8")
    metadata = json.loads((subfeature_dir / ".subfeature-meta.json").read_text(encoding="utf-8"))
    planning_module = load_module(PLANNING_SCRIPT, "manage_planning_for_assess")
    planning_meta = planning_module.read_metadata(str(subfeature_dir))

    assert "docs/features/checkout/discover.md" in impact_text
    assert "`CHK-01`" in impact_text
    assert "`CHK-102`" in impact_text
    assert "`I1`" in impact_text
    assert metadata["status"] == "impact_ready"
    assert not (subfeature_dir / ".planning-meta.json").exists()
    assert planning_meta["status"] == "discovery_ready"
    assert metadata["affected_artifacts"] == [
        "docs/features/checkout/discover.md",
        "docs/features/checkout/system-design.md",
        "docs/features/checkout/user-stories.md",
        "docs/features/checkout/slice-planning.md",
        "docs/features/checkout/slice-traceability.md",
    ]
    assert metadata["affected_story_ids"] == ["CHK-01", "CHK-02"]
    assert metadata["affected_slice_ids"] == ["CHK-101", "CHK-102"]


def test_analyze_accepts_manual_additions(tmp_path, monkeypatch):
    impact_module = load_module(IMPACT_SCRIPT, "analyze_impact")
    monkeypatch.chdir(tmp_path)
    feature_dir = setup_feature(tmp_path)
    add_subfeature(tmp_path, monkeypatch)

    assert run_cli(
        impact_module,
        "analyze_impact.py",
        monkeypatch,
        "checkout",
        "replace-legacy-flow",
        "--story-id",
        "CHK-299",
        "--slice-id",
        "CHK-999",
        "--affected-artifact",
        "docs/features/checkout/custom.md",
    ) == 0

    subfeature_dir = feature_dir / "subfeatures" / "replace-legacy-flow"
    metadata = json.loads((subfeature_dir / ".subfeature-meta.json").read_text(encoding="utf-8"))

    assert "CHK-299" in metadata["affected_story_ids"]
    assert "CHK-999" in metadata["affected_slice_ids"]
    assert "docs/features/checkout/custom.md" in metadata["affected_artifacts"]


def test_analyze_refuses_to_overwrite_without_force(tmp_path, monkeypatch, capsys):
    impact_module = load_module(IMPACT_SCRIPT, "analyze_impact")
    monkeypatch.chdir(tmp_path)
    setup_feature(tmp_path)
    add_subfeature(tmp_path, monkeypatch)

    assert run_cli(
        impact_module,
        "analyze_impact.py",
        monkeypatch,
        "checkout",
        "replace-legacy-flow",
    ) == 0
    assert run_cli(
        impact_module,
        "analyze_impact.py",
        monkeypatch,
        "checkout",
        "replace-legacy-flow",
    ) == 2

    captured = capsys.readouterr()
    assert "already exists" in captured.err

    assert run_cli(
        impact_module,
        "analyze_impact.py",
        monkeypatch,
        "checkout",
        "replace-legacy-flow",
        "--force",
    ) == 0
