import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "scaffold_breakdown.py"
SUBFEATURE_SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "add-subfeature"
    / "scripts"
    / "manage_subfeatures.py"
)
PLANNING_SCRIPT_PATH = (
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


def run_cli(module, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["scaffold_breakdown.py", *args])
    return module.main()


def run_subfeature_cli(module, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["manage_subfeatures.py", *args])
    return module.main()


def write_file(path: Path, content: str = "# doc\n"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def setup_feature(tmp_path: Path) -> Path:
    planning_module = load_module(PLANNING_SCRIPT_PATH, "manage_planning")
    feature_dir = tmp_path / "docs" / "features" / "checkout"
    feature_dir.mkdir(parents=True, exist_ok=True)
    (tmp_path / ".skills").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".skills" / "planning.json").write_text(
        json.dumps({"planning_dir": "docs/features"}) + "\n",
        encoding="utf-8",
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
    write_file(feature_dir / "user-stories.md", "# Stories\n")
    write_file(feature_dir / "slice-planning.md", "# Slice Planning\n")
    write_file(feature_dir / "slice-traceability.md", "# Traceability\n")
    planning_module.sync_registry()
    return feature_dir


def test_scaffold_defaults_to_docs_features(tmp_path, monkeypatch):
    module = load_module(SCRIPT_PATH, "scaffold_breakdown")
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "demo-feature") == 0

    target_dir = tmp_path / "docs" / "features" / "demo-feature"
    assert (target_dir / "slice-planning.md").exists()
    assert (target_dir / "slice-traceability.md").exists()


def test_scaffold_uses_planning_config_dir(tmp_path, monkeypatch):
    module = load_module(SCRIPT_PATH, "scaffold_breakdown")
    monkeypatch.chdir(tmp_path)

    config_dir = tmp_path / ".skills"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "planning.json").write_text(
        json.dumps({"planning_dir": "planning/features"}) + "\n",
        encoding="utf-8",
    )

    assert run_cli(module, monkeypatch, "demo-feature") == 0

    target_dir = tmp_path / "planning" / "features" / "demo-feature"
    assert (target_dir / "slice-planning.md").exists()
    assert (target_dir / "slice-traceability.md").exists()


def test_scaffold_base_dir_flag_overrides_planning_config_dir(tmp_path, monkeypatch):
    module = load_module(SCRIPT_PATH, "scaffold_breakdown")
    monkeypatch.chdir(tmp_path)

    config_dir = tmp_path / ".skills"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "planning.json").write_text(
        json.dumps({"planning_dir": "planning/features"}) + "\n",
        encoding="utf-8",
    )

    assert (
        run_cli(module, monkeypatch, "demo-feature", "--base-dir", "custom/planning")
        == 0
    )

    assert (tmp_path / "custom" / "planning" / "demo-feature" / "slice-planning.md").exists()
    assert not (tmp_path / "planning" / "features" / "demo-feature").exists()


def test_scaffold_rejects_non_string_planning_config_dir(tmp_path, monkeypatch, capsys):
    module = load_module(SCRIPT_PATH, "scaffold_breakdown")
    monkeypatch.chdir(tmp_path)

    config_dir = tmp_path / ".skills"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "planning.json").write_text(
        json.dumps({"planning_dir": 123}) + "\n",
        encoding="utf-8",
    )

    assert run_cli(module, monkeypatch, "demo-feature") == 1

    captured = capsys.readouterr()
    assert "Planning config field 'planning_dir' must be a string." in captured.err


def test_scaffold_ignores_conventions_planning_dir(tmp_path, monkeypatch):
    module = load_module(SCRIPT_PATH, "scaffold_breakdown")
    monkeypatch.chdir(tmp_path)

    config_dir = tmp_path / ".skills"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "conventions.json").write_text(
        json.dumps({"planning_dir": "legacy/features"}) + "\n",
        encoding="utf-8",
    )

    assert run_cli(module, monkeypatch, "demo-feature") == 0

    assert (tmp_path / "docs" / "features" / "demo-feature" / "slice-planning.md").exists()
    assert not (tmp_path / "legacy" / "features" / "demo-feature").exists()


def test_scaffold_accepts_explicit_subfeature_path(tmp_path, monkeypatch):
    module = load_module(SCRIPT_PATH, "scaffold_breakdown")
    monkeypatch.chdir(tmp_path)

    target = "docs/features/demo-feature/subfeatures/replace-legacy-flow"

    assert run_cli(module, monkeypatch, target) == 0

    target_dir = tmp_path / "docs" / "features" / "demo-feature" / "subfeatures" / "replace-legacy-flow"
    assert (target_dir / "slice-planning.md").exists()
    assert (target_dir / "slice-traceability.md").exists()


def test_scaffold_subfeature_seeds_subfeature_context(tmp_path, monkeypatch):
    module = load_module(SCRIPT_PATH, "scaffold_breakdown")
    subfeature_module = load_module(SUBFEATURE_SCRIPT_PATH, "manage_subfeatures")
    monkeypatch.chdir(tmp_path)
    feature_dir = setup_feature(tmp_path)

    assert run_subfeature_cli(
        subfeature_module,
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
    metadata_path = subfeature_dir / ".subfeature-meta.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["status"] = "design_ready"
    metadata["affected_artifacts"] = [
        "docs/features/checkout/discover.md",
        "docs/features/checkout/slice-planning.md",
    ]
    metadata["affected_story_ids"] = ["CHK-01", "CHK-02"]
    metadata["affected_slice_ids"] = ["CHK-101", "CHK-102"]
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    write_file(subfeature_dir / "impact-analysis.md", "# Impact Analysis\n")
    write_file(subfeature_dir / "system-design.md", "# Design\n")

    target = "docs/features/checkout/subfeatures/replace-legacy-flow"
    assert run_cli(module, monkeypatch, target) == 0

    slice_planning = (subfeature_dir / "slice-planning.md").read_text(encoding="utf-8")
    slice_traceability = (subfeature_dir / "slice-traceability.md").read_text(encoding="utf-8")

    assert "## 0. Subfeature Context" in slice_planning
    assert "- Parent feature: `checkout`" in slice_planning
    assert "- Subfeature ID: `replace-legacy-flow`" in slice_planning
    assert "- Subfeature type: `superseding`" in slice_planning
    assert "- `impact-analysis.md`" in slice_planning
    assert "- `CHK-01`" in slice_planning
    assert "- `CHK-101`" in slice_planning
    assert "- `docs/features/checkout/discover.md`" in slice_planning
    assert "parent `docs/features/checkout/user-stories.md`" in slice_planning
    assert "Plan only the new or amended slices required by this subfeature." in slice_planning
    assert (
        "Keep this subfeature's `slice-planning.md` and `slice-traceability.md` as the execution-planning source of truth for the child capability."
        in slice_planning
    )

    assert "## Subfeature Context" in slice_traceability
    assert "- Parent feature: `checkout`" in slice_traceability
    assert "- Subfeature ID: `replace-legacy-flow`" in slice_traceability
    assert (
        "Keep subfeature-local traceability in this folder instead of folding it back into parent feature breakdown docs."
        in slice_traceability
    )
    assert "Record superseded or narrowed parent slice IDs in `Notes`" in slice_traceability


def test_scaffold_traceability_template_uses_distinct_planned_and_execution_columns(tmp_path, monkeypatch):
    module = load_module(SCRIPT_PATH, "scaffold_breakdown")
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "demo-feature") == 0

    traceability = (
        tmp_path / "docs" / "features" / "demo-feature" / "slice-traceability.md"
    ).read_text(encoding="utf-8")
    assert "Planned Slice IDs" in traceability
    assert "Execution Slice IDs" in traceability
    assert "exactly one planned slice ID" in traceability
    assert "Follow-on row for the same story" in traceability
