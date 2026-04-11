import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "report_artifacts.py"
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
    monkeypatch.setattr(sys, "argv", ["report_artifacts.py", *args])
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
    report = load_module(SCRIPT_PATH, "report_artifacts")

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
    feature_path = Path(feature_dir)
    planning.sync_registry()

    proposal_dir, _ = propose.create_proposal(
        "checkout-audit", summary="Audit checkout artifacts", target_feature="checkout"
    )
    proposal_metadata = propose.read_metadata(proposal_dir)
    proposal_metadata["status"] = "accepted"
    proposal_metadata["updated_at"] = "2026-01-01T00:00:00"
    propose.write_metadata(proposal_dir, proposal_metadata)

    planning_metadata = planning.read_metadata(feature_dir)
    planning_metadata["status"] = "planning_reviewed"
    planning_metadata["updated_at"] = "2026-02-10T00:00:00"
    planning.write_metadata(feature_dir, planning_metadata)

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
    subfeature_metadata["status"] = "reviewed"
    subfeature_metadata["updated_at"] = "2026-02-14T00:00:00"
    subfeatures.write_metadata(subfeature_dir, subfeature_metadata)

    execution.create_slice("CHK-101", "Checkout Slice")
    _, _, slice_registry = execution.get_registry_paths(required_config=False)
    slice_rows = execution.load_registry_json(slice_registry)
    slice_row = next(row for row in slice_rows if row["id"] == "CHK-101")
    slice_row["status"] = "closed"
    slice_row["updated_at"] = "2026-02-13T00:00:00"
    execution.write_registry(slice_rows)
    metadata = execution.load_slice_metadata(execution.slice_path_for_row(slice_row))
    metadata["status"] = "closed"
    metadata["updated_at"] = "2026-02-13T00:00:00"
    metadata["closed_at"] = "2026-02-13T00:00:00"
    execution.write_slice_metadata(execution.slice_path_for_row(slice_row), metadata)

    return {"report": report}


def groups_by_key(payload: dict) -> dict:
    return {group["key"]: group for group in payload["groups"]}


def test_run_report_overview_counts_by_type_and_staleness(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch)

    payload = env["report"].build_report_result(
        group_by="overview",
        stale_days=30,
        now=datetime(2026, 2, 15),
    )

    groups = groups_by_key(payload)
    assert payload["summary"]["total"] == 4
    assert payload["summary"]["stale"] == 1
    assert groups["proposal"]["stale"] == 1
    assert groups["slice"]["count"] == 1


def test_run_report_groups_by_status(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch)

    payload = env["report"].build_report_result(
        group_by="status",
        stale_days=30,
        now=datetime(2026, 2, 15),
    )

    groups = groups_by_key(payload)
    assert {"accepted", "planning_reviewed", "reviewed", "closed"}.issubset(groups)


def test_cli_json_groups_by_parent_for_selected_artifact_type(tmp_path, monkeypatch, capsys):
    env = setup_repo(tmp_path, monkeypatch)

    assert (
        run_cli(
            env["report"],
            monkeypatch,
            "--artifact-type",
            "subfeature",
            "--group-by",
            "parent",
            "--json",
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    groups = groups_by_key(payload)

    assert payload["summary"]["total"] == 1
    assert groups["checkout"]["count"] == 1


def test_cli_rejects_non_positive_stale_days(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch)

    try:
        run_cli(env["report"], monkeypatch, "--stale-days", "0")
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("Expected argparse to reject stale-days=0")
