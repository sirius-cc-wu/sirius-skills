# Implementation Plan: Add one-slice finishing and resume orchestration

**Slice**: `taw-ship-slice-loop`  
**Date**: 2026-04-22  
**Status**: Execution Ready  
**Spec**: `brief.md`

## 1. Summary

`taw-ship-slice-loop` introduces the first explicit `ship-slice` skill. The
skill resolves one active slice, reuses the `ship` handoff payload contract,
reads durable learnings, writes checkpoint and event-log records, and reports
the next owner for the slice without taking over backlog traversal.

## 2. Technical Context

- Target modules / files:
  - `skills/ship-slice/SKILL.md`
  - `skills/ship-slice/scripts/ship_slice.py`
  - `skills/ship-slice/tests/test_ship_slice.py`
  - `scripts/sync_shared_skill_runtime.py`
  - `Makefile`
  - `README.md`
  - packaging/runtime sync tests
- Constraints:
  - keep the skill additive and one-slice scoped
  - prefer execution artifacts over stale checkpoints
  - reuse the shared runtime for learnings, checkpoints, and event logs

## 3. Requirement Traceability

| Requirement | Implementation Steps | Validation |
| --- | --- | --- |
| FR-001 | S001, S002 | V001 |
| FR-002 | S002 | V001 |
| FR-003 | S003 | V001 |
| FR-004 | S001, S003 | V001 |
| FR-005 | S004 | V001, V002 |

## 4. Execution Plan

### Packet P01: Add the one-slice finisher CLI

- [x] **S001** Add `ship-slice` CLI support for selector, handoff, and resume
  checkpoint inputs.
- [x] **S002** Read scope-matched active and candidate learnings before
  returning the next owner for the slice.
- [x] **S003** Persist runtime checkpoint and execution-log records for each
  stop boundary.
- Validation:
  - [x] **V001** `pytest -q skills/ship-slice/tests/test_ship_slice.py -k finish_or_resume`

### Packet P02: Wire packaging and docs

- [x] **S004** Add the new skill to packaged runtime sync, managed skill lists,
  and top-level docs.
- Validation:
  - [x] **V002** `pytest -q tests/test_sync_shared_skill_runtime.py tests/test_install_target_modes.py`

## 5. Execution Review Outcome

- Outcome: ready for closure
- Review finding classification:
  - no blocking brief-to-implementation gaps found
  - no blocking intent-to-brief gaps found
- Validation evidence:
  - `pytest -q skills/ship-slice/tests/test_ship_slice.py -k finish_or_resume`
  - `pytest -q tests/test_sync_shared_skill_runtime.py tests/test_install_target_modes.py`
