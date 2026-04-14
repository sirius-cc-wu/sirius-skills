# System Design: Multi Slice Execution

## Design summary

`multi-slice-execution` adds a batch-style execution capability above the
existing one-slice execution workflow. The new capability accepts a reviewed and
committed feature or subfeature planning scope, resolves its planned slices and
dependencies, then drives the existing execution skills one slice at a time.

The design is intentionally conservative:

- keep `slice`, `guide-execution`, `review-execution`, `close-slice`, and
  `commit` as the owners of their current stages
- add one orchestrator that resolves the target scope, chooses the next ready
  planned slice, and stops after any blocking failure
- require a commit after each slice closes so one execution slice still maps to
  one durable Git checkpoint

## Goals and non-goals

### Goals

- Execute all planned slices for one feature or subfeature in dependency order.
- Support resume by reading durable planning and execution artifacts.
- Preserve one-slice-at-a-time execution semantics and owner boundaries.
- Enforce one separate commit per completed slice.

### Non-goals

- Run multiple slices in parallel.
- Replace the existing single-slice entrypoints.
- Add batch-specific lifecycle states to planning or execution registries.
- Auto-open PRs or merge branches as part of the first version.

## Architecture

### 1. Planning-scope resolver

The new capability should first resolve exactly one planning scope:

- canonical feature folder under `docs/features/<feature>/`
- or durable subfeature folder under
  `docs/features/<feature>/subfeatures/<subfeature>/`

The resolver should use the same planning metadata and scope rules already used
elsewhere in `sirius-skills`. It must reject ambiguous or unapproved planning
targets instead of guessing.

The planning-scope resolver should confirm:

- the target packet is `planning_reviewed` or `slice_ready`
- the planning artifacts were explicitly approved and committed
- the packet has planned slices in `slice-planning.md` and
  `slice-traceability.md`

### 2. Planned-slice backlog resolver

Once the scope is resolved, the orchestrator needs a durable view of "what work
remains." The source of truth should stay in planning artifacts plus execution
state:

- planned slice IDs and declared dependencies from `slice-planning.md`
- planned-to-execution lineage from `slice-traceability.md`
- execution slice closure state from `slices/registry.json` and `.slice-meta.json`

The resolver should derive three sets:

1. all planned slices for the target scope
2. slices already completed because their mapped execution slices are closed
3. ready-next slices whose dependencies are already completed

The orchestrator should stop if no ready-next slice exists while uncompleted
planned slices remain, because that indicates inconsistent planning or execution
state.

### 3. Sequential execution orchestrator

The new user-facing capability should be a dedicated skill, tentatively
`execute-all-slices`, that loops over the ready-next planned slice set:

1. bootstrap the next planned slice through `slice`
2. continue execution through `guide-execution`
3. require review through `review-execution`
4. close the slice through `close-slice`
5. create a commit through `commit`
6. re-evaluate the remaining planned slices

The orchestrator should never hold more than one active slice at a time. It
should refuse to move on while the current slice is still open or the worktree
is not clean after the per-slice commit.

### 4. Per-slice commit checkpoint

The commit boundary should occur after slice closure so each commit can include:

- code and tests for the slice
- any slice-scoped artifact updates created during execution and review
- the closure metadata for that slice

This keeps each commit aligned with one fully completed execution slice and
prevents later commits from retroactively absorbing prior closure metadata.

The orchestrator should treat commit failure as a hard stop. It should not
continue to the next slice until the current slice has a durable commit
checkpoint.

### 5. Stop and resume semantics

The orchestrator should stop on:

- no approved planning scope
- no ready-next slice when unfinished planned slices remain
- any execution, review, closure, or commit failure
- any request for clarification from an owning skill

Resume should not need a new progress file. A later run can recompute progress
from:

- closed execution slices already mapped to the target planned slices
- the active slice, if one exists
- remaining unfulfilled dependencies in planning artifacts

## Interfaces and dependencies

- **New skill**: `skills/execute-all-slices/`
  - resolves feature/subfeature planning scope
  - computes remaining planned slices
  - drives the sequential execution loop

- **Existing execution owners**
  - `skills/slice/`
  - `skills/guide-execution/`
  - `skills/review-execution/`
  - `skills/close-slice/`
  - `skills/commit/`

- **Planning lineage inputs**
  - `slice-planning.md`
  - `slice-traceability.md`
  - planning metadata for the target feature/subfeature

The new skill should reuse existing helper scripts where possible instead of
copying readiness logic into a second state machine.

## Data flow, state, and lifecycle

1. Resolve one approved feature or subfeature scope.
2. Read planned slices and dependencies from durable planning artifacts.
3. Determine the next ready planned slice from planning plus execution closure
   state.
4. Execute that slice through existing execution owners.
5. Commit the closed slice.
6. Repeat until all planned slices for the target scope are complete.

The first version should avoid adding any new persistent lifecycle state.
Completion is inferred from existing planning and execution records.

## Failure handling and operational constraints

- Do not skip a failed slice and continue to later slices.
- Do not create more than one active slice for the same target scope.
- Do not treat unstaged or unrelated changes as part of the current slice
  checkpoint.
- If a slice exposes new planning gaps, stop and send the work back through the
  normal planning review path instead of improvising new batch semantics.

## Risks, assumptions, and open questions

- Some repositories may need explicit rules for what counts as "planning was
  committed"; the first version may need a conservative approximation such as a
  clean worktree before starting.
- Planned-slice dependency parsing should stay aligned with the durable planning
  templates so it does not drift from `breakdown`.
- Future work may want reporting or dashboard views of batch progress, but that
  should build on the same durable state rather than adding batch-only metadata.

## Validation strategy

- Add unit tests for:
  - feature vs subfeature scope resolution
  - ready-next slice selection from planned dependencies and closed slices
  - stop-on-failure behavior for execution, closure, or commit steps
  - resume behavior after some planned slices are already closed
- Validate targeted workflow behavior with:
  - `pytest -q skills/execute-all-slices/tests/test_execute_all_slices.py`
  - targeted existing execution tests for any touched helpers

## Summary

`multi-slice-execution` should add one orchestration layer above the current
execution workflow, not a new execution state model. It uses existing planning
and execution artifacts as durable truth, executes one slice at a time, and
keeps Git history aligned with slice boundaries by requiring one commit per
completed slice.
