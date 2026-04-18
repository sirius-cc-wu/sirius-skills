# Implementation Plan: Enforce one commit per completed slice

**Slice**: `EW-MSE-04-per-slice-commit-checkpoints`  
**Date**: 2026-04-14  
**Status**: Closed  
**Spec**: `brief.md`

## 1. Summary

`EW-MSE-04-per-slice-commit-checkpoints` integrated a commit checkpoint into the
`execute-all-slices` loop. After each slice closes, the orchestrator requires a
clean worktree checkpoint before it can advance to the next ready slice, handing
control to `commit` when the repository is still dirty and keeping repository
history aligned with slice boundaries.

## 2. Technical Context

- Current system context:
  - the batch loop already resolves backlog order and stops safely on blockers
  - existing closure and commit flows already exist outside the orchestrator
  - the missing behavior was enforcing one commit boundary per closed slice
- Target modules / files:
  - `skills/execute-all-slices/scripts/execute_all_slices.py`
  - `skills/execute-all-slices/tests/test_execute_all_slices.py`
- Constraints:
  - preserve the existing commit-skill boundary
  - do not advance when the worktree remains dirty
  - keep the checkpoint exactly once per closed slice

## 3. Requirement Traceability

| Requirement | Implementation Steps | Validation |
| --- | --- | --- |
| FR-001 | S001 | V001 |
| FR-002 | S002 | V001 |
| FR-003 | S001, S003 | V001 |
| FR-004 | S002 | V001 |

## 4. Execution Plan

### Packet P01: Add per-slice commit enforcement

- Scope: require one commit checkpoint between one closed slice and the next slice start.
- Steps:
  - [x] **S001** Gate the next slice on a clean worktree checkpoint after closure.
  - [x] **S002** Stop immediately when the worktree remains dirty and hand control back to `commit`.
  - [x] **S003** Preserve exactly one commit checkpoint per closed slice during traversal.
- Validation:
  - [x] **V001** `pytest -q skills/execute-all-slices/tests/test_execute_all_slices.py -k commit_checkpoint`

## 5. Supporting Notes

- Verification scenarios:
  - stop when a dirty worktree demands a commit checkpoint
  - refuse to start the next slice on a dirty worktree
  - allow ordered traversal once the previous slice is committed cleanly
- Durable artifact note:
  - this slice keeps the batch loop compatible with the repository rule of one
    commit per completed slice

## 6. Execution Review Outcome

- Outcome: closed
- Validation evidence:
  - `pytest -q skills/execute-all-slices/tests/test_execute_all_slices.py -k commit_checkpoint`
