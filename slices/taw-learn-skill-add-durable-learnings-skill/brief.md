# Slice Specification: Add durable learnings skill

**Slice**: `taw-learn-skill`  
**Created**: 2026-04-22  
**Status**: Draft  
**Input**: `taw-learn-skill`

## 1. Work Item Summary

- **Work Item**: Add an explicit `learn` skill that queries, promotes, and
  prunes repo-scoped workflow learnings on top of the new shared runtime store.
- **Source Story / Increment / Slice**: `TAW-04` / `I1` / `taw-learn-skill`
- **Requested Outcome**: As a repeat user of `sirius-skills`, I want one
  durable `learn` skill so workflow learnings can be searched, promoted, and
  pruned explicitly instead of staying hidden in chat history or ad hoc JSON
  edits.
- **Why this matters**: Later accelerator skills are supposed to reuse explicit
  learnings, and that only works if the repository has a stable owner for
  learning retrieval and lifecycle changes.
- **Independent Test**: `pytest -q skills/learn/tests/test_learn.py`

## 2. Acceptance Scenarios

1. **Given** a repo-scoped learnings store exists, **When** a maintainer runs
   the `learn` skill in query mode, **Then** the skill returns matching
   learnings filtered by scope, skill, or state.
2. **Given** a candidate learning should become durable guidance, **When** a
   maintainer promotes it through `learn`, **Then** the learning state changes
   to `active` without requiring manual JSON editing.
3. **Given** a learning is stale or no longer trustworthy, **When** a
   maintainer prunes it through `learn`, **Then** the learning remains durable
   in the store but is marked `pruned` for later consumers.

## 3. Functional Requirements

- **FR-001**: The repository MUST provide a dedicated `learn` skill.
- **FR-002**: The `learn` skill MUST query repo-scoped learnings from the
  shared runtime store with optional scope, skill, and state filters.
- **FR-003**: The `learn` skill MUST promote an existing learning to `active`
  without requiring manual store edits.
- **FR-004**: The `learn` skill MUST prune an existing learning by marking it
  `pruned` instead of deleting it.
- **FR-005**: The skill and packaged install workflow MUST include the shared
  runtime dependency it consumes.

## 4. Key Entities

- **Learning record**: One repo-scoped runtime record describing guidance,
  scope, owning skill, and lifecycle state.
- **Learn skill**: The explicit owner for human-readable querying and lifecycle
  changes on learning records.
- **Learning state**: The lifecycle flag for one record, expected to include at
  least `candidate`, `active`, and `pruned`.

## 5. Edge Cases

- The learnings store may not exist yet; queries should return an empty result
  instead of failing.
- Promotion or pruning may target an unknown learning ID and should fail
  clearly.
- Filters may return zero matching learnings and should still produce valid
  structured output.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: `taw-runtime-foundation` already established the shared
  `workflow_runtime` package and the packaged runtime sync surface.
- **A2**: This slice owns the explicit human-facing `learn` skill interface,
  not automatic learning capture by other accelerators.

### Dependencies

- **D1**: `lib/workflow_runtime/learnings.py`
- **D2**: `scripts/sync_shared_skill_runtime.py`
- **D3**: managed skill installation surfaces such as `Makefile` and the
  managed-skill documentation lists

## 7. Success Criteria

- **SC-001**: Maintainers can query learnings by repo-relevant filters through
  one explicit skill.
- **SC-002**: Maintainers can promote or prune learnings without manual file
  edits.
- **SC-003**: Packaged installs include the runtime dependency required by the
  new skill.

## 8. Open Clarifications

- None.
