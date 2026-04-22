# Slice Specification: Stop on blockers and resume from durable state

**Slice**: `mse-stop-and-resume-semantics`  
**Created**: 2026-04-14  
**Status**: Closed  
**Input**: `mse-stop-and-resume-semantics`

## 1. Work Item Summary

- **Work Item**: Stop batch execution safely on blockers and resume from durable slice state.
- **Source Story / Increment / Slice**: `EW-03` / `I2` / `mse-stop-and-resume-semantics`
- **Requested Outcome**: As a maintainer, I want the batch executor to stop on active-slice or dependency blockers and resume later from closed-slice state instead of maintaining a second progress ledger.
- **Why this matters**: Multi-slice execution is only trustworthy if interruptions do not create hidden progress or skip blocked work.
- **Independent Test**: `pytest -q skills/ship/tests/test_ship.py -k stop_or_resume`

## 2. Acceptance Scenarios

1. **Given** a batch run encounters an active slice or dependency block, **When** orchestration evaluates progress, **Then** it stops without advancing to later slices.
2. **Given** earlier slices are closed and a later slice remains ready, **When** the batch run resumes, **Then** it derives the next step from durable slice and planning artifacts.
3. **Given** no new progress has been recorded durably, **When** the batch run resumes, **Then** it does not claim work was completed.

## 3. Functional Requirements

- **FR-001**: The system MUST stop on active-slice and dependency-blocked conditions.
- **FR-002**: The system MUST resume from durable planning and closed-slice state instead of batch-local progress files.
- **FR-003**: The system MUST preserve backlog order when resuming after a stop condition clears.
- **FR-004**: The system MUST surface blocker reasons explicitly.

## 4. Key Entities

- **Stop condition**: An active slice, failed step, or dependency blocker that prevents safe advancement.
- **Resume point**: The next ready slice derived from durable state after prior closed work is accounted for.
- **Durable progress state**: Planning lineage plus slice registry and metadata, rather than a batch-specific store.

## 5. Edge Cases

- A slice remains open after bootstrap; later slices must not start until the owning execution flow advances it durably.
- A dependency remains open; resume should continue to report it as blocked.
- A rerun begins after some slices were already closed in an earlier attempt; resume should continue from the next ready slice.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: Ordered orchestration from `mse-sequential-slice-orchestration` is already in place.
- **A2**: Closed-slice metadata is sufficient to derive resume position without extra batch state.

### Dependencies

- **D1**: `mse-sequential-slice-orchestration` remains the prerequisite traversal loop.
- **D2**: Existing execution metadata remains the only source of truth for active and closed slice state.

## 7. Success Criteria

- **SC-001**: Blocked or failed runs stop without advancing later slices.
- **SC-002**: Resume behavior is derived entirely from durable repository artifacts.
- **SC-003**: Blocker reasons remain explicit across reruns.

## 8. Open Clarifications

- None.
