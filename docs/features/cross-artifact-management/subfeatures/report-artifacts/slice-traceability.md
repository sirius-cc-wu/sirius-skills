# Slice Traceability

## Conventions

- Keep parent story IDs stable from `docs/features/cross-artifact-management/user-stories.md`.
- Preserve planned slice IDs when execution bootstraps the durable slice.
- Leave `Execution Slice IDs` blank until `slice` creates the execution slice.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CAM-03 | M | Report active, reviewed, stale, and closed workflow artifacts | I1 | rpt-artifact-state-report | Shared reporting records, grouped summaries, stale classification, skill/docs/tests |  | rpt-artifact-state-report | One read-only slice that turns durable metadata into operational views |

## Notes

- `Planned Slice IDs` names the execution-ready work item before bootstrap.
- `Execution Slice IDs` is filled after `slice` creates the durable execution
  slice under `slices/`.
