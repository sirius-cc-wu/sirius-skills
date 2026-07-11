from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Protocol, TypeAlias


RegistryRow: TypeAlias = Dict[str, object]


class MetadataReaderModule(Protocol):
    def read_metadata(self, __artifact_dir: str) -> Mapping[str, object]:
        ...


class RegistryModule(Protocol):
    def normalize_registry_row(self, __row: RegistryRow) -> RegistryRow:
        ...


class MarkdownRegistryModule(RegistryModule, Protocol):
    def parse_registry_markdown(self, __registry_path: str) -> List[RegistryRow]:
        ...


class ProposalStateModule(MetadataReaderModule, RegistryModule, Protocol):
    pass


class ScopeRuntimeModule(Protocol):
    def resolve_scope_context(
        self, start_path: Optional[str] = None, explicit_scope: Optional[str] = None
    ) -> object:
        ...


class PlanningStateModule(MetadataReaderModule, MarkdownRegistryModule, Protocol):
    @property
    def SCOPE_RUNTIME(self) -> ScopeRuntimeModule:
        ...

    def sync_registry(
        self,
        seed_rows: Optional[List[RegistryRow]] = None,
        scope_context: Optional[object] = None,
    ) -> List[RegistryRow]:
        ...

    def resolve_feature_lookup(
        self, __selector: str, explicit_scope: Optional[str] = None
    ) -> tuple[List[RegistryRow], Optional[RegistryRow], object]:
        ...

    def feature_dir_for_row(
        self, __row: RegistryRow, scope_context: Optional[object] = None
    ) -> str:
        ...

    def relative_path_from_scope_root(self, __path: str, __scope_context: object) -> str:
        ...

    def can_transition(self, __current: str, __target: str) -> bool:
        ...

    def update_feature_status(
        self,
        __rows: List[RegistryRow],
        __feature: RegistryRow,
        __status: str,
        force: bool = False,
        review_note: Optional[str] = None,
        slice_ids: Optional[List[str]] = None,
        requires_ui_flow: Optional[bool] = None,
        consolidation: Optional[RegistryRow] = None,
        scope_context: Optional[object] = None,
    ) -> tuple[bool, str]:
        ...


class SubfeatureStateModule(MetadataReaderModule, RegistryModule, Protocol):
    def subfeature_registry_paths(self, __feature_dir: str) -> tuple[str, str, str]:
        ...

    def ensure_subfeature_registry(self, __feature_dir: str) -> None:
        ...

    def load_registry(self, __feature_dir: str) -> List[RegistryRow]:
        ...

    def write_registry(self, __feature_dir: str, __rows: List[RegistryRow]) -> None:
        ...

    def find_subfeature(
        self, __rows: List[RegistryRow], __selector: str
    ) -> Optional[RegistryRow]:
        ...

    def can_transition(self, __current: str, __target: str) -> bool:
        ...

    def update_subfeature_status(
        self,
        __manage_planning: PlanningStateModule,
        __feature_dir: str,
        __subfeature: RegistryRow,
        __status: str,
        __scope_context: object,
        force: bool = False,
        subfeature_type: Optional[str] = None,
        summary: Optional[str] = None,
        review_note: Optional[str] = None,
        affected_artifacts: Optional[List[str]] = None,
        affected_story_ids: Optional[List[str]] = None,
        story_ids: Optional[List[str]] = None,
        affected_slice_ids: Optional[List[str]] = None,
        consolidation: Optional[RegistryRow] = None,
    ) -> tuple[bool, str]:
        ...


class ExecutionStateModule(MarkdownRegistryModule, Protocol):
    def default_archive_dir(self, __slice_root: str) -> str:
        ...

    def slice_path_for_row(self, __row: RegistryRow) -> str:
        ...


def _required_str(row: Mapping[str, object], field_name: str, row_type: str) -> str:
    value = row.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"{row_type} registry row field '{field_name}' must be a non-empty string."
        )
    return value


def _optional_str(row: Mapping[str, object], field_name: str) -> Optional[str]:
    value = row.get(field_name)
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


@dataclass(frozen=True)
class ScopeContext:
    start_dir: Path
    repo_root: Path
    scope_root: Path
    scope_chain: tuple[Path, ...]
    planning_config_path: Path


@dataclass(frozen=True)
class ProposalRegistryRow:
    proposal: str
    status: str
    path: str
    updated_at: Optional[str] = None

    @classmethod
    def from_mapping(cls, row: Mapping[str, object]) -> "ProposalRegistryRow":
        return cls(
            proposal=_required_str(row, "proposal", "proposal"),
            status=_required_str(row, "status", "proposal"),
            path=_required_str(row, "path", "proposal"),
            updated_at=_optional_str(row, "updated_at"),
        )

    def to_dict(self) -> RegistryRow:
        payload: RegistryRow = {
            "proposal": self.proposal,
            "status": self.status,
            "path": self.path,
        }
        if self.updated_at is not None:
            payload["updated_at"] = self.updated_at
        return payload


@dataclass(frozen=True)
class PlanningRegistryRow:
    feature: str
    status: str
    path: str
    updated_at: Optional[str] = None

    @classmethod
    def from_mapping(cls, row: Mapping[str, object]) -> "PlanningRegistryRow":
        return cls(
            feature=_required_str(row, "feature", "planning"),
            status=_required_str(row, "status", "planning"),
            path=_required_str(row, "path", "planning"),
            updated_at=_optional_str(row, "updated_at"),
        )

    def to_dict(self) -> RegistryRow:
        payload: RegistryRow = {
            "feature": self.feature,
            "status": self.status,
            "path": self.path,
        }
        if self.updated_at is not None:
            payload["updated_at"] = self.updated_at
        return payload


@dataclass(frozen=True)
class SubfeatureRegistryRow:
    subfeature_id: str
    status: str
    path: str
    feature: Optional[str] = None
    subfeature_type: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_mapping(cls, row: Mapping[str, object]) -> "SubfeatureRegistryRow":
        return cls(
            subfeature_id=_required_str(row, "subfeature_id", "subfeature"),
            status=_required_str(row, "status", "subfeature"),
            path=_required_str(row, "path", "subfeature"),
            feature=_optional_str(row, "feature"),
            subfeature_type=_optional_str(row, "subfeature_type") or _optional_str(row, "type"),
            updated_at=_optional_str(row, "updated_at"),
        )

    def to_dict(self) -> RegistryRow:
        payload: RegistryRow = {
            "subfeature_id": self.subfeature_id,
            "status": self.status,
            "path": self.path,
        }
        if self.feature is not None:
            payload["feature"] = self.feature
        if self.subfeature_type is not None:
            payload["subfeature_type"] = self.subfeature_type
        if self.updated_at is not None:
            payload["updated_at"] = self.updated_at
        return payload


@dataclass(frozen=True)
class SliceRegistryRow:
    id: str
    feature: str
    status: str
    path: str
    updated_at: Optional[str] = None
    archived_at: Optional[str] = None

    @classmethod
    def from_mapping(cls, row: Mapping[str, object]) -> "SliceRegistryRow":
        return cls(
            id=_required_str(row, "id", "slice"),
            feature=_required_str(row, "feature", "slice"),
            status=_required_str(row, "status", "slice"),
            path=_required_str(row, "path", "slice"),
            updated_at=_optional_str(row, "updated_at"),
            archived_at=_optional_str(row, "archived_at"),
        )

    def to_dict(self) -> RegistryRow:
        payload: RegistryRow = {
            "id": self.id,
            "feature": self.feature,
            "status": self.status,
            "path": self.path,
        }
        if self.updated_at is not None:
            payload["updated_at"] = self.updated_at
        if self.archived_at is not None:
            payload["archived_at"] = self.archived_at
        return payload


@dataclass
class RegistryStatus:
    artifact_type: str
    owner_id: Optional[str]
    root_path: str
    readme_path: str
    registry_path: str
    root_exists: bool
    readme_exists: bool
    registry_exists: bool
    error: Optional[str] = None


@dataclass
class InventoryContext:
    propose: ProposalStateModule
    planning: PlanningStateModule
    subfeatures: SubfeatureStateModule
    execution: ExecutionStateModule
    proposal_root: Path
    proposal_readme: Path
    proposal_registry: Path
    planning_root: Path
    planning_readme: Path
    planning_registry: Path
    slice_root: Path
    slice_readme: Path
    slice_registry: Path


@dataclass
class Inventory:
    context: InventoryContext
    registry_statuses: List[RegistryStatus]
    proposal_rows: List[RegistryRow]
    planning_rows: List[RegistryRow]
    slice_rows: List[RegistryRow]
    proposal_dirs: List[Path]
    feature_dirs: List[Path]
    subfeature_dirs_by_feature: Dict[str, List[Path]]
    slice_dirs: List[Path]
    subfeature_registry_rows: Dict[str, List[RegistryRow]]
    proposal_registry: List[ProposalRegistryRow] = field(init=False)
    planning_registry: List[PlanningRegistryRow] = field(init=False)
    slice_registry: List[SliceRegistryRow] = field(init=False)
    subfeature_registries: Dict[str, List[SubfeatureRegistryRow]] = field(init=False)

    def __post_init__(self) -> None:
        self.proposal_registry = [
            ProposalRegistryRow.from_mapping(row) for row in self.proposal_rows
        ]
        self.planning_registry = [
            PlanningRegistryRow.from_mapping(row) for row in self.planning_rows
        ]
        self.slice_registry = [SliceRegistryRow.from_mapping(row) for row in self.slice_rows]
        self.subfeature_registries = {
            feature_id: [SubfeatureRegistryRow.from_mapping(row) for row in rows]
            for feature_id, rows in self.subfeature_registry_rows.items()
        }


@dataclass
class TraceabilityRecord:
    owner_type: str
    owner_id: str
    owner_path: str
    story_id: str
    story_size: Optional[str]
    increments: str
    planned_slice_ids: List[str]
    execution_slice_ids: List[str]
    notes: str


@dataclass
class SemanticPreviewRecord:
    artifact_type: str
    artifact_id: str
    path: str
    code: str
    message: str
    apply_supported: bool = False

    def to_dict(self) -> Dict[str, object]:
        return {
            "artifact_type": self.artifact_type,
            "artifact_id": self.artifact_id,
            "path": self.path,
            "code": self.code,
            "message": self.message,
            "apply_supported": self.apply_supported,
        }


@dataclass
class TransitionCheckResult:
    outcome: str
    findings: List[SemanticPreviewRecord]
    override_flag: Optional[str] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "outcome": self.outcome,
            "findings": [item.to_dict() for item in self.findings],
            "override_flag": self.override_flag,
        }


@dataclass
class InstalledParityRecord:
    skill_name: str
    relative_path: str
    code: str
    message: str
    repo_path: str
    installed_path: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "skill_name": self.skill_name,
            "relative_path": self.relative_path,
            "code": self.code,
            "message": self.message,
            "repo_path": self.repo_path,
            "installed_path": self.installed_path,
        }
