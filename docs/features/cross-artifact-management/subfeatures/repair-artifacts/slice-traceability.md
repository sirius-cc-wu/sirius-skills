# Slice Traceability

## Conventions

- Keep parent story IDs stable from `docs/features/cross-artifact-management/user-stories.md`.
- Preserve planned slice IDs when execution bootstraps the durable slice.
- Leave `Execution Slice IDs` blank until `slice` creates the execution slice.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CAM-04 | M | Repair registry and readme drift from durable artifact metadata | I1 | rpr-registry-drift-repair | Rebuilt rows, dry-run repair plans, apply mode, skill/docs/tests |  | rpr-registry-drift-repair | One conservative slice focused on active registry regeneration |

## Notes

- `Planned Slice IDs` names the execution-ready work item before bootstrap.
- `Execution Slice IDs` is filled after `slice` creates the durable execution
  slice under `slices/`.
