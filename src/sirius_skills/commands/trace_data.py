#!/usr/bin/env python3

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple


SCRIPT_DIR = Path(__file__).resolve().parent
IMPORT_PATH_CANDIDATES = (
    SCRIPT_DIR,
    SCRIPT_DIR.parent / "lib",
    SCRIPT_DIR.parents[2] / "lib",
    SCRIPT_DIR.parents[1] / "lib",
)

for candidate in reversed(IMPORT_PATH_CANDIDATES):
    if candidate.is_dir() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from sirius_skills.lib.workflow_state.inventory import (  # noqa: E402
    iter_subfeature_dirs,
    iter_traceability_records,
    load_inventory,
    normalize_dir_relpath,
)
from sirius_skills.lib.workflow_state.models import (  # noqa: E402
    Inventory,
    TraceabilityRecord,
)


NODE_TYPES = ("proposal", "feature", "subfeature", "planned-slice", "slice")
TYPE_ALIASES = {
    "proposal": "proposal",
    "feature": "feature",
    "subfeature": "subfeature",
    "planned-slice": "planned-slice",
    "planned_slice": "planned-slice",
    "execution-slice": "slice",
    "execution_slice": "slice",
    "slice": "slice",
}
@dataclass
class TraceNode:
    artifact_type: str
    artifact_id: str
    path: str
    label: str
    details: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        payload: Dict[str, object] = {
            "artifact_type": self.artifact_type,
            "artifact_id": self.artifact_id,
            "path": self.path,
            "label": self.label,
        }
        if self.details:
            payload["details"] = dict(self.details)
        return payload


@dataclass
class TraceEdge:
    source_type: str
    source_id: str
    target_type: str
    target_id: str
    relation: str
    source_path: str
    details: Dict[str, object]

    def to_dict(self) -> Dict[str, object]:
        payload: Dict[str, object] = {
            "source_type": self.source_type,
            "source_id": self.source_id,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "relation": self.relation,
            "source_path": self.source_path,
        }
        if self.details:
            payload["details"] = dict(self.details)
        return payload


@dataclass
class TraceGraph:
    inventory: Inventory
    nodes: Dict[Tuple[str, str], TraceNode]
    edges: List[TraceEdge]


class TraceLookupError(RuntimeError):
    pass


def normalize_artifact_type(value: str) -> str:
    normalized = TYPE_ALIASES.get(value.strip().lower())
    if not normalized:
        raise ValueError(f"Unsupported artifact type: {value}")
    return normalized


def node_key(artifact_type: str, artifact_id: str) -> Tuple[str, str]:
    return artifact_type, artifact_id


def _safe_read_metadata(reader, path: Path) -> Optional[Dict[str, object]]:
    try:
        return reader(str(path))
    except RuntimeError:
        return None


def _normalize_string_list(value: object) -> List[str]:
    if not isinstance(value, list):
        return []
    normalized: List[str] = []
    seen = set()
    for item in value:
        if not isinstance(item, str):
            continue
        candidate = item.strip()
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        normalized.append(candidate)
    return normalized


def _normalize_consolidation_summary(metadata: Optional[Dict[str, object]]) -> Optional[Dict[str, object]]:
    if not isinstance(metadata, dict):
        return None
    raw = metadata.get("consolidation")
    if not isinstance(raw, dict):
        return None
    disposition = raw.get("disposition")
    if not isinstance(disposition, str) or not disposition.strip():
        return None
    targets: List[Dict[str, str]] = []
    for item in raw.get("targets", []):
        if not isinstance(item, dict):
            continue
        kind = item.get("kind")
        ref = item.get("ref")
        change = item.get("change")
        if not all(isinstance(field, str) and field.strip() for field in (kind, ref, change)):
            continue
        targets.append(
            {
                "kind": kind.strip(),
                "ref": ref.strip(),
                "change": change.strip(),
            }
        )
    justification = raw.get("justification")
    return {
        "disposition": disposition.strip().lower(),
        "targets": targets,
        "historical_artifacts": _normalize_string_list(raw.get("historical_artifacts")),
        "surface_simplifications": _normalize_string_list(raw.get("surface_simplifications")),
        "justification": justification.strip() if isinstance(justification, str) and justification.strip() else None,
    }


def _consolidation_target_type(kind: str) -> Optional[str]:
    try:
        return normalize_artifact_type(kind)
    except ValueError:
        return None


def _consolidation_target_id(target_type: str, ref: str) -> str:
    normalized_ref = ref.strip().rstrip("/")
    if "/" not in normalized_ref:
        return normalized_ref
    if target_type in {"feature", "subfeature"}:
        return normalized_ref.split("/")[-1]
    return normalized_ref.split("/")[-1]


def _add_consolidation_metadata(
    graph: "TraceGraph",
    artifact_type: str,
    artifact_id: str,
    path: str,
    summary: Optional[Dict[str, object]],
) -> None:
    if summary is None:
        return
    add_node(
        graph,
        artifact_type,
        artifact_id,
        path,
        artifact_id,
        details={"consolidation": summary},
    )
    for target in summary["targets"]:
        target_type = _consolidation_target_type(target["kind"])
        if target_type is None:
            continue
        target_id = _consolidation_target_id(target_type, target["ref"])
        add_node(graph, target_type, target_id)
        add_edge(
            graph,
            artifact_type,
            artifact_id,
            target_type,
            target_id,
            target["change"],
            path,
            target_ref=target["ref"],
            target_kind=target["kind"],
            disposition=summary["disposition"],
            historical_artifacts=list(summary["historical_artifacts"]),
            surface_simplifications=list(summary["surface_simplifications"]),
            justification=summary["justification"],
        )


def add_node(
    graph: TraceGraph,
    artifact_type: str,
    artifact_id: str,
    path: str = "",
    label: Optional[str] = None,
    details: Optional[Dict[str, object]] = None,
) -> None:
    key = node_key(artifact_type, artifact_id)
    existing = graph.nodes.get(key)
    if existing is None:
        graph.nodes[key] = TraceNode(
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            path=path,
            label=label or artifact_id,
            details=dict(details or {}),
        )
        return
    if not existing.path and path:
        existing.path = path
    if existing.label == existing.artifact_id and label:
        existing.label = label
    if details:
        existing.details.update(details)


def add_edge(
    graph: TraceGraph,
    source_type: str,
    source_id: str,
    target_type: str,
    target_id: str,
    relation: str,
    source_path: str,
    **details: object,
) -> None:
    add_node(graph, source_type, source_id)
    add_node(graph, target_type, target_id)
    graph.edges.append(
        TraceEdge(
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
            relation=relation,
            source_path=source_path,
            details={key: value for key, value in details.items() if value not in (None, "", [], {})},
        )
    )


def build_trace_graph() -> TraceGraph:
    inventory = load_inventory()
    graph = TraceGraph(inventory=inventory, nodes={}, edges=[])

    for proposal_dir in inventory.proposal_dirs:
        add_node(
            graph,
            "proposal",
            proposal_dir.name,
            normalize_dir_relpath(proposal_dir),
            proposal_dir.name,
        )
    for feature_dir in inventory.feature_dirs:
        metadata = _safe_read_metadata(inventory.context.planning.read_metadata, feature_dir)
        add_node(
            graph,
            "feature",
            feature_dir.name,
            normalize_dir_relpath(feature_dir),
            feature_dir.name,
        )
        _add_consolidation_metadata(
            graph,
            "feature",
            feature_dir.name,
            normalize_dir_relpath(feature_dir),
            _normalize_consolidation_summary(metadata),
        )
    for subfeature_dir in iter_subfeature_dirs(inventory):
        metadata = _safe_read_metadata(inventory.context.subfeatures.read_metadata, subfeature_dir)
        add_node(
            graph,
            "subfeature",
            subfeature_dir.name,
            normalize_dir_relpath(subfeature_dir),
            subfeature_dir.name,
        )
        _add_consolidation_metadata(
            graph,
            "subfeature",
            subfeature_dir.name,
            normalize_dir_relpath(subfeature_dir),
            _normalize_consolidation_summary(metadata),
        )
    for row in inventory.slice_rows:
        add_node(
            graph,
            "slice",
            str(row["id"]),
            str(row["path"]),
            str(row["id"]),
        )

    for proposal_dir in inventory.proposal_dirs:
        metadata = _safe_read_metadata(inventory.context.propose.read_metadata, proposal_dir)
        if metadata is None:
            continue
        proposal_id = proposal_dir.name
        for field_name, relation in (
            ("target_feature", "targets_feature"),
            ("promoted_feature", "promoted_to_feature"),
        ):
            feature_id = metadata.get(field_name)
            if not isinstance(feature_id, str) or not feature_id.strip():
                continue
            add_node(graph, "feature", feature_id)
            add_edge(
                graph,
                "proposal",
                proposal_id,
                "feature",
                feature_id,
                relation,
                normalize_dir_relpath(proposal_dir),
            )

    for subfeature_dir in iter_subfeature_dirs(inventory):
        metadata = _safe_read_metadata(inventory.context.subfeatures.read_metadata, subfeature_dir)
        if metadata is None:
            continue
        parent_feature_slug = metadata.get("parent_feature_slug")
        if not isinstance(parent_feature_slug, str) or not parent_feature_slug.strip():
            continue
        add_node(graph, "feature", parent_feature_slug)
        add_edge(
            graph,
            "subfeature",
            subfeature_dir.name,
            "feature",
            parent_feature_slug,
            "subfeature_of",
            normalize_dir_relpath(subfeature_dir),
        )

    for record in iter_traceability_records(inventory):
        for planned_slice_id in record.planned_slice_ids:
            add_node(graph, "planned-slice", planned_slice_id, record.owner_path, planned_slice_id)
            add_edge(
                graph,
                record.owner_type,
                record.owner_id,
                "planned-slice",
                planned_slice_id,
                "plans_slice",
                record.owner_path,
                story_id=record.story_id,
                increments=record.increments,
                notes=record.notes,
            )
            for execution_slice_id in record.execution_slice_ids:
                add_node(graph, "slice", execution_slice_id)
                add_edge(
                    graph,
                    "planned-slice",
                    planned_slice_id,
                    "slice",
                    execution_slice_id,
                    "bootstrapped_as",
                    record.owner_path,
                    story_id=record.story_id,
                    increments=record.increments,
                )

    for row in inventory.slice_rows:
        slice_id = str(row["id"])
        metadata = inventory.context.execution.load_slice_metadata(
            inventory.context.execution.slice_path_for_row(row)
        )
        relations = metadata.get("relations", [])
        if not isinstance(relations, list):
            continue
        for relation in relations:
            if not isinstance(relation, dict):
                continue
            target_slice = relation.get("target_slice")
            relation_type = relation.get("type")
            if not isinstance(target_slice, str) or not target_slice.strip():
                continue
            if not isinstance(relation_type, str) or not relation_type.strip():
                continue
            add_node(graph, "slice", target_slice)
            add_edge(
                graph,
                "slice",
                slice_id,
                "slice",
                target_slice,
                relation_type,
                str(row["path"]),
                recorded_at=str(relation.get("recorded_at", "")),
            )

    return graph


def summarize_counts(nodes: Iterable[TraceNode], edges: Iterable[TraceEdge]) -> Dict[str, Dict[str, int]]:
    node_counts: Dict[str, int] = {}
    for node in nodes:
        node_counts[node.artifact_type] = node_counts.get(node.artifact_type, 0) + 1
    edge_counts: Dict[str, int] = {}
    for edge in edges:
        edge_counts[edge.relation] = edge_counts.get(edge.relation, 0) + 1
    return {"node_counts": node_counts, "edge_counts": edge_counts}


def _component_keys(graph: TraceGraph, start: Tuple[str, str]) -> Set[Tuple[str, str]]:
    adjacency: Dict[Tuple[str, str], Set[Tuple[str, str]]] = {}
    for edge in graph.edges:
        source = node_key(edge.source_type, edge.source_id)
        target = node_key(edge.target_type, edge.target_id)
        adjacency.setdefault(source, set()).add(target)
        adjacency.setdefault(target, set()).add(source)

    visited: Set[Tuple[str, str]] = set()
    pending = [start]
    while pending:
        current = pending.pop()
        if current in visited:
            continue
        visited.add(current)
        pending.extend(sorted(adjacency.get(current, set())))
    return visited


def build_trace_result(
    graph: TraceGraph, artifact_type: Optional[str] = None, artifact_id: Optional[str] = None
) -> Dict[str, object]:
    if artifact_type is None and artifact_id is None:
        nodes = sorted(graph.nodes.values(), key=lambda item: (item.artifact_type, item.artifact_id))
        edges = sorted(
            graph.edges,
            key=lambda item: (
                item.source_type,
                item.source_id,
                item.relation,
                item.target_type,
                item.target_id,
            ),
        )
        return {
            "ok": True,
            "target": None,
            "summary": summarize_counts(nodes, edges),
            "nodes": [node.to_dict() for node in nodes],
            "edges": [edge.to_dict() for edge in edges],
        }

    if artifact_type is None or artifact_id is None:
        raise TraceLookupError("Provide both --artifact-type and --artifact-id, or neither.")

    normalized_type = normalize_artifact_type(artifact_type)
    start = node_key(normalized_type, artifact_id)
    if start not in graph.nodes:
        raise TraceLookupError(f"Artifact not found: {normalized_type}:{artifact_id}")

    component = _component_keys(graph, start)
    nodes = sorted(
        (graph.nodes[key] for key in component),
        key=lambda item: (item.artifact_type, item.artifact_id),
    )
    edges = sorted(
        (
            edge
            for edge in graph.edges
            if node_key(edge.source_type, edge.source_id) in component
            and node_key(edge.target_type, edge.target_id) in component
        ),
        key=lambda item: (
            item.source_type,
            item.source_id,
            item.relation,
            item.target_type,
            item.target_id,
        ),
    )
    return {
        "ok": True,
        "target": graph.nodes[start].to_dict(),
        "summary": summarize_counts(nodes, edges),
        "nodes": [node.to_dict() for node in nodes],
        "edges": [edge.to_dict() for edge in edges],
    }
