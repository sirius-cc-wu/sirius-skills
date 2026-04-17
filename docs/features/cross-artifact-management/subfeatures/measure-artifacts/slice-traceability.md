# Slice Traceability

Use this file to map repo story IDs to execution slices without moving story
ownership outside repository planning artifacts.

## Subfeature Context

- Parent feature: `cross-artifact-management`
- Subfeature ID: `measure-artifacts`
- Subfeature type: `additive`
- Use `Planned Slice IDs` for the new or amended slices defined by this
  subfeature.
- Keep subfeature-local traceability in this folder instead of folding it back
  into parent feature breakdown docs.
- Record superseded or narrowed parent slice IDs in `Notes`, not
  `Execution Slice IDs`.

## Conventions

- Keep repo story IDs exactly as they appear in `user-stories.md`.
- Use one primary row per repo story.
- List increment IDs as a comma-separated list when a story spans multiple
  increments.
- List multiple slice IDs as a comma-separated list.
- Record only real execution blockers in `Blocked By`.
- Leave `Execution Slice IDs` blank until `slice` bootstraps execution slices.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CAM-06 | L | Record durable implementation metrics and workflow evidence for completed features and subfeatures | I1, I2 | CAM-06-metrics-foundation, CAM-06-metrics-consumers | Metrics schema and sidecar storage, artifact-derived evidence engine, skill CLI, reporting integration | CAM-06-metrics-foundation -> CAM-06-metrics-consumers |  | Split because evidence derivation/storage and consumer integration have different validation paths and different failure surfaces |

## Notes

- `Blocked By` should use execution-slice relationships, not story
  relationships.
- `Planned Slice IDs` records the planned identifiers before slice bootstrap.
- `Execution Slice IDs` records the actual bootstrapped slice IDs after `slice`
  runs.
- `Increments` records planning-level grouping only; do not treat it as an
  execution state.
- If a story fans out into multiple executable slices, keep the fan-out here
  instead of inventing story-state outside the planning artifacts.
