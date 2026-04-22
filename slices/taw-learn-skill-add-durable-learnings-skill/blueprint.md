# Implementation Plan: Add durable learnings skill

**Slice**: `taw-learn-skill`  
**Date**: 2026-04-22  
**Status**: Execution Ready  
**Spec**: `brief.md`

## 1. Summary

`taw-learn-skill` adds the first explicit human-facing owner for repo-scoped
workflow learnings. The slice introduces a `learn` skill with `query`,
`promote`, and `prune` commands on top of `workflow_runtime.learnings`, wires
the shared runtime into packaged installs for the new skill, and updates the
managed skill lists and tests that describe available repo skills.

## 2. Technical Context

- Current system context:
  - `lib/workflow_runtime/learnings.py` already provides low-level append,
    query, and state-update helpers
  - no current managed skill owns human-facing learning retrieval or lifecycle
    transitions
  - managed skill installation and docs enumerate actual available skills
- Target modules / files:
  - new `skills/learn/SKILL.md`
  - new `skills/learn/scripts/learn.py`
  - new `skills/learn/tests/test_learn.py`
  - `Makefile`
  - `README.md`
  - `scripts/sync_shared_skill_runtime.py`
  - `tests/test_sync_shared_skill_runtime.py`
  - `tests/test_install_target_modes.py`
- Constraints:
  - keep learnings project-scoped by default
  - mark records `active` or `pruned`; do not hard-delete them
  - reuse the shared runtime instead of introducing a second learnings store

## 3. Gate Outcomes

- **Architecture / Constraints**: pass
  - the slice reuses the shared runtime and keeps learnings as supplemental
    repo-scoped state
- **Risk / Compliance**: pass
  - the main risk is install/docs drift when the new skill is added
- **Testability**: pass
  - query/promote/prune behavior is deterministic and can be covered with
    isolated CLI tests

## 4. Requirement Traceability

| Requirement | Implementation Steps | Validation |
| --- | --- | --- |
| FR-001 | S001 | V001 |
| FR-002 | S001, S002 | V001 |
| FR-003 | S001, S002 | V001 |
| FR-004 | S001, S002 | V001 |
| FR-005 | S003, S004 | V002 |

## 5. Execution Plan

### Packet P01: Implement the learn skill CLI

- Scope: add the new managed `learn` skill and its query/promote/prune command
  surface.
- Steps:
  - [x] **S001** Create `skills/learn/` with a `SKILL.md`, CLI script, and
    tests that resolve the repo-scoped learnings path and expose `query`,
    `promote`, and `prune`.
  - [x] **S002** Keep lifecycle changes explicit by updating learning state
    through `workflow_runtime.learnings` instead of manual JSON rewriting in
    the skill.
- Validation:
  - [x] **V001** `pytest -q skills/learn/tests/test_learn.py`

### Packet P02: Wire the skill into packaged installs and managed docs

- Scope: make the new skill available through the managed install workflow and
  top-level skill lists.
- Steps:
  - [x] **S003** Extend `scripts/sync_shared_skill_runtime.py` so `learn`
    receives the packaged `workflow_runtime` copy it depends on.
  - [x] **S004** Update managed skill lists and install/runtime sync tests so
    the new skill is packaged and documented consistently.
- Validation:
  - [x] **V002** `pytest -q tests/test_sync_shared_skill_runtime.py tests/test_install_target_modes.py`

## 6. Supporting Notes

- The first `learn` slice does not need to implement automatic learning capture;
  it only needs an explicit human-facing owner for querying and lifecycle
  changes.
- Output can stay minimal and deterministic. JSON output is useful for tests and
  later automation even if the first human-facing output stays simple.
- If docs mention accelerator skills at a high level, keep `ship-slice` and
  `autoplan` clearly labeled as planned or future if they are not implemented
  yet.

## 7. Validation Plan

- `pytest -q skills/learn/tests/test_learn.py`
- `pytest -q tests/test_sync_shared_skill_runtime.py tests/test_install_target_modes.py`

## 8. Delivery Notes

- Land `learn` as a small explicit owner now so later slices can depend on a
  real command surface instead of future work.
- Keep managed-skill documentation aligned with actual repo contents so packaged
  installs and top-level docs do not drift.

## 9. Execution Review Outcome

- Outcome: ready for closure
- Review finding classification:
  - no blocking brief-to-implementation gaps found
  - no blocking intent-to-brief gaps found
- Validation evidence:
  - `pytest -q skills/learn/tests/test_learn.py tests/test_sync_shared_skill_runtime.py tests/test_install_target_modes.py`
