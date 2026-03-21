import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "manage_specs.py"


def load_manage_specs_module():
    spec = importlib.util.spec_from_file_location("manage_specs", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_cli(module, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["manage_specs.py", *args])
    return module.main()


def test_init_creates_human_and_machine_registry(tmp_path, monkeypatch):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init", "tracks") == 0

    readme = (tmp_path / "tracks" / "README.md").read_text(encoding="utf-8")
    registry = json.loads((tmp_path / "tracks" / "registry.json").read_text(encoding="utf-8"))

    assert "| ID | Feature | Status | Updated | Closed | Path |" in readme
    assert registry["tracks"] == []


def test_init_defaults_to_tracks_directory(tmp_path, monkeypatch):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init") == 0

    assert (tmp_path / "tracks" / "README.md").exists()
    config = json.loads((tmp_path / ".specs" / "config.json").read_text(encoding="utf-8"))
    assert config["spec_dir"] == "tracks"


def test_add_creates_track_metadata_and_registry_entries(tmp_path, monkeypatch):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init", "tracks") == 0
    assert run_cli(module, monkeypatch, "add", "DEMO", "Demo Feature") == 0

    track_dir = tmp_path / "tracks" / "DEMO-demo-feature"
    metadata = json.loads((track_dir / ".track-meta.json").read_text(encoding="utf-8"))
    registry = json.loads((tmp_path / "tracks" / "registry.json").read_text(encoding="utf-8"))

    assert metadata["track_id"] == "DEMO"
    assert metadata["status"] == "draft"
    assert metadata["created_at"]
    assert metadata["updated_at"]
    assert registry["tracks"][0]["id"] == "DEMO"
    assert registry["tracks"][0]["updated_at"] == metadata["updated_at"]
    assert registry["tracks"][0]["closed_at"] is None


def test_set_status_blocks_invalid_transition(tmp_path, monkeypatch, capsys):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init", "tracks") == 0
    assert run_cli(module, monkeypatch, "add", "DEMO", "Demo Feature") == 0

    exit_code = run_cli(module, monkeypatch, "set-status", "DEMO", "closed")
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Invalid status transition" in captured.err


def test_closing_track_records_closed_at_and_updates_registry(tmp_path, monkeypatch):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init", "tracks") == 0
    assert run_cli(module, monkeypatch, "add", "DEMO", "Demo Feature") == 0

    track_dir = tmp_path / "tracks" / "DEMO-demo-feature"
    (track_dir / "spec.md").write_text("# spec\n", encoding="utf-8")
    assert run_cli(module, monkeypatch, "set-status", "DEMO", "spec_ready") == 0

    (track_dir / "plan.md").write_text("# plan\n", encoding="utf-8")
    assert run_cli(module, monkeypatch, "set-status", "DEMO", "plan_ready") == 0
    assert run_cli(module, monkeypatch, "set-status", "DEMO", "execution_ready") == 0
    assert run_cli(module, monkeypatch, "set-status", "DEMO", "closed") == 0

    metadata = json.loads((track_dir / ".track-meta.json").read_text(encoding="utf-8"))
    registry = json.loads((tmp_path / "tracks" / "registry.json").read_text(encoding="utf-8"))
    readme = (tmp_path / "tracks" / "README.md").read_text(encoding="utf-8")

    assert metadata["status"] == "closed"
    assert metadata["closed_at"]
    assert registry["tracks"][0]["status"] == "closed"
    assert registry["tracks"][0]["closed_at"] == metadata["closed_at"]
    assert "| DEMO | Demo Feature | closed |" in readme


def test_legacy_markdown_registry_is_migrated_to_json(tmp_path, monkeypatch):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)

    (tmp_path / ".specs").mkdir()
    (tmp_path / ".specs" / "config.json").write_text(
        json.dumps({"spec_dir": "specs", "preferred_workflow": "TDD"}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "specs").mkdir()
    (tmp_path / "specs" / "README.md").write_text(
        "# Track Registry\n\n"
        "| ID | Feature | Status | Path |\n"
        "|---|---|---|---|\n"
        "| DEMO | Demo Feature | draft | specs/DEMO-demo-feature/ |\n",
        encoding="utf-8",
    )

    rows = module.parse_registry()

    registry = json.loads((tmp_path / "specs" / "registry.json").read_text(encoding="utf-8"))
    assert rows[0]["id"] == "DEMO"
    assert registry["tracks"][0]["id"] == "DEMO"


def test_add_relation_records_reciprocal_scope_and_registry(tmp_path, monkeypatch):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init", "tracks") == 0
    assert run_cli(module, monkeypatch, "add", "OLD", "Old Feature") == 0
    assert run_cli(module, monkeypatch, "add", "NEW", "New Feature") == 0

    assert (
        run_cli(
            module,
            monkeypatch,
            "add-relation",
            "NEW",
            "supersedes",
            "OLD",
            "--story-title",
            "Story 2 - Old flow",
            "--requirement-id",
            "FR-002",
            "--selector",
            "legacy checkout path",
        )
        == 0
    )

    new_meta = json.loads(
        (tmp_path / "tracks" / "NEW-new-feature" / ".track-meta.json").read_text(
            encoding="utf-8"
        )
    )
    old_meta = json.loads(
        (tmp_path / "tracks" / "OLD-old-feature" / ".track-meta.json").read_text(
            encoding="utf-8"
        )
    )
    registry = json.loads((tmp_path / "tracks" / "registry.json").read_text(encoding="utf-8"))

    assert new_meta["relations"][0]["type"] == "supersedes"
    assert new_meta["relations"][0]["target_track"] == "OLD"
    assert new_meta["relations"][0]["scope"]["story_title"] == "Story 2 - Old flow"
    assert new_meta["relations"][0]["scope"]["requirement_ids"] == ["FR-002"]
    assert old_meta["relations"][0]["type"] == "superseded_by"
    assert old_meta["relations"][0]["target_track"] == "NEW"
    assert registry["tracks"][1]["relations"][0]["type"] == "supersedes"


def test_audit_relations_reports_missing_reciprocal(tmp_path, monkeypatch):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init", "tracks") == 0
    assert run_cli(module, monkeypatch, "add", "OLD", "Old Feature") == 0
    assert run_cli(module, monkeypatch, "add", "NEW", "New Feature") == 0
    assert run_cli(module, monkeypatch, "add-relation", "NEW", "supersedes", "OLD") == 0

    old_meta_path = tmp_path / "tracks" / "OLD-old-feature" / ".track-meta.json"
    old_meta = json.loads(old_meta_path.read_text(encoding="utf-8"))
    old_meta["relations"] = []
    old_meta_path.write_text(json.dumps(old_meta, indent=2) + "\n", encoding="utf-8")

    exit_code = run_cli(module, monkeypatch, "audit-relations", "--track", "NEW")

    assert exit_code == 3
