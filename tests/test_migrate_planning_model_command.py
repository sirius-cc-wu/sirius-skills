from __future__ import annotations

import json
from pathlib import Path

from sirius_skills.commands import (
    manage_planning,
    manage_subfeatures,
    migrate_planning_model,
)


def test_package_migrate_planning_model_dry_run_reports_legacy_shapes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    feature_dir = tmp_path / "docs" / "features" / "checkout"
    manage_planning.write_metadata(str(feature_dir), manage_planning.build_metadata("checkout"))
    manage_planning.write_registry(
        [
            {
                "feature": "checkout",
                "status": "discovery_pending",
                "updated_at": None,
                "path": "docs/features/checkout/",
            },
            {
                "feature": "render-doc",
                "status": "discovery_pending",
                "updated_at": None,
                "path": "docs/features/checkout/subfeatures/render-doc/",
            },
        ]
    )
    subfeature_dir = feature_dir / "subfeatures" / "render-doc"
    manage_subfeatures.write_metadata(
        str(subfeature_dir),
        manage_subfeatures.build_metadata("checkout", "render-doc"),
    )
    (subfeature_dir / "discover.md").write_text(
        "# Discover\n\n- Parent story: `CHK-01`\n",
        encoding="utf-8",
    )
    (subfeature_dir / "user-stories.md").write_text("# Deprecated\n", encoding="utf-8")

    result = migrate_planning_model.build_migration_result(apply=False)

    kinds = {item["kind"] for item in result["actions"]}
    assert "ensure_subfeature_registry" in kinds
    assert "rebuild_subfeature_registry" in kinds
    assert "rebuild_feature_registry" in kinds
    assert "deprecated_subfeature_user_stories" in kinds
    assert "populate_subfeature_story_ids" in kinds
    assert result["summary"]["applied"] == 0


def test_package_migrate_planning_model_apply_safe_actions(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    feature_dir = tmp_path / "docs" / "features" / "checkout"
    manage_planning.write_metadata(str(feature_dir), manage_planning.build_metadata("checkout"))
    manage_planning.write_registry(
        [
            {
                "feature": "checkout",
                "status": "discovery_pending",
                "updated_at": None,
                "path": "docs/features/checkout/",
            },
            {
                "feature": "render-doc",
                "status": "discovery_pending",
                "updated_at": None,
                "path": "docs/features/checkout/subfeatures/render-doc/",
            },
        ]
    )
    subfeature_dir = feature_dir / "subfeatures" / "render-doc"
    manage_subfeatures.write_metadata(
        str(subfeature_dir),
        manage_subfeatures.build_metadata("checkout", "render-doc"),
    )
    (subfeature_dir / "discover.md").write_text(
        "# Discover\n\n- Parent story: `CHK-01`\n",
        encoding="utf-8",
    )

    result = migrate_planning_model.build_migration_result(apply=True)

    assert result["summary"]["applied"] >= 2
    assert (feature_dir / "subfeatures" / "registry.json").exists()
    subfeature_registry = json.loads(
        (feature_dir / "subfeatures" / "registry.json").read_text(encoding="utf-8")
    )
    assert [row["subfeature_id"] for row in subfeature_registry["subfeatures"]] == ["render-doc"]
    registry = json.loads((tmp_path / "docs" / "features" / "registry.json").read_text(encoding="utf-8"))
    assert [row["feature"] for row in registry["features"]] == ["checkout"]
    metadata = manage_subfeatures.read_metadata(str(subfeature_dir))
    assert metadata["story_ids"] == ["CHK-01"]


def test_package_migrate_planning_model_reads_list_form_registry(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)

    feature_dir = tmp_path / "docs" / "features" / "checkout"
    manage_planning.write_metadata(str(feature_dir), manage_planning.build_metadata("checkout"))
    subfeature_dir = feature_dir / "subfeatures" / "render-doc"
    manage_subfeatures.write_metadata(
        str(subfeature_dir),
        manage_subfeatures.build_metadata("checkout", "render-doc"),
    )
    registry_path = tmp_path / "docs" / "features" / "registry.json"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(
        json.dumps(
            [
                {
                    "feature": "checkout",
                    "status": "discovery_pending",
                    "updated_at": None,
                    "path": "docs/features/checkout/",
                },
                {
                    "feature": "render-doc",
                    "status": "discovery_pending",
                    "updated_at": None,
                    "path": "docs/features/checkout/subfeatures/render-doc/",
                },
            ]
        ),
        encoding="utf-8",
    )

    result = migrate_planning_model.build_migration_result(apply=False)

    assert any(item["kind"] == "rebuild_feature_registry" for item in result["actions"])
