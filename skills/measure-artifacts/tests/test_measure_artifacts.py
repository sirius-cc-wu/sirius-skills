import importlib.util
import json
import sys
from pathlib import Path


ENGINE_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "metrics_engine.py"
CLI_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "measure_artifacts.py"
STORE_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "metrics_store.py"
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
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def write_scope_config(root: Path, filename: str, payload: dict):
    skills_dir = root / ".skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    (skills_dir / filename).write_text(json.dumps(payload) + "\n", encoding="utf-8")


def run_cli(module, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["measure_artifacts.py", *args])
    return module.main()


def write_traceability(
    target_dir: Path,
    *,
    story_size: str,
    planned_slice_ids: list[str],
    execution_slice_ids: list[str],
    story_id: str = "CHK-01",
):
    planned = ", ".join(planned_slice_ids)
    execution = ", ".join(execution_slice_ids)
    target_dir.joinpath("slice-traceability.md").write_text(
        "\n".join(
            [
                "# Slice Traceability",
                "",
                "| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                f"| {story_id} | {story_size} | Summary | I1 | {planned} | area |  | {execution} | Test row |",
                "",
            ]
        ),
        encoding="utf-8",
    )


def create_closed_slice(execution, slice_id: str, feature_name: str):
    _, created = execution.create_slice(slice_id, feature_name)
    assert created is True
    rows = execution.parse_registry()
    slice_row = execution.resolve_slice(rows, slice_id)
    assert slice_row is not None
    success, _ = execution.update_slice_status(rows, slice_row, "closed", force=True)
    assert success is True


def setup_repo(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    planning = load_module(PLANNING_SCRIPT, "measure_test_manage_planning")
    subfeatures = load_module(SUBFEATURE_SCRIPT, "measure_test_manage_subfeatures")
    execution = load_module(EXECUTION_SCRIPT, "measure_test_manage_execution")
    engine = load_module(ENGINE_SCRIPT, "measure_test_metrics_engine")
    cli = load_module(CLI_SCRIPT, "measure_test_measure_artifacts")
    store = load_module(STORE_SCRIPT, "measure_test_metrics_store")

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

    return {
        "planning": planning,
        "subfeatures": subfeatures,
        "execution": execution,
        "engine": engine,
        "cli": cli,
        "store": store,
    }


def create_feature_target(env, slug: str, *, story_size: str, execution_slice_ids: list[str]):
    planning = env["planning"]
    feature_dir, _ = planning.create_feature(slug)
    feature_path = Path(feature_dir)
    feature_path.joinpath("discover.md").write_text("# Discover\n", encoding="utf-8")
    feature_path.joinpath("system-design.md").write_text("# System Design\n", encoding="utf-8")
    feature_path.joinpath("slice-planning.md").write_text("# Slice Planning\n", encoding="utf-8")
    write_traceability(
        feature_path,
        story_size=story_size,
        planned_slice_ids=["CHK-101"],
        execution_slice_ids=execution_slice_ids,
    )
    metadata = planning.read_metadata(feature_dir)
    metadata["status"] = "implemented"
    planning.write_metadata(feature_dir, metadata)
    planning.sync_registry()
    return feature_path


def create_finalized_subfeature_target(env):
    planning = env["planning"]
    subfeatures = env["subfeatures"]
    execution = env["execution"]

    feature_dir, _ = planning.create_feature("checkout")
    feature_path = Path(feature_dir)
    feature_path.joinpath("discover.md").write_text("# Discover\n", encoding="utf-8")
    feature_path.joinpath("system-design.md").write_text("# System Design\n", encoding="utf-8")
    feature_path.joinpath("slice-planning.md").write_text("# Slice Planning\n", encoding="utf-8")
    feature_path.joinpath("slice-traceability.md").write_text("# Slice Traceability\n", encoding="utf-8")
    feature_metadata = planning.read_metadata(feature_dir)
    feature_metadata["status"] = "implemented"
    planning.write_metadata(feature_dir, feature_metadata)

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
    subfeature_path = Path(subfeature_dir)
    subfeature_path.joinpath("discover.md").write_text("# Discover\n", encoding="utf-8")
    subfeature_path.joinpath("impact-analysis.md").write_text("# Impact Analysis\n", encoding="utf-8")
    subfeature_path.joinpath("system-design.md").write_text("# System Design\n", encoding="utf-8")
    subfeature_path.joinpath("slice-planning.md").write_text("# Slice Planning\n", encoding="utf-8")
    subfeature_path.joinpath("slice-traceability.md").write_text(
        "\n".join(
            [
                "# Slice Traceability",
                "",
                "| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                "| CAM-06 | L | Summary | I1 | mea-metrics-foundation | Metrics |  | mea-metrics-foundation | Foundation |",
                "| CAM-06 | L | Summary | I2 | mea-metrics-consumers | CLI | mea-metrics-foundation | mea-metrics-consumers | Consumers |",
                "",
            ]
        ),
        encoding="utf-8",
    )

    create_closed_slice(execution, "mea-metrics-foundation", "Foundation")
    create_closed_slice(execution, "mea-metrics-consumers", "Consumers")

    subfeature_metadata = subfeatures.read_metadata(subfeature_dir)
    subfeature_metadata["status"] = "finalized"
    subfeatures.write_metadata(subfeature_dir, subfeature_metadata)

    planning_metadata = planning.read_metadata(subfeature_dir)
    planning_metadata["status"] = "implemented"
    planning.write_metadata(subfeature_dir, planning_metadata)
    planning.sync_registry()
    return subfeature_path


def test_resolve_target_returns_implemented_feature(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch)
    feature_path = create_feature_target(
        env, "checkout", story_size="M", execution_slice_ids=[]
    )

    target = env["engine"].resolve_measurement_target("checkout")

    assert target.artifact_type == "feature"
    assert target.artifact_id == "checkout"
    assert target.artifact_path == feature_path
    assert target.status == "implemented"


def test_build_metrics_record_derives_direct_feature_metrics(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch)
    create_feature_target(env, "checkout", story_size="M", execution_slice_ids=[])

    record = env["engine"].build_metrics_record(
        "checkout", computed_at="2026-04-18T02:00:00"
    )

    assert record["story_size"]["sum_points"] == 3
    assert record["story_size"]["unsupported_sizes"] == []
    assert record["slices"]["planned_count"] == 1
    assert record["slices"]["linked_slice_ids"] == []
    assert record["execution_mode"] == "direct"
    assert record["implementation_churn"]["confidence"] == "unavailable"
    assert record["implementation_churn"]["total_changed_lines"] is None


def test_build_metrics_record_derives_guided_subfeature_metrics(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch)
    subfeature_path = create_finalized_subfeature_target(env)

    record = env["engine"].build_metrics_record(
        str(subfeature_path), computed_at="2026-04-18T02:00:00"
    )

    assert record["artifact_type"] == "subfeature"
    assert record["artifact_id"] == "replace-legacy-flow"
    assert record["story_size"]["sum_points"] == 5
    assert record["slices"]["planned_count"] == 2
    assert record["slices"]["linked_slice_ids"] == [
        "mea-metrics-foundation",
        "mea-metrics-consumers",
    ]
    assert record["execution_mode"] == "guided"


def test_build_metrics_record_surfaces_unsupported_story_sizes(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch)
    create_feature_target(env, "checkout", story_size="XL", execution_slice_ids=[])

    record = env["engine"].build_metrics_record(
        "checkout", computed_at="2026-04-18T02:00:00"
    )

    assert record["story_size"]["sum_points"] is None
    assert record["story_size"]["unsupported_sizes"] == ["XL"]


def test_sidecar_write_is_deterministic(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch)
    feature_path = create_feature_target(
        env, "checkout", story_size="S", execution_slice_ids=[]
    )
    record = env["engine"].build_metrics_record(
        "checkout", computed_at="2026-04-18T02:00:00"
    )

    sidecar_path = env["store"].write_metrics(feature_path, record)
    first = sidecar_path.read_text(encoding="utf-8")
    env["store"].write_metrics(feature_path, record)
    second = sidecar_path.read_text(encoding="utf-8")

    assert first == second
    assert env["store"].read_metrics(feature_path) == record


def test_cli_json_can_persist_metrics_sidecar(tmp_path, monkeypatch, capsys):
    env = setup_repo(tmp_path, monkeypatch)
    create_feature_target(env, "checkout", story_size="S", execution_slice_ids=[])

    assert run_cli(env["cli"], monkeypatch, "checkout", "--json", "--write") == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["artifact_id"] == "checkout"
    assert payload["persisted"] is True
    sidecar_path = Path(payload["sidecar_path"])
    assert sidecar_path.exists()


def test_cli_text_reports_unavailable_churn(tmp_path, monkeypatch, capsys):
    env = setup_repo(tmp_path, monkeypatch)
    create_feature_target(env, "checkout", story_size="M", execution_slice_ids=[])

    assert run_cli(env["cli"], monkeypatch, "checkout") == 0

    output = capsys.readouterr().out
    assert "Measurement target: feature checkout" in output
    assert "Execution mode: direct" in output
    assert "total changed lines: unavailable" in output
