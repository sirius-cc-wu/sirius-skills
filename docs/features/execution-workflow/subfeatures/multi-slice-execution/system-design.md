# System Design: Multi Slice Execution

## Design summary

`multi-slice-execution` adds a batch-style execution capability above the
existing one-slice execution workflow. The new capability accepts a reviewed or
implemented feature or subfeature planning scope, resolves its planned slices
and dependencies, then bootstraps or resumes one mapped execution slice at a
time while handing work back to the existing execution owners.

The design is intentionally conservative:

- keep `slice`, `guide-execution`, `review-execution`, `close-slice`, and
  `commit` as the owners of their current stages
- add one orchestrator that resolves the target scope, chooses the next ready
  planned slice, and stops at active-slice, dependency, or clean-worktree
  checkpoints
- require a clean worktree before advancing past a completed slice so one
  execution slice still maps to one durable Git checkpoint

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

- the target packet is `planning_reviewed`, `slice_ready`, or `implemented`
- the target is explicitly approved in durable planning metadata
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
`ship`, that operates conservatively over the ready-next planned
slice set:

1. bootstrap the next planned slice through the execution owner helper when no
   mapped slice is already active
2. record the execution-slice lineage back into `slice-traceability.md`
3. hand the active slice back to `guide-execution` and the existing downstream
   owners
4. refuse to bootstrap a later slice while the current slice is still active or
   the worktree is dirty after a completed slice
5. re-evaluate the remaining planned slices on the next invocation

The first version does not directly run `review-execution`, `close-slice`, or
`commit`. It enforces the checkpoints around those owners and resumes once
durable repository state shows that the prior slice has progressed.

The orchestrator should never hold more than one active slice at a time. It
should refuse to move on while the current slice is still open or the worktree
is not clean after the per-slice checkpoint.

### 4. Per-slice commit checkpoint

The commit boundary should occur after slice closure so each commit can include:

- code and tests for the slice
- any slice-scoped artifact updates created during execution and review
- the closure metadata for that slice

This keeps each commit aligned with one fully completed execution slice and
prevents later commits from retroactively absorbing prior closure metadata.

The implemented first version uses a clean-worktree check as the conservative
checkpoint before continuing. When a completed slice still leaves uncommitted
changes, the orchestrator should hand control back to `commit` and stop. It
does not inspect Git history directly to prove that a new commit was created.

### 5. Stop and resume semantics

The orchestrator should stop on:

- no approved planning scope
- no ready-next slice when unfinished planned slices remain
- an already-active mapped execution slice that still needs owner-driven work
- unresolved dependency blocks between planned slices
- a dirty worktree after a completed mapped slice

Resume should not need a new progress file. A later run can recompute progress
from:

- closed execution slices already mapped to the target planned slices
- the active slice, if one exists
- remaining unfulfilled dependencies in planning artifacts

## Interfaces and dependencies

- **New skill**: `skills/ship/`
  - resolves feature/subfeature planning scope
  - computes remaining planned slices
  - bootstraps the next ready slice or resumes the active mapped slice
  - hands execution back to existing owners between invocations

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
4. Bootstrap or resume one mapped slice and hand off to existing execution
   owners.
5. Re-evaluate the backlog after durable closure state and a clean worktree
   checkpoint exist.
6. Repeat across later invocations until all planned slices for the target scope
   are complete.

The first version should avoid adding any new persistent lifecycle state.
Completion is inferred from existing planning and execution records.

## Failure handling and operational constraints

- Do not skip an active or blocked slice and continue to later slices.
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
  - stop behavior for active slices, blocked backlogs, and dirty-worktree
    checkpoints
  - resume behavior after some planned slices are already closed
- Validate targeted workflow behavior with:
  - `pytest -q skills/ship/tests/test_ship.py`
  - targeted existing execution tests for any touched helpers

## Summary

`multi-slice-execution` should add one orchestration layer above the current
execution workflow, not a new execution state model. It uses existing planning
and execution artifacts as durable truth, executes one slice at a time, and
keeps Git history aligned with slice boundaries by requiring one commit per
completed slice.

<!-- archived-slice-summaries:start -->
## Archived Slice Summaries

<!-- archived-slice-summary:mse-per-slice-commit-checkpoints:start -->
### `mse-per-slice-commit-checkpoints`: Enforce one commit per completed slice

#### Work Item Summary

- **Work Item**: Require a clean commit checkpoint after each closed slice before the batch loop advances.
- **Source Story / Increment / Slice**: `EW-04` / `I3` / `mse-per-slice-commit-checkpoints`
- **Requested Outcome**: As a maintainer, I want every completed slice in a batch run to become its own Git checkpoint so the history remains aligned with slice boundaries.
- **Why this matters**: Batch execution should preserve the same durable closure and commit discipline expected from one-slice-at-a-time work.
- **Independent Test**: `pytest -q skills/ship/tests/test_ship.py -k commit_checkpoint`

#### Detailed Design Summary

`mse-per-slice-commit-checkpoints` integrated a commit checkpoint into the `ship` loop. After each slice closes, the orchestrator requires a clean worktree checkpoint before it can advance to the next ready slice, handing control to `commit` when the repository is still dirty and keeping repository history aligned with slice boundaries.
<!-- archived-slice-summary:mse-per-slice-commit-checkpoints:end -->

<!-- archived-slice-summary:mse-scope-and-backlog-resolution:start -->
### `mse-scope-and-backlog-resolution`: Resolve planning scope and remaining planned slices

#### Work Item Summary

- **Work Item**: Resolve one reviewed feature or subfeature target into one ordered remaining-slice backlog.
- **Source Story / Increment / Slice**: `EW-01` / `I1` / `mse-scope-and-backlog-resolution`
- **Requested Outcome**: As a maintainer, I want `ship` to identify the active planning scope and the next ready planned slice so batch execution starts from durable repository state instead of ad hoc input.
- **Why this matters**: Later orchestration depends on one canonical view of planned slices, closed execution slices, and feature vs subfeature scope.
- **Independent Test**: `pytest -q skills/ship/tests/test_ship.py -k scope_or_backlog`

#### Detailed Design Summary

`mse-scope-and-backlog-resolution` established the planning-target and backlog-resolution foundation for `ship`. The slice resolves one feature or subfeature target, reads its planned slice lineage, excludes already closed execution slices, and returns the next ready slice without mutating planning or execution state.
<!-- archived-slice-summary:mse-scope-and-backlog-resolution:end -->

<!-- archived-slice-summary:mse-sequential-slice-orchestration:start -->
### `mse-sequential-slice-orchestration`: Orchestrate sequential slice execution

#### Work Item Summary

- **Work Item**: Drive one planned slice at a time through slice bootstrap and execution handoff.
- **Source Story / Increment / Slice**: `EW-01` / `I2` / `mse-sequential-slice-orchestration`
- **Requested Outcome**: As a maintainer, I want the batch executor to process one ready slice at a time so multi-slice execution stays aligned with existing execution owners.
- **Why this matters**: Batch execution should automate traversal, not absorb slice bootstrap, review, or closure ownership into a new state machine.
- **Independent Test**: `pytest -q skills/ship/tests/test_ship.py -k orchestration`

#### Detailed Design Summary

`mse-sequential-slice-orchestration` added the orchestration loop for `ship`. The slice reuses backlog resolution from `mse-scope-and-backlog-resolution`, bootstraps one ready slice at a time, routes execution through the existing execution owners, and preserves one-active-slice semantics across the run.
<!-- archived-slice-summary:mse-sequential-slice-orchestration:end -->

<!-- archived-slice-summary:mse-stop-and-resume-semantics:start -->
### `mse-stop-and-resume-semantics`: Stop on blockers and resume from durable state

#### Work Item Summary

- **Work Item**: Stop batch execution safely on blockers and resume from durable slice state.
- **Source Story / Increment / Slice**: `EW-03` / `I2` / `mse-stop-and-resume-semantics`
- **Requested Outcome**: As a maintainer, I want the batch executor to stop on active-slice or dependency blockers and resume later from closed-slice state instead of maintaining a second progress ledger.
- **Why this matters**: Multi-slice execution is only trustworthy if interruptions do not create hidden progress or skip blocked work.
- **Independent Test**: `pytest -q skills/ship/tests/test_ship.py -k stop_or_resume`

#### Detailed Design Summary

`mse-stop-and-resume-semantics` added safe stop conditions and durable resume behavior to `ship`. The slice stops the batch loop on active-slice or dependency-blocked conditions, then resumes later by recalculating progress from closed slices and planning lineage rather than any batch-local state file.
<!-- archived-slice-summary:mse-stop-and-resume-semantics:end -->

<!-- archived-slice-summaries:end -->
