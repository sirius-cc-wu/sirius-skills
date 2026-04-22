# Implementation Plan: Add shared accelerator runtime support

**Slice**: `taw-runtime-foundation`  
**Date**: 2026-04-22  
**Status**: Execution Ready  
**Spec**: `brief.md`

## 1. Summary

`taw-runtime-foundation` establishes the shared supplemental runtime layer for
future accelerator skills. The slice introduces `lib/workflow_runtime/`,
extends packaged runtime syncing so consuming skills can ship that runtime, and
adds the baseline tests needed to keep the new runtime explicit and
self-contained.

## 2. Technical Context

- Current system context:
  - `lib/workflow_state/` already provides shared durable workflow-state logic
    for planning and execution truth
  - `scripts/sync_shared_skill_runtime.py` currently syncs only
    `lib/workflow_state/` plus one report-artifacts helper file
  - packaged install tests currently assert the managed skill list and shared
    runtime sync command surface
- Target modules / files:
  - new `lib/workflow_runtime/`
  - `scripts/sync_shared_skill_runtime.py`
  - `tests/test_sync_shared_skill_runtime.py`
  - `tests/test_install_target_modes.py`
  - likely consuming skills that will need packaged runtime copies next
- Constraints:
  - keep runtime support supplemental to repo planning and execution artifacts
  - avoid blending `workflow_runtime` into `workflow_state`
  - prefer typed helpers over ad hoc JSON/file handling in future accelerators

## 3. Gate Outcomes

- **Architecture / Constraints**: pass
  - the slice preserves the existing `workflow_state` ownership boundary and
    adds a separate runtime package for supplemental state
- **Risk / Compliance**: pass
  - no new external service or credential surface is introduced
  - the main risk is packaged install drift, which this slice addresses with
    sync-script and test updates
- **Testability**: pass
  - the slice can be validated through runtime sync tests plus packaging-surface
    verification

## 4. Requirement Traceability

| Requirement | Implementation Steps | Validation |
| --- | --- | --- |
| FR-001 | S001, S002 | V001 |
| FR-002 | S001, S003 | V001, V002 |
| FR-003 | S003, S004 | V001, V002 |
| FR-004 | S001, S002 | V001 |

## 5. Execution Plan

### Packet P01: Create the shared runtime package

- Scope: add the new `workflow_runtime` package with the minimum helpers and
  export surface needed by later accelerator slices.
- Steps:
  - [x] **S001** Create `lib/workflow_runtime/__init__.py` and the first helper
    modules for locking, handoff serialization, checkpoints, event logs, and
    learnings I/O.
  - [x] **S002** Keep the helper interfaces typed and small so later
    accelerator skills can import them without embedding raw JSON/file logic.
- Validation:
  - [x] **V001** targeted runtime unit coverage for the new helper package

### Packet P02: Extend packaged shared runtime sync

- Scope: teach the shared runtime sync workflow to distribute
  `workflow_runtime` to consuming skill packages alongside `workflow_state`.
- Steps:
  - [x] **S003** Extend `scripts/sync_shared_skill_runtime.py` to track source
    and target trees for both `workflow_state` and `workflow_runtime`.
  - [x] **S004** Update sync-script tests and packaged install tests so
    packaged skill refreshes remain explicit and reproducible.
- Validation:
  - [x] **V002** `pytest -q tests/test_sync_shared_skill_runtime.py tests/test_install_target_modes.py`

## 6. Supporting Notes

- Future slices expected to consume this runtime first:
  - `learn`
  - `ship`
  - `ship-slice`
  - `autoplan`
- This slice should avoid prematurely wiring runtime imports into all future
  consuming skills unless the sync surface and package shape are already stable.
- If new consuming skill targets are added to the sync script in this slice,
  keep the list narrowly scoped to skills that will actually import the runtime
  in the next slices.

## 7. Validation Plan

- baseline validation:
  - [x] `pytest -q tests/test_sync_shared_skill_runtime.py`
  - [x] `pytest -q tests/test_install_target_modes.py`
- targeted regression check:
  - [x] `pytest -q skills/ship/tests/test_ship.py -k runtime`

## 8. Delivery Notes

- Land the shared runtime package before any slice that depends on it for
  learnings, checkpoints, or handoff serialization.
- Preserve the explicit design boundary: runtime files may support later resume
  or acceleration, but they must not become the source of truth for workflow
  state.

## 9. Execution Review Outcome

- Outcome: ready for closure
- Review finding classification:
  - no blocking brief-to-implementation gaps found
  - no blocking intent-to-brief gaps found
- Validation evidence:
  - `pytest -q tests/test_workflow_runtime.py tests/test_sync_shared_skill_runtime.py tests/test_install_target_modes.py skills/ship/tests/test_ship.py -k 'runtime or sync_shared_skill_runtime or install_target_modes'`
  - `pytest -q tests/test_install_target_modes.py skills/ship/tests/test_ship.py -k runtime`
