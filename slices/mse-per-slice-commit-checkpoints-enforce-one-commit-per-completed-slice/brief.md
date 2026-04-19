# Slice Specification: Enforce one commit per completed slice

**Slice**: `mse-per-slice-commit-checkpoints`  
**Created**: 2026-04-14  
**Status**: Closed  
**Input**: `mse-per-slice-commit-checkpoints`

## 1. Work Item Summary

- **Work Item**: Require a clean commit checkpoint after each closed slice before the batch loop advances.
- **Source Story / Increment / Slice**: `EW-04` / `I3` / `mse-per-slice-commit-checkpoints`
- **Requested Outcome**: As a maintainer, I want every completed slice in a batch run to become its own Git checkpoint so the history remains aligned with slice boundaries.
- **Why this matters**: Batch execution should preserve the same durable closure and commit discipline expected from one-slice-at-a-time work.
- **Independent Test**: `pytest -q skills/execute-all-slices/tests/test_execute_all_slices.py -k commit_checkpoint`

## 2. Acceptance Scenarios

1. **Given** a slice closes successfully during batch execution, **When** orchestration prepares to continue, **Then** it requires a commit checkpoint before the next slice starts.
2. **Given** the worktree is dirty after a completed slice, **When** orchestration evaluates the next step, **Then** it stops and hands control to `commit` instead of advancing to later slices.
3. **Given** one slice has been committed successfully, **When** more backlog remains, **Then** the next slice can start from a clean checkpoint.

## 3. Functional Requirements

- **FR-001**: The system MUST require a commit checkpoint after each completed slice.
- **FR-002**: The system MUST stop when the post-closure checkpoint leaves the worktree dirty.
- **FR-003**: The system MUST preserve one commit per closed slice during batch traversal.
- **FR-004**: The system MUST keep commit enforcement outside the slice-closure owner itself and integrate it as an orchestration checkpoint.

## 4. Key Entities

- **Commit checkpoint**: The required Git boundary between one closed slice and the next.
- **Closed slice boundary**: The point at which execution work is complete and commit enforcement begins.
- **Clean worktree prerequisite**: The state required before the next slice can start.

## 5. Edge Cases

- The worktree remains dirty after closure; later slices must not start.
- The worktree still has changes after the checkpoint step; the batch run should stop.
- The final slice closes and commits; the batch run should end without looking for another slice.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: `mse-stop-and-resume-semantics` already stops safely and resumes from durable state.
- **A2**: Commit behavior continues to live behind the existing `commit` skill boundary.

### Dependencies

- **D1**: `mse-stop-and-resume-semantics` remains the prerequisite orchestration behavior.
- **D2**: Existing closure and commit integrations remain available from the batch loop.

## 7. Success Criteria

- **SC-001**: Each completed slice leaves one durable commit checkpoint before later batch work begins.
- **SC-002**: Dirty-worktree or failed-commit conditions stop the run immediately.
- **SC-003**: Git history stays aligned with slice boundaries during batch execution.

## 8. Open Clarifications

- None.
