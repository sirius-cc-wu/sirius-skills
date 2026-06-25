# Slice Contract: Add AST-based Direct I/O Guardrail Test

**Slice**: `dalc-foundation-guardrail`  
**Created**: 2026-06-25  
**Status**: Draft  
**Input**: `data-access-layer-consolidation / dalc-foundation-guardrail`

## 1. Summary

- **Work Item**: Add a regression test that scans command modules for new direct workspace-file write patterns.
- **Source Story / Increment / Slice**: `DALC-04` / `I1` / `dalc-foundation-guardrail`
- **Requested Outcome**: Future command code cannot introduce new direct filesystem writes to workspace artifacts without the validation suite flagging it.
- **Why this matters**: The DAL refactor only stays maintainable if direct writes stop spreading across command modules.
- **Independent Test**: `pytest tests/test_direct_io_guardrails.py`

## 2. Acceptance Scenarios

1. **Given** the current command package, **When** the guardrail test scans for direct workspace-file write patterns, **Then** the existing compatibility allowlist passes cleanly.
2. **Given** a new command module that starts writing workspace artifacts directly, **When** the guardrail test runs, **Then** it reports the new direct write pattern.
3. **Given** the repository’s existing command owners, **When** the guardrail runs, **Then** it does not require any runtime changes outside the test suite.

## 3. Functional Requirements

- **FR-001**: The system MUST provide a regression test for direct workspace-file write patterns in `src/sirius_skills/commands/`.
- **FR-002**: The guardrail MUST distinguish current compatibility exceptions from new direct-write regressions.
- **FR-003**: The test MUST be deterministic and runnable through the standard pytest suite.
- **FR-004**: The slice MUST preserve current command behavior while adding the regression guardrail.

## 4. Edge Cases

- Compatibility shims or currently owned writer modules remain allowed for now.
- A new command module introduces a direct write call and should fail the guardrail.
- Read-only file access should not be treated as a write regression.

## 5. Assumptions and Dependencies

### Assumptions

- **A1**: The guardrail is intentionally additive in this slice and will be tightened as later repository slices move write ownership into shared repositories.
- **A2**: The existing command package is stable enough for a static AST scan.

### Dependencies

- **D1**: The first foundation slice must already have moved the shared scope runtime foundation into the library package.
- **D2**: Existing pytest support remains available for the new regression test.

## 6. Success Criteria

- **SC-001**: The guardrail test passes on the current repository state.
- **SC-002**: A newly introduced direct workspace write in an unapproved command module causes a test failure.
- **SC-003**: The slice adds no runtime behavior changes.

## 7. Open Clarifications

- None.
