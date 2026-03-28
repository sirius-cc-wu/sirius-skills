import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "scaffold_breakdown.py"
CHANGE_SCRIPT_PATH = (
    Path(__file__).resolve().parents[2] / "evolve-feature" / "scripts" / "manage_feature_changes.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("scaffold_breakdown", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_change_module():
    spec = importlib.util.spec_from_file_location("manage_feature_changes", CHANGE_SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_cli(module, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["scaffold_breakdown.py", *args])
    return module.main()


def run_change_cli(module, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["manage_feature_changes.py", *args])
    return module.main()


def write_file(path: Path, content: str = "# doc\n"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def setup_feature(tmp_path: Path) -> Path:
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
    return feature_dir


def test_scaffold_defaults_to_docs_features(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "demo-feature") == 0

    target_dir = tmp_path / "docs" / "features" / "demo-feature"
    assert (target_dir / "slice-planning.md").exists()
    assert (target_dir / "slice-traceability.md").exists()


def test_scaffold_uses_planning_config_dir(tmp_path, monkeypatch):
    module = load_module()
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
    module = load_module()
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
    module = load_module()
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
    module = load_module()
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


def test_scaffold_accepts_explicit_change_packet_path(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    target = "docs/features/demo-feature/changes/replace-legacy-flow"

    assert run_cli(module, monkeypatch, target) == 0

    target_dir = tmp_path / "docs" / "features" / "demo-feature" / "changes" / "replace-legacy-flow"
    assert (target_dir / "slice-planning.md").exists()
    assert (target_dir / "slice-traceability.md").exists()


def test_scaffold_change_packet_seeds_change_context(tmp_path, monkeypatch):
    module = load_module()
    change_module = load_change_module()
    monkeypatch.chdir(tmp_path)
    feature_dir = setup_feature(tmp_path)

    assert run_change_cli(
        change_module,
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
    metadata_path = change_dir / ".feature-change-meta.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["status"] = "design_ready"
    metadata["affected_artifacts"] = [
        "docs/features/checkout/discover.md",
        "docs/features/checkout/slice-planning.md",
    ]
    metadata["affected_story_ids"] = ["CHK-01", "CHK-02"]
    metadata["affected_slice_ids"] = ["CHK-101", "CHK-102"]
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    write_file(change_dir / "impact-analysis.md", "# Impact Analysis\n")
    write_file(change_dir / "system-design.md", "# Design\n")

    target = "docs/features/checkout/changes/replace-legacy-flow"
    assert run_cli(module, monkeypatch, target) == 0

    slice_planning = (change_dir / "slice-planning.md").read_text(encoding="utf-8")
    slice_traceability = (change_dir / "slice-traceability.md").read_text(encoding="utf-8")

    assert "## 0. Change Context" in slice_planning
    assert "- Canonical feature: `checkout`" in slice_planning
    assert "- Change ID: `replace-legacy-flow`" in slice_planning
    assert "- Change type: `superseding`" in slice_planning
    assert "- `impact-analysis.md`" in slice_planning
    assert "- `CHK-01`" in slice_planning
    assert "- `CHK-101`" in slice_planning
    assert "- `docs/features/checkout/discover.md`" in slice_planning
    assert "canonical `docs/features/checkout/user-stories.md`" in slice_planning
    assert "Plan only the new or amended slices required by this change packet." in slice_planning

    assert "## Change Context" in slice_traceability
    assert "- Canonical feature: `checkout`" in slice_traceability
    assert "- Change ID: `replace-legacy-flow`" in slice_traceability
    assert "Record superseded or narrowed canonical slice IDs in `Notes`" in slice_traceability


def test_scaffold_traceability_template_uses_distinct_planned_and_execution_columns(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "demo-feature") == 0

    traceability = (
        tmp_path / "docs" / "features" / "demo-feature" / "slice-traceability.md"
    ).read_text(encoding="utf-8")
    assert "Planned Slice IDs" in traceability
    assert "Execution Slice IDs" in traceability
