import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[3] / "src" / "sirius_skills" / "commands" / "record_review.py"
PLANNING_SCRIPT_PATH = (
    Path(__file__).resolve().parents[3] / "src" / "sirius_skills" / "commands" / "manage_planning.py"
)
SUBFEATURE_SCRIPT_PATH = (
    Path(__file__).resolve().parents[3] / "src" / "sirius_skills" / "commands" / "manage_subfeatures.py"
)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_cli(module, script_name: str, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", [script_name, *args])
    return module.main()


def write_file(path: Path, content: str = "# doc\n"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def setup_feature(tmp_path: Path):
    planning_module = load_module(PLANNING_SCRIPT_PATH, "review_manage_planning")
    feature_dir = tmp_path / "docs" / "features" / "checkout"
    feature_dir.mkdir(parents=True, exist_ok=True)
    (tmp_path / ".skills").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".skills" / "planning.json").write_text(
        json.dumps({"planning_dir": "docs/features"}) + "\n", encoding="utf-8"
    )
    feature_dir_str, _ = planning_module.create_feature("checkout")
    feature_path = Path(feature_dir_str)
    write_file(feature_path / "discover.md", "# Discover\n")
    write_file(feature_path / "system-design.md", "# Design\n")
    write_file(feature_path / "slice-planning.md", "# Slice Planning\n")
    write_file(feature_path / "slice-traceability.md", "# Slice Traceability\n")
    rows = planning_module.parse_registry()
    feature = planning_module.find_feature(rows, "checkout")
    assert feature is not None
    for status in ("discovery_ready", "design_ready", "breakdown_ready"):
        ok, message = planning_module.update_feature_status(rows, feature, status)
        assert ok, message
    return feature_path


def setup_subfeature(tmp_path: Path, monkeypatch):
    planning_module = load_module(PLANNING_SCRIPT_PATH, "review_manage_planning_sub")
    subfeature_module = load_module(SUBFEATURE_SCRIPT_PATH, "review_manage_subfeatures")
    monkeypatch.chdir(tmp_path)
    feature_path = setup_feature(tmp_path)
    assert run_cli(
        subfeature_module,
        "manage_subfeatures.py",
        monkeypatch,
        "add",
        "checkout",
        "replace-legacy-flow",
    ) == 0
    subfeature_path = feature_path / "subfeatures" / "replace-legacy-flow"
    write_file(subfeature_path / "impact-analysis.md", "# Impact\n")
    write_file(subfeature_path / "system-design.md", "# Design\n")
    write_file(subfeature_path / "slice-planning.md", "# Slice Planning\n")
    write_file(subfeature_path / "slice-traceability.md", "# Slice Traceability\n")
    assert run_cli(
        subfeature_module,
        "manage_subfeatures.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "impact_ready",
    ) == 0
    assert run_cli(
        subfeature_module,
        "manage_subfeatures.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "design_ready",
    ) == 0
    assert run_cli(
        subfeature_module,
        "manage_subfeatures.py",
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "breakdown_ready",
    ) == 0
    return subfeature_path, planning_module, subfeature_module


def test_record_review_advances_feature_to_planning_reviewed(tmp_path, monkeypatch):
    module = load_module(SCRIPT_PATH, "record_review")
    planning_module = load_module(PLANNING_SCRIPT_PATH, "review_manage_planning_check")
    monkeypatch.chdir(tmp_path)
    feature_path = setup_feature(tmp_path)

    assert run_cli(
        module,
        "record_review.py",
        monkeypatch,
        "checkout",
        "--review-note",
        "Ready for approval",
    ) == 0

    metadata = planning_module.read_metadata(str(feature_path))
    assert metadata["status"] == "planning_reviewed"
    assert metadata["review_note"] == "Ready for approval"


def test_record_review_advances_subfeature_to_reviewed(tmp_path, monkeypatch):
    module = load_module(SCRIPT_PATH, "record_review_sub")
    monkeypatch.chdir(tmp_path)
    subfeature_path, planning_module, subfeature_module = setup_subfeature(tmp_path, monkeypatch)

    assert run_cli(
        module,
        "record_review.py",
        monkeypatch,
        "docs/features/checkout/subfeatures/replace-legacy-flow",
        "--review-note",
        "Ready for approval",
    ) == 0

    subfeature_metadata = subfeature_module.read_metadata(str(subfeature_path))
    planning_metadata = planning_module.read_metadata(str(subfeature_path))
    assert subfeature_metadata["status"] == "reviewed"
    assert subfeature_metadata["review_note"] == "Ready for approval"
    assert planning_metadata["status"] == "planning_reviewed"
