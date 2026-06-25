"""Tests for the workflow_state repository modules added in the
dalc-repo-metadata slice.

Covers:
- planning_repository
- proposal_repository
- subfeature_repository
- execution_repository
- command-level compatibility (round-trip through refactored manage_* functions)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from sirius_skills.lib.workflow_state import (
    planning_repository,
    proposal_repository,
    subfeature_repository,
    execution_repository,
)


# ---------------------------------------------------------------------------
# planning_repository
# ---------------------------------------------------------------------------

class TestPlanningRepository:
    def test_ensure_registry_creates_missing_files(self, tmp_path: Path) -> None:
        planning_dir = tmp_path / "docs" / "features"
        planning_repository.ensure_registry(planning_dir)

        readme = planning_dir / "README.md"
        registry = planning_dir / "registry.json"
        assert readme.exists()
        assert registry.exists()
        assert "Planning Registry" in readme.read_text(encoding="utf-8")
        payload = json.loads(registry.read_text(encoding="utf-8"))
        assert payload == {"features": []}

    def test_ensure_registry_is_idempotent(self, tmp_path: Path) -> None:
        planning_dir = tmp_path / "docs" / "features"
        planning_repository.ensure_registry(planning_dir)
        # Mutate the file, then call ensure_registry again – it must not overwrite.
        registry = planning_dir / "registry.json"
        registry.write_text('{"features": [{"sentinel": true}]}\n', encoding="utf-8")
        planning_repository.ensure_registry(planning_dir)
        payload = json.loads(registry.read_text(encoding="utf-8"))
        assert payload["features"][0].get("sentinel") is True

    def test_read_registry_json_empty_when_absent(self, tmp_path: Path) -> None:
        result = planning_repository.read_registry_json(tmp_path / "registry.json")
        assert result == []

    def test_read_registry_json_object_form(self, tmp_path: Path) -> None:
        registry = tmp_path / "registry.json"
        registry.write_text(
            json.dumps({"features": [{"feature": "my-feat", "status": "draft", "path": "docs/features/my-feat/"}]}),
            encoding="utf-8",
        )
        rows = planning_repository.read_registry_json(registry)
        assert len(rows) == 1
        assert rows[0]["feature"] == "my-feat"

    def test_read_registry_json_list_form(self, tmp_path: Path) -> None:
        registry = tmp_path / "registry.json"
        registry.write_text(
            json.dumps([{"feature": "feat-a", "status": "draft", "path": "docs/features/feat-a/"}]),
            encoding="utf-8",
        )
        rows = planning_repository.read_registry_json(registry)
        assert len(rows) == 1
        assert rows[0]["feature"] == "feat-a"

    def test_write_and_read_registry_json_round_trip(self, tmp_path: Path) -> None:
        registry = tmp_path / "registry.json"
        rows = [{"feature": "f1", "status": "discovery_pending", "path": "docs/features/f1/"}]
        planning_repository.write_registry_json(registry, rows)
        result = planning_repository.read_registry_json(registry)
        assert result == rows

    def test_read_metadata_raw_raises_when_absent(self, tmp_path: Path) -> None:
        with pytest.raises(RuntimeError, match="Planning metadata not found"):
            planning_repository.read_metadata_raw(tmp_path / "nonexistent")

    def test_write_and_read_metadata_raw_round_trip(self, tmp_path: Path) -> None:
        feature_dir = tmp_path / "docs" / "features" / "my-feature"
        data = {"feature_slug": "my-feature", "status": "discovery_pending"}
        planning_repository.write_metadata_raw(feature_dir, data)
        result = planning_repository.read_metadata_raw(feature_dir)
        assert result == data

    def test_metadata_path_points_to_correct_file(self, tmp_path: Path) -> None:
        path = planning_repository.metadata_path(tmp_path / "features" / "feat")
        assert path.name == ".planning-meta.json"

    def test_subfeature_metadata_path_points_to_correct_file(self, tmp_path: Path) -> None:
        path = planning_repository.subfeature_metadata_path(tmp_path / "features" / "feat")
        assert path.name == ".subfeature-meta.json"


# ---------------------------------------------------------------------------
# proposal_repository
# ---------------------------------------------------------------------------

class TestProposalRepository:
    def test_ensure_registry_creates_missing_files(self, tmp_path: Path) -> None:
        proposal_dir = tmp_path / "docs" / "proposals"
        proposal_repository.ensure_registry(proposal_dir)

        readme = proposal_dir / "README.md"
        registry = proposal_dir / "registry.json"
        assert readme.exists()
        assert registry.exists()
        assert "Proposal Registry" in readme.read_text(encoding="utf-8")
        payload = json.loads(registry.read_text(encoding="utf-8"))
        assert payload == {"proposals": []}

    def test_read_registry_json_empty_when_absent(self, tmp_path: Path) -> None:
        assert proposal_repository.read_registry_json(tmp_path / "registry.json") == []

    def test_write_and_read_registry_json_round_trip(self, tmp_path: Path) -> None:
        registry = tmp_path / "registry.json"
        rows = [{"proposal": "p1", "status": "draft", "path": "docs/proposals/p1/"}]
        proposal_repository.write_registry_json(registry, rows)
        result = proposal_repository.read_registry_json(registry)
        assert result == rows

    def test_read_metadata_raw_raises_when_absent(self, tmp_path: Path) -> None:
        with pytest.raises(RuntimeError, match="Proposal metadata not found"):
            proposal_repository.read_metadata_raw(tmp_path / "nonexistent")

    def test_write_and_read_metadata_raw_round_trip(self, tmp_path: Path) -> None:
        proposal_dir = tmp_path / "docs" / "proposals" / "my-proposal"
        data = {"proposal_slug": "my-proposal", "status": "draft"}
        proposal_repository.write_metadata_raw(proposal_dir, data)
        result = proposal_repository.read_metadata_raw(proposal_dir)
        assert result == data

    def test_metadata_path_points_to_correct_file(self, tmp_path: Path) -> None:
        path = proposal_repository.metadata_path(tmp_path / "proposals" / "p1")
        assert path.name == ".proposal-meta.json"


# ---------------------------------------------------------------------------
# subfeature_repository
# ---------------------------------------------------------------------------

class TestSubfeatureRepository:
    def test_registry_paths_returns_correct_structure(self, tmp_path: Path) -> None:
        feature_dir = tmp_path / "docs" / "features" / "checkout"
        subfeatures_dir, readme, registry = subfeature_repository.registry_paths(feature_dir)
        assert subfeatures_dir.name == "subfeatures"
        assert readme.name == "README.md"
        assert registry.name == "registry.json"

    def test_ensure_registry_creates_missing_files(self, tmp_path: Path) -> None:
        feature_dir = tmp_path / "docs" / "features" / "checkout"
        subfeature_repository.ensure_registry(feature_dir)

        subfeatures_dir, readme, registry = subfeature_repository.registry_paths(feature_dir)
        assert subfeatures_dir.exists()
        assert readme.exists()
        assert registry.exists()
        assert "Subfeature Registry" in readme.read_text(encoding="utf-8")
        payload = json.loads(registry.read_text(encoding="utf-8"))
        assert payload == {"subfeatures": []}

    def test_read_registry_json_empty_when_absent(self, tmp_path: Path) -> None:
        assert subfeature_repository.read_registry_json(tmp_path / "registry.json") == []

    def test_write_and_read_registry_json_round_trip(self, tmp_path: Path) -> None:
        registry = tmp_path / "registry.json"
        rows = [{"subfeature_id": "sf1", "status": "draft", "path": "docs/features/f/subfeatures/sf1/"}]
        subfeature_repository.write_registry_json(registry, rows)
        result = subfeature_repository.read_registry_json(registry)
        assert result == rows

    def test_read_metadata_raw_raises_when_absent(self, tmp_path: Path) -> None:
        with pytest.raises(RuntimeError, match="Subfeature metadata not found"):
            subfeature_repository.read_metadata_raw(tmp_path / "nonexistent")

    def test_write_and_read_metadata_raw_round_trip(self, tmp_path: Path) -> None:
        sf_dir = tmp_path / "docs" / "features" / "checkout" / "subfeatures" / "replace-flow"
        data = {"subfeature_id": "replace-flow", "parent_feature_slug": "checkout", "status": "draft"}
        subfeature_repository.write_metadata_raw(sf_dir, data)
        result = subfeature_repository.read_metadata_raw(sf_dir)
        assert result == data

    def test_metadata_path_points_to_correct_file(self, tmp_path: Path) -> None:
        path = subfeature_repository.metadata_path(tmp_path / "sf")
        assert path.name == ".subfeature-meta.json"


# ---------------------------------------------------------------------------
# execution_repository
# ---------------------------------------------------------------------------

class TestExecutionRepository:
    def test_ensure_registry_creates_files_when_both_absent(self, tmp_path: Path) -> None:
        specs_dir = tmp_path / "slices"
        execution_repository.ensure_registry(specs_dir)

        readme = specs_dir / "README.md"
        registry = specs_dir / "registry.json"
        assert readme.exists()
        assert registry.exists()
        assert "Slice Registry" in readme.read_text(encoding="utf-8")
        payload = json.loads(registry.read_text(encoding="utf-8"))
        assert payload["version"] == 1
        assert payload["slices"] == []

    def test_ensure_registry_does_not_overwrite_existing_files(self, tmp_path: Path) -> None:
        specs_dir = tmp_path / "slices"
        specs_dir.mkdir()
        registry = specs_dir / "registry.json"
        registry.write_text('{"version": 1, "slices": [{"sentinel": true}]}\n', encoding="utf-8")
        readme = specs_dir / "README.md"
        readme.write_text("# Existing\n", encoding="utf-8")

        execution_repository.ensure_registry(specs_dir)
        # Both files should be untouched
        assert "sentinel" in registry.read_text(encoding="utf-8")
        assert "Existing" in readme.read_text(encoding="utf-8")

    def test_read_registry_json_empty_when_absent(self, tmp_path: Path) -> None:
        assert execution_repository.read_registry_json(tmp_path / "registry.json") == []

    def test_read_registry_json_object_form(self, tmp_path: Path) -> None:
        registry = tmp_path / "registry.json"
        payload = {
            "version": 1,
            "slices": [{"id": "SPC-001", "feature": "auth", "status": "draft", "path": "slices/SPC-001/"}],
        }
        registry.write_text(json.dumps(payload), encoding="utf-8")
        rows = execution_repository.read_registry_json(registry)
        assert len(rows) == 1
        assert rows[0]["id"] == "SPC-001"

    def test_write_registry_json_round_trip(self, tmp_path: Path) -> None:
        registry = tmp_path / "registry.json"
        rows = [{"id": "X-1", "feature": "f", "status": "draft", "path": "slices/X-1/"}]
        execution_repository.write_registry_json(registry, rows, generated_at="2025-01-01T00:00:00")
        payload = json.loads(registry.read_text(encoding="utf-8"))
        assert payload["version"] == 1
        assert payload["slices"] == rows
        assert payload["generated_at"] == "2025-01-01T00:00:00"

    def test_write_registry_json_without_generated_at(self, tmp_path: Path) -> None:
        registry = tmp_path / "registry.json"
        execution_repository.write_registry_json(registry, [])
        payload = json.loads(registry.read_text(encoding="utf-8"))
        assert "generated_at" not in payload

    def test_slice_metadata_path_points_to_correct_file(self, tmp_path: Path) -> None:
        path = execution_repository.slice_metadata_path(tmp_path / "slices" / "SPC-001")
        assert path.name == ".slice-meta.json"

    def test_read_slice_metadata_raw_returns_empty_dict_when_absent(self, tmp_path: Path) -> None:
        result = execution_repository.read_slice_metadata_raw(tmp_path / "nonexistent")
        assert result == {}

    def test_write_and_read_slice_metadata_raw_round_trip(self, tmp_path: Path) -> None:
        slice_dir = tmp_path / "slices" / "SPC-001"
        slice_dir.mkdir(parents=True)
        data = {"slice_id": "SPC-001", "feature": "auth", "status": "draft"}
        execution_repository.write_slice_metadata_raw(slice_dir, data)
        result = execution_repository.read_slice_metadata_raw(slice_dir)
        assert result == data

    def test_read_slice_metadata_raw_raises_on_invalid_json(self, tmp_path: Path) -> None:
        slice_dir = tmp_path / "slices" / "BAD"
        slice_dir.mkdir(parents=True)
        (slice_dir / ".slice-meta.json").write_text("not json!", encoding="utf-8")
        with pytest.raises(RuntimeError, match="not valid JSON"):
            execution_repository.read_slice_metadata_raw(slice_dir)


# ---------------------------------------------------------------------------
# Command-level compatibility: refactored manage_* functions still work
# ---------------------------------------------------------------------------

class TestCommandCompatibility:
    """Smoke-test the refactored command functions that now delegate to repositories."""

    def test_manage_planning_ensure_and_read_write_metadata(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        from sirius_skills.commands import manage_planning

        planning_dir = str(tmp_path / "docs" / "features")
        manage_planning.ensure_registry(planning_dir)
        assert (tmp_path / "docs" / "features" / "registry.json").exists()

        feature_dir = str(tmp_path / "docs" / "features" / "my-feat")
        metadata = manage_planning.build_metadata("my-feat")
        manage_planning.write_metadata(feature_dir, metadata)
        loaded = manage_planning.read_metadata(feature_dir)
        assert loaded["feature_slug"] == "my-feat"
        assert loaded["status"] == "discovery_pending"

    def test_manage_proposals_ensure_and_read_write_metadata(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        from sirius_skills.commands import manage_proposals

        proposal_dir = str(tmp_path / "docs" / "proposals")
        manage_proposals.ensure_registry(proposal_dir)
        assert (tmp_path / "docs" / "proposals" / "registry.json").exists()

        pd = str(tmp_path / "docs" / "proposals" / "my-proposal")
        metadata = manage_proposals.build_metadata("my-proposal", summary="A test proposal")
        manage_proposals.write_metadata(pd, metadata)
        loaded = manage_proposals.read_metadata(pd)
        assert loaded["proposal_slug"] == "my-proposal"
        assert loaded["status"] == "draft"

    def test_manage_subfeatures_ensure_and_read_write_metadata(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        from sirius_skills.commands import manage_subfeatures

        feature_dir = str(tmp_path / "docs" / "features" / "checkout")
        manage_subfeatures.ensure_subfeature_registry(feature_dir)
        assert (tmp_path / "docs" / "features" / "checkout" / "subfeatures" / "registry.json").exists()

        sf_dir = str(tmp_path / "docs" / "features" / "checkout" / "subfeatures" / "replace-flow")
        metadata = manage_subfeatures.build_metadata("checkout", "replace-flow")
        manage_subfeatures.write_metadata(sf_dir, metadata)
        loaded = manage_subfeatures.read_metadata(sf_dir)
        assert loaded["subfeature_id"] == "replace-flow"
        assert loaded["status"] == "draft"

    def test_manage_execution_load_and_write_slice_metadata(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        from sirius_skills.commands import manage_execution

        slice_dir = str(tmp_path / "slices" / "SPC-001")
        Path(slice_dir).mkdir(parents=True)

        # Empty metadata when absent
        result = manage_execution.load_slice_metadata(slice_dir)
        assert result == {}

        # Write and reload
        meta = {"slice_id": "SPC-001", "feature": "auth", "status": "draft"}
        manage_execution.write_slice_metadata(slice_dir, meta)
        loaded = manage_execution.load_slice_metadata(slice_dir)
        assert loaded["slice_id"] == "SPC-001"
        assert loaded["status"] == "draft"

    def test_manage_planning_load_registry_json_delegates_correctly(self, tmp_path: Path) -> None:
        from sirius_skills.commands import manage_planning

        registry_path = tmp_path / "registry.json"
        registry_path.write_text(
            json.dumps({
                "features": [
                    {"feature": "feat-a", "status": "discovery_pending", "updated_at": None, "path": "docs/features/feat-a/"}
                ]
            }),
            encoding="utf-8",
        )
        rows = manage_planning.load_registry_json(str(registry_path))
        assert len(rows) == 1
        assert rows[0]["feature"] == "feat-a"

    def test_manage_execution_write_registry_json_produces_versioned_payload(self, tmp_path: Path) -> None:
        from sirius_skills.commands import manage_execution

        registry_path = tmp_path / "registry.json"
        rows = [{"id": "SPC-1", "feature": "auth", "status": "draft", "path": "slices/SPC-1/"}]
        manage_execution.write_registry_json(str(registry_path), rows)
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
        assert payload["version"] == 1
        assert len(payload["slices"]) == 1
        assert "generated_at" in payload
