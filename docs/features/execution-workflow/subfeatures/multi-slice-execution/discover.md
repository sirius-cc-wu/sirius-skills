# Discover: Multi Slice Execution

## Parent Feature

- Feature: `execution-workflow`
- Subfeature ID: `multi-slice-execution`
- Subfeature Type: `additive`

## Subfeature summary

Add one execution-layer capability that can take a reviewed and committed
feature or subfeature backlog, execute its planned slices in dependency order,
and require a separate commit checkpoint after each slice closes.

## Problem statement

The current execution workflow is intentionally centered on one execution slice
at a time:

- `slice` bootstraps one execution slice from one execution-ready work item.
- `guide-execution` routes work for one active slice.
- `review-execution` and `close-slice` operate on one slice at a time.
- `commit` validates and commits whatever changes are currently staged, but it
  is not integrated into a higher-level slice-sequencing loop.

That works well for single-slice execution, but maintainers sometimes want to
say "work through all slices for this feature or subfeature until the backlog is
done." Today that requires a lot of manual coordination:

- resolve the target feature or subfeature packet
- figure out which planned slice is next and whether dependencies are already
  satisfied
- bootstrap and execute exactly one slice
- remember to commit that slice separately before moving on
- stop and resume manually if one slice fails review or cannot close

Without a dedicated capability, execution can drift from the planned order, per
slice commit boundaries are easy to lose, and resumable progress depends on
operator discipline rather than durable workflow rules.

## Desired outcome

The repository should provide one execution-layer capability that:

- accepts a feature or subfeature planning scope
- resolves the planned slice backlog and dependency order from durable planning
  artifacts
- executes at most one slice at a time through the existing execution workflow
- requires a separate commit after each slice closes successfully
- stops cleanly on blockers and can resume from durable slice and planning state

## Goals

- Preserve the existing single-slice ownership boundaries of `slice`,
  `guide-execution`, `review-execution`, `close-slice`, and `commit`.
- Add a higher-level orchestration capability for "all slices in this planning
  scope" without inventing parallel lifecycle states.
- Support both canonical feature packets and durable subfeature packets.
- Enforce one commit boundary per completed slice so the resulting Git history
  stays aligned with slice boundaries.
- Make resume behavior depend on durable repo state such as planned-slice
  lineage and closed execution slices, not transient chat memory.

## Non-goals

- Replacing the existing one-slice execution workflow.
- Executing multiple slices concurrently.
- Skipping review, closure, or commit boundaries to optimize throughput.
- Inventing batch-only slice states in planning or execution registries.
- Auto-merging or publishing PRs for the resulting commit series.

## Scope boundaries

### In scope

- one new execution-layer skill or command for feature/subfeature-wide slice
  traversal
- planned-slice selection and dependency ordering from durable planning
  artifacts
- per-slice execution loop integration with existing execution skills
- per-slice commit checkpoint rules
- stop/resume semantics grounded in durable artifact state

### Out of scope

- changes to how individual slice authoring works inside `brief`, `blueprint`,
  `review-execution`, or `close-slice`
- project-specific branching or PR sequencing beyond what `commit` and
  `create-pr` already own
- bulk execution across unrelated planning scopes in one run

## Constraints and assumptions

- A target feature or subfeature must already be planning-reviewed, explicitly
  approved, and committed before batch execution starts.
- Each planned slice still maps to exactly one execution slice and one commit.
- Existing execution owners remain authoritative for their stages; the new
  capability is an orchestrator, not a replacement for those skills.
- The orchestrator should infer progress from closed slices and planned-slice
  lineage instead of introducing a separate progress database.

## Risks

- Scope resolution is easy to get wrong when both features and subfeatures are
  supported in one command.
- A weak dependency resolver could run slices out of order or ignore blockers
  recorded in planning artifacts.
- If the per-slice commit checkpoint is placed at the wrong boundary, the
  resulting history may split slice closure metadata from slice implementation.
- Resume behavior can become brittle if it depends on transient agent state
  instead of durable registries and traceability docs.

## Success criteria

- A maintainer can target one reviewed and committed feature or subfeature and
  have the tool execute its planned slices one by one.
- The workflow stops when a slice cannot complete review, closure, or commit,
  rather than silently skipping ahead.
- Each completed slice produces its own commit.
- A later run can resume the remaining planned slices from durable repo state.

## Recommended next step

Use this subfeature packet to define the planning-scope resolver, sequential
execution loop, and per-slice commit checkpoint before adding a new user-facing
skill.
