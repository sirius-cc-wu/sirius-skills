# Implementation Plan: Resolve planning scope and remaining planned slices

**Slice**: `EW-MSE-01-scope-and-backlog-resolution`  
**Date**: 2026-04-14  
**Status**: Closed  
**Spec**: `brief.md`

## 1. Summary

`EW-MSE-01-scope-and-backlog-resolution` established the planning-target and
backlog-resolution foundation for `execute-all-slices`. The slice resolves one
feature or subfeature target, reads its planned slice lineage, excludes already
closed execution slices, and returns the next ready slice without mutating
planning or execution state.

## 2. Technical Context

- Current system context:
  - planning packets already encode target scope and slice lineage
  - execution metadata already records which execution slices are closed
  - no earlier batch helper resolved one planning scope into one ordered backlog
- Target modules / files:
  - `skills/execute-all-slices/scripts/execute_all_slices.py`
  - `skills/execute-all-slices/tests/test_execute_all_slices.py`
- Constraints:
  - keep target resolution read-only
  - preserve feature vs subfeature ownership boundaries
  - derive backlog state only from durable planning and execution artifacts

## 3. Requirement Traceability

| Requirement | Implementation Steps | Validation |
| --- | --- | --- |
| FR-001 | S001 | V001 |
| FR-002 | S002 | V001 |
| FR-003 | S002, S003 | V001 |
| FR-004 | S001, S003 | V001 |

## 4. Execution Plan

### Packet P01: Resolve one planning target into one remaining backlog

- Scope: add the target-resolution and next-ready-backlog logic that later batch
  slices depend on.
- Steps:
  - [x] **S001** Resolve one feature or subfeature target from durable planning metadata.
  - [x] **S002** Read planned slice lineage and subtract already-closed execution slices.
  - [x] **S003** Return the next ready slice in deterministic planned order without writing state.
- Validation:
  - [x] **V001** `pytest -q skills/execute-all-slices/tests/test_execute_all_slices.py -k scope_or_backlog`

## 5. Supporting Notes

- Verification scenarios:
  - resolve a mixed closed/unstarted backlog to the correct next slice
  - reject ambiguous or non-ready planning targets explicitly
- Durable artifact note:
  - this slice established the canonical backlog-resolution step reused by the
    later orchestration and resume logic

## 6. Execution Review Outcome

- Outcome: closed
- Validation evidence:
  - `pytest -q skills/execute-all-slices/tests/test_execute_all_slices.py -k scope_or_backlog`
