# Slice Specification: Add shared accelerator runtime support

**Slice**: `taw-runtime-foundation`  
**Created**: 2026-04-22  
**Status**: Draft  
**Input**: `taw-runtime-foundation`

## 1. Work Item Summary

- **Work Item**: Add the shared supplemental runtime package that later
  accelerator skills can reuse for checkpoints, event logs, learnings storage,
  and packaged runtime sync.
- **Source Story / Increment / Slice**: `TAW-03` / `I1` /
  `taw-runtime-foundation`
- **Requested Outcome**: As a maintainer working across long sessions, I want
  accelerator runtime support to persist checkpoints, events, and learnings in
  one reusable package so later `autoplan`, `ship`, `ship-slice`, and `learn`
  work does not invent ad hoc state handling.
- **Why this matters**: The throughput design depends on supplemental runtime
  support that is explicit, inspectable, packageable, and subordinate to repo
  planning and execution artifacts.
- **Independent Test**: `pytest -q tests/test_install_target_modes.py skills/ship/tests/test_ship.py -k runtime`

## 2. Acceptance Scenarios

1. **Given** accelerator skills need shared support for checkpoints, event logs,
   handoff payloads, or learnings, **When** they import the new runtime package,
   **Then** they reuse one shared typed helper layer instead of duplicating JSON
   file handling in each skill.
2. **Given** packaged installs depend on shared runtime sync, **When** the new
   runtime package is introduced, **Then** the packaging workflow includes the
   runtime for every consuming skill that needs it.
3. **Given** runtime files drift from repo planning or execution artifacts,
   **When** later accelerators reconcile state, **Then** runtime helpers allow
   repo artifacts to remain the source of truth instead of overwriting them.

## 3. Functional Requirements

- **FR-001**: The repository MUST add a shared `workflow_runtime` support
  package for accelerator-oriented checkpoints, event logs, learnings, locking,
  and handoff serialization.
- **FR-002**: The shared runtime MUST remain supplemental and MUST NOT replace
  planning or execution artifacts as workflow truth.
- **FR-003**: The packaging workflow MUST sync the shared runtime into any
  consuming managed skills so packaged installs remain self-contained.
- **FR-004**: The runtime support MUST provide typed helpers instead of leaving
  accelerators to hand-roll raw file I/O and JSON handling.

## 4. Key Entities

- **Workflow runtime package**: The shared code under `lib/workflow_runtime/`
  that owns runtime-oriented helpers for accelerator skills.
- **Runtime artifact**: A supplemental file such as a checkpoint, event log, or
  learnings store that supports resume or reuse but does not supersede repo
  truth.
- **Consuming skill**: A managed skill whose packaged install needs the shared
  runtime synced into its local `lib/` tree.

## 5. Edge Cases

- Some skills may consume only part of the runtime package at first.
- Packaged installs must stay valid even when repo-local shared runtime support
  grows.
- Runtime files may be missing, partially written, or stale compared with repo
  artifacts and still need safe reconciliation later.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: This slice establishes the reusable runtime foundation only; later
  slices own the concrete `learn`, `ship-slice`, and `autoplan` workflows.
- **A2**: Existing `workflow_state` ownership for planning and execution truth
  remains unchanged.

### Dependencies

- **D1**: `scripts/sync_shared_skill_runtime.py`
- **D2**: existing packaged install verification such as
  `tests/test_install_target_modes.py`
- **D3**: current `ship` behavior and tests remain available as a baseline for
  runtime-related extension points

## 7. Success Criteria

- **SC-001**: Accelerator-oriented runtime helpers exist in one shared package.
- **SC-002**: Managed packaging can include the shared runtime where needed.
- **SC-003**: The slice leaves a clear boundary that runtime state is
  supplemental to repo planning and execution artifacts.

## 8. Open Clarifications

- None.
