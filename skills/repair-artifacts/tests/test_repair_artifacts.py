import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "repair_artifacts.py"
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
    monkeypatch.setattr(sys, "argv", ["repair_artifacts.py", *args])
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
    repair = load_module(SCRIPT_PATH, "repair_artifacts")

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
    planning.sync_registry()
    proposal_dir, _ = propose.create_proposal(
        "checkout-audit", summary="Audit checkout artifacts", target_feature="checkout"
    )
    scope_context = planning.SCOPE_RUNTIME.resolve_scope_context()
    subfeatures.ensure_subfeature_registry(feature_dir)
    subfeatures.create_subfeature(
        planning,
        feature_dir,
        "checkout",
        "replace-legacy-flow",
        "additive",
        "Replace legacy flow",
        scope_context,
    )
    execution.create_slice("CHK-101", "Checkout Slice")

    propose.write_registry([])
    planning.write_registry([])
    subfeatures.write_registry(feature_dir, [])
    execution.write_registry([])

    return {
        "repair": repair,
        "propose": propose,
        "planning": planning,
        "subfeatures": subfeatures,
        "execution": execution,
        "proposal_dir": Path(proposal_dir),
        "feature_dir": Path(feature_dir),
    }


def test_build_repair_result_reports_dry_run_actions(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch)

    payload = env["repair"].build_repair_result()

    assert payload["summary"]["planned_actions"] == 4
    assert payload["summary"]["applied_actions"] == 0
    assert payload["summary"]["skipped_artifacts"] == 0


def test_build_repair_result_applies_registry_repairs(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch)

    payload = env["repair"].build_repair_result(apply=True)

    proposal_rows = env["propose"].load_registry()
    _, _, slice_registry = env["execution"].get_registry_paths(required_config=False)
    slice_rows = env["execution"].load_registry_json(slice_registry)

    assert payload["summary"]["applied_actions"] == 4
    assert len(proposal_rows) == 1
    assert proposal_rows[0]["proposal"] == "checkout-audit"
    assert len(slice_rows) == 1
    assert slice_rows[0]["id"] == "CHK-101"


def test_build_repair_result_skips_malformed_metadata(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch)
    metadata_path = env["proposal_dir"] / ".proposal-meta.json"
    metadata_path.write_text("{not-json}\n", encoding="utf-8")

    payload = env["repair"].build_repair_result()

    assert payload["summary"]["skipped_artifacts"] == 1
    assert payload["skipped"][0]["artifact_type"] == "proposal"


def test_cli_json_reports_selected_artifact_layer(tmp_path, monkeypatch, capsys):
    env = setup_repo(tmp_path, monkeypatch)

    assert run_cli(env["repair"], monkeypatch, "--artifact-type", "slice", "--json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["summary"]["planned_actions"] == 1
    assert payload["actions"][0]["artifact_type"] == "slice"
