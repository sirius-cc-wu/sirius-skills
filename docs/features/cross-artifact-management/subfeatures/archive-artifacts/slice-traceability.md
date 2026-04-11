# Slice Traceability

## Conventions

- Keep parent story IDs stable from `docs/features/cross-artifact-management/user-stories.md`.
- Preserve planned slice IDs when execution bootstraps the durable slice.
- Leave `Execution Slice IDs` blank until `slice` creates the execution slice.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CAM-05 | M | Report archive candidates and archive one closed slice safely | I1 | CAM-05-safe-slice-archival | Candidate discovery, explicit slice archival, skill/docs/tests |  | CAM-05-safe-slice-archival | One conservative slice that adds safe archival without broad cleanup side effects |

## Notes

- `Planned Slice IDs` names the execution-ready work item before bootstrap.
- `Execution Slice IDs` is filled after `slice` creates the durable execution
  slice under `slices/`.
