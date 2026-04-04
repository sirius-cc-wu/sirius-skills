import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "manage_planning.py"
PROPOSAL_SCRIPT_PATH = (
    Path(__file__).resolve().parents[2] / "propose" / "scripts" / "manage_proposals.py"
)


def load_manage_planning_module():
    spec = importlib.util.spec_from_file_location("manage_planning", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_manage_proposals_module():
    spec = importlib.util.spec_from_file_location("manage_proposals", PROPOSAL_SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_cli(module, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["manage_planning.py", *args])
    return module.main()


def write_file(path: Path, content: str = "# doc\n"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_planning_config(scope_root: Path, config: dict | None = None):
    skills_dir = scope_root / ".skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    (skills_dir / "planning.json").write_text(
        json.dumps(
            config
            if config is not None
            else {
                "planning_dir": "docs/features",
                "proposal_dir": "docs/proposals",
                "design_diagram_mode": "embedded",
            }
        )
        + "\n",
        encoding="utf-8",
    )


def advance_feature_to_slice_ready(module, monkeypatch, feature_slug: str, slice_id: str):
    assert run_cli(module, monkeypatch, "set-status", feature_slug, "discovery_ready") == 0
    assert run_cli(module, monkeypatch, "set-status", feature_slug, "design_ready") == 0
    assert run_cli(module, monkeypatch, "set-status", feature_slug, "breakdown_ready") == 0
    assert (
        run_cli(
            module,
            monkeypatch,
            "set-status",
            feature_slug,
            "planning_reviewed",
            "--review-note",
            "Reviewed for scope, sequencing, and validation readiness.",
        )
        == 0
    )
    assert (
        run_cli(
            module,
            monkeypatch,
            "set-status",
            feature_slug,
            "slice_ready",
            "--slice-id",
            slice_id,
        )
        == 0
    )


def test_init_defaults_to_docs_features_directory(tmp_path, monkeypatch):
    module = load_manage_planning_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init") == 0

    config = json.loads((tmp_path / ".skills" / "planning.json").read_text(encoding="utf-8"))
    registry = json.loads((tmp_path / "docs" / "features" / "registry.json").read_text(encoding="utf-8"))

    assert config["planning_dir"] == "docs/features"
    assert config["proposal_dir"] == "docs/proposals"
    assert config["design_diagram_mode"] == "embedded"
    assert registry["features"] == []


def test_init_preserves_existing_planning_config_keys(tmp_path, monkeypatch):
    module = load_manage_planning_module()
    monkeypatch.chdir(tmp_path)

    skills_dir = tmp_path / ".skills"
    skills_dir.mkdir()
    (skills_dir / "planning.json").write_text(
        json.dumps(
            {
                "planning_dir": "planning/features",
                "proposal_dir": "planning/proposals",
                "design_diagram_mode": "linked_svg",
                "custom_key": "keep-me",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    assert run_cli(module, monkeypatch, "init", "docs/features") == 0

    config = json.loads((skills_dir / "planning.json").read_text(encoding="utf-8"))

    assert config == {
        "planning_dir": "docs/features",
        "proposal_dir": "planning/proposals",
        "design_diagram_mode": "linked_svg",
        "custom_key": "keep-me",
    }


def test_init_from_nested_directory_uses_repo_root_config_location(tmp_path, monkeypatch):
    module = load_manage_planning_module()
    nested = tmp_path / "apps" / "payments"
    nested.mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    monkeypatch.chdir(nested)

    assert run_cli(module, monkeypatch, "init") == 0

    assert (tmp_path / ".skills" / "planning.json").exists()
    assert (tmp_path / "docs" / "features" / "registry.json").exists()
    assert not (nested / ".skills" / "planning.json").exists()
    assert not (nested / "docs" / "features" / "registry.json").exists()


def test_add_creates_feature_metadata_and_registry_entries(tmp_path, monkeypatch):
    module = load_manage_planning_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init") == 0
    assert run_cli(module, monkeypatch, "add", "habit-tracker") == 0

    feature_dir = tmp_path / "docs" / "features" / "habit-tracker"
    metadata = json.loads((feature_dir / ".planning-meta.json").read_text(encoding="utf-8"))
    registry = json.loads((tmp_path / "docs" / "features" / "registry.json").read_text(encoding="utf-8"))

    assert metadata["feature_slug"] == "habit-tracker"
    assert metadata["status"] == "discovery_pending"
    assert metadata["requires_ui_flow"] is False
    assert registry["features"][0]["feature"] == "habit-tracker"


def test_add_from_nested_directory_uses_root_scope_registry(tmp_path, monkeypatch):
    module = load_manage_planning_module()

    write_planning_config(tmp_path)

    nested = tmp_path / "apps" / "payments"
    nested.mkdir(parents=True)
    monkeypatch.chdir(nested)

    assert run_cli(module, monkeypatch, "add", "habit-tracker") == 0

    assert (tmp_path / "docs" / "features" / "habit-tracker" / ".planning-meta.json").exists()
    assert not (nested / "docs" / "features" / "habit-tracker" / ".planning-meta.json").exists()


def test_child_scope_feature_registry_stays_local(tmp_path, monkeypatch):
    module = load_manage_planning_module()
    write_planning_config(tmp_path)

    child_scope = tmp_path / "apps" / "payments"
    write_planning_config(child_scope)

    monkeypatch.chdir(tmp_path)
    assert run_cli(module, monkeypatch, "add", "habit-tracker") == 0

    monkeypatch.chdir(child_scope)
    assert run_cli(module, monkeypatch, "add", "habit-tracker") == 0

    child_feature_dir = child_scope / "docs" / "features" / "habit-tracker"
    write_file(child_feature_dir / "discover.md")
    assert run_cli(module, monkeypatch, "set-status", "habit-tracker", "discovery_ready") == 0

    root_feature_dir = tmp_path / "docs" / "features" / "habit-tracker"
    root_meta = json.loads((root_feature_dir / ".planning-meta.json").read_text(encoding="utf-8"))
    child_meta = json.loads((child_feature_dir / ".planning-meta.json").read_text(encoding="utf-8"))
    root_registry = json.loads(
        (tmp_path / "docs" / "features" / "registry.json").read_text(encoding="utf-8")
    )
    child_registry = json.loads(
        (child_scope / "docs" / "features" / "registry.json").read_text(encoding="utf-8")
    )

    assert root_meta["status"] == "discovery_pending"
    assert child_meta["status"] == "discovery_ready"
    assert root_registry["features"] == [
        {
            "feature": "habit-tracker",
            "status": "discovery_pending",
            "updated_at": root_meta["updated_at"],
            "path": "docs/features/habit-tracker/",
        }
    ]
    assert child_registry["features"] == [
        {
            "feature": "habit-tracker",
            "status": "discovery_ready",
            "updated_at": child_meta["updated_at"],
            "path": "docs/features/habit-tracker/",
        }
    ]


def test_nested_child_directory_uses_nearest_scope_and_sibling_path_falls_back_to_root(
    tmp_path, monkeypatch
):
    module = load_manage_planning_module()
    write_planning_config(tmp_path)

    child_scope = tmp_path / "apps" / "payments"
    write_planning_config(child_scope)

    child_workspace = child_scope / "src" / "ui"
    child_workspace.mkdir(parents=True)
    sibling_workspace = tmp_path / "apps" / "ops"
    sibling_workspace.mkdir(parents=True)

    monkeypatch.chdir(child_workspace)
    assert run_cli(module, monkeypatch, "add", "child-feature") == 0

    monkeypatch.chdir(sibling_workspace)
    assert run_cli(module, monkeypatch, "add", "root-feature") == 0

    child_registry = json.loads(
        (child_scope / "docs" / "features" / "registry.json").read_text(encoding="utf-8")
    )
    root_registry = json.loads(
        (tmp_path / "docs" / "features" / "registry.json").read_text(encoding="utf-8")
    )

    assert child_registry["features"] == [
        {
            "feature": "child-feature",
            "status": "discovery_pending",
            "updated_at": child_registry["features"][0]["updated_at"],
            "path": "docs/features/child-feature/",
        }
    ]
    assert root_registry["features"] == [
        {
            "feature": "root-feature",
            "status": "discovery_pending",
            "updated_at": root_registry["features"][0]["updated_at"],
            "path": "docs/features/root-feature/",
        }
    ]
    assert (child_scope / "docs" / "features" / "child-feature" / ".planning-meta.json").exists()
    assert (tmp_path / "docs" / "features" / "root-feature" / ".planning-meta.json").exists()
    assert not (tmp_path / "docs" / "features" / "child-feature").exists()
    assert not (child_scope / "docs" / "features" / "root-feature").exists()


def test_child_scope_inherits_parent_planning_config_and_keeps_child_overrides(
    tmp_path, monkeypatch
):
    module = load_manage_planning_module()
    (tmp_path / ".git").mkdir()
    write_planning_config(
        tmp_path,
        {
            "planning_dir": "planning/features",
            "proposal_dir": "planning/proposals",
            "design_diagram_mode": "linked_svg",
            "custom_key": "keep-me",
        },
    )

    child_scope = tmp_path / "apps" / "payments"
    write_planning_config(
        child_scope,
        {
            "design_diagram_mode": "embedded",
            "custom_child": "keep-child",
        },
    )

    monkeypatch.chdir(child_scope)
    config = module.load_raw_config()

    assert config["planning_dir"] == "planning/features"
    assert config["proposal_dir"] == "planning/proposals"
    assert config["design_diagram_mode"] == "embedded"
    assert config["custom_key"] == "keep-me"
    assert config["custom_child"] == "keep-child"

    assert run_cli(module, monkeypatch, "add", "child-feature") == 0

    assert (child_scope / "planning" / "features" / "child-feature" / ".planning-meta.json").exists()
    assert not (tmp_path / "planning" / "features" / "child-feature").exists()


def test_ambiguous_feature_lookup_requires_explicit_scope(tmp_path, monkeypatch, capsys):
    module = load_manage_planning_module()
    write_planning_config(tmp_path)

    child_scope = tmp_path / "apps" / "payments"
    write_planning_config(child_scope)

    monkeypatch.chdir(tmp_path)
    assert run_cli(module, monkeypatch, "add", "habit-tracker") == 0

    monkeypatch.chdir(child_scope)
    assert run_cli(module, monkeypatch, "add", "habit-tracker") == 0

    write_file(tmp_path / "docs" / "features" / "habit-tracker" / "discover.md")
    write_file(child_scope / "docs" / "features" / "habit-tracker" / "discover.md")

    monkeypatch.chdir(tmp_path)
    exit_code = run_cli(module, monkeypatch, "set-status", "habit-tracker", "discovery_ready")
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Ambiguous planning feature selector 'habit-tracker'" in captured.err
    assert "." in captured.err
    assert "apps/payments" in captured.err

    assert (
        run_cli(
            module,
            monkeypatch,
            "set-status",
            "habit-tracker",
            "discovery_ready",
            "--scope",
            str(child_scope),
        )
        == 0
    )

    root_meta = json.loads(
        (tmp_path / "docs" / "features" / "habit-tracker" / ".planning-meta.json").read_text(
            encoding="utf-8"
        )
    )
    child_meta = json.loads(
        (
            child_scope / "docs" / "features" / "habit-tracker" / ".planning-meta.json"
        ).read_text(encoding="utf-8")
    )

    assert root_meta["status"] == "discovery_pending"
    assert child_meta["status"] == "discovery_ready"


def test_discovery_ready_requires_discover_file(tmp_path, monkeypatch, capsys):
    module = load_manage_planning_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init") == 0
    assert run_cli(module, monkeypatch, "add", "habit-tracker") == 0

    exit_code = run_cli(module, monkeypatch, "set-status", "habit-tracker", "discovery_ready")
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Missing required file 'discover.md'." in captured.err


def test_ui_required_blocks_design_ready_without_ui_design(tmp_path, monkeypatch, capsys):
    module = load_manage_planning_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init") == 0
    assert run_cli(module, monkeypatch, "add", "habit-tracker", "--require-ui-flow") == 0

    feature_dir = tmp_path / "docs" / "features" / "habit-tracker"
    write_file(feature_dir / "discover.md")
    assert run_cli(module, monkeypatch, "set-status", "habit-tracker", "discovery_ready") == 0

    write_file(feature_dir / "system-design.md")
    exit_code = run_cli(module, monkeypatch, "set-status", "habit-tracker", "design_ready")
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Missing required file 'ui-design.md'." in captured.err


def test_slice_ready_requires_review_note_and_slice_ids(tmp_path, monkeypatch, capsys):
    module = load_manage_planning_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init") == 0
    assert run_cli(module, monkeypatch, "add", "habit-tracker") == 0

    feature_dir = tmp_path / "docs" / "features" / "habit-tracker"
    write_file(feature_dir / "discover.md")
    write_file(feature_dir / "system-design.md")
    write_file(feature_dir / "slice-planning.md")
    write_file(feature_dir / "slice-traceability.md")

    assert run_cli(module, monkeypatch, "set-status", "habit-tracker", "discovery_ready") == 0
    assert run_cli(module, monkeypatch, "set-status", "habit-tracker", "design_ready") == 0
    assert run_cli(module, monkeypatch, "set-status", "habit-tracker", "breakdown_ready") == 0

    exit_code = run_cli(module, monkeypatch, "set-status", "habit-tracker", "planning_reviewed")
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Planning review requires a non-empty review note." in captured.err

    assert (
        run_cli(
            module,
            monkeypatch,
            "set-status",
            "habit-tracker",
            "planning_reviewed",
            "--review-note",
            "Planning artifacts reviewed and ready for tracker bootstrap.",
        )
        == 0
    )

    exit_code = run_cli(module, monkeypatch, "set-status", "habit-tracker", "slice_ready")
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Slice readiness requires at least one ready slice ID." in captured.err

    assert (
        run_cli(
            module,
            monkeypatch,
            "set-status",
            "habit-tracker",
            "slice_ready",
            "--slice-id",
            "HAB-101",
        )
        == 0
    )

    metadata = json.loads((feature_dir / ".planning-meta.json").read_text(encoding="utf-8"))
    assert metadata["ready_slice_ids"] == ["HAB-101"]


def test_validate_feature_reports_success_for_ready_feature(tmp_path, monkeypatch):
    module = load_manage_planning_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init") == 0
    assert run_cli(module, monkeypatch, "add", "habit-tracker") == 0

    feature_dir = tmp_path / "docs" / "features" / "habit-tracker"
    write_file(feature_dir / "discover.md")
    write_file(feature_dir / "system-design.md")
    write_file(feature_dir / "slice-planning.md")
    write_file(feature_dir / "slice-traceability.md")

    advance_feature_to_slice_ready(module, monkeypatch, "habit-tracker", "HAB-101")

    monkeypatch.setattr(sys, "argv", ["manage_planning.py", "validate-feature", "habit-tracker"])
    exit_code = module.main()
    assert exit_code == 0


def test_implemented_is_terminal_and_does_not_require_ready_slice_ids(
    tmp_path, monkeypatch
):
    module = load_manage_planning_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init") == 0
    assert run_cli(module, monkeypatch, "add", "habit-tracker") == 0

    feature_dir = tmp_path / "docs" / "features" / "habit-tracker"
    write_file(feature_dir / "discover.md")
    write_file(feature_dir / "system-design.md")
    write_file(feature_dir / "slice-planning.md")
    write_file(feature_dir / "slice-traceability.md")

    advance_feature_to_slice_ready(module, monkeypatch, "habit-tracker", "HAB-101")
    assert run_cli(module, monkeypatch, "set-status", "habit-tracker", "implemented") == 0

    metadata = json.loads((feature_dir / ".planning-meta.json").read_text(encoding="utf-8"))
    metadata["ready_slice_ids"] = []
    (feature_dir / ".planning-meta.json").write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(sys, "argv", ["manage_planning.py", "validate-feature", "habit-tracker"])
    exit_code = module.main()
    assert exit_code == 0


def test_find_active_feature_skips_terminal_ready_and_implemented_rows():
    module = load_manage_planning_module()

    rows = [
        {
            "feature": "implemented-feature",
            "status": "implemented",
            "updated_at": "2026-04-04T04:00:00",
            "path": "docs/features/implemented-feature/",
        },
        {
            "feature": "slice-ready-feature",
            "status": "slice_ready",
            "updated_at": "2026-04-04T04:01:00",
            "path": "docs/features/slice-ready-feature/",
        },
        {
            "feature": "active-feature",
            "status": "planning_reviewed",
            "updated_at": "2026-04-04T03:59:00",
            "path": "docs/features/active-feature/",
        },
    ]

    feature = module.find_active_feature(rows)
    assert feature["feature"] == "active-feature"


def test_promote_proposal_creates_feature_and_copies_docs(tmp_path, monkeypatch):
    planning_module = load_manage_planning_module()
    proposal_module = load_manage_proposals_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(planning_module, monkeypatch, "init") == 0
    assert run_cli(proposal_module, monkeypatch, "add", "workflow-capability-upgrades") == 0

    proposal_dir = tmp_path / "docs" / "proposals" / "workflow-capability-upgrades"
    write_file(proposal_dir / "discover.md", "# Discover\n")
    write_file(proposal_dir / "user-stories.md", "# Stories\n")

    assert (
        run_cli(
            proposal_module,
            monkeypatch,
            "set-status",
            "workflow-capability-upgrades",
            "reviewed",
            "--review-note",
            "Proposal scoped and ready for decision.",
        )
        == 0
    )
    assert (
        run_cli(
            proposal_module,
            monkeypatch,
            "set-status",
            "workflow-capability-upgrades",
            "accepted",
            "--review-note",
            "Accepted for canonical planning.",
            "--target-feature",
            "workflow-capability-upgrades",
        )
        == 0
    )

    assert (
        run_cli(
            planning_module,
            monkeypatch,
            "promote-proposal",
            "workflow-capability-upgrades",
            "--feature-slug",
            "workflow-capability-upgrades",
        )
        == 0
    )

    feature_dir = tmp_path / "docs" / "features" / "workflow-capability-upgrades"
    feature_meta = json.loads((feature_dir / ".planning-meta.json").read_text(encoding="utf-8"))
    proposal_meta = json.loads((proposal_dir / ".proposal-meta.json").read_text(encoding="utf-8"))

    assert feature_meta["feature_slug"] == "workflow-capability-upgrades"
    assert (feature_dir / "discover.md").read_text(encoding="utf-8") == "# Discover\n"
    assert (feature_dir / "user-stories.md").read_text(encoding="utf-8") == "# Stories\n"
    assert proposal_meta["status"] == "promoted"
    assert proposal_meta["promoted_feature"] == "workflow-capability-upgrades"


def test_promote_proposal_requires_accepted_status(tmp_path, monkeypatch, capsys):
    planning_module = load_manage_planning_module()
    proposal_module = load_manage_proposals_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(planning_module, monkeypatch, "init") == 0
    assert run_cli(proposal_module, monkeypatch, "add", "workflow-capability-upgrades") == 0

    exit_code = run_cli(
        planning_module,
        monkeypatch,
        "promote-proposal",
        "workflow-capability-upgrades",
    )
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Only accepted proposals can be promoted." in captured.err


def test_promote_proposal_defaults_to_proposal_scope_without_target_scope(
    tmp_path, monkeypatch
):
    planning_module = load_manage_planning_module()
    proposal_module = load_manage_proposals_module()
    write_planning_config(tmp_path)
    child_scope = tmp_path / "apps" / "payments"
    write_planning_config(child_scope)

    monkeypatch.chdir(child_scope)
    assert run_cli(proposal_module, monkeypatch, "add", "workflow-capability-upgrades") == 0

    proposal_dir = child_scope / "docs" / "proposals" / "workflow-capability-upgrades"
    write_file(proposal_dir / "discover.md", "# Discover\n")
    write_file(proposal_dir / "user-stories.md", "# Stories\n")

    assert (
        run_cli(
            proposal_module,
            monkeypatch,
            "set-status",
            "workflow-capability-upgrades",
            "reviewed",
            "--review-note",
            "Proposal scoped and ready for decision.",
        )
        == 0
    )
    assert (
        run_cli(
            proposal_module,
            monkeypatch,
            "set-status",
            "workflow-capability-upgrades",
            "accepted",
            "--review-note",
            "Accepted for canonical planning.",
        )
        == 0
    )

    monkeypatch.chdir(tmp_path)
    assert (
        run_cli(
            planning_module,
            monkeypatch,
            "promote-proposal",
            "workflow-capability-upgrades",
            "--scope",
            str(child_scope),
        )
        == 0
    )

    assert (
        child_scope / "docs" / "features" / "workflow-capability-upgrades" / ".planning-meta.json"
    ).exists()
    assert not (tmp_path / "docs" / "features" / "workflow-capability-upgrades").exists()


def test_promote_proposal_supports_explicit_target_scope(tmp_path, monkeypatch):
    planning_module = load_manage_planning_module()
    proposal_module = load_manage_proposals_module()
    write_planning_config(tmp_path)
    child_scope = tmp_path / "apps" / "payments"
    write_planning_config(child_scope)

    monkeypatch.chdir(child_scope)
    assert run_cli(proposal_module, monkeypatch, "add", "workflow-capability-upgrades") == 0

    proposal_dir = child_scope / "docs" / "proposals" / "workflow-capability-upgrades"
    write_file(proposal_dir / "discover.md", "# Discover\n")
    write_file(proposal_dir / "user-stories.md", "# Stories\n")

    assert (
        run_cli(
            proposal_module,
            monkeypatch,
            "set-status",
            "workflow-capability-upgrades",
            "reviewed",
            "--review-note",
            "Proposal scoped and ready for decision.",
        )
        == 0
    )
    assert (
        run_cli(
            proposal_module,
            monkeypatch,
            "set-status",
            "workflow-capability-upgrades",
            "accepted",
            "--review-note",
            "Accepted for canonical planning.",
        )
        == 0
    )

    monkeypatch.chdir(tmp_path)
    assert (
        run_cli(
            planning_module,
            monkeypatch,
            "promote-proposal",
            "workflow-capability-upgrades",
            "--scope",
            str(child_scope),
            "--target-scope",
            str(tmp_path),
        )
        == 0
    )

    assert (tmp_path / "docs" / "features" / "workflow-capability-upgrades" / ".planning-meta.json").exists()
    assert not (child_scope / "docs" / "features" / "workflow-capability-upgrades").exists()


def test_promote_proposal_rejects_target_scope_outside_repo(tmp_path, monkeypatch, capsys):
    planning_module = load_manage_planning_module()
    proposal_module = load_manage_proposals_module()
    write_planning_config(tmp_path)
    child_scope = tmp_path / "apps" / "payments"
    write_planning_config(child_scope)

    monkeypatch.chdir(child_scope)
    assert run_cli(proposal_module, monkeypatch, "add", "workflow-capability-upgrades") == 0

    proposal_dir = child_scope / "docs" / "proposals" / "workflow-capability-upgrades"
    write_file(proposal_dir / "discover.md", "# Discover\n")
    write_file(proposal_dir / "user-stories.md", "# Stories\n")

    assert (
        run_cli(
            proposal_module,
            monkeypatch,
            "set-status",
            "workflow-capability-upgrades",
            "reviewed",
            "--review-note",
            "Proposal scoped and ready for decision.",
        )
        == 0
    )
    assert (
        run_cli(
            proposal_module,
            monkeypatch,
            "set-status",
            "workflow-capability-upgrades",
            "accepted",
            "--review-note",
            "Accepted for canonical planning.",
        )
        == 0
    )

    outside_scope = tmp_path.parent / "outside-scope"
    outside_scope.mkdir()

    monkeypatch.chdir(tmp_path)
    exit_code = run_cli(
        planning_module,
        monkeypatch,
        "promote-proposal",
        "workflow-capability-upgrades",
        "--scope",
        str(child_scope),
        "--target-scope",
        str(outside_scope),
    )
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "outside repository root" in captured.err
    assert not (tmp_path / "docs" / "features" / "workflow-capability-upgrades").exists()
