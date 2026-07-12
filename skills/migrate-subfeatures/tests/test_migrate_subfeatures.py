import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[3] / "src" / "sirius_skills" / "commands" / "migrate_subfeatures.py"
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
    write_file(feature_dir / "slice-planning.md", "# Slice Planning\n")
    write_file(feature_dir / "slice-traceability.md", "# Traceability\n")
    planning_module.sync_registry()
    return planning_module, feature_dir


def setup_legacy_change(feature_dir: Path, status: str = "reviewed"):
    changes_dir = feature_dir / "changes"
    change_dir = changes_dir / "replace-legacy-flow"
    change_dir.mkdir(parents=True, exist_ok=True)
    write_file(change_dir / "discover.md", "# Discover\n\nLegacy change.\n")
    write_file(change_dir / "system-design.md", "# Design\n")
    write_file(change_dir / "slice-planning.md", "# Slice Planning\n")
    write_file(change_dir / "slice-traceability.md", "# Traceability\n")

    payload = {
        "change_id": "replace-legacy-flow",
        "feature_slug": "checkout",
        "status": status,
        "created_at": "2026-01-02T00:00:00",
        "updated_at": "2026-01-03T00:00:00",
        "change_type": "superseding",
        "summary": "Replace the legacy checkout path",
        "affected_artifacts": ["docs/features/checkout/discover.md"],
        "affected_story_ids": ["CHK-01"],
        "affected_slice_ids": ["CHK-101"],
        "review_note": "Approved for migration.",
        "active_change": status != "closed",
        "reconciled_at": "2026-01-04T00:00:00" if status in {"reconciled", "closed"} else None,
        "reconciled_files": ["docs/features/checkout/discover.md"] if status in {"reconciled", "closed"} else [],
        "history_targets": [],
    }
    (change_dir / ".feature-change-meta.json").write_text(
        json.dumps(payload) + "\n",
        encoding="utf-8",
    )
    (changes_dir / "registry.json").write_text(
        json.dumps(
            {
                "changes": [
                    {
                        "change_id": "replace-legacy-flow",
                        "status": status,
                        "change_type": "superseding",
                        "updated_at": "2026-01-03T00:00:00",
                        "path": "docs/features/checkout/changes/replace-legacy-flow/",
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (changes_dir / "README.md").write_text(
        "# Feature Change Registry\n\n"
        "| Change | Status | Type | Updated | Path |\n"
        "|---|---|---|---|---|\n"
        "| replace-legacy-flow | reviewed | superseding | 2026-01-03T00:00:00 | docs/features/checkout/changes/replace-legacy-flow/ |\n",
        encoding="utf-8",
    )
    return change_dir


def test_scan_all_reports_legacy_change_candidates(tmp_path, monkeypatch, capsys):
    module = load_module(SCRIPT_PATH, "migrate_subfeatures")
    monkeypatch.chdir(tmp_path)
    _, feature_dir = setup_feature(tmp_path)
    setup_legacy_change(feature_dir)

    assert run_cli(module, "migrate_subfeatures.py", monkeypatch, "scan", "--all") == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert payload["mode"] == "scan"
    assert payload["features"][0]["feature"] == "checkout"
    assert payload["features"][0]["changes_found"] == 1
    assert payload["features"][0]["candidates"][0]["change_id"] == "replace-legacy-flow"
    assert payload["features"][0]["candidates"][0]["mapped_status"] == "reviewed"


def test_migrate_dry_run_leaves_legacy_layout_untouched(tmp_path, monkeypatch, capsys):
    module = load_module(SCRIPT_PATH, "migrate_subfeatures")
    monkeypatch.chdir(tmp_path)
    _, feature_dir = setup_feature(tmp_path)
    change_dir = setup_legacy_change(feature_dir)

    assert (
        run_cli(
            module,
            "migrate_subfeatures.py",
            monkeypatch,
            "migrate",
            "checkout",
            "--dry-run",
        )
        == 0
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert payload["dry_run"] is True
    assert payload["features"][0]["planned"][0]["change_id"] == "replace-legacy-flow"
    assert change_dir.exists()
    assert not (feature_dir / "subfeatures" / "replace-legacy-flow").exists()


def test_migrate_converts_legacy_change_packet_and_resyncs_registries(
    tmp_path, monkeypatch, capsys
):
    module = load_module(SCRIPT_PATH, "migrate_subfeatures")
    monkeypatch.chdir(tmp_path)
    _, feature_dir = setup_feature(tmp_path)
    setup_legacy_change(feature_dir)

    assert run_cli(module, "migrate_subfeatures.py", monkeypatch, "migrate", "checkout") == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    subfeature_dir = feature_dir / "subfeatures" / "replace-legacy-flow"
    metadata = json.loads((subfeature_dir / ".subfeature-meta.json").read_text(encoding="utf-8"))
    planning_module = load_module(PLANNING_SCRIPT, "manage_planning_for_migrate")
    planning_meta = planning_module.read_metadata(str(subfeature_dir))
    subfeature_registry = json.loads((feature_dir / "subfeatures" / "registry.json").read_text(encoding="utf-8"))
    planning_registry = json.loads((tmp_path / "docs" / "features" / "registry.json").read_text(encoding="utf-8"))

    assert payload["ok"] is True
    assert payload["features"][0]["migrated"][0]["change_id"] == "replace-legacy-flow"
    assert metadata["subfeature_id"] == "replace-legacy-flow"
    assert metadata["parent_feature_slug"] == "checkout"
    assert metadata["status"] == "reviewed"
    assert metadata["subfeature_type"] == "superseding"
    assert not (subfeature_dir / ".planning-meta.json").exists()
    assert planning_meta["status"] == "planning_reviewed"
    assert (subfeature_dir / "discover.md").exists()
    assert not (feature_dir / "changes").exists()
    assert subfeature_registry["subfeatures"][0]["subfeature_id"] == "replace-legacy-flow"
    assert [row["feature"] for row in planning_registry["features"]] == ["checkout"]
    assert any(
        row["path"] == "docs/features/checkout/subfeatures/replace-legacy-flow/"
        for row in planning_module.lookup_rows()
    )


def test_migrate_closed_change_maps_to_finalized(tmp_path, monkeypatch, capsys):
    module = load_module(SCRIPT_PATH, "migrate_subfeatures")
    monkeypatch.chdir(tmp_path)
    _, feature_dir = setup_feature(tmp_path)
    setup_legacy_change(feature_dir, status="closed")

    assert run_cli(module, "migrate_subfeatures.py", monkeypatch, "migrate", "checkout") == 0
    capsys.readouterr()

    subfeature_dir = feature_dir / "subfeatures" / "replace-legacy-flow"
    metadata = json.loads((subfeature_dir / ".subfeature-meta.json").read_text(encoding="utf-8"))
    planning_meta = load_module(PLANNING_SCRIPT, "manage_planning_for_migrate_closed").read_metadata(
        str(subfeature_dir)
    )

    assert metadata["status"] == "finalized"
    assert metadata["finalized_at"] == "2026-01-04T00:00:00"
    assert not (subfeature_dir / ".planning-meta.json").exists()
    assert planning_meta["status"] == "implemented"


def test_migrate_reports_conflict_when_target_subfeature_exists(
    tmp_path, monkeypatch, capsys
):
    module = load_module(SCRIPT_PATH, "migrate_subfeatures")
    planning_module, feature_dir = setup_feature(tmp_path)
    monkeypatch.chdir(tmp_path)
    change_dir = setup_legacy_change(feature_dir)

    subfeature_dir = feature_dir / "subfeatures" / "replace-legacy-flow"
    subfeature_dir.mkdir(parents=True, exist_ok=True)
    (subfeature_dir / ".planning-meta.json").write_text(
        json.dumps(
            {
                "feature_slug": "replace-legacy-flow",
                "status": "discovery_pending",
                "created_at": "2026-01-05T00:00:00",
                "updated_at": "2026-01-05T00:00:00",
                "requires_ui_flow": False,
                "review_note": None,
                "ready_slice_ids": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    planning_module.sync_registry()

    assert run_cli(module, "migrate_subfeatures.py", monkeypatch, "migrate", "checkout") == 3
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert payload["ok"] is False
    assert payload["features"][0]["blocked"][0]["reason"] == "Target subfeature already exists."
    assert change_dir.exists()
