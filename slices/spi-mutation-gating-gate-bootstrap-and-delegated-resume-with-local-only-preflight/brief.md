# Slice Specification: Gate bootstrap and delegated resume with local-only preflight

**Slice**: `spi-mutation-gating`
**Created**: 2026-04-24  
**Status**: Draft
**Input**: "spi-mutation-gating Gate bootstrap and delegated resume with local-only preflight"

## 1. Work Item Summary

- **Work Item**: Turn the local-only preflight contract into an actual mutation gate for `ship` so bootstrap and delegated resume stop before execution-state changes when existing local guardrails fail.
- **Source Story / Increment / Slice**: `SPI-02` / `I2` / `spi-mutation-gating`
- **Requested Outcome**: When `accelerators.ship.preflight.mode` is `local_only`, `ship --bootstrap-next` and mutation-capable `ship --resume` stop before mutation on approval or commit guardrail failures, while keeping the existing blocker codes canonical and marking the stop reason as preflight.
- **Why this matters**: This is the safety boundary of the subfeature: operators can tell not only that a run is unsafe, but that the stop happened before `ship` mutated slice state or delegated deeper execution.
- **Independent Test**: `pytest -q skills/ship/tests/test_ship.py skills/ship-slice/tests/test_ship_slice.py`

## 2. Acceptance Scenarios

1. **Given** `accelerators.ship.preflight.mode` is `local_only` and a maintainer tries `ship --bootstrap-next` while the repo is blocked by the commit checkpoint, **When** `ship` resolves readiness, **Then** it stops before creating the next slice and reports the canonical blocker with `stop_reason.phase=preflight`.
2. **Given** `accelerators.ship.preflight.mode` is `local_only`, delegation is enabled, and approval has not been recorded, **When** a maintainer runs `ship --resume`, **Then** `ship` stops before delegated execution begins and reports the canonical approval blocker with preflight metadata.
3. **Given** `accelerators.ship.preflight.mode` is `local_only` and a route-only resume does not mutate execution state, **When** a maintainer runs `ship --resume`, **Then** `ship` keeps reporting preflight as skipped rather than blocking a non-mutating route.

## 3. Functional Requirements

- **FR-001**: The system MUST evaluate local-only preflight before `ship --bootstrap-next` creates a new execution slice.
- **FR-002**: The system MUST evaluate local-only preflight before mutation-capable `ship --resume` delegates to `ship-slice`.
- **FR-003**: The system MUST reuse the existing canonical blocker codes for approval and commit checkpoint failures rather than inventing new preflight-specific blockers.
- **FR-004**: The system MUST mark `readiness.stop_reason.phase` as `preflight` when local-only preflight blocks a mutation-capable path.
- **FR-005**: The system MUST keep route-only resume non-blocking and continue to report preflight as skipped when no mutation-capable action is about to happen.

## 4. Key Entities

- **Preflight gate**: The local-only decision point that runs before bootstrap or delegated resume mutates execution state.
- **Canonical blocker code**: The existing readiness reason, such as `approval_required` or `commit_checkpoint`, that remains authoritative even when preflight is the phase that discovered it.
- **Stop reason phase**: The additional `phase=preflight` marker that tells operators the stop happened before mutation.

## 5. Edge Cases

- Multiple active mapped slices remain a hard error and should not be softened into a preflight block.
- If preflight is disabled, bootstrap and resume should keep their current behavior.
- Route-only resume must not be mislabeled as a blocked preflight path.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: The I1 preflight contract already emits stable nested preflight metadata and operation classification.
- **A2**: Local-only preflight will continue to use only local repo evidence and existing workflow guardrails.

### Dependencies

- **D1**: `spi-preflight-contract` is complete and provides the typed config plus readiness preflight summary.
- **D2**: Parent slice `taw-ship-slice-loop` remains the source of truth for delegated stop-policy behavior after `ship` decides delegation may start.

## 7. Success Criteria

- **SC-001**: `ship --bootstrap-next` stops before new slice creation when local-only preflight detects a commit checkpoint failure.
- **SC-002**: mutation-capable `ship --resume` stops before delegation when approval or commit guardrails fail and reports `phase=preflight`.
- **SC-003**: route-only resume remains non-blocking and keeps preflight classified as skipped.

