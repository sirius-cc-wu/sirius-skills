import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "bootstrap_slice.py"
PLANNING_SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "guide-planning"
    / "scripts"
    / "manage_planning.py"
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


def test_bootstrap_syncs_nested_planning_feature_to_slice_ready(tmp_path, monkeypatch):
    module = load_module()
    feature_dir = setup_planning_feature(
        tmp_path,
        monkeypatch,
        "environment-injection",
        Path("docs/features/host-safe-validation/subfeatures/environment-injection"),
    )

    assert run_cli(module, monkeypatch, "ENV-01", "environment-injection") == 0

    planning_metadata = json.loads(
        (feature_dir / ".planning-meta.json").read_text(encoding="utf-8")
    )

    assert planning_metadata["status"] == "slice_ready"
    assert planning_metadata["ready_slice_ids"] == ["ENV-01"]


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
