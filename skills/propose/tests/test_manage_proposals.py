import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "manage_proposals.py"


def load_module():
    spec = importlib.util.spec_from_file_location("manage_proposals", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_cli(module, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["manage_proposals.py", *args])
    return module.main()


def write_file(path: Path, content: str = "# doc\n"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_planning_config(scope_root: Path):
    skills_dir = scope_root / ".skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    (skills_dir / "planning.json").write_text(
        json.dumps(
            {
                "planning_dir": "docs/features",
                "proposal_dir": "docs/proposals",
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_init_defaults_to_docs_proposals_directory(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init") == 0

    config = json.loads((tmp_path / ".skills" / "planning.json").read_text(encoding="utf-8"))
    registry = json.loads((tmp_path / "docs" / "proposals" / "registry.json").read_text(encoding="utf-8"))

    assert config["planning_dir"] == "docs/features"
    assert config["proposal_dir"] == "docs/proposals"
    assert registry["proposals"] == []


def test_init_from_nested_directory_uses_repo_root_config_location(tmp_path, monkeypatch):
    module = load_module()
    nested = tmp_path / "apps" / "payments"
    nested.mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    monkeypatch.chdir(nested)

    assert run_cli(module, monkeypatch, "init") == 0

    assert (tmp_path / ".skills" / "planning.json").exists()
    assert (tmp_path / "docs" / "proposals" / "registry.json").exists()
    assert not (nested / ".skills" / "planning.json").exists()
    assert not (nested / "docs" / "proposals" / "registry.json").exists()


def test_add_creates_proposal_metadata_and_registry_entries(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init") == 0
    assert (
        run_cli(
            module,
            monkeypatch,
            "add",
            "workflow-capability-upgrades",
            "--summary",
            "Improve planning capabilities.",
        )
        == 0
    )

    proposal_dir = tmp_path / "docs" / "proposals" / "workflow-capability-upgrades"
    metadata = json.loads((proposal_dir / ".proposal-meta.json").read_text(encoding="utf-8"))
    registry = json.loads((tmp_path / "docs" / "proposals" / "registry.json").read_text(encoding="utf-8"))

    assert metadata["proposal_slug"] == "workflow-capability-upgrades"
    assert metadata["status"] == "draft"
    assert metadata["summary"] == "Improve planning capabilities."
    assert (proposal_dir / "discover.md").exists()
    assert registry["proposals"][0]["proposal"] == "workflow-capability-upgrades"


def test_add_from_nested_directory_uses_root_scope_registry(tmp_path, monkeypatch):
    module = load_module()

    write_planning_config(tmp_path)

    nested = tmp_path / "apps" / "payments"
    nested.mkdir(parents=True)
    monkeypatch.chdir(nested)

    assert run_cli(module, monkeypatch, "add", "workflow-capability-upgrades") == 0

    assert (
        tmp_path
        / "docs"
        / "proposals"
        / "workflow-capability-upgrades"
        / ".proposal-meta.json"
    ).exists()
    assert not (
        nested
        / "docs"
        / "proposals"
        / "workflow-capability-upgrades"
        / ".proposal-meta.json"
    ).exists()


def test_child_scope_proposal_registry_stays_local(tmp_path, monkeypatch):
    module = load_module()
    write_planning_config(tmp_path)

    child_scope = tmp_path / "apps" / "payments"
    write_planning_config(child_scope)

    monkeypatch.chdir(tmp_path)
    assert run_cli(module, monkeypatch, "add", "workflow-capability-upgrades") == 0

    monkeypatch.chdir(child_scope)
    assert run_cli(module, monkeypatch, "add", "workflow-capability-upgrades") == 0
    assert (
        run_cli(
            module,
            monkeypatch,
            "set-status",
            "workflow-capability-upgrades",
            "reviewed",
            "--review-note",
            "Child scope proposal reviewed.",
        )
        == 0
    )

    root_proposal_dir = tmp_path / "docs" / "proposals" / "workflow-capability-upgrades"
    child_proposal_dir = child_scope / "docs" / "proposals" / "workflow-capability-upgrades"
    root_meta = json.loads((root_proposal_dir / ".proposal-meta.json").read_text(encoding="utf-8"))
    child_meta = json.loads(
        (child_proposal_dir / ".proposal-meta.json").read_text(encoding="utf-8")
    )
    root_registry = json.loads(
        (tmp_path / "docs" / "proposals" / "registry.json").read_text(encoding="utf-8")
    )
    child_registry = json.loads(
        (child_scope / "docs" / "proposals" / "registry.json").read_text(encoding="utf-8")
    )

    assert root_meta["status"] == "draft"
    assert child_meta["status"] == "reviewed"
    assert root_registry["proposals"] == [
        {
            "proposal": "workflow-capability-upgrades",
            "status": "draft",
            "updated_at": root_meta["updated_at"],
            "path": "docs/proposals/workflow-capability-upgrades/",
        }
    ]
    assert child_registry["proposals"] == [
        {
            "proposal": "workflow-capability-upgrades",
            "status": "reviewed",
            "updated_at": child_meta["updated_at"],
            "path": "docs/proposals/workflow-capability-upgrades/",
        }
    ]


def test_nested_child_directory_uses_nearest_scope_and_sibling_path_falls_back_to_root(
    tmp_path, monkeypatch
):
    module = load_module()
    write_planning_config(tmp_path)

    child_scope = tmp_path / "apps" / "payments"
    write_planning_config(child_scope)

    child_workspace = child_scope / "src" / "ui"
    child_workspace.mkdir(parents=True)
    sibling_workspace = tmp_path / "apps" / "ops"
    sibling_workspace.mkdir(parents=True)

    monkeypatch.chdir(child_workspace)
    assert run_cli(module, monkeypatch, "add", "child-proposal") == 0

    monkeypatch.chdir(sibling_workspace)
    assert run_cli(module, monkeypatch, "add", "root-proposal") == 0

    child_registry = json.loads(
        (child_scope / "docs" / "proposals" / "registry.json").read_text(encoding="utf-8")
    )
    root_registry = json.loads(
        (tmp_path / "docs" / "proposals" / "registry.json").read_text(encoding="utf-8")
    )

    assert child_registry["proposals"] == [
        {
            "proposal": "child-proposal",
            "status": "draft",
            "updated_at": child_registry["proposals"][0]["updated_at"],
            "path": "docs/proposals/child-proposal/",
        }
    ]
    assert root_registry["proposals"] == [
        {
            "proposal": "root-proposal",
            "status": "draft",
            "updated_at": root_registry["proposals"][0]["updated_at"],
            "path": "docs/proposals/root-proposal/",
        }
    ]
    assert (child_scope / "docs" / "proposals" / "child-proposal" / ".proposal-meta.json").exists()
    assert (tmp_path / "docs" / "proposals" / "root-proposal" / ".proposal-meta.json").exists()
    assert not (tmp_path / "docs" / "proposals" / "child-proposal").exists()
    assert not (child_scope / "docs" / "proposals" / "root-proposal").exists()


def test_ambiguous_proposal_lookup_requires_explicit_scope(tmp_path, monkeypatch, capsys):
    module = load_module()
    write_planning_config(tmp_path)

    child_scope = tmp_path / "apps" / "payments"
    write_planning_config(child_scope)

    monkeypatch.chdir(tmp_path)
    assert run_cli(module, monkeypatch, "add", "workflow-capability-upgrades") == 0

    monkeypatch.chdir(child_scope)
    assert run_cli(module, monkeypatch, "add", "workflow-capability-upgrades") == 0

    monkeypatch.chdir(tmp_path)
    exit_code = run_cli(
        module,
        monkeypatch,
        "set-status",
        "workflow-capability-upgrades",
        "reviewed",
        "--review-note",
        "Reviewed from the active scope.",
    )
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Ambiguous proposal selector 'workflow-capability-upgrades'" in captured.err
    assert "." in captured.err
    assert "apps/payments" in captured.err

    assert (
        run_cli(
            module,
            monkeypatch,
            "set-status",
            "workflow-capability-upgrades",
            "reviewed",
            "--review-note",
            "Child scope proposal reviewed.",
            "--scope",
            str(child_scope),
        )
        == 0
    )

    root_meta = json.loads(
        (
            tmp_path / "docs" / "proposals" / "workflow-capability-upgrades" / ".proposal-meta.json"
        ).read_text(encoding="utf-8")
    )
    child_meta = json.loads(
        (
            child_scope
            / "docs"
            / "proposals"
            / "workflow-capability-upgrades"
            / ".proposal-meta.json"
        ).read_text(encoding="utf-8")
    )

    assert root_meta["status"] == "draft"
    assert child_meta["status"] == "reviewed"


def test_reviewed_requires_review_note(tmp_path, monkeypatch, capsys):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init") == 0
    assert run_cli(module, monkeypatch, "add", "workflow-capability-upgrades") == 0

    exit_code = run_cli(
        module,
        monkeypatch,
        "set-status",
        "workflow-capability-upgrades",
        "reviewed",
    )
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Proposal review requires a non-empty review note." in captured.err


def test_accepted_proposal_remains_proposal_scoped(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init") == 0
    assert run_cli(module, monkeypatch, "add", "workflow-capability-upgrades") == 0

    proposal_dir = tmp_path / "docs" / "proposals" / "workflow-capability-upgrades"
    write_file(proposal_dir / "discover.md", "# Discover\n")
    write_file(proposal_dir / "user-stories.md", "# Stories\n")

    assert (
        run_cli(
            module,
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
            module,
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

    proposal_meta = json.loads((proposal_dir / ".proposal-meta.json").read_text(encoding="utf-8"))

    assert proposal_meta["status"] == "accepted"
    assert proposal_meta["target_feature"] == "workflow-capability-upgrades"
    assert proposal_meta["promoted_feature"] is None
    assert not (tmp_path / "docs" / "features" / "workflow-capability-upgrades").exists()


def test_validate_proposal_reports_success_for_accepted_proposal(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "init") == 0
    assert run_cli(module, monkeypatch, "add", "workflow-capability-upgrades") == 0
    proposal_dir = tmp_path / "docs" / "proposals" / "workflow-capability-upgrades"
    write_file(proposal_dir / "discover.md", "# Discover\n")

    assert (
        run_cli(
            module,
            monkeypatch,
            "set-status",
            "workflow-capability-upgrades",
            "reviewed",
            "--review-note",
            "Reviewed as a proposal candidate.",
        )
        == 0
    )
    assert (
        run_cli(
            module,
            monkeypatch,
            "set-status",
            "workflow-capability-upgrades",
            "accepted",
            "--review-note",
            "Accepted for promotion.",
        )
        == 0
    )

    monkeypatch.setattr(
        sys,
        "argv",
        ["manage_proposals.py", "validate-proposal", "workflow-capability-upgrades"],
    )
    assert module.main() == 0
