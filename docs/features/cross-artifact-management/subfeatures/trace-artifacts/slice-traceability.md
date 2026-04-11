# Slice Traceability

## Conventions

- Keep parent story IDs stable from `docs/features/cross-artifact-management/user-stories.md`.
- Use planned slice IDs before execution bootstrap and preserve them when
  possible.
- Leave `Execution Slice IDs` blank until `slice` bootstraps the actual
  execution slice.
- Keep lineage planning local to `trace-artifacts/`; do not move the parent
  feature backlog into this child folder.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CAM-02 | L | Trace lineage across proposals, features, subfeatures, planned slices, and execution slices | I1 | CAM-02-trace-artifact-lineage | Shared inventory reuse, traceability parser, lineage graph, skill/docs/tests |  | CAM-02-trace-artifact-lineage | One cohesive slice that builds the reusable lineage model for later reporting |

## Notes

- `Blocked By` should list real execution blockers only.
- `Planned Slice IDs` names the execution-ready work item before slice bootstrap.
- `Execution Slice IDs` is filled after `slice` creates the durable execution
  slice under `slices/`.
