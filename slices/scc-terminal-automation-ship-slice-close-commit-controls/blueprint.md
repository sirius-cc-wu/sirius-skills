# Implementation Plan: Auto-format, close, and commit owned changes

**Slice**: `scc-terminal-automation`  
**Date**: 2026-04-23  
**Status**: Execution Ready  
**Spec**: `brief.md`

## 1. Summary

This slice adds the terminal automation tail for delegated `ship-slice` runs.
It should optionally format owned files, close the slice through the existing
closure tooling, and create an owned-file-only commit while preserving explicit
partial-success reporting when commit automation stops after closure.

## 2. Technical Context

- Target modules / files:
  - `skills/ship-slice/scripts/ship_slice.py`
  - `skills/ship-slice/tests/test_ship_slice.py`
- Constraints:
  - keep owned-file tracking from `scc-owned-change-set` as the source of truth
  - require `auto_commit` to imply `auto_close`
  - do not stage or commit unrelated dirty files outside the owned set
  - preserve structured readiness output for review, close, commit, and failure
    states

## 3. Gate Outcomes

- Architecture / Constraints: pass
  - the change layers terminal automation onto existing `ship-slice` routing
    and reuses `close-slice`
- Risk / Compliance: pass
  - owned-file staging and spillover checks remain defensive even when
    automation continues
- Testability: pass
  - the terminal path can be covered with focused temp-repo tests

## 4. Requirement Traceability

| Requirement | Implementation Steps | Validation |
| --- | --- | --- |
| FR-001 | S001 | V001 |
| FR-002 | S002 | V001 |
| FR-003 | S003 | V001 |
| FR-004 | S004 | V001 |
| FR-005 | S003, S004 | V001 |

## 5. Execution Plan

### Packet P01: Add terminal automation flow

- [x] **S001** Parse and validate terminal automation config in `ship_slice.py`,
  including the `auto_commit` => `auto_close` invariant.
- [x] **S002** Add formatter execution helpers that run only on owned files and
  stop on spillover or formatter failure.
- [x] **S003** Add close-slice delegation plus partial-success reporting when
  closure succeeds but later automation stops.
- [x] **S004** Add owned-file-only staging and commit creation for automated
  commit checkpoints.
- Validation:
  - [x] **V001** `pytest -q skills/ship-slice/tests/test_ship_slice.py skills/close-slice/tests/test_close_slice.py`

## 6. Delivery Notes

- Keep formatter execution generic enough to take a repo-supplied command plus
  owned paths.
- Recompute worktree ownership after formatting and closure so commit staging
  uses the final owned dirty set.
- Keep commit automation resumable: a later `ship-slice --resume` should be
  able to finish a closed-but-uncommitted owned change set.
