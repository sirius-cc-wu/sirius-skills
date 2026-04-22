# Implementation Plan: Add high-autonomy planning orchestration

**Slice**: `taw-autoplan`  
**Date**: 2026-04-22  
**Status**: Execution Ready  
**Spec**: `brief.md`

## 1. Summary

`taw-autoplan` introduces the planning-side accelerator above
`guide-planning`. The first version resolves one planning target, reads durable
learnings, persists checkpoint and event-log context, reports the next planning
owner, and stops explicitly at the approval boundary.

## 2. Technical Context

- Target modules / files:
  - `skills/autoplan/SKILL.md`
  - `skills/autoplan/scripts/autoplan.py`
  - `skills/autoplan/tests/test_autoplan.py`
  - `scripts/sync_shared_skill_runtime.py`
  - `Makefile`
  - `README.md`
- Constraints:
  - keep planning registry state authoritative
  - preserve the approval boundary
  - reuse the shared runtime for learnings and checkpoints

## 3. Requirement Traceability

| Requirement | Implementation Steps | Validation |
| --- | --- | --- |
| FR-001 | S001 | V001 |
| FR-002 | S002 | V001 |
| FR-003 | S003 | V001 |
| FR-004 | S001 | V001 |
| FR-005 | S001 | V001 |

## 4. Execution Plan

### Packet P01: Add the planning accelerator CLI

- [x] **S001** Resolve one planning target through `guide-planning` state and
  map it to the next planning owner plus stop action.
- [x] **S002** Read scope-matched learnings before emitting the next-owner
  result.
- [x] **S003** Persist runtime checkpoint and event-log records for resume.
- Validation:
  - [x] **V001** `pytest -q skills/autoplan/tests/test_autoplan.py`

## 5. Execution Review Outcome

- Outcome: ready for closure
- Review finding classification:
  - no blocking brief-to-implementation gaps found
  - no blocking intent-to-brief gaps found
- Validation evidence:
  - `pytest -q skills/autoplan/tests/test_autoplan.py`
