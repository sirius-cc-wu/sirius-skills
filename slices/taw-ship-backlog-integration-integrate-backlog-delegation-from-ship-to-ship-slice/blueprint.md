# Implementation Plan: Integrate backlog delegation from ship to ship-slice

**Slice**: `taw-ship-backlog-integration`  
**Date**: 2026-04-22  
**Status**: Execution Ready  
**Spec**: `brief.md`

## 1. Summary

`taw-ship-backlog-integration` makes the one-slice finisher reachable from
backlog mode. `ship` stays responsible for backlog traversal, but it can now
optionally hand the active slice to `ship-slice` when execution config enables
delegation.

## 2. Technical Context

- Target modules / files:
  - `skills/ship/scripts/ship.py`
  - `skills/ship/tests/test_ship.py`
  - `.skills/execution.json`
- Constraints:
  - keep delegation opt-in
  - preserve existing standalone `ship` behavior when disabled
  - return delegated output without replacing repo artifacts as workflow truth

## 3. Requirement Traceability

| Requirement | Implementation Steps | Validation |
| --- | --- | --- |
| FR-001 | S001 | V001 |
| FR-002 | S001, S002 | V001 |
| FR-003 | S002 | V001 |
| FR-004 | S003 | V001 |
| FR-005 | S002 | V001 |

## 4. Execution Plan

### Packet P01: Delegate one active slice optionally

- [x] **S001** Extend `ship` to read accelerator delegation config and invoke
  `ship-slice` with the active handoff payload when enabled.
- [x] **S002** Return delegated output in `ship --json` while preserving the
  existing non-delegated path.
- [x] **S003** Update repo execution config with explicit accelerator defaults.
- Validation:
  - [x] **V001** `pytest -q skills/ship/tests/test_ship.py skills/ship-slice/tests/test_ship_slice.py -k delegation`

## 5. Execution Review Outcome

- Outcome: ready for closure
- Review finding classification:
  - no blocking brief-to-implementation gaps found
  - no blocking intent-to-brief gaps found
- Validation evidence:
  - `pytest -q skills/ship/tests/test_ship.py skills/ship-slice/tests/test_ship_slice.py -k delegation`
