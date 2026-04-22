# Slice Specification: Resolve planning scope and remaining planned slices

**Slice**: `mse-scope-and-backlog-resolution`  
**Created**: 2026-04-14  
**Status**: Closed  
**Input**: `mse-scope-and-backlog-resolution`

## 1. Work Item Summary

- **Work Item**: Resolve one reviewed feature or subfeature target into one ordered remaining-slice backlog.
- **Source Story / Increment / Slice**: `EW-01` / `I1` / `mse-scope-and-backlog-resolution`
- **Requested Outcome**: As a maintainer, I want `ship` to identify the active planning scope and the next ready planned slice so batch execution starts from durable repository state instead of ad hoc input.
- **Why this matters**: Later orchestration depends on one canonical view of planned slices, closed execution slices, and feature vs subfeature scope.
- **Independent Test**: `pytest -q skills/ship/tests/test_ship.py -k scope_or_backlog`

## 2. Acceptance Scenarios

1. **Given** a reviewed feature or finalized subfeature with planned slices, **When** the batch flow resolves its scope, **Then** it returns the canonical planning target and its remaining backlog in planned order.
2. **Given** some execution slices are already closed, **When** backlog resolution runs, **Then** it excludes completed work and picks the next ready planned slice.
3. **Given** the target scope is ambiguous or not execution-ready, **When** resolution runs, **Then** it fails explicitly instead of inferring progress from undocumented state.

## 3. Functional Requirements

- **FR-001**: The system MUST resolve one reviewed feature or finalized subfeature target from durable planning artifacts.
- **FR-002**: The system MUST derive the remaining planned-slice backlog from planning traceability and closed execution slices.
- **FR-003**: The system MUST preserve planned ordering and dependency-aware readiness when selecting the next slice.
- **FR-004**: The system MUST remain read-only with respect to planning and execution metadata during backlog resolution.

## 4. Key Entities

- **Planning scope target**: The feature or subfeature packet chosen for batch execution.
- **Planned-slice backlog**: The ordered list of execution-ready planned slices still remaining for the resolved scope.
- **Closed execution slice set**: The durable slice state used to filter already-completed work.

## 5. Edge Cases

- A target has no remaining planned slices; the result should be explicit and empty.
- A target mixes closed and unstarted slices; only the remaining ready slice should be selected next.
- A target is not reviewed or finalized; backlog resolution should fail explicitly.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: `slice-traceability.md` and slice registries are the canonical durable sources for planned and closed slice linkage.
- **A2**: This slice establishes selection semantics only; later slices own orchestration, stop/resume, and commit checkpoints.

### Dependencies

- **D1**: The execution-workflow subfeature planning packet remains the source of truth for the `mse-scope-and-backlog-resolution` scope and ordering.
- **D2**: Existing execution metadata remains the source of truth for which execution slices are already closed.

## 7. Success Criteria

- **SC-001**: One reviewed planning target resolves to one deterministic remaining backlog.
- **SC-002**: Already-closed execution slices are excluded from future batch work.
- **SC-003**: Later orchestration can depend on this resolved backlog without inventing a second progress store.

## 8. Open Clarifications

- None.
