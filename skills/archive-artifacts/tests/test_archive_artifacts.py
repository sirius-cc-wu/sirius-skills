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


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_closed_slice(execution, slice_id: str, feature_name: str, brief: str, blueprint: str):
    execution.create_slice(slice_id, feature_name)
    _, _, slice_registry = execution.get_registry_paths(required_config=False)
    slice_rows = execution.load_registry_json(slice_registry)
    slice_row = next(row for row in slice_rows if row["id"] == slice_id)
    slice_row["status"] = "closed"
    execution.write_registry(slice_rows)

    slice_dir = Path(execution.slice_path_for_row(slice_row))
    write_file(slice_dir / "brief.md", brief)
    write_file(slice_dir / "blueprint.md", blueprint)

    metadata = execution.load_slice_metadata(execution.slice_path_for_row(slice_row))
    metadata["status"] = "closed"
    metadata["closed_at"] = "2026-02-13T00:00:00"
    execution.write_slice_metadata(execution.slice_path_for_row(slice_row), metadata)
    return slice_dir


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
    feature_path = Path(feature_dir)
    write_file(feature_path / "system-design.md", "# System Design\n\nBaseline feature design.\n")
    write_file(
        feature_path / "slice-planning.md",
        "# Slice Planning\n\n"
        "## 4. Execution Slice Backlog\n\n"
        "| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        "| CHK-101 | CHK-01 | Archive checkout flow | Summarize and archive the checkout slice. | `checkout/` | primary | `pytest -q` | create slice |  | yes |\n",
    )

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
    subfeature_path = Path(subfeature_dir)
    write_file(subfeature_path / "system-design.md", "# System Design\n\nBaseline subfeature design.\n")
    write_file(
        subfeature_path / "slice-planning.md",
        "# Slice Planning\n\n"
        "## 4. Execution Slice Backlog\n\n"
        "| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        "| SUB-201 | CHK-02 | Replace legacy flow | Summarize and archive the subfeature slice. | `checkout/subfeature/` | primary | `pytest -q` | create slice |  | yes |\n",
    )

    create_closed_slice(
        execution,
        "CHK-101",
        "checkout",
        "# Slice Specification: Archive checkout flow\n\n"
        "## 1. Work Item Summary\n\n"
        "- **Work Item**: Archive checkout flow\n"
        "- **Requested Outcome**: Preserve the checkout slice as durable planning history.\n"
        "- **Why this matters**: The feature docs should retain the implementation summary.\n",
        "# Implementation Plan: Archive checkout flow\n\n"
        "## 1. Summary\n\n"
        "Capture the execution design for the checkout archive flow in one durable place.\n\n"
        "## 6. Supporting Notes\n\n"
        "```plantuml\n"
        "@startuml\n"
        "Alice -> Bob: archive\n"
        "@enduml\n"
        "```\n\n"
        "![Checkout Archive Diagram](figures/checkout-archive.svg)\n",
    )
    write_file(
        tmp_path / "slices" / "CHK-101-checkout" / "figures" / "checkout-archive.svg",
        "<svg></svg>\n",
    )

    create_closed_slice(
        execution,
        "SUB-201",
        "replace-legacy-flow",
        "# Slice Specification: Replace legacy flow\n\n"
        "## 1. Work Item Summary\n\n"
        "- **Work Item**: Replace legacy flow\n"
        "- **Requested Outcome**: Keep a durable summary in the subfeature design doc.\n",
        "# Implementation Plan: Replace legacy flow\n\n"
        "## 1. Summary\n\n"
        "Document the replacement flow design before archival.\n",
    )

    return {
        "archive": archive,
        "execution": execution,
        "feature_dir": feature_path,
        "subfeature_dir": subfeature_path,
    }


def test_build_archive_result_lists_scope_and_slice_candidates(tmp_path, monkeypatch):
    env = setup_repo(tmp_path, monkeypatch)

    payload = env["archive"].build_archive_result()

    assert payload["summary"]["candidate_count"] == 5
    assert payload["summary"]["archivable_count"] == 4


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
    assert "requires --artifact-type slice, feature, or subfeature" in capsys.readouterr().err


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
    assert archived_row["path"].startswith("slices/.archived/")


def test_build_archive_result_applies_feature_archive_and_updates_system_design(
    tmp_path, monkeypatch
):
    env = setup_repo(tmp_path, monkeypatch)

    payload = env["archive"].build_archive_result(
        artifact_type="feature",
        artifact_id="checkout",
        apply=True,
    )

    design_text = (env["feature_dir"] / "system-design.md").read_text(encoding="utf-8")
    _, _, slice_registry = env["execution"].get_registry_paths(required_config=False)
    slice_rows = env["execution"].load_registry_json(slice_registry)
    archived_row = next(row for row in slice_rows if row["id"] == "CHK-101")
    subfeature_row = next(row for row in slice_rows if row["id"] == "SUB-201")

    assert payload["applied"]["artifact_id"] == "checkout"
    assert payload["applied"]["archived_slice_ids"] == ["CHK-101"]
    assert archived_row["path"].startswith("slices/.archived/CHK-101-checkout/")
    assert not subfeature_row["path"].startswith("slices/.archived/SUB-201")
    assert "## Archived Slice Summaries" in design_text
    assert "`CHK-101`: Archive checkout flow" in design_text
    assert "Preserve the checkout slice as durable planning history." in design_text
    assert "Capture the execution design for the checkout archive flow" in design_text
    assert "```plantuml" in design_text
    assert "Archived from:" not in design_text
    assert "Archived to:" not in design_text
    assert "checkout-archive.svg" not in design_text


def test_build_archive_result_applies_subfeature_archive_and_updates_system_design(
    tmp_path, monkeypatch
):
    env = setup_repo(tmp_path, monkeypatch)

    payload = env["archive"].build_archive_result(
        artifact_type="subfeature",
        artifact_id="replace-legacy-flow",
        apply=True,
    )

    design_text = (env["subfeature_dir"] / "system-design.md").read_text(encoding="utf-8")
    _, _, slice_registry = env["execution"].get_registry_paths(required_config=False)
    slice_rows = env["execution"].load_registry_json(slice_registry)
    archived_row = next(row for row in slice_rows if row["id"] == "SUB-201")

    assert payload["applied"]["artifact_id"] == "replace-legacy-flow"
    assert payload["applied"]["archived_slice_ids"] == ["SUB-201"]
    assert archived_row["path"].startswith("slices/.archived/SUB-201-replace-legacy-flow/")
    assert "`SUB-201`: Replace legacy flow" in design_text
    assert "Document the replacement flow design before archival." in design_text


def test_cli_json_filters_one_artifact_type(tmp_path, monkeypatch, capsys):
    env = setup_repo(tmp_path, monkeypatch)

    assert run_cli(env["archive"], monkeypatch, "--artifact-type", "feature", "--json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["summary"]["candidate_count"] == 1
    assert payload["candidates"][0]["artifact_type"] == "feature"
