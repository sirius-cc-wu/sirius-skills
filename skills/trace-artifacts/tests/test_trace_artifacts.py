import importlib.util
import json
import shutil
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "trace_artifacts.py"
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


def run_cli(module, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["trace_artifacts.py", *args])
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
    trace = load_module(SCRIPT_PATH, "trace_artifacts")

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
    feature_metadata = planning.read_metadata(feature_dir)
    feature_metadata["consolidation"] = {
        "disposition": "narrowing",
        "targets": [
            {"kind": "subfeature", "ref": "checkout/subfeatures/replace-legacy-flow", "change": "narrows"}
        ],
        "historical_artifacts": ["docs/features/checkout/discover.md"],
        "surface_simplifications": ["keep one checkout planning path"],
        "justification": "The checkout baseline should stay canonical.",
    }
    planning.write_metadata(feature_dir, feature_metadata)
    planning.sync_registry()

    proposal_dir, _ = propose.create_proposal(
        "checkout-audit", summary="Audit checkout artifacts", target_feature="checkout"
    )

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
    execution.create_slice("CHK-102", "Followup Slice")

    subfeature_path = Path(subfeature_dir)
    (subfeature_path / "slice-traceability.md").write_text(
        "\n".join(
            [
                "# Slice Traceability",
                "",
                "| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                "| CHK-02 | M | Replace legacy flow | I1 | CHK-201 | parser, cli |  | CHK-101 | Primary migration slice |",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    _, _, slice_registry = execution.get_registry_paths(required_config=False)
    slice_rows = execution.load_registry_json(slice_registry)
    source_slice = next(row for row in slice_rows if row["id"] == "CHK-101")
    metadata = execution.load_slice_metadata(execution.slice_path_for_row(source_slice))
    metadata["relations"] = [
        {
            "type": "supersedes",
            "target_slice": "CHK-102",
            "recorded_at": "2026-01-03T00:00:00",
        }
    ]
    execution.write_slice_metadata(execution.slice_path_for_row(source_slice), metadata)
    subfeature_metadata = subfeatures.read_metadata(subfeature_dir)
    subfeature_metadata["consolidation"] = {
        "disposition": "superseding",
        "targets": [
            {"kind": "feature", "ref": "checkout", "change": "narrows"},
        ],
        "historical_artifacts": ["docs/features/checkout/system-design.md"],
        "surface_simplifications": ["route maintainers through the subfeature packet"],
        "justification": "The old flow should become historical context.",
    }
    subfeatures.write_metadata(subfeature_dir, subfeature_metadata)

    return {
        "trace": trace,
        "proposal_dir": Path(proposal_dir),
        "feature_dir": feature_path,
        "subfeature_dir": subfeature_path,
    }


def node_ids(payload: dict, artifact_type: str) -> set[str]:
    return {
        node["artifact_id"]
        for node in payload["nodes"]
        if node["artifact_type"] == artifact_type
    }


def edge_relations(payload: dict) -> set[str]:
    return {edge["relation"] for edge in payload["edges"]}


def test_run_trace_targets_proposal_lineage(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch)

    payload = env["trace"].run_trace("proposal", "checkout-audit")

    assert payload["target"]["artifact_type"] == "proposal"
    assert payload["target"]["artifact_id"] == "checkout-audit"
    assert "checkout" in node_ids(payload, "feature")
    assert "targets_feature" in edge_relations(payload)


def test_run_trace_targets_subfeature_with_planned_and_execution_slices(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch)

    payload = env["trace"].run_trace("subfeature", "replace-legacy-flow")

    assert "checkout" in node_ids(payload, "feature")
    assert "CHK-201" in node_ids(payload, "planned-slice")
    assert "CHK-101" in node_ids(payload, "slice")
    assert payload["target"]["details"]["consolidation"]["disposition"] == "superseding"
    assert payload["target"]["details"]["consolidation"]["historical_artifacts"] == [
        "docs/features/checkout/system-design.md"
    ]
    assert {"subfeature_of", "plans_slice", "bootstrapped_as", "narrows"}.issubset(
        edge_relations(payload)
    )


def test_cli_json_summary_includes_slice_relations(tmp_path, monkeypatch, capsys):
    env = setup_repo(tmp_path, monkeypatch)

    assert run_cli(env["trace"], monkeypatch, "--json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["ok"] is True
    assert payload["summary"]["node_counts"]["planned-slice"] == 1
    assert "supersedes" in payload["summary"]["edge_counts"]


def test_render_text_surfaces_consolidation_context(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch)

    payload = env["trace"].run_trace("feature", "checkout")
    rendered = env["trace"].render_text(payload)

    assert "consolidation=narrowing" in rendered
    assert "historical=1" in rendered


def test_cli_fails_for_missing_target(tmp_path, monkeypatch, capsys):
    env = setup_repo(tmp_path, monkeypatch)

    assert (
        run_cli(
            env["trace"],
            monkeypatch,
            "--artifact-type",
            "planned-slice",
            "--artifact-id",
            "MISSING-1",
        )
        == env["trace"].ERROR_EXIT_CODE
    )
    assert "Artifact not found: planned-slice:MISSING-1" in capsys.readouterr().err


def test_trace_module_loads_from_self_contained_skill_copy(tmp_path):
    isolated_root = copy_skill_for_isolated_import(tmp_path, "trace-artifacts")

    module = load_module(
        isolated_root / "scripts" / "trace_data.py",
        "isolated_trace_data",
    )

    assert hasattr(module, "build_trace_graph")
