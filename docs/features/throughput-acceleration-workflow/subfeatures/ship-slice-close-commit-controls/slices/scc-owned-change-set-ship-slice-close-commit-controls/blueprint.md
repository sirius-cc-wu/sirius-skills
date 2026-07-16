# Implementation Plan: Track owned changes and formatter scope

**Slice**: `scc-owned-change-set`  
**Date**: 2026-04-23  
**Status**: Execution Ready  
**Spec**: `brief.md`

## 1. Summary

This slice adds the owned-change-set contract that later terminal automation
depends on. `ship-slice` should capture a pre-run snapshot of worktree state,
derive which files belong to the delegated run, and use that ownership model to
scope formatting and to classify dirty-worktree conditions as either safe,
blocking, or spillover.

## 2. Technical Context

- Target modules / files:
  - `skills/ship-slice/scripts/ship_slice.py`
  - `skills/ship-slice/tests/test_ship_slice.py`
- Constraints:
  - preserve existing readiness and stop-reason reporting
  - do not block on unrelated dirty files outside the owned file set
  - treat same-file mixed ownership and formatter spillover as hard stops
  - keep the implementation local to `ship-slice`; no new control plane in this
    slice

## 3. Gate Outcomes

- Architecture / Constraints: pass
  - the change extends `ship-slice` state classification without changing owner
    boundaries
- Risk / Compliance: pass
  - the slice is defensive and does not yet mutate closure or Git checkpoint
    state
- Testability: pass
  - all requirements map to focused `ship-slice` tests

## 4. Requirement Traceability

| Requirement | Implementation Steps | Validation |
| --- | --- | --- |
| FR-001 | S001 | V001 |
| FR-002 | S002 | V001 |
| FR-003 | S001, S003 | V001 |
| FR-004 | S002, S003 | V001 |
| FR-005 | S001, S003 | V001 |

## 5. Execution Plan

### Packet P01: Capture delegated ownership state

- [x] **S001** Add a worktree snapshot/helper path in `ship_slice.py` that
  records pre-run dirty paths and derives an owned change set from the diff
  created during the delegated run.
- [x] **S002** Add formatting-scope evaluation that compares post-format paths
  against the owned change set and classifies spillover explicitly.
- [x] **S003** Extend readiness/stop-reason payloads so unrelated dirty files,
  same-file ownership conflicts, and formatter spillover are reported
  deterministically.
- Validation:
  - [x] **V001** `pytest -q skills/ship-slice/tests/test_ship_slice.py`

## 6. Delivery Notes

- Implement the ownership helpers in a way that can be reused by the later
  terminal automation slice.
- Keep any formatter-specific behavior abstract enough that later
  `auto_format` orchestration can call into the same owned-file checks instead
  of reclassifying paths again.
- Do not introduce `auto_format` config reads yet; this slice should establish
  the ownership model and stop semantics first.
