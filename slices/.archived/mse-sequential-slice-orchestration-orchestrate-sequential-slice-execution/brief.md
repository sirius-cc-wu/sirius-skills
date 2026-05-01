# Slice Specification: Orchestrate sequential slice execution

**Slice**: `mse-sequential-slice-orchestration`  
**Created**: 2026-04-14  
**Status**: Closed  
**Input**: `mse-sequential-slice-orchestration`

## 1. Work Item Summary

- **Work Item**: Drive one planned slice at a time through slice bootstrap and execution handoff.
- **Source Story / Increment / Slice**: `EW-01` / `I2` / `mse-sequential-slice-orchestration`
- **Requested Outcome**: As a maintainer, I want the batch executor to process one ready slice at a time so multi-slice execution stays aligned with existing execution owners.
- **Why this matters**: Batch execution should automate traversal, not absorb slice bootstrap, review, or closure ownership into a new state machine.
- **Independent Test**: `pytest -q skills/ship/tests/test_ship.py -k orchestration`

## 2. Acceptance Scenarios

1. **Given** a resolved backlog with a ready next slice, **When** orchestration runs, **Then** it bootstraps only that slice and routes execution through the existing execution flow.
2. **Given** later slices remain in the backlog, **When** the current slice is still active, **Then** orchestration does not start another slice in parallel.
3. **Given** the batch run advances normally, **When** one slice completes its owned steps, **Then** orchestration proceeds to the next ready slice in backlog order.

## 3. Functional Requirements

- **FR-001**: The system MUST bootstrap at most one ready slice at a time from the resolved backlog.
- **FR-002**: The system MUST reuse the existing slice, guide-execution, review-execution, and close-slice boundaries instead of reimplementing them.
- **FR-003**: The system MUST preserve one-active-slice semantics across the batch run.
- **FR-004**: The system MUST keep backlog traversal ordered and dependency-aware.

## 4. Key Entities

- **Active slice**: The one execution slice currently being bootstrapped or routed.
- **Backlog traversal loop**: The ordered control flow that advances from one ready slice to the next.
- **Execution owner handoff**: The boundary where orchestration invokes existing slice and execution skills.

## 5. Edge Cases

- No ready slices remain after resolution; orchestration should exit cleanly.
- A slice is already active; orchestration should not start another one.
- A later slice depends on an earlier slice; traversal should respect that dependency order.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: `mse-scope-and-backlog-resolution` already provides deterministic target and backlog resolution.
- **A2**: Existing execution-layer skills remain the only owners of bootstrap, review, and closure semantics.

### Dependencies

- **D1**: `mse-scope-and-backlog-resolution` remains the prerequisite backlog reader.
- **D2**: Existing execution-owner integrations stay available from the repository root.

## 7. Success Criteria

- **SC-001**: Batch execution never creates multiple active slices at once.
- **SC-002**: Orchestration reuses existing execution owners instead of diverging from them.
- **SC-003**: Ordered backlog traversal works across more than one planned slice.

## 8. Open Clarifications

- None.
