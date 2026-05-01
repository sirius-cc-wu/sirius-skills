# Implementation Plan: Orchestrate sequential slice execution

**Slice**: `mse-sequential-slice-orchestration`  
**Date**: 2026-04-14  
**Status**: Closed  
**Spec**: `brief.md`

## 1. Summary

`mse-sequential-slice-orchestration` added the orchestration loop for
`ship`. The slice reuses backlog resolution from `mse-scope-and-backlog-resolution`,
bootstraps one ready slice at a time, routes execution through the existing
execution owners, and preserves one-active-slice semantics across the run.

## 2. Technical Context

- Current system context:
  - backlog resolution already determines the next ready slice
  - execution-layer skills already own slice bootstrap, review, and closure
  - the missing capability was ordered orchestration across more than one slice
- Target modules / files:
  - `skills/ship/scripts/ship.py`
  - `skills/ship/tests/test_ship.py`
- Constraints:
  - do not create concurrent active slices
  - do not duplicate execution-layer state machines
  - keep ordering deterministic and dependency-aware

## 3. Requirement Traceability

| Requirement | Implementation Steps | Validation |
| --- | --- | --- |
| FR-001 | S001 | V001 |
| FR-002 | S002 | V001 |
| FR-003 | S001, S003 | V001 |
| FR-004 | S003 | V001 |

## 4. Execution Plan

### Packet P01: Add ordered orchestration over the resolved backlog

- Scope: turn one resolved backlog into sequential slice bootstrap and handoff.
- Steps:
  - [x] **S001** Start only one ready slice at a time from the remaining backlog.
  - [x] **S002** Route bootstrap and execution through the existing owner skills.
  - [x] **S003** Advance to the next planned slice only after the current slice leaves the active state.
- Validation:
  - [x] **V001** `pytest -q skills/ship/tests/test_ship.py -k orchestration`

## 5. Supporting Notes

- Verification scenarios:
  - bootstrap only the next ready slice
  - refuse to parallelize when another slice is still active
  - preserve planned ordering across more than one slice
- Durable artifact note:
  - this slice established the ordered traversal loop that later blocker and
    commit-checkpoint behavior depend on

## 6. Execution Review Outcome

- Outcome: closed
- Validation evidence:
  - `pytest -q skills/ship/tests/test_ship.py -k orchestration`
