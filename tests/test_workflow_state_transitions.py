from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Callable

from sirius_skills.lib.workflow_state.models import (
    Inventory,
    InventoryContext,
    PlanningRegistryRow,
    ProposalRegistryRow,
    SemanticPreviewRecord,
    SliceRegistryRow,
    SubfeatureRegistryRow,
    TraceabilityRecord,
)
from sirius_skills.lib.workflow_state import transitions


def _slice_row(status: str) -> dict[str, object]:
    return {
        "id": "slice-a",
        "feature": "feature-a",
        "status": status,
        "path": "slices/slice-a/",
    }


def _inventory(
    tmp_path: Path,
    *,
    read_subfeature_metadata: Callable[[str], dict[str, object]] | None = None,
    slice_rows: list[dict[str, object]] | None = None,
) -> Inventory:
    feature_dir = tmp_path / "docs" / "features" / "feature-a"
    subfeature_dir = feature_dir / "subfeatures" / "sub-a"
    slice_root = tmp_path / "slices"
    feature_dir.mkdir(parents=True)
    subfeature_dir.mkdir(parents=True)
    slice_root.mkdir(parents=True)

    subfeatures = SimpleNamespace(
        read_metadata=read_subfeature_metadata or (lambda _path: {"status": "draft"})
    )
    context = InventoryContext(
        propose=SimpleNamespace(),
        planning=SimpleNamespace(),
        subfeatures=subfeatures,
        execution=SimpleNamespace(default_archive_dir=lambda root: str(Path(root) / "archive")),
        proposal_root=tmp_path / "docs" / "proposals",
        proposal_readme=tmp_path / "docs" / "proposals" / "README.md",
        proposal_registry=tmp_path / "docs" / "proposals" / "registry.json",
        planning_root=tmp_path / "docs" / "features",
        planning_readme=tmp_path / "docs" / "features" / "README.md",
        planning_registry=tmp_path / "docs" / "features" / "registry.json",
        slice_root=slice_root,
        slice_readme=slice_root / "README.md",
        slice_registry=slice_root / "registry.json",
    )
    return Inventory(
        context=context,
        registry_statuses=[],
        proposal_rows=[],
        planning_rows=[
            {
                "feature": "feature-a",
                "status": "slice_ready",
                "path": "docs/features/feature-a/",
            }
        ],
        slice_rows=slice_rows or [],
        proposal_dirs=[],
        feature_dirs=[feature_dir],
        subfeature_dirs_by_feature={"feature-a": [subfeature_dir]},
        slice_dirs=[],
        subfeature_registry_rows={},
    )


def _trace_record(slice_id: str) -> TraceabilityRecord:
    return TraceabilityRecord(
        owner_type="subfeature",
        owner_id="sub-a",
        owner_path="docs/features/feature-a/subfeatures/sub-a/",
        story_id="ST-1",
        story_size=None,
        increments="",
        planned_slice_ids=[slice_id],
        execution_slice_ids=[],
        notes="",
    )


def _patch_transition_inventory(monkeypatch, inventory: Inventory) -> None:
    monkeypatch.setattr(transitions, "load_inventory", lambda: inventory)
    monkeypatch.setattr(
        transitions,
        "iter_traceability_records",
        lambda _inventory: [_trace_record("slice-a")],
    )


def test_registry_row_models_preserve_serialized_field_names() -> None:
    assert ProposalRegistryRow.from_mapping(
        {
            "proposal": "proposal-a",
            "status": "draft",
            "path": "docs/proposals/proposal-a/",
            "updated_at": "2026-01-01T00:00:00",
        }
    ).to_dict()["updated_at"] == "2026-01-01T00:00:00"
    assert PlanningRegistryRow.from_mapping(
        {
            "feature": "feature-a",
            "status": "slice_ready",
            "path": "docs/features/feature-a/",
            "updated_at": "2026-01-01T00:00:00",
        }
    ).to_dict()["updated_at"] == "2026-01-01T00:00:00"
    assert SubfeatureRegistryRow.from_mapping(
        {
            "subfeature_id": "sub-a",
            "status": "impact_ready",
            "path": "docs/features/feature-a/subfeatures/sub-a/",
            "subfeature_type": "additive",
            "updated_at": "2026-01-01T00:00:00",
        }
    ).to_dict()["subfeature_type"] == "additive"
    assert SliceRegistryRow.from_mapping(
        {
            "id": "slice-a",
            "feature": "feature-a",
            "status": "closed",
            "path": "slices/slice-a/",
            "updated_at": "2026-01-01T00:00:00",
            "archived_at": "2026-01-02T00:00:00",
        }
    ).to_dict()["archived_at"] == "2026-01-02T00:00:00"


def test_slice_transition_returns_force_override_when_inventory_is_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(
        transitions,
        "load_inventory",
        lambda: (_ for _ in ()).throw(RuntimeError("missing")),
    )

    result = transitions.evaluate_slice_transition("slice-a", "closed")

    assert result.outcome == transitions.OK_OUTCOME
    assert result.override_flag == "--force"
    assert result.findings == []


def test_feature_transition_rewrites_semantic_preview_as_warning(tmp_path: Path, monkeypatch) -> None:
    inventory = _inventory(tmp_path)
    preview = SemanticPreviewRecord(
        artifact_type="feature",
        artifact_id="feature-a",
        path="docs/features/feature-a/",
        code="repair_planning_status_handoff",
        message="Preview only: update feature status.",
    )
    monkeypatch.setattr(transitions, "load_inventory", lambda: inventory)
    monkeypatch.setattr(transitions, "build_semantic_preview", lambda _inventory, _types: [preview])

    result = transitions.evaluate_feature_transition("feature-a", "slice_ready")

    assert result.outcome == transitions.WARNING_OUTCOME
    assert [finding.code for finding in result.findings] == ["repair_planning_status_handoff"]
    assert result.findings[0].message == "Transition warning: update feature status."


def test_subfeature_finalize_warns_when_linked_slice_is_open(tmp_path: Path, monkeypatch) -> None:
    inventory = _inventory(
        tmp_path,
        slice_rows=[_slice_row("blueprint_ready")],
    )
    _patch_transition_inventory(monkeypatch, inventory)
    monkeypatch.setattr(transitions, "build_semantic_preview", lambda _inventory, _types: [])

    result = transitions.evaluate_subfeature_transition("sub-a", "finalized")

    assert result.outcome == transitions.WARNING_OUTCOME
    assert [finding.code for finding in result.findings] == ["transition_open_execution_slices"]
    assert "slice-a" in result.findings[0].message


def test_slice_close_blocks_unreviewed_subfeature_and_reports_force_override(
    tmp_path: Path, monkeypatch
) -> None:
    inventory = _inventory(
        tmp_path,
        read_subfeature_metadata=lambda _path: {"status": "draft"},
        slice_rows=[_slice_row("review_ready")],
    )
    _patch_transition_inventory(monkeypatch, inventory)
    monkeypatch.setattr(transitions, "build_semantic_preview", lambda _inventory, _types: [])

    result = transitions.evaluate_slice_transition("slice-a", "closed")

    assert result.outcome == transitions.BLOCK_OUTCOME
    assert result.override_flag == "--force"
    assert [finding.code for finding in result.findings] == ["transition_subfeature_review_required"]
    assert "subfeature 'sub-a' in status 'draft'" in result.findings[0].message


def test_slice_close_warns_when_related_owner_has_semantic_preview(
    tmp_path: Path, monkeypatch
) -> None:
    inventory = _inventory(
        tmp_path,
        read_subfeature_metadata=lambda _path: {"status": "reviewed"},
        slice_rows=[_slice_row("review_ready")],
    )
    preview = SemanticPreviewRecord(
        artifact_type="subfeature",
        artifact_id="sub-a",
        path="docs/features/feature-a/subfeatures/sub-a/",
        code="repair_subfeature_status_handoff",
        message="Preview only: update subfeature status.",
    )
    _patch_transition_inventory(monkeypatch, inventory)
    monkeypatch.setattr(transitions, "build_semantic_preview", lambda _inventory, _types: [preview])

    result = transitions.evaluate_slice_transition("slice-a", "closed")

    assert result.outcome == transitions.WARNING_OUTCOME
    assert result.override_flag == "--force"
    assert [finding.code for finding in result.findings] == ["repair_subfeature_status_handoff"]
    assert result.findings[0].message == "Transition warning: update subfeature status."
