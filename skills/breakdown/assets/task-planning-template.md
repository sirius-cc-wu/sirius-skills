# Task Planning

Use this file to decompose repo stories into execution-ready slices before bootstrapping execution tracks.

## 1. Planning Scope

- Feature:
- Planning sources:
  - `discover.md`
  - `system-design.md`
  - `ui-design.md` (if applicable)
  - `user-stories.md`
- Execution tracker: <tracker name or none>
- Execution mode: `single-agent` | `multi-agent`
- Notes:

## 2. Story Decisions

| Story ID | Story Size | Decision | Reason | Output Task Count |
| --- | --- | --- | --- | --- |
| AUTH-03 | L | split | Separate API and tests for cleaner verification | 2 |
| <story-id> | <S/M/L/XL> | <keep|split|defer> | <reason> | <n> |

Decision rules:

- `keep` means the story is already small enough to map to one executable task.
- `split` means the story fans out into multiple execution-ready slices.
- `defer` means the story is not ready and should not create tracker work yet.

## 3. Increment Plan

Use increments to group related slices into small, demonstrable outcomes. Increment 1 should usually be the simplest end-to-end usable path.

| Increment | Goal / User-Visible Value | Included Story IDs | Planned Slice IDs | Demo / Verification Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | First usable refresh flow | AUTH-03 | AUTH-03-api, AUTH-03-tests | User can refresh a token successfully in an end-to-end test run | Simplest end-to-end path |
| I2 | Operational hardening for refresh flow | AUTH-03 | AUTH-03-rate-limit | Refresh path enforces retry or abuse limits | Optional follow-on increment |
| <I1/I2/...> | <small demonstrable outcome> | <story-id[, ...]> | <slice-id[, ...]> | <demo, test command, or artifact check> | <ordering, scope, or risk note> |

Rules:

- keep increments feature-scoped planning artifacts, not execution tracks
- each increment should be demonstrable without requiring the full project to be complete
- an increment can include one or many execution-ready slices
- tracker tasks and execution tracks remain task-scoped even when they belong to the same increment

## 4. Execution Task Backlog

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Tracker Action | Depends On | Track Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AUTH-03-api | AUTH-03 | Implement refresh token endpoint | Add refresh endpoint and token rotation logic | `auth/api` | primary | `pytest tests/auth/test_refresh.py` | create task |  | yes |
| AUTH-03-tests | AUTH-03 | Add refresh token integration tests | Cover refresh flow end-to-end | `tests/auth` | primary | `pytest tests/auth/test_refresh.py` | create task | AUTH-03-api | yes |
| <slice-id> | <story-id> | <task title> | <short summary> | <module/path> | <lane name or primary> | <command or manual check> | <create task | defer> | <slice-id[, ...] or blank> | <yes|no> |

## 5. Dependency Notes

- Critical path:
- Explicit blockers:
- Parallel-safe slices:
- Increment ordering:
- Lane owners and handoffs:
- Integration checkpoints:

## 6. Bootstrap Order

1.
2.
3.

## 7. Open Questions / Stop-and-Ask Items

- Question 1:
- Question 2:

## Notes

- This file is feature-scoped planning, not track-scoped execution.
- Keep increment definitions here, not in execution-track artifacts.
- Once tracker tasks are created, record the actual task IDs in `task-traceability.md`.
- Keep slice IDs stable enough that they can be cross-referenced from traceability notes and planning discussion.
