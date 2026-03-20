# Task Planning

Use this file to decompose repo stories into execution-ready slices before bootstrapping spec tracks.

## 1. Planning Scope

- Project:
- Planning sources:
  - `discover.md`
  - `system-design.md`
  - `ui-design.md` (if applicable)
  - `user-stories.md`
- Execution tracker: `sb-tracker` | other
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

## 3. Execution Task Backlog

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Tracker Action | Depends On | Track Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AUTH-03-api | AUTH-03 | Implement refresh token endpoint | Add refresh endpoint and token rotation logic | `auth/api` | primary | `pytest tests/auth/test_refresh.py` | `sb add` |  | yes |
| AUTH-03-tests | AUTH-03 | Add refresh token integration tests | Cover refresh flow end-to-end | `tests/auth` | primary | `pytest tests/auth/test_refresh.py` | `sb add` | AUTH-03-api | yes |
| <slice-id> | <story-id> | <task title> | <short summary> | <module/path> | <lane name or primary> | <command or manual check> | <sb add | sb add --id ... | defer> | <slice-id[, ...] or blank> | <yes|no> |

## 4. Dependency Notes

- Critical path:
- Explicit blockers:
- Parallel-safe slices:
- Lane owners and handoffs:
- Integration checkpoints:

## 5. Bootstrap Order

1.
2.
3.

## 6. Open Questions / Stop-and-Ask Items

- Question 1:
- Question 2:

## Notes

- This file is project-scoped planning, not track-scoped execution.
- Once tracker tasks are created, record the actual `sb` IDs in `task-traceability.md`.
- Keep slice IDs stable enough that they can be cross-referenced from traceability notes and planning discussion.
