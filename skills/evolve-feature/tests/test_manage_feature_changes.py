import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "manage_feature_changes.py"


def load_module():
    spec = importlib.util.spec_from_file_location("manage_feature_changes", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_cli(module, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["manage_feature_changes.py", *args])
    return module.main()


def write_file(path: Path, content: str = "# doc\n"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def setup_feature(tmp_path: Path):
    feature_dir = tmp_path / "docs" / "features" / "checkout"
    feature_dir.mkdir(parents=True, exist_ok=True)
    (tmp_path / ".skills").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".skills" / "planning.json").write_text(
        json.dumps({"planning_dir": "docs/features"}) + "\n", encoding="utf-8"
    )
    (feature_dir / ".planning-meta.json").write_text(
        json.dumps(
            {
                "feature_slug": "checkout",
                "status": "planning_reviewed",
                "created_at": "2026-01-01T00:00:00",
                "updated_at": "2026-01-01T00:00:00",
                "requires_ui_flow": False,
                "review_note": "ready",
                "ready_slice_ids": ["CHK-101"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return feature_dir


def test_init_feature_creates_registry_files(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.chdir(tmp_path)
    feature_dir = setup_feature(tmp_path)

    assert run_cli(module, monkeypatch, "init-feature", "checkout") == 0

    changes_dir = feature_dir / "changes"
    assert (changes_dir / "README.md").exists()
    registry = json.loads((changes_dir / "registry.json").read_text(encoding="utf-8"))
    assert registry["changes"] == []


def test_add_creates_change_packet_and_metadata(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.chdir(tmp_path)
    feature_dir = setup_feature(tmp_path)

    assert (
        run_cli(
            module,
            monkeypatch,
            "add",
            "checkout",
            "replace-legacy-flow",
            "--type",
            "superseding",
            "--summary",
            "Replace the legacy checkout path",
        )
        == 0
    )

    change_dir = feature_dir / "changes" / "replace-legacy-flow"
    metadata = json.loads((change_dir / ".feature-change-meta.json").read_text(encoding="utf-8"))
    registry = json.loads((feature_dir / "changes" / "registry.json").read_text(encoding="utf-8"))

    assert metadata["change_id"] == "replace-legacy-flow"
    assert metadata["feature_slug"] == "checkout"
    assert metadata["status"] == "draft"
    assert metadata["change_type"] == "superseding"
    assert metadata["summary"] == "Replace the legacy checkout path"
    assert metadata["active_change"] is True
    assert (change_dir / "discover.md").exists()
    assert registry["changes"][0]["change_id"] == "replace-legacy-flow"


def test_add_rejects_second_active_open_change(tmp_path, monkeypatch, capsys):
    module = load_module()
    monkeypatch.chdir(tmp_path)
    setup_feature(tmp_path)

    assert run_cli(module, monkeypatch, "add", "checkout", "replace-legacy-flow") == 0
    assert run_cli(module, monkeypatch, "add", "checkout", "add-fast-lane") == 2

    captured = capsys.readouterr()
    assert "active open change" in captured.err


def test_get_active_returns_open_change(tmp_path, monkeypatch, capsys):
    module = load_module()
    monkeypatch.chdir(tmp_path)
    setup_feature(tmp_path)

    assert run_cli(module, monkeypatch, "add", "checkout", "replace-legacy-flow") == 0
    capsys.readouterr()
    assert run_cli(module, monkeypatch, "get-active", "checkout") == 0

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["change_id"] == "replace-legacy-flow"


def test_impact_ready_requires_impact_analysis(tmp_path, monkeypatch, capsys):
    module = load_module()
    monkeypatch.chdir(tmp_path)
    feature_dir = setup_feature(tmp_path)

    assert run_cli(module, monkeypatch, "add", "checkout", "replace-legacy-flow") == 0
    exit_code = run_cli(
        module,
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "impact_ready",
    )
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Missing required file 'impact-analysis.md'." in captured.err

    write_file(feature_dir / "changes" / "replace-legacy-flow" / "impact-analysis.md")
    assert run_cli(
        module,
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "impact_ready",
        "--affected-artifact",
        "docs/features/checkout/discover.md",
        "--story-id",
        "CHK-01",
    ) == 0


def test_reviewed_requires_review_note_and_closed_allows_new_change(tmp_path, monkeypatch, capsys):
    module = load_module()
    monkeypatch.chdir(tmp_path)
    feature_dir = setup_feature(tmp_path)

    assert run_cli(module, monkeypatch, "add", "checkout", "replace-legacy-flow") == 0
    change_dir = feature_dir / "changes" / "replace-legacy-flow"
    write_file(change_dir / "impact-analysis.md")
    write_file(change_dir / "system-design.md")
    write_file(change_dir / "slice-planning.md")
    write_file(change_dir / "slice-traceability.md")

    assert run_cli(
        module,
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "impact_ready",
    ) == 0
    assert run_cli(
        module,
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "design_ready",
    ) == 0
    assert run_cli(
        module,
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "breakdown_ready",
    ) == 0

    exit_code = run_cli(
        module,
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "reviewed",
    )
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Reviewed state requires a non-empty review note." in captured.err

    assert run_cli(
        module,
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "reviewed",
        "--review-note",
        "Reviewed and ready for reconciliation planning.",
    ) == 0
    write_file(change_dir / "reconciliation.md")
    assert run_cli(
        module,
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "reconciled",
        "--reconciled-file",
        "docs/features/checkout/system-design.md",
    ) == 0
    assert run_cli(
        module,
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "closed",
        "--history-target",
        "docs/features/checkout/changes/README.md",
    ) == 0

    metadata = json.loads((change_dir / ".feature-change-meta.json").read_text(encoding="utf-8"))
    assert metadata["active_change"] is False
    assert run_cli(module, monkeypatch, "add", "checkout", "add-fast-lane") == 0


def test_validate_reports_success_for_closed_change(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.chdir(tmp_path)
    feature_dir = setup_feature(tmp_path)

    assert run_cli(module, monkeypatch, "add", "checkout", "replace-legacy-flow") == 0
    change_dir = feature_dir / "changes" / "replace-legacy-flow"
    write_file(change_dir / "impact-analysis.md")
    write_file(change_dir / "system-design.md")
    write_file(change_dir / "slice-planning.md")
    write_file(change_dir / "slice-traceability.md")
    write_file(change_dir / "reconciliation.md")

    assert run_cli(module, monkeypatch, "set-status", "checkout", "replace-legacy-flow", "impact_ready") == 0
    assert run_cli(module, monkeypatch, "set-status", "checkout", "replace-legacy-flow", "design_ready") == 0
    assert run_cli(module, monkeypatch, "set-status", "checkout", "replace-legacy-flow", "breakdown_ready") == 0
    assert run_cli(
        module,
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "reviewed",
        "--review-note",
        "Reviewed and ready for reconciliation planning.",
    ) == 0
    assert run_cli(
        module,
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "reconciled",
        "--reconciled-file",
        "docs/features/checkout/system-design.md",
    ) == 0
    assert run_cli(
        module,
        monkeypatch,
        "set-status",
        "checkout",
        "replace-legacy-flow",
        "closed",
    ) == 0

    monkeypatch.setattr(
        sys,
        "argv",
        ["manage_feature_changes.py", "validate", "checkout", "replace-legacy-flow"],
    )
    assert module.main() == 0
