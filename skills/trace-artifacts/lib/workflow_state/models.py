from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


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
    propose: object
    planning: object
    subfeatures: object
    execution: object
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
    proposal_rows: List[Dict[str, object]]
    planning_rows: List[Dict[str, object]]
    slice_rows: List[Dict[str, object]]
    proposal_dirs: List[Path]
    feature_dirs: List[Path]
    subfeature_dirs_by_feature: Dict[str, List[Path]]
    slice_dirs: List[Path]
    subfeature_registry_rows: Dict[str, List[Dict[str, object]]]


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
