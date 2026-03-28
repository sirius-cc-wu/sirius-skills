# Slice Traceability

Use this file to map repo story IDs to execution slices without moving story ownership outside repository planning artifacts.

## Conventions

- Keep repo story IDs exactly as they appear in `user-stories.md`.
- Use one primary row per repo story.
- List increment IDs as a comma-separated list when a story spans multiple increments.
- List multiple slice IDs as a comma-separated list.
- Record only real execution blockers in `Blocked By`.
- Leave `Execution Slice IDs` blank until `slice` bootstraps execution slices.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AUTH-03 | L | Refresh token support | I1 | slice-a1b2c3, slice-d4e5f6 | API, Tests | slice-d4e5f6 -> slice-a1b2c3 | slice-a1b2c3, slice-d4e5f6 | Split into API and tests |
| <story-id> | <S/M/L/XL> | <short summary> | <I1[, I2...]> | <slice-id[, slice-id...]> | <area[, area...]> | <blocker relation or blank> | <slice-id[, slice-id...] or blank> | <notes> |

## Notes

- `Blocked By` should use execution-slice relationships, not story relationships.
- `Planned Slice IDs` records the planned identifiers before slice bootstrap.
- `Execution Slice IDs` records the actual bootstrapped slice IDs after `slice` runs.
- `Increments` records planning-level grouping only; do not treat it as an execution state.
- If a story fans out into multiple executable slices, keep the fan-out here instead of inventing story-state outside the planning artifacts.
