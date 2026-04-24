# Slice Specification: Add typed ship preflight contract and readiness metadata

**Slice**: `spi-preflight-contract`
**Created**: 2026-04-24  
**Status**: Draft
**Input**: "spi-preflight-contract Add typed ship preflight contract and readiness metadata"

## 1. Work Item Summary

- **Work Item**: Add the first shipped contract for `ship` preflight so maintainers can see whether preflight is disabled, skipped, passed, or blocked without changing the existing readiness blocker taxonomy.
- **Source Story / Increment / Slice**: `SPI-02`, `SPI-03` / `I1` / `spi-preflight-contract`
- **Requested Outcome**: When a maintainer runs `ship --json`, `ship --bootstrap-next`, or `ship --resume`, the readiness payload includes consistent nested preflight metadata driven by typed repo config under `accelerators.ship.preflight`.
- **Why this matters**: This establishes the machine-readable contract that later gating and operator docs depend on, while keeping preflight repo-owned and non-disruptive by default.
- **Independent Test**: `pytest -q skills/ship/tests/test_ship.py`

## 2. Acceptance Scenarios

1. **Given** execution config leaves `accelerators.ship.preflight.mode` unset or sets it to `off`, **When** a maintainer resolves ship readiness, **Then** readiness reports preflight as disabled and existing blocker codes remain unchanged.
2. **Given** execution config sets `accelerators.ship.preflight.mode` to `local_only`, **When** a maintainer resolves a route for `ship --resume` or `ship --bootstrap-next`, **Then** readiness includes the selected operation and a deterministic preflight status without requiring network access or new CLI controls.
3. **Given** a route that only recomputes backlog state and does not mutate execution state, **When** readiness is reported, **Then** preflight can be marked skipped rather than blocked or passed.

## 3. Functional Requirements

- **FR-001**: The system MUST parse a typed `accelerators.ship.preflight.mode` value from execution config under the existing `accelerators.ship` owner.
- **FR-002**: The system MUST support `off` and `local_only` as the first rollout modes for ship preflight behavior.
- **FR-003**: The system MUST classify the current ship operation so readiness can report whether preflight is disabled, skipped, passed, or blocked.
- **FR-004**: The system MUST expose nested `readiness.preflight` metadata for ship readiness output without replacing or renaming the existing canonical blocker codes.
- **FR-005**: The system MUST keep repo-owned configuration as the only control surface for this slice and MUST NOT require new CLI flags or environment variables.

## 4. Key Entities

- **Ship preflight config**: The typed execution-config object under `accelerators.ship.preflight` that controls whether preflight is off or local-only.
- **Preflight summary**: The nested readiness payload that explains mode, operation, status, and any blocking checks while preserving existing stop-reason semantics.
- **Ship operation class**: The resolved route category used to determine whether preflight is applicable, including read-only recomputation and mutation-capable paths.

## 5. Edge Cases

- Unknown or malformed preflight config values should fail clearly instead of silently defaulting to a misleading status.
- Read-only backlog resolution should not be reported as a passed mutation preflight.
- Existing readiness blockers must remain canonical even when preflight metadata is present.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: Parent ship backlog and runtime slices already provide the underlying readiness and delegation state this slice annotates.
- **A2**: The repository will keep v1 preflight local-only and deterministic, with no remote freshness checks in this slice.

### Dependencies

- **D1**: Closed parent slices `taw-runtime-foundation` and `taw-ship-backlog-integration` remain the baseline for the ship runtime and backlog contract.
- **D2**: The active work stays limited to the I1 contract surface; mutation blocking behavior lands in the later `spi-mutation-gating` slice.

## 7. Success Criteria

- **SC-001**: Ship readiness output consistently includes preflight metadata for the supported operation classes and config modes.
- **SC-002**: Existing blocker codes and stop-reason kinds remain stable while preflight adds explanatory context.
- **SC-003**: Repository authors can enable or disable the first rollout solely through typed execution config.

