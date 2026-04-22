# Slice Planning

## 1. Planning Scope

- Feature: Multi slice execution
- Planning sources:
  - `discover.md`
  - `impact-analysis.md`
  - `system-design.md`
  - parent `docs/features/execution-workflow/user-stories.md`
- Execution system: repository-managed code changes and tests
- Execution mode: `single-agent`
- Notes:
  - This subfeature extends the execution workflow above the current one-slice
    entrypoints instead of replacing them.
  - The first execution slice should establish durable planning-scope and
    backlog resolution before adding the orchestration loop.

## 2. Story Decisions

| Story ID | Story Size | Story Risk | Decision | Reason | Output Slice Count |
| --- | --- | --- | --- | --- | --- |
| EW-01 | M | medium | split | The new capability changes how reviewed planning targets are selected and how slices are bootstrapped from that scope, so selection logic and orchestration should not land as one packet. | 2 |
| EW-03 | L | high | split | Sequential orchestration and stop/resume behavior are tightly coupled but still separable from commit checkpoint enforcement. | 2 |
| EW-04 | L | high | keep | Per-slice commit and closure boundaries form one cohesive execution checkpoint capability. | 1 |

## 3. Increment Plan

| Increment | Goal / User-Visible Value | Included Story IDs | Planned Slice IDs | Demo / Verification Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | A reviewed feature or subfeature can resolve its remaining planned slice backlog | EW-01 | mse-scope-and-backlog-resolution | The capability can target one planning scope, read its planned slices, and identify the next ready slice without executing work yet. | Establish the durable input model first |
| I2 | The workflow can execute the backlog one slice at a time and stop safely on blockers | EW-01, EW-03 | mse-sequential-slice-orchestration, mse-stop-and-resume-semantics | The orchestrator can bootstrap one ready slice at a time, stop on execution failures, and resume from durable state. | Depends on I1 |
| I3 | Each finished slice becomes its own durable Git checkpoint before the next slice starts | EW-04 | mse-per-slice-commit-checkpoints | A completed slice must close and commit before the next planned slice can begin. | Depends on I2 |

## 4. Execution Slice Backlog

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mse-scope-and-backlog-resolution | EW-01 | Resolve planning scope and remaining planned slices | Add scope resolution for feature/subfeature execution targets plus durable backlog derivation from planning traceability and closed execution slices. | new `skills/ship/`, shared planning-lineage helper(s), integration with existing planning/execution metadata | primary | `pytest -q skills/ship/tests/test_ship.py -k scope_or_backlog` | create slice |  | yes |
| mse-sequential-slice-orchestration | EW-01 | Orchestrate sequential slice execution | Drive `slice`, `guide-execution`, `review-execution`, and `close-slice` one planned slice at a time while keeping only one active slice. | `skills/ship/`, execution-owner integration points | primary | `pytest -q skills/ship/tests/test_ship.py -k orchestration` | create slice | mse-scope-and-backlog-resolution | yes |
| mse-stop-and-resume-semantics | EW-03 | Stop on blockers and resume from durable state | Detect active-slice, failed-step, and dependency-blocked conditions, then resume from closed-slice and planned-slice lineage without extra progress state. | `skills/ship/`, possible helper reuse from `guide-execution` and `trace-artifacts` | primary | `pytest -q skills/ship/tests/test_ship.py -k stop_or_resume` | create slice | mse-sequential-slice-orchestration | yes |
| mse-per-slice-commit-checkpoints | EW-04 | Enforce one commit per completed slice | Integrate the existing `commit` skill boundary into the orchestration loop so a slice must close and commit before the next slice begins. | `skills/ship/`, `skills/commit/`, closure/clean-worktree handoff points | primary | `pytest -q skills/ship/tests/test_ship.py -k commit_checkpoint` | create slice | mse-stop-and-resume-semantics | yes |

## 5. Dependency Notes

- Critical path: scope/backlog resolution -> sequential orchestration -> stop/resume semantics -> per-slice commit checkpoints.
- Explicit blockers:
  - `mse-sequential-slice-orchestration` should not start until planning-scope and ready-next-slice resolution are durable.
  - `mse-stop-and-resume-semantics` depends on the orchestration loop so resume uses the same state model as normal execution.
  - `mse-per-slice-commit-checkpoints` depends on closure-aware orchestration so commits are aligned with completed slices.
- Parallel-safe slices: none recommended; the batch capability shares one orchestrator and one state model.
- Increment ordering: I1 -> I2 -> I3.
- Lane owners and handoffs: the new orchestrator owns backlog traversal only; existing skills remain owners for slice bootstrap, execution routing, review, closure, and commit.
- Integration checkpoints:
  - verify that a feature/subfeature target with mixed closed and unstarted slices resolves the correct next slice
  - verify that failed execution or commit stops the run without advancing to later slices
  - verify that each completed slice leaves a clean checkpoint before the next one begins

## 6. Bootstrap Order

1. mse-scope-and-backlog-resolution
2. mse-sequential-slice-orchestration
3. mse-stop-and-resume-semantics
4. mse-per-slice-commit-checkpoints

## 7. Review Notes

- Review outcome: ready for `slice` after planning approval and commit.
- Blocking findings: none. The packet keeps the existing execution skills as the
  source of truth and limits the new work to planning-scope resolution,
  orchestration, and commit checkpoints.
- Handoff note: keep the new skill orchestration-only; do not absorb detailed
  brief, blueprint, review, or closure ownership into the batch loop.

## 8. Notes

- This breakdown stays subfeature-scoped; it does not replace the parent
  feature's generic one-slice execution model.
- The first version should prefer durable artifact inspection over a new progress
  database or batch-only registry fields.
