# Slice Traceability

## Conventions

- Keep parent story IDs stable from `docs/features/cross-artifact-management/user-stories.md`.
- Use planned slice IDs before execution bootstrap and preserve them when
  possible.
- Leave `Execution Slice IDs` blank until `slice` bootstraps the actual
  execution slice.
- Keep subfeature planning local to `audit-artifacts/`; do not move the parent
  feature backlog into this child folder.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CAM-01 | L | Audit artifact health across proposals, features, subfeatures, and slices | I1 | CAM-01-cross-artifact-audit | Inventory helper, delegated validators, cross-artifact checks, skill/docs/tests |  | CAM-01-cross-artifact-audit | One cohesive slice that establishes the shared finding model for later subfeatures |

## Notes

- `Blocked By` should list real execution blockers only.
- `Planned Slice IDs` names the execution-ready work item before slice bootstrap.
- `Execution Slice IDs` is filled after `slice` creates the durable execution
  slice under `slices/`.
