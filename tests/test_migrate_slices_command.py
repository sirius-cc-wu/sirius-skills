from __future__ import annotations

import json
from pathlib import Path

from sirius_skills.commands import bootstrap, migrate_slices


def test_package_migrate_slices_requires_exactly_one_target(capsys) -> None:
    result = migrate_slices.main(["scan"])

    captured = capsys.readouterr()
    assert result == 2
    assert "Specify exactly one target: a feature or --all." in captured.err


def test_package_migrate_slices_moves_active_and_archived_slices(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    assert bootstrap.main(["--mode", "default"]) == 0

    from sirius_skills.commands import manage_execution, manage_planning

    _, created = manage_planning.create_feature("checkout")
    assert created is True

    active_folder, created = manage_execution.create_slice("SPC-001", "checkout")
    assert created is True

    archived_folder, created = manage_execution.create_slice("SPC-002", "checkout")
    assert created is True

    rows = manage_execution.parse_registry()
    archived_row = manage_execution.resolve_slice(rows, archived_folder)
    assert archived_row is not None
    ok, message = manage_execution.update_slice_status(rows, archived_row, "closed", force=True)
    assert ok, message

    rows = manage_execution.parse_registry()
    archived_row = manage_execution.resolve_slice(rows, archived_folder)
    assert archived_row is not None
    ok, message, archived_row = manage_execution.archive_slice(rows, archived_row)
    assert ok, message
    assert archived_row["path"].startswith("slices/.archived/")

    assert migrate_slices.main(["migrate", "--all"]) == 0

    feature_slice_root = tmp_path / "docs" / "features" / "checkout" / "slices"
    assert (feature_slice_root / active_folder).exists()
    assert (feature_slice_root / ".archived" / archived_folder).exists()
    assert (tmp_path / "docs" / "features" / "checkout" / ".skills" / "planning.json").exists()
    assert (tmp_path / "docs" / "features" / "checkout" / ".skills" / "execution.json").exists()

    feature_registry = json.loads((feature_slice_root / "registry.json").read_text(encoding="utf-8"))
    assert feature_registry["version"] == 1
    assert len(feature_registry["slices"]) == 2
    assert {row["id"] for row in feature_registry["slices"]} == {"SPC-001", "SPC-002"}
    archived_rows = [row for row in feature_registry["slices"] if row["path"].startswith("slices/.archived/")]
    assert len(archived_rows) == 1
    assert archived_rows[0]["id"] == "SPC-002"

    root_registry = json.loads((tmp_path / "slices" / "registry.json").read_text(encoding="utf-8"))
    assert root_registry["slices"] == []


def test_package_migrate_slices_moves_mapped_slices_into_subfeature_scope(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)

    assert bootstrap.main(["--mode", "default"]) == 0

    from sirius_skills.commands import manage_execution, manage_planning, manage_subfeatures

    feature_dir, created = manage_planning.create_feature("checkout")
    assert created is True
    feature_path = Path(feature_dir)
    manage_subfeatures.ensure_subfeature_registry(feature_dir)
    scope_context = manage_planning.SCOPE_RUNTIME.resolve_scope_context()
    subfeature_dir, created = manage_subfeatures.create_subfeature(
        manage_planning,
        feature_dir,
        "checkout",
        "replace-legacy-flow",
        "replacement",
        "Replace the old checkout flow.",
        scope_context,
    )
    assert created is True
    subfeature_path = Path(subfeature_dir)
    (subfeature_path / "slice-traceability.md").write_text(
        "# Slice Traceability\n\n"
        "| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        "| CHK-01 | M | Replace flow | I1 | CHK-001 | checkout |  | CHK-001 | mapped |\n",
        encoding="utf-8",
    )

    root_folder, created = manage_execution.create_slice("CHK-001", "checkout")
    assert created is True

    assert migrate_slices.main(["migrate", "checkout"]) == 0

    assert (subfeature_path / "slices" / root_folder).exists()
    assert (subfeature_path / ".skills" / "execution.json").exists()
    assert not (feature_path / "slices" / root_folder).exists()
    assert not (tmp_path / "slices" / root_folder).exists()

    subfeature_registry = json.loads(
        (subfeature_path / "slices" / "registry.json").read_text(encoding="utf-8")
    )
    assert subfeature_registry["slices"][0]["id"] == "CHK-001"
    assert subfeature_registry["slices"][0]["path"].startswith("slices/")

    root_registry = json.loads((tmp_path / "slices" / "registry.json").read_text(encoding="utf-8"))
    assert root_registry["slices"] == []


def test_package_migrate_slices_all_uses_traceability_when_feature_field_is_title(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)

    assert bootstrap.main(["--mode", "default"]) == 0

    from sirius_skills.commands import manage_execution, manage_planning, manage_subfeatures

    feature_dir, created = manage_planning.create_feature("checkout")
    assert created is True
    manage_subfeatures.ensure_subfeature_registry(feature_dir)
    scope_context = manage_planning.SCOPE_RUNTIME.resolve_scope_context()
    subfeature_dir, created = manage_subfeatures.create_subfeature(
        manage_planning,
        feature_dir,
        "checkout",
        "replace-legacy-flow",
        "replacement",
        "Replace the old checkout flow.",
        scope_context,
    )
    assert created is True
    subfeature_path = Path(subfeature_dir)
    (subfeature_path / "slice-traceability.md").write_text(
        "# Slice Traceability\n\n"
        "| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        "| CHK-01 | M | Replace flow | I1 | CHK-001 | checkout |  | CHK-001 | mapped |\n"
        "| CHK-02 | S | Confirm redirect | I1 | CHK-002 | checkout |  | CHK-002 | mapped |\n",
        encoding="utf-8",
    )

    first_folder, created = manage_execution.create_slice("CHK-001", "Replace checkout flow")
    assert created is True
    second_folder, created = manage_execution.create_slice("CHK-002", "Confirm redirect")
    assert created is True

    assert migrate_slices.main(["migrate", "--all"]) == 0

    assert (subfeature_path / "slices" / first_folder).exists()
    assert (subfeature_path / "slices" / second_folder).exists()
    subfeature_registry = json.loads(
        (subfeature_path / "slices" / "registry.json").read_text(encoding="utf-8")
    )
    assert {row["id"] for row in subfeature_registry["slices"]} == {"CHK-001", "CHK-002"}

    root_registry = json.loads((tmp_path / "slices" / "registry.json").read_text(encoding="utf-8"))
    assert root_registry["slices"] == []


def test_package_migrate_slices_all_refreshes_root_registry_between_features(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)

    assert bootstrap.main(["--mode", "default"]) == 0

    from sirius_skills.commands import manage_execution, manage_planning

    for feature_slug, slice_id in (("checkout", "CHK-001"), ("billing", "BIL-001")):
        _, created = manage_planning.create_feature(feature_slug)
        assert created is True
        _, created = manage_execution.create_slice(slice_id, feature_slug)
        assert created is True

    assert migrate_slices.main(["migrate", "--all"]) == 0

    assert (
        tmp_path / "docs" / "features" / "checkout" / "slices" / "CHK-001-checkout"
    ).exists()
    assert (
        tmp_path / "docs" / "features" / "billing" / "slices" / "BIL-001-billing"
    ).exists()
    root_registry = json.loads((tmp_path / "slices" / "registry.json").read_text(encoding="utf-8"))
    assert root_registry["slices"] == []


def test_package_migrate_slices_scan_does_not_create_feature_scope(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    assert bootstrap.main(["--mode", "default"]) == 0

    from sirius_skills.commands import manage_execution, manage_planning

    _, created = manage_planning.create_feature("checkout")
    assert created is True

    _, created = manage_execution.create_slice("SPC-001", "checkout")
    assert created is True

    assert migrate_slices.main(["scan", "--all"]) == 0
    capsys.readouterr()

    assert not (tmp_path / "docs" / "features" / "checkout" / ".skills").exists()
