# Task Traceability

Use this file to map repo story IDs to execution tasks without moving story ownership into the tracker.

## Conventions

- Keep repo story IDs exactly as they appear in `user-stories.md`.
- Use one primary row per repo story.
- List multiple `sb` task IDs as a comma-separated list.
- Record only real execution blockers in `Blocked By`.
- Leave `Track IDs` blank until `track` bootstraps execution tracks.

## Mapping Table

| Story ID | Story Size | Story Summary | sb Task IDs | Task Slices | Blocked By | Track IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AUTH-03 | L | Refresh token support | BNC-a1b2c3, BNC-d4e5f6 | API, Tests | BNC-d4e5f6 -> BNC-a1b2c3 | BNC-a1b2c3, BNC-d4e5f6 | Split into API and tests |
| <story-id> | <S/M/L/XL> | <short summary> | <sb-id[, sb-id...]> | <slice[, slice...]> | <sb blocker relation or blank> | <track-id[, track-id...] or blank> | <notes> |

## Notes

- `Blocked By` should use execution-task relationships, not story relationships.
- If a story maps 1:1 to one `sb` task, the same ID may later appear in `Track IDs` after `track` runs.
- If a story fans out into multiple executable tasks, keep the fan-out here instead of inventing story-state in `sb`.
