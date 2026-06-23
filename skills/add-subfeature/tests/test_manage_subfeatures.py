import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[3] / "src" / "sirius_skills" / "commands" / "manage_subfeatures.py"
PLANNING_SCRIPT_PATH = (
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
    planning_module = load_module(PLANNING_SCRIPT_PATH, "manage_planning")
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
    return feature_dir


def write_execution_config(scope_root: Path):
    skills_dir = scope_root / ".skills"
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


def test_init_feature_creates_subfeature_registry_files(tmp_path, monkeypatch):
    module = load_module(SCRIPT_PATH, "manage_subfeatures")
    monkeypatch.chdir(tmp_path)
    feature_dir = setup_feature(tmp_path)

    assert run_cli(module, "manage_subfeatures.py", monkeypatch, "init-feature", "checkout") == 0

    subfeatures_dir = feature_dir / "subfeatures"
    assert (subfeatures_dir / "README.md").exists()
    registry = json.loads((subfeatures_dir / "registry.json").read_text(encoding="utf-8"))
    assert registry["subfeatures"] == []


def test_add_creates_durable_subfeature_and_updates_planning_registry(tmp_path, monkeypatch):
    module = load_module(SCRIPT_PATH, "manage_subfeatures")
    planning_module = load_module(PLANNING_SCRIPT_PATH, "manage_planning_for_add")
    monkeypatch.chdir(tmp_path)
    feature_dir = setup_feature(tmp_path)

    assert (
        run_cli(
            module,
            "manage_subfeatures.py",
            monkeypatch,
            "add",
            "checkout",
            "replace-legacy-flow",
            "--type",
            "superseding",
            "--summary",
            "Replace the legacy checkout path",
        )
        == 0
    )

    subfeature_dir = feature_dir / "subfeatures" / "replace-legacy-flow"
    metadata = json.loads((subfeature_dir / ".subfeature-meta.json").read_text(encoding="utf-8"))
    registry = json.loads((feature_dir / "subfeatures" / "registry.json").read_text(encoding="utf-8"))
    planning_registry = json.loads((tmp_path / "docs" / "features" / "registry.json").read_text(encoding="utf-8"))
    discover = (subfeature_dir / "discover.md").read_text(encoding="utf-8")
    planning_meta = planning_module.read_metadata(str(subfeature_dir))

    assert metadata["subfeature_id"] == "replace-legacy-flow"
    assert metadata["parent_feature_slug"] == "checkout"
    assert metadata["status"] == "draft"
    assert metadata["approval_status"] == "pending"
    assert metadata["subfeature_type"] == "superseding"
    assert metadata["summary"] == "Replace the legacy checkout path"
    assert metadata["ready_slice_ids"] == []
    assert metadata["consolidation"] is None
    assert not (subfeature_dir / ".planning-meta.json").exists()
    assert planning_meta["feature_slug"] == "replace-legacy-flow"
    assert planning_meta["status"] == "discovery_pending"
    assert registry["subfeatures"][0]["subfeature_id"] == "replace-legacy-flow"
    assert any(
        row["path"] == "docs/features/checkout/subfeatures/replace-legacy-flow/"
        for row in planning_registry["features"]
    )
    assert discover.startswith("<!-- add-subfeature:discover-stub -->")
    assert "Bootstrap stub created by `add-subfeature`." in discover
    assert "Replace this scaffold with the real discovery packet via the `discover` skill." in discover
    assert "## Subfeature Execution Planning" in discover
    assert "## Consolidation Expectations" in discover
    assert "user-facing simplification" in discover


def test_impact_ready_requires_impact_analysis_and_syncs_planning_status(tmp_path, monkeypatch, capsys):
    module = load_module(SCRIPT_PATH, "manage_subfeatures")
    planning_module = load_module(PLANNING_SCRIPT_PATH, "manage_planning_for_impact")
    monkeypatch.chdir(tmp_path)
    feature_dir = setup_feature(tmp_path)

    assert run_cli(module, "manage_subfeatures.py", monkeypatch, "add", "checkout", "replace-legacy-flow") == 0
    exit_code = run_cli(
        module,
        "manage_subfeatures.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "impact_ready",
    )
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Missing required file 'impact-analysis.md'." in captured.err

    write_file(feature_dir / "subfeatures" / "replace-legacy-flow" / "impact-analysis.md")
    assert run_cli(
        module,
        "manage_subfeatures.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "impact_ready",
        "--affected-artifact",
        "docs/features/checkout/discover.md",
        "--story-id",
        "CHK-01",
    ) == 0

    planning_meta = planning_module.read_metadata(
        str(feature_dir / "subfeatures" / "replace-legacy-flow")
    )
    assert planning_meta["status"] == "discovery_ready"


def test_guide_planning_rejects_mutating_subfeature_status(tmp_path, monkeypatch, capsys):
    module = load_module(SCRIPT_PATH, "manage_subfeatures")
    planning_module = load_module(PLANNING_SCRIPT_PATH, "manage_planning_for_guardrail")
    monkeypatch.chdir(tmp_path)
    feature_dir = setup_feature(tmp_path)

    assert run_cli(module, "manage_subfeatures.py", monkeypatch, "add", "checkout", "replace-legacy-flow") == 0
    write_file(feature_dir / "subfeatures" / "replace-legacy-flow" / "impact-analysis.md")

    exit_code = run_cli(
        planning_module,
        "manage_planning.py",
        monkeypatch,
        "set-status",
        "replace-legacy-flow",
        "planning_reviewed",
    )
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "use add-subfeature set-status instead" in captured.err


def test_reviewed_requires_review_note_and_validate_reports_success(tmp_path, monkeypatch, capsys):
    module = load_module(SCRIPT_PATH, "manage_subfeatures")
    monkeypatch.chdir(tmp_path)
    feature_dir = setup_feature(tmp_path)

    assert run_cli(module, "manage_subfeatures.py", monkeypatch, "add", "checkout", "replace-legacy-flow") == 0
    subfeature_dir = feature_dir / "subfeatures" / "replace-legacy-flow"
    write_file(subfeature_dir / "impact-analysis.md")
    write_file(subfeature_dir / "system-design.md")
    write_file(subfeature_dir / "slice-planning.md")
    write_file(subfeature_dir / "slice-traceability.md")

    assert run_cli(
        module,
        "manage_subfeatures.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "impact_ready",
    ) == 0
    assert run_cli(
        module,
        "manage_subfeatures.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "design_ready",
    ) == 0
    assert run_cli(
        module,
        "manage_subfeatures.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "breakdown_ready",
    ) == 0

    exit_code = run_cli(
        module,
        "manage_subfeatures.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "reviewed",
    )
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Reviewed state requires a non-empty review note." in captured.err

    assert run_cli(
        module,
        "manage_subfeatures.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "reviewed",
        "--review-note",
        "Reviewed and awaiting explicit human approval.",
    ) == 0

    monkeypatch.setattr(
        sys,
        "argv",
        ["manage_subfeatures.py", "validate", "checkout", "replace-legacy-flow"],
    )
    assert module.main() == 0


def test_approve_records_human_approval_and_slice_ready_handoff(tmp_path, monkeypatch):
    module = load_module(SCRIPT_PATH, "manage_subfeatures")
    planning_module = load_module(PLANNING_SCRIPT_PATH, "manage_planning_for_approval")
    monkeypatch.chdir(tmp_path)
    feature_dir = setup_feature(tmp_path)

    assert run_cli(module, "manage_subfeatures.py", monkeypatch, "add", "checkout", "replace-legacy-flow") == 0
    subfeature_dir = feature_dir / "subfeatures" / "replace-legacy-flow"
    write_file(subfeature_dir / "impact-analysis.md")
    write_file(subfeature_dir / "system-design.md")
    write_file(subfeature_dir / "slice-planning.md")
    write_file(subfeature_dir / "slice-traceability.md")

    assert run_cli(
        module,
        "manage_subfeatures.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "impact_ready",
    ) == 0
    assert run_cli(
        module,
        "manage_subfeatures.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "design_ready",
    ) == 0
    assert run_cli(
        module,
        "manage_subfeatures.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "breakdown_ready",
    ) == 0
    assert run_cli(
        module,
        "manage_subfeatures.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "reviewed",
        "--review-note",
        "Reviewed and awaiting explicit human approval.",
    ) == 0

    assert run_cli(
        module,
        "manage_subfeatures.py",
        monkeypatch,
        "approve",
        "checkout",
        "replace-legacy-flow",
        "--approved-by",
        "maintainer",
        "--approval-note",
        "Approved for execution bootstrap.",
        "--slice-id",
        "CHK-201",
    ) == 0

    metadata = json.loads((subfeature_dir / ".subfeature-meta.json").read_text(encoding="utf-8"))
    planning_meta = planning_module.read_metadata(str(subfeature_dir))

    assert metadata["approval_status"] == "approved"
    assert metadata["approved_by"] == "maintainer"
    assert metadata["approval_note"] == "Approved for execution bootstrap."
    assert metadata["ready_slice_ids"] == ["CHK-201"]
    assert metadata["approved_at"]
    assert planning_meta["status"] == "slice_ready"
    assert planning_meta["ready_slice_ids"] == ["CHK-201"]


def test_set_status_persists_normalized_consolidation_summary(tmp_path, monkeypatch):
    module = load_module(SCRIPT_PATH, "manage_subfeatures")
    monkeypatch.chdir(tmp_path)
    feature_dir = setup_feature(tmp_path)

    assert run_cli(module, "manage_subfeatures.py", monkeypatch, "add", "checkout", "replace-legacy-flow") == 0
    subfeature_dir = feature_dir / "subfeatures" / "replace-legacy-flow"
    write_file(subfeature_dir / "impact-analysis.md")

    assert run_cli(
        module,
        "manage_subfeatures.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "impact_ready",
        "--consolidation-json",
        json.dumps(
            {
                "disposition": "superseding",
                "targets": [
                    {
                        "kind": "artifact",
                        "ref": "docs/features/checkout/discover.md",
                        "change": "narrows",
                    }
                ],
                "historical_artifacts": ["docs/features/checkout/legacy.md"],
                "surface_simplifications": ["use one checkout path"],
                "justification": "Avoids parallel child workflows.",
            }
        ),
    ) == 0

    metadata = json.loads((subfeature_dir / ".subfeature-meta.json").read_text(encoding="utf-8"))
    assert metadata["consolidation"] == {
        "disposition": "superseding",
        "targets": [
            {
                "kind": "artifact",
                "ref": "docs/features/checkout/discover.md",
                "change": "narrows",
            }
        ],
        "historical_artifacts": ["docs/features/checkout/legacy.md"],
        "surface_simplifications": ["use one checkout path"],
        "justification": "Avoids parallel child workflows.",
    }


def test_finalized_warns_when_linked_execution_slices_remain_open(
    tmp_path, monkeypatch, capsys
):
    module = load_module(SCRIPT_PATH, "manage_subfeatures")
    monkeypatch.chdir(tmp_path)
    feature_dir = setup_feature(tmp_path)
    write_execution_config(tmp_path)
    (tmp_path / ".skills" / "planning.json").write_text(
        json.dumps({"planning_dir": "docs/features", "proposal_dir": "docs/proposals"}) + "\n",
        encoding="utf-8",
    )

    assert run_cli(module, "manage_subfeatures.py", monkeypatch, "add", "checkout", "replace-legacy-flow") == 0
    subfeature_dir = feature_dir / "subfeatures" / "replace-legacy-flow"
    write_file(subfeature_dir / "impact-analysis.md")
    write_file(subfeature_dir / "system-design.md")
    write_file(subfeature_dir / "slice-planning.md")
    write_file(
        subfeature_dir / "slice-traceability.md",
        "# Slice Traceability\n\n"
        "| Story ID | Increments | Planned Slice IDs | Execution Slice IDs | Notes |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| CHK-01 | I1 | CHK-101 |  | demo |\n",
    )

    assert run_cli(
        module,
        "manage_subfeatures.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "impact_ready",
    ) == 0
    assert run_cli(
        module,
        "manage_subfeatures.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "design_ready",
    ) == 0
    assert run_cli(
        module,
        "manage_subfeatures.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "breakdown_ready",
    ) == 0
    assert run_cli(
        module,
        "manage_subfeatures.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "reviewed",
        "--review-note",
        "Reviewed and awaiting explicit human approval.",
    ) == 0

    slices_dir = tmp_path / "slices"
    slices_dir.mkdir(parents=True, exist_ok=True)
    (slices_dir / "registry.json").write_text(
        json.dumps(
            {
                "slices": [
                    {
                        "id": "CHK-101",
                        "feature": "replace-legacy-flow",
                        "status": "execution_ready",
                        "path": "slices/CHK-101-replace-legacy-flow/",
                        "updated_at": "2026-01-01T00:00:00",
                        "closed_at": None,
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )

    assert run_cli(
        module,
        "manage_subfeatures.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "finalized",
    ) == 0
    captured = capsys.readouterr()

    assert "transition_open_execution_slices" in captured.out
