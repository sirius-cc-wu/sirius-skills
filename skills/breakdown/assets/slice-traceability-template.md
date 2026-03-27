# Slice Traceability

Use this file to map repo story IDs to execution slices without moving story ownership into the tracker.

## Conventions

- Keep repo story IDs exactly as they appear in `user-stories.md`.
- Use one primary row per repo story.
- List increment IDs as a comma-separated list when a story spans multiple increments.
- List multiple slice IDs as a comma-separated list.
- Record only real execution blockers in `Blocked By`.
- Leave `Slice IDs` blank until `slice` bootstraps execution slices.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Slice IDs | Slice Slices | Blocked By | Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AUTH-03 | L | Refresh token support | I1 | slice-a1b2c3, slice-d4e5f6 | API, Tests | slice-d4e5f6 -> slice-a1b2c3 | slice-a1b2c3, slice-d4e5f6 | Split into API and tests |
| <story-id> | <S/M/L/XL> | <short summary> | <I1[, I2...]> | <slice-id[, slice-id...]> | <slice[, slice...]> | <blocker relation or blank> | <slice-id[, slice-id...] or blank> | <notes> |

## Notes

- `Blocked By` should use execution-slice relationships, not story relationships.
- `Increments` records planning-level grouping only; do not treat it as a tracker state.
- If a story maps 1:1 to one tracker slice, the same ID may later appear in `Slice IDs` after `slice` runs.
- If a story fans out into multiple executable slices, keep the fan-out here instead of inventing story-state in the tracker.
