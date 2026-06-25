# Slice Contract: Implement Storage/Models and Relocate Scope Runtime

**Slice**: `dalc-foundation-storage`  
**Created**: 2026-06-25  
**Status**: Draft  
**Input**: `data-access-layer-consolidation / dalc-foundation-storage`

## 1. Summary

- **Work Item**: Establish the storage and shared model foundation for workflow-state handling, and move the scope runtime into the library-owned boundary.
- **Source Story / Increment / Slice**: `DALC-03` / `I1` / `dalc-foundation-storage`
- **Requested Outcome**: Commands and later repository modules can depend on one shared scope/runtime and one shared storage/model layer instead of re-implementing those boundaries.
- **Why this matters**: This is the foundation slice for the DAL refactor; the later metadata, guardrail, and markdown slices depend on it.
- **Independent Test**: `pytest tests/test_workflow_runtime.py` plus the existing CLI tests that exercise scope resolution continue to pass after the relocation.

## 2. Acceptance Scenarios

1. **Given** planning or execution commands that resolve scope, **When** they use the shared library runtime, **Then** they resolve the same repo and scope paths as before.
2. **Given** workflow-state code that needs shared records or file helpers, **When** it depends on the foundation layer, **Then** it can use common storage and normalized models without duplicating that logic in command modules.
3. **Given** current callers of the scope runtime, **When** the runtime is relocated, **Then** existing behavior stays compatible and the callers do not need to change their observed scope results.

## 3. Functional Requirements

- **FR-001**: The system MUST provide a shared workflow-state storage boundary for common text and JSON loading and persistence.
- **FR-002**: The system MUST provide normalized shared models for data exchanged between commands and workflow-state repositories.
- **FR-003**: The system MUST make scope resolution available from the library-owned runtime boundary without changing current scope behavior.
- **FR-004**: The system MUST preserve existing planning and execution config ownership and path resolution semantics.
- **FR-005**: The slice MUST remain backward compatible for current callers that depend on the runtime and shared workflow-state foundation.

## 4. Edge Cases

- Nested scopes still resolve to the same active scope as before.
- Missing config or malformed JSON still surfaces explicit failures.
- Existing command callers continue to work after the runtime moves into the library boundary.

## 5. Assumptions and Dependencies

### Assumptions

- **A1**: Existing runtime and workflow-state tests are sufficient to detect behavioral drift in this foundation slice.
- **A2**: This slice is foundation-only; later slices will migrate the remaining repository call sites.

### Dependencies

- **D1**: The approved planning packet and planned slice traceability remain the source of truth for scope.
- **D2**: Existing workflow-state and execution tests remain available for regression checks.

## 6. Success Criteria

- **SC-001**: Scope/runtime resolution behaves identically before and after the relocation.
- **SC-002**: Shared storage and shared models are available for the later repository slices.
- **SC-003**: The slice passes its independent regression test set without changing workspace layout.

## 7. Open Clarifications

- None.
