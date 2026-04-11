import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "archive_artifacts.py"
PROPOSE_SCRIPT = Path(__file__).resolve().parents[2] / "propose" / "scripts" / "manage_proposals.py"
PLANNING_SCRIPT = (
    Path(__file__).resolve().parents[2] / "guide-planning" / "scripts" / "manage_planning.py"
)
SUBFEATURE_SCRIPT = (
    Path(__file__).resolve().parents[2] / "add-subfeature" / "scripts" / "manage_subfeatures.py"
)
EXECUTION_SCRIPT = (
    Path(__file__).resolve().parents[2] / "guide-execution" / "scripts" / "manage_execution.py"
)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_cli(module, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["archive_artifacts.py", *args])
    return module.main()


def write_scope_config(root: Path, filename: str, payload: dict):
    skills_dir = root / ".skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    (skills_dir / filename).write_text(json.dumps(payload) + "\n", encoding="utf-8")


def setup_repo(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    propose = load_module(PROPOSE_SCRIPT, "manage_proposals")
    planning = load_module(PLANNING_SCRIPT, "manage_planning")
    subfeatures = load_module(SUBFEATURE_SCRIPT, "manage_subfeatures")
    execution = load_module(EXECUTION_SCRIPT, "manage_execution")
    archive = load_module(SCRIPT_PATH, "archive_artifacts")

    write_scope_config(
        tmp_path,
        "planning.json",
        {"planning_dir": "docs/features", "proposal_dir": "docs/proposals"},
    )
    write_scope_config(
        tmp_path,
        "execution.json",
        {
            "slice_dir": "slices",
            "preferred_workflow": "TDD",
            "auto_start_implementation": True,
        },
    )

    feature_dir, _ = planning.create_feature("checkout")
    proposal_dir, _ = propose.create_proposal(
        "checkout-audit", summary="Audit checkout artifacts", target_feature="checkout"
    )
    proposal_metadata = propose.read_metadata(proposal_dir)
    proposal_metadata["status"] = "promoted"
    propose.write_metadata(proposal_dir, proposal_metadata)

    scope_context = planning.SCOPE_RUNTIME.resolve_scope_context()
    subfeatures.ensure_subfeature_registry(feature_dir)
    subfeature_dir, _ = subfeatures.create_subfeature(
        planning,
        feature_dir,
        "checkout",
        "replace-legacy-flow",
        "additive",
        "Replace legacy flow",
        scope_context,
    )
    subfeature_metadata = subfeatures.read_metadata(subfeature_dir)
    subfeature_metadata["status"] = "finalized"
    subfeatures.write_metadata(subfeature_dir, subfeature_metadata)

    execution.create_slice("CHK-101", "Checkout Slice")
    _, _, slice_registry = execution.get_registry_paths(required_config=False)
    slice_rows = execution.load_registry_json(slice_registry)
    slice_row = next(row for row in slice_rows if row["id"] == "CHK-101")
    slice_row["status"] = "closed"
    execution.write_registry(slice_rows)
    metadata = execution.load_slice_metadata(execution.slice_path_for_row(slice_row))
    metadata["status"] = "closed"
    metadata["closed_at"] = "2026-02-13T00:00:00"
    execution.write_slice_metadata(execution.slice_path_for_row(slice_row), metadata)

    return {
        "archive": archive,
        "execution": execution,
    }


def test_build_archive_result_lists_candidates(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch)

    payload = env["archive"].build_archive_result()

    assert payload["summary"]["candidate_count"] == 3
    assert payload["summary"]["archivable_count"] == 1


def test_cli_rejects_unsupported_apply_request(tmp_path, monkeypatch, capsys):
    env = setup_repo(tmp_path, monkeypatch)

    assert (
        run_cli(
            env["archive"],
            monkeypatch,
            "--artifact-type",
            "proposal",
            "--artifact-id",
            "checkout-audit",
            "--apply",
        )
        == env["archive"].ERROR_EXIT_CODE
    )
    assert "requires --artifact-type slice" in capsys.readouterr().err


def test_build_archive_result_applies_closed_slice_archive(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch)

    payload = env["archive"].build_archive_result(
        artifact_type="slice",
        artifact_id="CHK-101",
        apply=True,
    )

    _, _, slice_registry = env["execution"].get_registry_paths(required_config=False)
    slice_rows = env["execution"].load_registry_json(slice_registry)
    archived_row = next(row for row in slice_rows if row["id"] == "CHK-101")

    assert payload["applied"]["artifact_id"] == "CHK-101"
    assert archived_row["path"] != "slices/CHK-101-checkout-slice/"


def test_cli_json_filters_one_artifact_type(tmp_path, monkeypatch, capsys):
    env = setup_repo(tmp_path, monkeypatch)

    assert run_cli(env["archive"], monkeypatch, "--artifact-type", "slice", "--json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["summary"]["candidate_count"] == 1
    assert payload["candidates"][0]["artifact_type"] == "slice"
