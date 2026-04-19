import importlib.util
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "report_artifacts.py"
VALIDATION_HOOK_SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "validate_workflow_state.py"
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


def copy_skill_for_isolated_import(tmp_path: Path, skill_name: str) -> Path:
    source_root = Path(__file__).resolve().parents[1]
    isolated_root = tmp_path / skill_name
    shutil.copytree(source_root / "scripts", isolated_root / "scripts")
    skill_lib = source_root / "lib"
    if skill_lib.exists():
        shutil.copytree(skill_lib, isolated_root / "lib")
    return isolated_root


def copy_installed_skill(tmp_path: Path, skill_name: str) -> Path:
    source_root = Path(__file__).resolve().parents[2] / skill_name
    installed_root = tmp_path / "installed-skills" / skill_name
    shutil.copytree(source_root, installed_root)
    return installed_root


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
    report_parity = report.build_report_result.__globals__["inspect_installed_skill_parity"]
    monkeypatch.setitem(
        report.build_report_result.__globals__,
        "inspect_installed_skill_parity",
        lambda installed_skills=None: [],
    )

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

    execution.create_slice("CHK-101", "checkout")
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

    return {
        "report": report,
        "report_parity": report_parity,
        "execution": execution,
    }


def groups_by_key(payload: dict) -> dict:
    return {group["key"]: group for group in payload["groups"]}


def archive_closed_slice(execution, slice_id: str) -> dict:
    rows = execution.parse_registry()
    slice_row = execution.resolve_slice(rows, slice_id)
    assert slice_row is not None
    archived, _, updated_slice = execution.archive_slice(rows, slice_row)
    assert archived is True
    return updated_slice


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


def test_run_report_excludes_archived_slices_from_default_operational_view(
    tmp_path, monkeypatch
):
    env = setup_repo(tmp_path, monkeypatch)
    archive_closed_slice(env["execution"], "CHK-101")

    payload = env["report"].build_report_result(
        group_by="overview",
        stale_days=30,
        now=datetime(2026, 2, 15),
    )

    assert payload["summary"]["total"] == 3
    assert all(record["artifact_type"] != "slice" for record in payload["records"])
    assert "slice" not in groups_by_key(payload)


def test_run_report_preserves_raw_subfeature_status_when_reader_rejects_it(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch)
    subfeature_meta_path = (
        tmp_path
        / "docs"
        / "features"
        / "checkout"
        / "subfeatures"
        / "replace-legacy-flow"
        / ".subfeature-meta.json"
    )
    payload = json.loads(subfeature_meta_path.read_text(encoding="utf-8"))
    payload["status"] = "planning_reviewed"
    subfeature_meta_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    report = env["report"].build_report_result(
        artifact_types=["subfeature"],
        group_by="status",
        stale_days=30,
        now=datetime(2026, 2, 15),
    )

    groups = groups_by_key(report)
    assert groups["planning_reviewed"]["count"] == 1
    assert report["records"][0]["status"] == "planning_reviewed"


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


def test_run_report_includes_persisted_metrics_when_sidecar_exists(tmp_path, monkeypatch, capsys):
    env = setup_repo(tmp_path, monkeypatch)
    subfeature_dir = (
        tmp_path
        / "docs"
        / "features"
        / "checkout"
        / "subfeatures"
        / "replace-legacy-flow"
    )
    sidecar_payload = {
        "artifact_type": "subfeature",
        "artifact_id": "replace-legacy-flow",
        "computed_at": "2026-02-15T00:00:00",
        "status": "implemented",
        "execution_mode": "guided",
        "story_size": {
            "weights": {"S": 1, "M": 3, "L": 5},
            "sum_points": 5,
            "unsupported_sizes": [],
        },
        "slices": {"planned_count": 2, "linked_slice_ids": ["CHK-101", "CHK-102"]},
        "implementation_churn": {
            "added_lines": None,
            "deleted_lines": None,
            "total_changed_lines": None,
            "source_commit_shas": [],
            "confidence": "unavailable",
        },
        "workflow_outcomes": {
            "follow_up_fix_count": None,
            "review_findings_count": None,
            "planning_drift": None,
        },
    }
    (subfeature_dir / "implementation-metrics.json").write_text(
        json.dumps(sidecar_payload) + "\n", encoding="utf-8"
    )

    payload = env["report"].build_report_result(
        artifact_types=["subfeature"],
        group_by="parent",
        stale_days=30,
        now=datetime(2026, 2, 15),
    )

    assert payload["records"][0]["implementation_metrics"]["execution_mode"] == "guided"
    assert payload["records"][0]["implementation_metrics"]["story_size"]["sum_points"] == 5

    assert run_cli(
        env["report"], monkeypatch, "--artifact-type", "subfeature", "--group-by", "parent"
    ) == 0
    output = capsys.readouterr().out
    assert "metrics mode=guided" in output


def test_run_report_surfaces_semantic_preview_separately(tmp_path, monkeypatch, capsys):
    env = setup_repo(tmp_path, monkeypatch)

    payload = env["report"].build_report_result(
        artifact_types=["feature"],
        group_by="overview",
        stale_days=30,
        now=datetime(2026, 2, 15),
    )

    assert payload["summary"]["semantic_preview_count"] == 1
    assert payload["semantic_preview"][0]["code"] == "repair_planning_status_handoff"

    assert run_cli(env["report"], monkeypatch, "--artifact-type", "feature") == 0
    output = capsys.readouterr().out
    assert "Semantic preview:" in output
    assert "repair_planning_status_handoff" in output


def test_workflow_state_validation_hook_runs_from_repo_root_and_returns_exit_code(monkeypatch):
    module = load_module(VALIDATION_HOOK_SCRIPT, "validate_workflow_state_main")
    calls = {}

    def fake_run(command, cwd, check):
        calls["command"] = command
        calls["cwd"] = cwd
        calls["check"] = check
        return subprocess.CompletedProcess(command, 7)

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    assert module.main(["--", "-k", "parity"]) == 7
    assert calls["command"] == [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "skills/audit-artifacts/tests/test_audit_artifacts.py",
        "skills/report-artifacts/tests/test_report_artifacts.py",
        "skills/guide-planning/tests/test_manage_planning.py",
        "skills/close-slice/tests/test_close_slice.py",
        "-k",
        "parity",
    ]
    assert calls["cwd"] == module.REPO_ROOT
    assert calls["check"] is False


def test_run_report_keeps_clean_installed_parity_quiet(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch)
    installed_root = copy_installed_skill(tmp_path, "report-artifacts")
    monkeypatch.setitem(
        env["report"].build_report_result.__globals__,
        "inspect_installed_skill_parity",
        env["report_parity"],
    )

    payload = env["report"].build_report_result(
        group_by="overview",
        stale_days=30,
        now=datetime(2026, 2, 15),
        installed_skills=[{"name": "report-artifacts", "path": str(installed_root)}],
        check_packaged_parity=True,
    )

    assert payload["summary"]["installed_parity_count"] == 0
    assert payload["installed_parity"] == []


def test_run_report_surfaces_installed_parity_separately(tmp_path, monkeypatch, capsys):
    env = setup_repo(tmp_path, monkeypatch)
    installed_root = copy_installed_skill(tmp_path, "report-artifacts")
    monkeypatch.setitem(
        env["report"].build_report_result.__globals__,
        "inspect_installed_skill_parity",
        env["report_parity"],
    )
    installed_script = installed_root / "scripts" / "report_data.py"
    installed_script.write_text(
        installed_script.read_text(encoding="utf-8") + "\n# stale installed copy\n",
        encoding="utf-8",
    )

    payload = env["report"].build_report_result(
        artifact_types=["feature"],
        group_by="overview",
        stale_days=30,
        now=datetime(2026, 2, 15),
        installed_skills=[{"name": "report-artifacts", "path": str(installed_root)}],
        check_packaged_parity=True,
    )

    assert payload["summary"]["installed_parity_count"] == 1
    assert payload["installed_parity"][0]["code"] == "content_mismatch"
    assert payload["installed_parity"][0]["relative_path"] == "scripts/report_data.py"

    text = env["report"].render_text(payload)
    assert "Installed parity:" in text
    assert "scripts/report_data.py" in text


def test_run_report_surfaces_installed_parity_unavailable_without_crashing(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch)
    monkeypatch.setitem(
        env["report"].build_report_result.__globals__,
        "inspect_installed_skill_parity",
        env["report_parity"],
    )
    monkeypatch.setattr(env["report_parity"].__globals__["Path"], "home", lambda: tmp_path)

    payload = env["report"].build_report_result(
        artifact_types=["feature"],
        group_by="overview",
        stale_days=30,
        now=datetime(2026, 2, 15),
        check_packaged_parity=True,
    )

    assert payload["summary"]["installed_parity_count"] == 1
    assert payload["installed_parity"][0]["code"] == "installed_parity_unavailable"
    assert "no installed skills found under" in payload["installed_parity"][0]["message"]


def test_run_report_discovers_local_skill_home_without_cli_dependency(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch)
    monkeypatch.setitem(
        env["report"].build_report_result.__globals__,
        "inspect_installed_skill_parity",
        env["report_parity"],
    )
    fake_home = tmp_path / "fake-home"
    installed_root = fake_home / ".agents" / "skills" / "report-artifacts"
    shutil.copytree(Path(__file__).resolve().parents[2] / "report-artifacts", installed_root)
    monkeypatch.setattr(env["report_parity"].__globals__["Path"], "home", lambda: fake_home)

    payload = env["report"].build_report_result(
        artifact_types=["feature"],
        group_by="overview",
        stale_days=30,
        now=datetime(2026, 2, 15),
        check_packaged_parity=True,
    )

    assert payload["summary"]["installed_parity_count"] == 0
    assert payload["installed_parity"] == []


def test_run_report_skips_packaged_parity_by_default(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("installed parity should be opt-in")

    monkeypatch.setitem(
        env["report"].build_report_result.__globals__,
        "inspect_installed_skill_parity",
        fail_if_called,
    )

    payload = env["report"].build_report_result(
        artifact_types=["feature"],
        group_by="overview",
        stale_days=30,
        now=datetime(2026, 2, 15),
    )

    assert payload["check_packaged_parity"] is False
    assert payload["summary"]["installed_parity_count"] == 0
    assert payload["installed_parity"] == []
    assert "Installed parity findings" not in env["report"].render_text(payload)


def test_report_module_loads_from_self_contained_skill_copy(tmp_path):
    isolated_root = copy_skill_for_isolated_import(tmp_path, "report-artifacts")

    module = load_module(
        isolated_root / "scripts" / "report_data.py",
        "isolated_report_data",
    )

    assert hasattr(module, "build_report_result")


def test_report_cli_runs_from_installed_style_copy(tmp_path):
    for dependency in (
        "propose",
        "guide-planning",
        "add-subfeature",
        "guide-execution",
    ):
        copy_installed_skill(tmp_path, dependency)
    installed_root = copy_installed_skill(tmp_path, "report-artifacts")

    completed = subprocess.run(
        [sys.executable, str(installed_root / "scripts" / "report_artifacts.py"), "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert "Report operational workflow state across proposals" in completed.stdout
