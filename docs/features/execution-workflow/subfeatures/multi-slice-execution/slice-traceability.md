# Slice Traceability

## Conventions

- Use stable story IDs from `docs/features/execution-workflow/user-stories.md`.
- Use planned slice IDs from this subfeature's `slice-planning.md`.
- Leave `Execution Slice IDs` blank until actual slice bootstrap occurs.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Resolve one planning scope into one ordered execution backlog | I1 | EW-MSE-01-scope-and-backlog-resolution | Scope resolution, planned-slice backlog selection |  |  | Establishes durable scope and ready-next resolution before any batch bootstrap |
| EW-01 | M | Resolve one planning scope into one ordered execution backlog | I2 | EW-MSE-02-sequential-slice-orchestration | One-slice-at-a-time bootstrap, execution-owner handoff | EW-MSE-01-scope-and-backlog-resolution |  | Extends slice bootstrap from one explicit work item to one ordered backlog |
| EW-03 | L | Stop safely on blockers and resume from durable slice state | I2 | EW-MSE-03-stop-and-resume-semantics | Stop conditions, resume semantics, dependency-aware traversal | EW-MSE-02-sequential-slice-orchestration |  | Keeps batch progress grounded in closed-slice and planned-slice state |
| EW-04 | L | Close and commit each completed slice before moving on | I3 | EW-MSE-04-per-slice-commit-checkpoints | Closure-to-commit checkpoint enforcement | EW-MSE-03-stop-and-resume-semantics |  | Keeps Git history aligned with slice boundaries |

## Notes

- `Blocked By` shows execution-slice sequencing rather than story ownership.
- These mappings are intended to seed later slice bootstrap and backlog refinement work.
