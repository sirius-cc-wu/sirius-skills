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
- Add additional rows when one story fans out into multiple planned slices and
  execution bootstrap needs one planned slice per row.
- List increment IDs as a comma-separated list when a story spans multiple
  increments.
- List multiple slice IDs as a comma-separated list.
- Record only real execution blockers in `Blocked By`.
- Leave `Execution Slice IDs` blank until `slice` bootstraps execution slices.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CAM-06 | L | Record durable implementation metrics and workflow evidence for completed features and subfeatures | I1 | CAM-06-metrics-foundation | Metrics schema and sidecar storage, artifact-derived evidence engine |  | CAM-06-metrics-foundation | Foundation slice for the reusable evidence model and deterministic sidecar persistence |
| CAM-06 | L | Record durable implementation metrics and workflow evidence for completed features and subfeatures | I2 | CAM-06-metrics-consumers | Skill CLI, reporting integration | CAM-06-metrics-foundation |  | Consumer slice depends on the foundation interfaces and keeps archive-facing display out of the initial rollout |

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
- When batch bootstrap tooling is expected to record execution slice IDs back
  into this file, use one planned slice per row so the mapping stays
  deterministic.
