import importlib.util
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[3] / "src" / "sirius_skills" / "commands" / "bootstrap_slice.py"
PLANNING_SCRIPT_PATH = (
    Path(__file__).resolve().parents[3] / "src" / "sirius_skills" / "commands" / "manage_planning.py"
)


def load_module_from_path(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_module():
    return load_module_from_path(SCRIPT_PATH, "bootstrap_slice")


def load_planning_module():
    return load_module_from_path(PLANNING_SCRIPT_PATH, "manage_planning")


def run_cli(module, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["bootstrap_slice.py", *args])
    return module.main()


def write_scope_config(scope_root: Path, filename: str, data: dict):
    skills_dir = scope_root / ".skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    (skills_dir / filename).write_text(json.dumps(data) + "\n", encoding="utf-8")


def write_planning_file(feature_dir: Path, filename: str, content: str):
    (feature_dir / filename).write_text(content, encoding="utf-8")


def init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init", "--quiet"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Copilot Test"], cwd=root, check=True)
    subprocess.run(
        ["git", "config", "user.email", "copilot@example.test"],
        cwd=root,
        check=True,
    )


def commit_all(root: Path, message: str = "checkpoint") -> None:
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "--quiet", "-m", message], cwd=root, check=True)


def setup_planning_feature(
    tmp_path: Path,
    monkeypatch,
    feature_slug: str,
    relative_path: Path | None = None,
) -> Path:
    planning = load_planning_module()
    monkeypatch.chdir(tmp_path)
    write_scope_config(
        tmp_path,
        "planning.json",
        {"planning_dir": "docs/features", "proposal_dir": "docs/proposals"},
    )

    if relative_path is None:
        feature_dir, _ = planning.create_feature(feature_slug)
    else:
        feature_dir, _ = planning.create_feature_at_path(
            str(tmp_path / relative_path),
            feature_slug,
            scope_context=planning.SCOPE_RUNTIME.resolve_scope_context(),
        )

    feature_path = Path(feature_dir)
    write_planning_file(feature_path, "discover.md", "# Discover\n\nReady.\n")
    write_planning_file(feature_path, "system-design.md", "# System Design\n\nReady.\n")
    write_planning_file(feature_path, "slice-planning.md", "# Slice Planning\n\nReady.\n")
    write_planning_file(
        feature_path,
        "slice-traceability.md",
        "# Slice Traceability\n\nReady.\n",
    )

    metadata = planning.read_metadata(str(feature_path))
    metadata["status"] = "planning_reviewed"
    metadata["review_note"] = "Planning approved for slice bootstrap."
    planning.write_metadata(str(feature_path), metadata)
    planning.sync_registry()
    return feature_path


def setup_reviewed_subfeature(
    tmp_path: Path,
    monkeypatch,
    *,
    feature_slug: str,
    subfeature_id: str,
    approval_status: str,
) -> Path:
    planning = load_planning_module()
    monkeypatch.chdir(tmp_path)
    write_scope_config(
        tmp_path,
        "planning.json",
        {"planning_dir": "docs/features", "proposal_dir": "docs/proposals"},
    )

    feature_dir, _ = planning.create_feature(feature_slug)
    feature_path = Path(feature_dir)
    subfeatures_dir = feature_path / "subfeatures"
    subfeatures_dir.mkdir(parents=True, exist_ok=True)
    (subfeatures_dir / "README.md").write_text(
        "# Subfeature Registry\n\n| Subfeature | Status | Type | Updated | Path |\n|---|---|---|---|---|\n",
        encoding="utf-8",
    )
    (subfeatures_dir / "registry.json").write_text(
        json.dumps(
            {
                "subfeatures": [
                    {
                        "subfeature_id": subfeature_id,
                        "status": "reviewed",
                        "subfeature_type": "additive",
                        "updated_at": "2026-01-02T00:00:00",
                        "path": f"docs/features/{feature_slug}/subfeatures/{subfeature_id}/",
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )

    subfeature_dir = subfeatures_dir / subfeature_id
    subfeature_dir.mkdir(parents=True, exist_ok=True)
    write_planning_file(subfeature_dir, "discover.md", "# Discover\n\nReady.\n")
    write_planning_file(subfeature_dir, "system-design.md", "# System Design\n\nReady.\n")
    write_planning_file(subfeature_dir, "slice-planning.md", "# Slice Planning\n\nReady.\n")
    write_planning_file(
        subfeature_dir,
        "slice-traceability.md",
        "# Slice Traceability\n\nReady.\n",
    )
    (subfeature_dir / ".subfeature-meta.json").write_text(
        json.dumps(
            {
                "subfeature_id": subfeature_id,
                "parent_feature_slug": feature_slug,
                "status": "reviewed",
                "approval_status": approval_status,
                "created_at": "2026-01-01T00:00:00",
                "updated_at": "2026-01-02T00:00:00",
                "subfeature_type": "additive",
                "summary": "Subfeature ready for approval",
                "affected_artifacts": [],
                "affected_story_ids": [],
                "affected_slice_ids": [],
                "ready_slice_ids": [],
                "consolidation": None,
                "review_note": "Reviewed and awaiting explicit human approval.",
                "approved_at": "2026-01-03T00:00:00" if approval_status == "approved" else None,
                "approved_by": "maintainer" if approval_status == "approved" else None,
                "approval_note": "Approved for execution bootstrap."
                if approval_status == "approved"
                else None,
                "finalized_at": None,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    planning.sync_registry()
    return subfeature_dir


def test_bootstrap_initializes_default_execution_registry(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    assert run_cli(module, monkeypatch, "DEMO", "Demo Feature") == 0

    execution = json.loads(
        (tmp_path / ".skills" / "execution.json").read_text(encoding="utf-8")
    )
    registry = json.loads((tmp_path / "slices" / "registry.json").read_text(encoding="utf-8"))
    metadata = json.loads(
        (tmp_path / "slices" / "DEMO-demo-feature" / ".slice-meta.json").read_text(
            encoding="utf-8"
        )
    )

    assert execution == {
        "slice_dir": "slices",
        "preferred_workflow": "TDD",
        "auto_start_implementation": True,
    }
    assert registry["slices"][0]["id"] == "DEMO"
    assert metadata["status"] == "draft"


def test_bootstrap_syncs_planning_feature_to_slice_ready(tmp_path, monkeypatch):
    module = load_module()
    feature_dir = setup_planning_feature(tmp_path, monkeypatch, "demo-feature")

    assert run_cli(module, monkeypatch, "DEMO", "demo-feature") == 0
    assert run_cli(module, monkeypatch, "DEMO", "demo-feature") == 0

    planning_metadata = json.loads(
        (feature_dir / ".planning-meta.json").read_text(encoding="utf-8")
    )
    registry = json.loads(
        (tmp_path / "docs" / "features" / "registry.json").read_text(encoding="utf-8")
    )

    assert planning_metadata["status"] == "slice_ready"
    assert planning_metadata["ready_slice_ids"] == ["DEMO"]
    assert next(
        row for row in registry["features"] if row["feature"] == "demo-feature"
    )["status"] == "slice_ready"


def test_bootstrap_blocks_unapproved_reviewed_subfeature(tmp_path, monkeypatch, capsys):
    module = load_module()
    setup_reviewed_subfeature(
        tmp_path,
        monkeypatch,
        feature_slug="host-safe-validation",
        subfeature_id="environment-injection",
        approval_status="pending",
    )

    exit_code = run_cli(module, monkeypatch, "ENV-01", "environment-injection")
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "must record explicit human approval before slice bootstrap" in captured.err


def test_bootstrap_syncs_approved_subfeature_to_slice_ready(tmp_path, monkeypatch):
    module = load_module()
    subfeature_dir = setup_reviewed_subfeature(
        tmp_path,
        monkeypatch,
        feature_slug="host-safe-validation",
        subfeature_id="environment-injection",
        approval_status="approved",
    )
    planning = load_planning_module()

    assert run_cli(module, monkeypatch, "ENV-01", "environment-injection") == 0

    subfeature_metadata = json.loads(
        (subfeature_dir / ".subfeature-meta.json").read_text(encoding="utf-8")
    )
    planning_metadata = planning.read_metadata(str(subfeature_dir))

    assert planning_metadata["status"] == "slice_ready"
    assert planning_metadata["ready_slice_ids"] == ["ENV-01"]
    assert subfeature_metadata["ready_slice_ids"] == ["ENV-01"]
    assert (subfeature_dir / ".skills" / "execution.json").exists()
    assert (
        subfeature_dir
        / "slices"
        / "ENV-01-environment-injection"
        / ".slice-meta.json"
    ).exists()
    assert not (tmp_path / "slices" / "ENV-01-environment-injection").exists()


def test_bootstrap_blocks_dirty_approved_subfeature_until_planning_is_committed(
    tmp_path, monkeypatch, capsys
):
    init_git_repo(tmp_path)
    module = load_module()
    setup_reviewed_subfeature(
        tmp_path,
        monkeypatch,
        feature_slug="host-safe-validation",
        subfeature_id="environment-injection",
        approval_status="approved",
    )

    exit_code = run_cli(module, monkeypatch, "ENV-01", "environment-injection")
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Planning artifacts must be committed before slice bootstrap." in captured.err


def test_bootstrap_allows_committed_approved_subfeature_in_git_repo(tmp_path, monkeypatch):
    init_git_repo(tmp_path)
    module = load_module()
    subfeature_dir = setup_reviewed_subfeature(
        tmp_path,
        monkeypatch,
        feature_slug="host-safe-validation",
        subfeature_id="environment-injection",
        approval_status="approved",
    )
    commit_all(tmp_path, "Commit approved planning packet")
    planning = load_planning_module()

    assert run_cli(module, monkeypatch, "ENV-01", "environment-injection") == 0

    subfeature_metadata = json.loads(
        (subfeature_dir / ".subfeature-meta.json").read_text(encoding="utf-8")
    )
    planning_metadata = planning.read_metadata(str(subfeature_dir))

    assert planning_metadata["status"] == "slice_ready"
    assert planning_metadata["ready_slice_ids"] == ["ENV-01"]
    assert subfeature_metadata["ready_slice_ids"] == ["ENV-01"]
    assert (subfeature_dir / ".skills" / "execution.json").exists()
    assert (
        subfeature_dir
        / "slices"
        / "ENV-01-environment-injection"
        / ".slice-meta.json"
    ).exists()


def test_bootstrap_uses_explicit_slice_dir_when_config_missing(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    assert (
        run_cli(
            module,
            monkeypatch,
            "--slice-dir",
            "work/slices",
            "DEMO",
            "Demo Feature",
        )
        == 0
    )

    execution = json.loads(
        (tmp_path / ".skills" / "execution.json").read_text(encoding="utf-8")
    )
    assert execution["slice_dir"] == "work/slices"
    assert (tmp_path / "work" / "slices" / "DEMO-demo-feature").exists()


def test_bootstrap_rejects_defaults_only_execution_config_without_slice_dir(
    tmp_path, monkeypatch, capsys
):
    module = load_module()
    monkeypatch.chdir(tmp_path)
    write_scope_config(
        tmp_path,
        "execution.json",
        {"preferred_workflow": "Kanban", "auto_start_implementation": False},
    )

    exit_code = run_cli(module, monkeypatch, "DEMO", "Demo Feature")
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "does not define 'slice_dir'" in captured.err
    assert not (tmp_path / "slices").exists()


def test_bootstrap_can_initialize_defaults_only_execution_config_with_explicit_slice_dir(
    tmp_path, monkeypatch
):
    module = load_module()
    monkeypatch.chdir(tmp_path)
    write_scope_config(
        tmp_path,
        "execution.json",
        {"preferred_workflow": "Kanban", "auto_start_implementation": False},
    )

    assert (
        run_cli(
            module,
            monkeypatch,
            "--slice-dir",
            "work/slices",
            "DEMO",
            "Demo Feature",
        )
        == 0
    )

    execution = json.loads(
        (tmp_path / ".skills" / "execution.json").read_text(encoding="utf-8")
    )
    assert execution == {
        "slice_dir": "work/slices",
        "preferred_workflow": "Kanban",
        "auto_start_implementation": False,
    }
    assert (tmp_path / "work" / "slices" / "DEMO-demo-feature").exists()


def test_bootstrap_reuses_existing_execution_config_and_deduplicates(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.chdir(tmp_path)

    skills_dir = tmp_path / ".skills"
    skills_dir.mkdir()
    (skills_dir / "execution.json").write_text(
        json.dumps({"slice_dir": "custom-slices", "preferred_workflow": "BDD"}) + "\n",
        encoding="utf-8",
    )

    assert run_cli(module, monkeypatch, "DEMO", "Demo Feature") == 0
    assert run_cli(module, monkeypatch, "DEMO", "Demo Feature") == 0

    registry = json.loads(
        (tmp_path / "custom-slices" / "registry.json").read_text(encoding="utf-8")
    )
    execution = json.loads(
        (tmp_path / ".skills" / "execution.json").read_text(encoding="utf-8")
    )

    assert len(registry["slices"]) == 1
    assert registry["slices"][0]["id"] == "DEMO"
    assert execution == {"slice_dir": "custom-slices", "preferred_workflow": "BDD"}


def test_bootstrap_uses_child_scope_registry_with_inherited_execution_config(
    tmp_path, monkeypatch
):
    module = load_module()
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

    monkeypatch.chdir(child_scope)
    assert run_cli(module, monkeypatch, "DEMO", "Demo Feature") == 0

    registry = json.loads(
        (child_scope / "team-slices" / "registry.json").read_text(encoding="utf-8")
    )

    assert registry["slices"][0]["id"] == "DEMO"
    assert (child_scope / "team-slices" / "DEMO-demo-feature" / ".slice-meta.json").exists()
    assert not (child_scope / ".skills" / "execution.json").exists()
    assert not (tmp_path / "team-slices" / "DEMO-demo-feature").exists()
