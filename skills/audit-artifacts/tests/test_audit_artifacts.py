import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "audit_artifacts.py"
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
    monkeypatch.setattr(sys, "argv", ["audit_artifacts.py", *args])
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
    audit = load_module(SCRIPT_PATH, "audit_artifacts")

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
    (feature_path / "discover.md").write_text("# Discover\n", encoding="utf-8")
    planning.sync_registry()

    proposal_dir, _ = propose.create_proposal(
        "checkout-audit", summary="Audit checkout artifacts", target_feature="checkout"
    )
    propose_rows = propose.load_registry()
    proposal_row = propose.find_proposal(propose_rows, "checkout-audit")
    assert proposal_row is not None

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

    execution.create_slice("CHK-101", "Checkout Slice")

    return {
        "audit": audit,
        "propose": propose,
        "planning": planning,
        "subfeatures": subfeatures,
        "execution": execution,
        "feature_dir": feature_path,
        "proposal_dir": Path(proposal_dir),
        "proposal_row": proposal_row,
        "subfeature_dir": Path(subfeature_dir),
        "slice_dir": tmp_path / "slices" / "CHK-101-checkout-slice",
    }


def finding_codes(result: dict) -> set[str]:
    return {finding["code"] for finding in result["findings"]}


def test_run_audit_reports_clean_inventory(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch)

    result = env["audit"].run_audit()

    assert result["ok"] is True
    assert result["findings"] == []


def test_run_audit_reports_metadata_read_error_without_stopping(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch)
    (env["proposal_dir"] / ".proposal-meta.json").write_text("{not-json}\n", encoding="utf-8")

    result = env["audit"].run_audit(["proposal", "feature"])

    assert result["ok"] is False
    assert "metadata_read_error" in finding_codes(result)
    assert any(finding["artifact_type"] == "proposal" for finding in result["findings"])


def test_run_audit_reports_missing_promoted_feature_and_subfeature_registry_drift(
    tmp_path, monkeypatch
):
    env = setup_repo(tmp_path, monkeypatch)
    propose = env["propose"]

    metadata = propose.read_metadata(str(env["proposal_dir"]))
    metadata["status"] = "promoted"
    metadata["promoted_feature"] = "missing-feature"
    metadata["promoted_at"] = "2026-01-03T00:00:00"
    metadata["review_note"] = "Promoted."
    propose.write_metadata(str(env["proposal_dir"]), metadata)

    rows = propose.load_registry()
    row = propose.find_proposal(rows, "checkout-audit")
    assert row is not None
    row["status"] = "promoted"
    propose.write_registry(rows)

    (env["subfeature_dir"]).rename(env["subfeature_dir"].with_name("moved-subfeature"))

    result = env["audit"].run_audit()

    assert result["ok"] is False
    assert "missing_promoted_feature" in finding_codes(result)
    assert "planning_registry_path_missing" in finding_codes(result)
    assert "subfeature_registry_path_missing" in finding_codes(result)


def test_cli_json_reports_slice_relation_issues(tmp_path, monkeypatch, capsys):
    env = setup_repo(tmp_path, monkeypatch)

    metadata = json.loads((env["slice_dir"] / ".slice-meta.json").read_text(encoding="utf-8"))
    metadata["relations"] = [
        {
            "type": "supersedes",
            "target_slice": "CHK-999",
            "recorded_at": "2026-01-03T00:00:00",
        }
    ]
    (env["slice_dir"] / ".slice-meta.json").write_text(
        json.dumps(metadata) + "\n", encoding="utf-8"
    )

    assert run_cli(env["audit"], monkeypatch, "--json") == env["audit"].FINDINGS_EXIT_CODE
    payload = json.loads(capsys.readouterr().out)

    assert payload["ok"] is False
    assert "missing_target_slice" in finding_codes(payload)
