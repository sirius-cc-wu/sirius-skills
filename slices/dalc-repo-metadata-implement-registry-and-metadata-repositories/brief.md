# Slice Contract: Implement Registry and Metadata Repositories

**Slice**: `dalc-repo-metadata`  
**Created**: 2026-06-25  
**Status**: Draft  
**Input**: `data-access-layer-consolidation / dalc-repo-metadata`

## 1. Summary

- **Work Item**: Move planning, proposal, subfeature, and execution metadata/registry access behind shared repository modules.
- **Source Story / Increment / Slice**: `DALC-02`, `DALC-03` / `I2` / `dalc-repo-metadata`
- **Requested Outcome**: Commands stop duplicating metadata and registry parsing/writing logic and delegate to shared library repositories.
- **Why this matters**: The DAL refactor only pays off if the shared ownership boundary is explicit and reusable.
- **Independent Test**: `pytest`

## 2. Acceptance Scenarios

1. **Given** the metadata-focused repository modules, **When** a command reads or writes planning/proposal/subfeature/execution metadata, **Then** the shared library repository owns the data access path.
2. **Given** the current CLI workflows, **When** the existing command entrypoints run, **Then** behavior remains compatible.
3. **Given** the repository layer, **When** a metadata payload is invalid, **Then** validation fails at the library boundary rather than silently persisting bad state.

## 3. Functional Requirements

- **FR-001**: The system MUST provide shared repository modules for planning, proposal, subfeature, and execution metadata/registry access.
- **FR-002**: The repository modules MUST own registry loading, registry writing, metadata reading, and metadata writing for their artifact family.
- **FR-003**: The command modules MUST use the shared repository modules for the relevant data-access operations.
- **FR-004**: The slice MUST preserve current workflow behavior and CLI output conventions.
- **FR-005**: The repository boundary MUST continue to validate normalized JSON and registry shapes.

## 4. Edge Cases

- Legacy metadata files remain on disk and must continue to load.
- Registry markdown and JSON projections must stay in sync.
- Subfeature metadata updates may still project through the parent feature as today.
- Commands that only orchestrate business logic should not regress when their storage helpers move.

## 5. Assumptions and Dependencies

### Assumptions

- **A1**: The current command logic can be split into reusable repository helpers without changing artifact formats.
- **A2**: Existing inventory and transition helpers remain authoritative for cross-artifact orchestration.

### Dependencies

- **D1**: The shared storage/scoped-runtime foundation is already in place.
- **D2**: The direct-write guardrail slice is already closing the door on new command-owned writes.

## 6. Success Criteria

- **SC-001**: Metadata and registry reads/writes are available through library repository modules.
- **SC-002**: Command modules use the library repositories for the moved data-access responsibilities.
- **SC-003**: The relevant pytest suite passes without behavior regressions.

## 7. Open Clarifications

- None.
