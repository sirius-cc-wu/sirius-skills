# Task Traceability

Use this file to map repo story IDs to execution tasks without moving story ownership into the tracker.

## Conventions

- Keep repo story IDs exactly as they appear in `user-stories.md`.
- Use one primary row per repo story.
- List increment IDs as a comma-separated list when a story spans multiple increments.
- List multiple task IDs as a comma-separated list.
- Record only real execution blockers in `Blocked By`.
- Leave `Track IDs` blank until `track` bootstraps execution tracks.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Task IDs | Task Slices | Blocked By | Track IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AUTH-03 | L | Refresh token support | I1 | task-a1b2c3, task-d4e5f6 | API, Tests | task-d4e5f6 -> task-a1b2c3 | task-a1b2c3, task-d4e5f6 | Split into API and tests |
| <story-id> | <S/M/L/XL> | <short summary> | <I1[, I2...]> | <task-id[, task-id...]> | <slice[, slice...]> | <blocker relation or blank> | <track-id[, track-id...] or blank> | <notes> |

## Notes

- `Blocked By` should use execution-task relationships, not story relationships.
- `Increments` records planning-level grouping only; do not treat it as a tracker state.
- If a story maps 1:1 to one tracker task, the same ID may later appear in `Track IDs` after `track` runs.
- If a story fans out into multiple executable tasks, keep the fan-out here instead of inventing story-state in the tracker.
