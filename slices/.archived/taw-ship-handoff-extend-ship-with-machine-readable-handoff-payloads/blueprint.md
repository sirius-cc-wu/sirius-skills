# Implementation Plan: Extend ship with machine-readable handoff payloads

**Slice**: `taw-ship-handoff`  
**Date**: 2026-04-22  
**Status**: Execution Ready  
**Spec**: `brief.md`

## 1. Summary

`taw-ship-handoff` adds the first explicit machine-readable handoff contract to
`ship`. The slice keeps the existing human-facing backlog output and next-owner
logic intact while emitting a stable `handoff_payload` derived from the active
slice and the planned-slice backlog entry.

## 2. Technical Context

- Current system context:
  - `ship` already computes an `active_slice_handoff` dict for the active slice
  - `workflow_runtime.handoff` already defines a typed payload contract
  - current JSON output lacks a stable top-level handoff payload for downstream
    accelerators
- Target modules / files:
  - `skills/ship/scripts/ship.py`
  - `skills/ship/tests/test_ship.py`
  - `skills/ship/SKILL.md`
  - `README.md`
- Constraints:
  - keep `ship` standalone and additive
  - derive the payload from existing backlog and execution artifacts
  - preserve backward compatibility for existing JSON consumers

## 3. Gate Outcomes

- **Architecture / Constraints**: pass
  - the slice reuses the shared handoff contract instead of inventing another
    shape inside `ship`
- **Risk / Compliance**: pass
  - the change is additive to JSON output and does not mutate workflow truth
- **Testability**: pass
  - the handoff payload shape is deterministic and can be asserted directly in
    ship CLI tests

## 4. Requirement Traceability

| Requirement | Implementation Steps | Validation |
| --- | --- | --- |
| FR-001 | S001, S002 | V001 |
| FR-002 | S001 | V001 |
| FR-003 | S001 | V001 |
| FR-004 | S002 | V001 |
| FR-005 | S003 | V001 |

## 5. Execution Plan

### Packet P01: Emit a typed active-slice handoff payload

- Scope: extend the active-slice handoff data structure with a stable payload
  derived through `workflow_runtime.handoff`.
- Steps:
  - [x] **S001** Import `HandoffPayload` into `ship.py`, resolve repo/skill lib
    paths for packaged and repo-local execution, and attach a typed payload to
    active-slice handoff output.
  - [x] **S002** Mirror that payload at the top level of `ship --json` output
    so downstream accelerators have a stable entrypoint without losing the
    existing human-facing fields.
- Validation:
  - [x] **V001** `pytest -q skills/ship/tests/test_ship.py -k handoff`

### Packet P02: Document and lock the contract

- Scope: describe the machine-readable handoff surface in ship-facing docs and
  regression tests.
- Steps:
  - [x] **S003** Update `skills/ship/SKILL.md`, `README.md`, and ship tests so
    the new contract is described and asserted explicitly.
- Validation:
  - [x] **V001** `pytest -q skills/ship/tests/test_ship.py -k handoff`

## 6. Supporting Notes

- The first machine-readable contract does not yet delegate to `ship-slice`; it
  only publishes the stable payload that later slices can consume.
- The payload action stays `resume_active_slice` because downstream one-slice
  accelerators should reconcile the current active slice rather than recreate
  backlog traversal semantics.

## 7. Validation Plan

- `pytest -q skills/ship/tests/test_ship.py -k handoff`

## 8. Delivery Notes

- Keep the contract additive so existing JSON consumers that only read
  `next_owner` or `active_slice_handoff` continue to work.
- Use the shared runtime contract now so later `ship-slice` work does not need
  to normalize multiple payload shapes.

## 9. Execution Review Outcome

- Outcome: ready for closure
- Review finding classification:
  - no blocking brief-to-implementation gaps found
  - no blocking intent-to-brief gaps found
- Validation evidence:
  - `pytest -q skills/ship/tests/test_ship.py -k handoff`
