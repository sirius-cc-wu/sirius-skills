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


def advance_feature_to_planning_reviewed(planning, monkeypatch, feature_slug: str):
    assert run_cli(planning, monkeypatch, "set-status", feature_slug, "discovery_ready") == 0
    assert run_cli(planning, monkeypatch, "set-status", feature_slug, "design_ready") == 0
    assert run_cli(planning, monkeypatch, "set-status", feature_slug, "breakdown_ready") == 0
    assert (
        run_cli(
            planning,
            monkeypatch,
            "set-status",
            feature_slug,
            "planning_reviewed",
            "--review-note",
            "Reviewed for execution handoff readiness.",
        )
        == 0
    )


def setup_repo(
    tmp_path: Path,
    monkeypatch,
    *,
    include_slice: bool = False,
    sync_planning_handoff: bool = False,
):
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
    (feature_path / "system-design.md").write_text("# System Design\n", encoding="utf-8")
    (feature_path / "slice-planning.md").write_text("# Slice Planning\n", encoding="utf-8")
    (feature_path / "slice-traceability.md").write_text("# Slice Traceability\n", encoding="utf-8")
    advance_feature_to_planning_reviewed(planning, monkeypatch, "checkout")
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

    slice_dir = None
    if include_slice:
        execution.create_slice("CHK-101", "checkout")
        slice_dir = tmp_path / "slices" / "CHK-101-checkout"
        if sync_planning_handoff:
            assert (
                run_cli(
                    planning,
                    monkeypatch,
                    "set-status",
                    "checkout",
                    "slice_ready",
                    "--slice-id",
                    "CHK-101",
                )
                == 0
            )

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
        "slice_dir": slice_dir,
    }


def finding_codes(result: dict) -> set[str]:
    return {finding["code"] for finding in result["findings"]}


def write_subfeature_traceability(
    subfeature_dir: Path, *, planned_slice_ids: list[str], execution_slice_ids: list[str]
):
    planned = ", ".join(planned_slice_ids)
    execution = ", ".join(execution_slice_ids)
    (subfeature_dir / "slice-traceability.md").write_text(
        "\n".join(
            [
                "# Slice Traceability",
                "",
                "| Story ID | Increments | Planned Slice IDs | Execution Slice IDs | Notes |",
                "| --- | --- | --- | --- | --- |",
                f"| CHK-01 | I1 | {planned} | {execution} | Test row |",
                "",
            ]
        ),
        encoding="utf-8",
    )


def create_closed_slice(execution, tmp_path: Path, slice_id: str, feature_name: str) -> Path:
    folder, created = execution.create_slice(slice_id, feature_name)
    assert created is True

    rows = execution.parse_registry()
    slice_row = execution.resolve_slice(rows, slice_id)
    assert slice_row is not None

    success, _ = execution.update_slice_status(rows, slice_row, "closed", force=True)
    assert success is True
    return tmp_path / "slices" / folder


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


def test_run_audit_reports_invalid_subfeature_status_as_metadata_read_error(
    tmp_path, monkeypatch
):
    # Arrange: Create a repo whose subfeature metadata uses a planning-layer status.
    env = setup_repo(tmp_path, monkeypatch)
    subfeature_meta_path = env["subfeature_dir"] / ".subfeature-meta.json"
    metadata = json.loads(subfeature_meta_path.read_text(encoding="utf-8"))
    metadata["status"] = "planning_reviewed"
    subfeature_meta_path.write_text(json.dumps(metadata) + "\n", encoding="utf-8")

    # Act: Run the audit against the affected artifact layer.
    result = env["audit"].run_audit(["subfeature"])

    # Assert: The audit reports the metadata failure instead of crashing.
    assert result["ok"] is False
    assert "metadata_read_error" in finding_codes(result)
    assert any(
        finding["artifact_type"] == "subfeature" for finding in result["findings"]
    )


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


def test_run_audit_reports_feature_status_drift_when_execution_exists(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch, include_slice=True)

    result = env["audit"].run_audit(["feature"])

    assert result["ok"] is False
    assert "planning_status_precedes_execution" in finding_codes(result)
    assert any(
        finding["artifact_type"] == "feature"
        and finding["artifact_id"] == "checkout"
        for finding in result["findings"]
    )


def test_run_audit_reports_subfeature_closed_execution_drift(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch)

    create_closed_slice(env["execution"], tmp_path, "CHK-201", "Replace Legacy Flow")
    write_subfeature_traceability(
        env["subfeature_dir"],
        planned_slice_ids=["CHK-201"],
        execution_slice_ids=["CHK-201"],
    )

    result = env["audit"].run_audit(["subfeature"])

    assert result["ok"] is False
    assert "subfeature_affected_slice_ids_out_of_sync" in finding_codes(result)
    assert "subfeature_status_precedes_closed_execution" in finding_codes(result)
    assert any(
        finding["artifact_type"] == "subfeature"
        and finding["artifact_id"] == "replace-legacy-flow"
        for finding in result["findings"]
    )


def test_run_audit_reports_missing_traceability_execution_slice_for_subfeature(
    tmp_path, monkeypatch
):
    env = setup_repo(tmp_path, monkeypatch)
    write_subfeature_traceability(
        env["subfeature_dir"],
        planned_slice_ids=["CHK-999"],
        execution_slice_ids=["CHK-999"],
    )

    result = env["audit"].run_audit(["subfeature"])

    assert result["ok"] is False
    assert "missing_traceability_execution_slice" in finding_codes(result)


def test_cli_json_reports_slice_relation_issues(tmp_path, monkeypatch, capsys):
    env = setup_repo(tmp_path, monkeypatch, include_slice=True, sync_planning_handoff=True)
    capsys.readouterr()

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
