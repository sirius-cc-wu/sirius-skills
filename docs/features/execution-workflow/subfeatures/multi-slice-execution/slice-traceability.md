# Slice Traceability

## Conventions

- Use stable story IDs from `docs/features/execution-workflow/user-stories.md`.
- Use planned slice IDs from this subfeature's `slice-planning.md`.
- Leave `Execution Slice IDs` blank until actual slice bootstrap occurs.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Resolve one planning scope into one ordered execution backlog | I1 | mse-scope-and-backlog-resolution | Scope resolution, planned-slice backlog selection |  | mse-scope-and-backlog-resolution | Establishes durable scope and ready-next resolution before any batch bootstrap |
| EW-01 | M | Resolve one planning scope into one ordered execution backlog | I2 | mse-sequential-slice-orchestration | One-slice-at-a-time bootstrap, execution-owner handoff | mse-scope-and-backlog-resolution | mse-sequential-slice-orchestration | Extends slice bootstrap from one explicit work item to one ordered backlog |
| EW-03 | L | Stop safely on blockers and resume from durable slice state | I2 | mse-stop-and-resume-semantics | Stop conditions, resume semantics, dependency-aware traversal | mse-sequential-slice-orchestration | mse-stop-and-resume-semantics | Keeps batch progress grounded in closed-slice and planned-slice state |
| EW-04 | L | Close and commit each completed slice before moving on | I3 | mse-per-slice-commit-checkpoints | Closure-to-commit checkpoint enforcement | mse-stop-and-resume-semantics | mse-per-slice-commit-checkpoints | Keeps Git history aligned with slice boundaries |

## Notes

- `Blocked By` shows execution-slice sequencing rather than story ownership.
- These mappings now record the closed execution slices that correspond to the implemented backlog.
