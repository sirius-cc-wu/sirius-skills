import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "manage_execution.py"


def load_manage_specs_module():
    spec = importlib.util.spec_from_file_location("manage_execution", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_cli(module, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["manage_execution.py", *args])
    return module.main()


def write_scope_config(scope_root: Path, filename: str, data: dict):
    skills_dir = scope_root / ".skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    (skills_dir / filename).write_text(json.dumps(data) + "\n", encoding="utf-8")


def write_planning_config(scope_root: Path):
    write_scope_config(
        scope_root,
        "planning.json",
        {"planning_dir": "docs/features", "proposal_dir": "docs/proposals"},
    )


def write_transition_guardrail_feature(
    tmp_path: Path, slice_id: str, *, subfeature_status: str = "reviewed"
):
    feature_dir = tmp_path / "docs" / "features" / "checkout"
    subfeature_dir = feature_dir / "subfeatures" / "replace-legacy-flow"
    subfeature_dir.mkdir(parents=True, exist_ok=True)
    (feature_dir / ".planning-meta.json").write_text(
        json.dumps(
            {
                "feature_slug": "checkout",
                "status": "planning_reviewed",
                "created_at": "2026-01-01T00:00:00",
                "updated_at": "2026-01-01T00:00:00",
                "requires_ui_flow": False,
                "review_note": "ready",
                "ready_slice_ids": [slice_id],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (subfeature_dir / ".planning-meta.json").write_text(
        json.dumps(
            {
                "feature_slug": "replace-legacy-flow",
                "status": "planning_reviewed",
                "created_at": "2026-01-01T00:00:00",
                "updated_at": "2026-01-01T00:00:00",
                "requires_ui_flow": False,
                "review_note": "ready",
                "ready_slice_ids": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (subfeature_dir / ".subfeature-meta.json").write_text(
        json.dumps(
            {
                "parent_feature_slug": "checkout",
                "subfeature_id": "replace-legacy-flow",
                "status": subfeature_status,
                "created_at": "2026-01-01T00:00:00",
                "updated_at": "2026-01-01T00:00:00",
                "subfeature_type": "replacement",
                "summary": "Replace legacy flow",
                "affected_artifacts": [],
                "affected_story_ids": [],
                "affected_slice_ids": [slice_id],
                "review_note": "ready",
                "finalized_at": (
                    "2026-01-01T00:00:00" if subfeature_status == "finalized" else None
                ),
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (subfeature_dir / "slice-traceability.md").write_text(
        "# Slice Traceability\n\n"
        "| Story ID | Increments | Planned Slice IDs | Execution Slice IDs | Notes |\n"
        "| --- | --- | --- | --- | --- |\n"
        f"| CHK-01 | I2 | {slice_id} |  | demo |\n",
        encoding="utf-8",
    )


def test_init_creates_human_and_machine_registry(tmp_path, monkeypatch):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init", "slices") == 0

    readme = (tmp_path / "slices" / "README.md").read_text(encoding="utf-8")
    registry = json.loads((tmp_path / "slices" / "registry.json").read_text(encoding="utf-8"))

    assert "| ID | Feature | Status | Updated | Closed | Path |" in readme
    assert registry["slices"] == []


def test_init_defaults_to_slices_directory(tmp_path, monkeypatch):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init") == 0

    assert (tmp_path / "slices" / "README.md").exists()
    config = json.loads(
        (tmp_path / ".skills" / "execution.json").read_text(encoding="utf-8")
    )
    assert config["slice_dir"] == "slices"
    assert config["auto_start_implementation"] is True
    assert not (tmp_path / ".specs").exists()


def test_add_creates_slice_metadata_and_registry_entries(tmp_path, monkeypatch):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init", "slices") == 0
    assert run_cli(module, monkeypatch, "add", "DEMO", "Demo Feature") == 0

    slice_dir = tmp_path / "slices" / "DEMO-demo-feature"
    metadata = json.loads((slice_dir / ".slice-meta.json").read_text(encoding="utf-8"))
    registry = json.loads((tmp_path / "slices" / "registry.json").read_text(encoding="utf-8"))

    assert metadata["slice_id"] == "DEMO"
    assert metadata["status"] == "draft"
    assert metadata["created_at"]
    assert metadata["updated_at"]
    assert registry["slices"][0]["id"] == "DEMO"
    assert registry["slices"][0]["updated_at"] == metadata["updated_at"]
    assert registry["slices"][0]["closed_at"] is None


def test_scope_aware_loaders_merge_parent_and_child_execution_configs(tmp_path):
    module = load_manage_specs_module()
    (tmp_path / ".git").mkdir()
    write_scope_config(
        tmp_path,
        "planning.json",
        {"planning_dir": "docs/features", "proposal_dir": "docs/proposals"},
    )
    write_scope_config(
        tmp_path,
        "execution.json",
        {
            "slice_dir": "team-slices",
            "preferred_workflow": "BDD",
            "auto_start_implementation": False,
        },
    )
    write_scope_config(
        tmp_path,
        "conventions.json",
        {
            "commit_format": "{scope}: {summary}",
            "id_pattern": r"^[A-Z]+-[0-9]+$",
        },
    )

    child_scope = tmp_path / "apps" / "payments"
    write_scope_config(child_scope, "planning.json", {})
    write_scope_config(child_scope, "execution.json", {"preferred_workflow": "Kanban"})
    write_scope_config(
        child_scope,
        "conventions.json",
        {"issue_url_template": "https://jira.example.test/browse/{ID}"},
    )

    scope_context = module.SCOPE_RUNTIME.resolve_scope_context(start_path=child_scope)
    execution_config = module.load_config(scope_context=scope_context)
    conventions = module.load_conventions_config(scope_context=scope_context)

    assert execution_config == {
        "slice_dir": "team-slices",
        "preferred_workflow": "Kanban",
        "auto_start_implementation": False,
    }
    assert conventions == {
        "commit_format": "{scope}: {summary}",
        "id_pattern": r"^[A-Z]+-[0-9]+$",
        "issue_url_template": "https://jira.example.test/browse/{ID}",
    }


def test_nested_scope_add_uses_local_registry_with_inherited_slice_dir(tmp_path, monkeypatch):
    module = load_manage_specs_module()
    (tmp_path / ".git").mkdir()
    write_scope_config(
        tmp_path,
        "planning.json",
        {"planning_dir": "docs/features", "proposal_dir": "docs/proposals"},
    )
    write_scope_config(
        tmp_path,
        "execution.json",
        {"slice_dir": "team-slices", "preferred_workflow": "BDD"},
    )

    child_scope = tmp_path / "apps" / "payments"
    write_scope_config(child_scope, "planning.json", {})
    workspace = child_scope / "src" / "ui"
    workspace.mkdir(parents=True)

    monkeypatch.chdir(workspace)
    assert run_cli(module, monkeypatch, "add", "DEMO", "Demo Feature") == 0

    child_registry = json.loads(
        (child_scope / "team-slices" / "registry.json").read_text(encoding="utf-8")
    )

    assert (child_scope / "team-slices" / "DEMO-demo-feature" / ".slice-meta.json").exists()
    assert child_registry["slices"][0]["path"] == "team-slices/DEMO-demo-feature/"
    assert not (tmp_path / "team-slices" / "DEMO-demo-feature").exists()


def test_init_in_nested_scope_writes_local_execution_config(tmp_path, monkeypatch):
    module = load_manage_specs_module()
    (tmp_path / ".git").mkdir()
    write_scope_config(
        tmp_path,
        "planning.json",
        {"planning_dir": "docs/features", "proposal_dir": "docs/proposals"},
    )
    child_scope = tmp_path / "apps" / "payments"
    write_scope_config(child_scope, "planning.json", {})

    monkeypatch.chdir(child_scope)
    assert run_cli(module, monkeypatch, "init", "team-slices") == 0

    execution = json.loads(
        (child_scope / ".skills" / "execution.json").read_text(encoding="utf-8")
    )

    assert execution["slice_dir"] == "team-slices"
    assert (child_scope / "team-slices" / "registry.json").exists()
    assert not (tmp_path / ".skills" / "execution.json").exists()


def test_set_status_blocks_invalid_transition(tmp_path, monkeypatch, capsys):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init", "slices") == 0
    assert run_cli(module, monkeypatch, "add", "DEMO", "Demo Feature") == 0

    exit_code = run_cli(module, monkeypatch, "set-status", "DEMO", "closed")
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Invalid status transition" in captured.err


def test_brief_ready_requires_requirements_checklist(tmp_path, monkeypatch, capsys):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init", "slices") == 0
    assert run_cli(module, monkeypatch, "add", "DEMO", "Demo Feature") == 0

    slice_dir = tmp_path / "slices" / "DEMO-demo-feature"
    (slice_dir / "brief.md").write_text("# brief\n", encoding="utf-8")

    exit_code = run_cli(module, monkeypatch, "set-status", "DEMO", "brief_ready")
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "missing_requirements_checklist" in captured.err


def test_closing_slice_records_closed_at_and_updates_registry(tmp_path, monkeypatch):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init", "slices") == 0
    assert run_cli(module, monkeypatch, "add", "DEMO", "Demo Feature") == 0

    slice_dir = tmp_path / "slices" / "DEMO-demo-feature"
    (slice_dir / "brief.md").write_text("# brief\n", encoding="utf-8")
    (slice_dir / "checklists").mkdir()
    (slice_dir / "checklists" / "requirements.md").write_text(
        "- [x] requirements complete\n", encoding="utf-8"
    )
    assert run_cli(module, monkeypatch, "set-status", "DEMO", "brief_ready") == 0

    (slice_dir / "blueprint.md").write_text("# plan\n", encoding="utf-8")
    assert run_cli(module, monkeypatch, "set-status", "DEMO", "blueprint_ready") == 0
    assert run_cli(module, monkeypatch, "set-status", "DEMO", "execution_ready") == 0
    assert run_cli(module, monkeypatch, "set-status", "DEMO", "closed") == 0

    metadata = json.loads((slice_dir / ".slice-meta.json").read_text(encoding="utf-8"))
    registry = json.loads((tmp_path / "slices" / "registry.json").read_text(encoding="utf-8"))
    readme = (tmp_path / "slices" / "README.md").read_text(encoding="utf-8")

    assert metadata["status"] == "closed"
    assert metadata["closed_at"]
    assert registry["slices"][0]["status"] == "closed"
    assert registry["slices"][0]["closed_at"] == metadata["closed_at"]
    assert "| DEMO | Demo Feature | closed |" in readme


def test_closing_slice_blocks_when_linked_subfeature_is_not_reviewed(
    tmp_path, monkeypatch, capsys
):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)
    write_planning_config(tmp_path)

    assert run_cli(module, monkeypatch, "init", "slices") == 0
    assert run_cli(module, monkeypatch, "add", "DEMO", "Demo Feature") == 0

    slice_dir = tmp_path / "slices" / "DEMO-demo-feature"
    (slice_dir / "brief.md").write_text("# brief\n", encoding="utf-8")
    (slice_dir / "checklists").mkdir()
    (slice_dir / "checklists" / "requirements.md").write_text(
        "- [x] requirements complete\n", encoding="utf-8"
    )
    assert run_cli(module, monkeypatch, "set-status", "DEMO", "brief_ready") == 0

    (slice_dir / "blueprint.md").write_text("# plan\n", encoding="utf-8")
    assert run_cli(module, monkeypatch, "set-status", "DEMO", "blueprint_ready") == 0
    assert run_cli(module, monkeypatch, "set-status", "DEMO", "execution_ready") == 0

    write_transition_guardrail_feature(tmp_path, "DEMO", subfeature_status="breakdown_ready")

    exit_code = run_cli(module, monkeypatch, "set-status", "DEMO", "closed")
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "transition_subfeature_review_required" in captured.err


def test_closing_slice_allows_linked_reviewed_subfeature(tmp_path, monkeypatch, capsys):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)
    write_planning_config(tmp_path)

    assert run_cli(module, monkeypatch, "init", "slices") == 0
    assert run_cli(module, monkeypatch, "add", "DEMO", "Demo Feature") == 0

    slice_dir = tmp_path / "slices" / "DEMO-demo-feature"
    (slice_dir / "brief.md").write_text("# brief\n", encoding="utf-8")
    (slice_dir / "checklists").mkdir()
    (slice_dir / "checklists" / "requirements.md").write_text(
        "- [x] requirements complete\n", encoding="utf-8"
    )
    assert run_cli(module, monkeypatch, "set-status", "DEMO", "brief_ready") == 0

    (slice_dir / "blueprint.md").write_text("# plan\n", encoding="utf-8")
    assert run_cli(module, monkeypatch, "set-status", "DEMO", "blueprint_ready") == 0
    assert run_cli(module, monkeypatch, "set-status", "DEMO", "execution_ready") == 0

    write_transition_guardrail_feature(tmp_path, "DEMO", subfeature_status="reviewed")

    assert run_cli(module, monkeypatch, "set-status", "DEMO", "closed") == 0
    captured = capsys.readouterr()

    assert "transition_subfeature_review_required" not in captured.err


def test_archive_slice_moves_closed_slice_and_updates_registry(tmp_path, monkeypatch):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init", "slices") == 0
    assert run_cli(module, monkeypatch, "add", "DEMO", "Demo Feature") == 0

    slice_dir = tmp_path / "slices" / "DEMO-demo-feature"
    (slice_dir / "brief.md").write_text("# brief\n", encoding="utf-8")
    (slice_dir / "checklists").mkdir()
    (slice_dir / "checklists" / "requirements.md").write_text(
        "- [x] requirements complete\n", encoding="utf-8"
    )
    assert run_cli(module, monkeypatch, "set-status", "DEMO", "brief_ready") == 0

    (slice_dir / "blueprint.md").write_text("# plan\n", encoding="utf-8")
    assert run_cli(module, monkeypatch, "set-status", "DEMO", "blueprint_ready") == 0
    assert run_cli(module, monkeypatch, "set-status", "DEMO", "execution_ready") == 0
    assert run_cli(module, monkeypatch, "set-status", "DEMO", "closed") == 0

    rows = module.parse_registry()
    slice = module.resolve_slice(rows, "DEMO")
    assert slice is not None

    success, _, archived_slice = module.archive_slice(rows, slice)
    registry = json.loads((tmp_path / "slices" / "registry.json").read_text(encoding="utf-8"))
    archived_dir = tmp_path / "slices" / ".archived" / "DEMO-demo-feature"
    metadata = json.loads((archived_dir / ".slice-meta.json").read_text(encoding="utf-8"))

    assert success is True
    assert archived_dir.exists()
    assert not (tmp_path / "slices" / "DEMO-demo-feature").exists()
    assert metadata["archived_at"]
    assert metadata["archived_from"] == "slices/DEMO-demo-feature/"
    assert metadata["path"] == "slices/.archived/DEMO-demo-feature/"
    assert archived_slice["path"] == "slices/.archived/DEMO-demo-feature/"
    assert registry["slices"][0]["path"] == "slices/.archived/DEMO-demo-feature/"
    assert registry["slices"][0]["archived_at"] == metadata["archived_at"]


def test_archive_slice_requires_closed_status(tmp_path, monkeypatch):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init", "slices") == 0
    assert run_cli(module, monkeypatch, "add", "DEMO", "Demo Feature") == 0

    rows = module.parse_registry()
    slice = module.resolve_slice(rows, "DEMO")
    assert slice is not None

    success, message, _ = module.archive_slice(rows, slice)

    assert success is False
    assert message == "Only closed slices can be archived."


def test_delete_slice_removes_registry_entry_and_relation_backlinks(tmp_path, monkeypatch):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init", "slices") == 0
    assert run_cli(module, monkeypatch, "add", "OLD", "Old Feature") == 0
    assert run_cli(module, monkeypatch, "add", "NEW", "New Feature") == 0

    new_dir = tmp_path / "slices" / "NEW-new-feature"
    (new_dir / "brief.md").write_text("# brief\n", encoding="utf-8")
    (new_dir / "checklists").mkdir()
    (new_dir / "checklists" / "requirements.md").write_text(
        "- [x] requirements complete\n", encoding="utf-8"
    )
    assert run_cli(module, monkeypatch, "set-status", "NEW", "brief_ready") == 0
    (new_dir / "blueprint.md").write_text("# plan\n", encoding="utf-8")
    assert run_cli(module, monkeypatch, "set-status", "NEW", "blueprint_ready") == 0
    assert run_cli(module, monkeypatch, "set-status", "NEW", "execution_ready") == 0
    assert run_cli(module, monkeypatch, "set-status", "NEW", "closed") == 0

    rows = module.parse_registry()
    new_slice = module.resolve_slice(rows, "NEW")
    assert new_slice is not None
    success, _ = module.add_relation(rows, new_slice, "supersedes", "OLD")
    assert success is True

    rows = module.parse_registry()
    new_slice = module.resolve_slice(rows, "NEW")
    assert new_slice is not None
    success, message, _ = module.delete_slice(rows, new_slice)

    old_meta = json.loads(
        (tmp_path / "slices" / "OLD-old-feature" / ".slice-meta.json").read_text(
            encoding="utf-8"
        )
    )
    registry = json.loads((tmp_path / "slices" / "registry.json").read_text(encoding="utf-8"))

    assert success is True
    assert message == "Removed closed slice NEW"
    assert not new_dir.exists()
    assert old_meta["relations"] == []
    assert [row["id"] for row in registry["slices"]] == ["OLD"]


def test_blueprint_ready_auto_starts_execution_when_enabled(
    tmp_path, monkeypatch, capsys
):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init", "slices") == 0
    assert run_cli(module, monkeypatch, "add", "DEMO", "Demo Feature") == 0

    slice_dir = tmp_path / "slices" / "DEMO-demo-feature"
    (slice_dir / "brief.md").write_text("# brief\n", encoding="utf-8")
    (slice_dir / "checklists").mkdir()
    (slice_dir / "checklists" / "requirements.md").write_text(
        "- [x] requirements complete\n", encoding="utf-8"
    )
    assert run_cli(module, monkeypatch, "set-status", "DEMO", "brief_ready") == 0

    (slice_dir / "blueprint.md").write_text("# plan\n", encoding="utf-8")
    assert run_cli(module, monkeypatch, "set-status", "DEMO", "blueprint_ready") == 0
    captured = capsys.readouterr()

    metadata = json.loads((slice_dir / ".slice-meta.json").read_text(encoding="utf-8"))
    registry = json.loads((tmp_path / "slices" / "registry.json").read_text(encoding="utf-8"))

    assert "auto-started implementation" in captured.out
    assert metadata["status"] == "execution_ready"
    assert registry["slices"][0]["status"] == "execution_ready"


def test_blueprint_ready_stays_manual_for_legacy_config_without_auto_start_flag(
    tmp_path, monkeypatch
):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)

    skills_dir = tmp_path / ".skills"
    skills_dir.mkdir()
    (skills_dir / "execution.json").write_text(
        json.dumps({"slice_dir": "slices", "preferred_workflow": "TDD"}) + "\n",
        encoding="utf-8",
    )

    assert run_cli(module, monkeypatch, "init") == 0
    assert run_cli(module, monkeypatch, "add", "DEMO", "Demo Feature") == 0

    slice_dir = tmp_path / "slices" / "DEMO-demo-feature"
    (slice_dir / "brief.md").write_text("# brief\n", encoding="utf-8")
    (slice_dir / "checklists").mkdir()
    (slice_dir / "checklists" / "requirements.md").write_text(
        "- [x] requirements complete\n", encoding="utf-8"
    )
    assert run_cli(module, monkeypatch, "set-status", "DEMO", "brief_ready") == 0

    (slice_dir / "blueprint.md").write_text("# plan\n", encoding="utf-8")
    assert run_cli(module, monkeypatch, "set-status", "DEMO", "blueprint_ready") == 0

    metadata = json.loads((slice_dir / ".slice-meta.json").read_text(encoding="utf-8"))
    config = json.loads((skills_dir / "execution.json").read_text(encoding="utf-8"))

    assert config["auto_start_implementation"] is False
    assert metadata["status"] == "blueprint_ready"


def test_legacy_markdown_registry_is_migrated_to_json(tmp_path, monkeypatch):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)

    (tmp_path / ".skills").mkdir()
    (tmp_path / ".skills" / "execution.json").write_text(
        json.dumps({"slice_dir": "specs", "preferred_workflow": "TDD"}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "specs").mkdir()
    (tmp_path / "specs" / "README.md").write_text(
        "# Slice Registry\n\n"
        "| ID | Feature | Status | Path |\n"
        "|---|---|---|---|\n"
        "| DEMO | Demo Feature | draft | specs/DEMO-demo-feature/ |\n",
        encoding="utf-8",
    )

    rows = module.parse_registry()

    registry = json.loads((tmp_path / "specs" / "registry.json").read_text(encoding="utf-8"))
    assert rows[0]["id"] == "DEMO"
    assert registry["slices"][0]["id"] == "DEMO"


def test_validate_slice_reports_missing_slice_metadata(tmp_path, monkeypatch, capsys):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init", "slices") == 0
    assert run_cli(module, monkeypatch, "add", "DEMO", "Demo Feature") == 0

    slice_dir = tmp_path / "slices" / "DEMO-demo-feature"
    (slice_dir / ".slice-meta.json").unlink()

    exit_code = run_cli(module, monkeypatch, "validate-slice", "DEMO")
    captured = capsys.readouterr()

    assert exit_code == 3
    assert "missing_slice_metadata" in captured.out


def test_add_requires_execution_driver_config(tmp_path, monkeypatch, capsys):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)

    exit_code = run_cli(module, monkeypatch, "add", "DEMO", "Demo Feature")

    captured = capsys.readouterr()
    assert exit_code == 2
    assert ".skills/execution.json" in captured.err


def test_add_relation_records_reciprocal_scope_and_registry(tmp_path, monkeypatch):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init", "slices") == 0
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
        (tmp_path / "slices" / "NEW-new-feature" / ".slice-meta.json").read_text(
            encoding="utf-8"
        )
    )
    old_meta = json.loads(
        (tmp_path / "slices" / "OLD-old-feature" / ".slice-meta.json").read_text(
            encoding="utf-8"
        )
    )
    registry = json.loads((tmp_path / "slices" / "registry.json").read_text(encoding="utf-8"))

    assert new_meta["relations"][0]["type"] == "supersedes"
    assert new_meta["relations"][0]["target_slice"] == "OLD"
    assert new_meta["relations"][0]["scope"]["story_title"] == "Story 2 - Old flow"
    assert new_meta["relations"][0]["scope"]["requirement_ids"] == ["FR-002"]
    assert old_meta["relations"][0]["type"] == "superseded_by"
    assert old_meta["relations"][0]["target_slice"] == "NEW"
    assert registry["slices"][1]["relations"][0]["type"] == "supersedes"


def test_audit_relations_reports_missing_reciprocal(tmp_path, monkeypatch):
    module = load_manage_specs_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init", "slices") == 0
    assert run_cli(module, monkeypatch, "add", "OLD", "Old Feature") == 0
    assert run_cli(module, monkeypatch, "add", "NEW", "New Feature") == 0
    assert run_cli(module, monkeypatch, "add-relation", "NEW", "supersedes", "OLD") == 0

    old_meta_path = tmp_path / "slices" / "OLD-old-feature" / ".slice-meta.json"
    old_meta = json.loads(old_meta_path.read_text(encoding="utf-8"))
    old_meta["relations"] = []
    old_meta_path.write_text(json.dumps(old_meta, indent=2) + "\n", encoding="utf-8")

    exit_code = run_cli(module, monkeypatch, "audit-relations", "--slice", "NEW")

    assert exit_code == 3
