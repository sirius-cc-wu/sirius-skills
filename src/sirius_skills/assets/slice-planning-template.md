# Slice Planning

Use this file to decompose repo stories into execution-ready slices before bootstrapping execution slices.

## Slice ID Naming

- Default naming: `<scope-prefix>-<capability-slug>`
- Use a short lowercase alias derived from the owning feature slug for
  feature-scoped breakdown.
- Use a short lowercase alias derived from the owning subfeature ID for
  subfeature-scoped breakdown.
- Avoid meaningless generic prefixes such as bare `slice-*` unless a
  repository-specific convention explicitly requires them.

## 1. Planning Scope

- Feature:
- Planning sources:
  - `discover.md`
  - `system-design.md`
  - `ui-design.md` (if applicable)
  - `user-stories.md`
- Execution system: repository-managed slices
- Execution mode: `single-agent` | `multi-agent`
- Notes:

## 2. Story Decisions

| Story ID | Story Size | Story Risk | Decision | Reason | Output Slice Count |
| --- | --- | --- | --- | --- | --- |
| AUTH-03 | L | medium | split | Separate API and tests for cleaner verification and lower handoff risk | 2 |
| <story-id> | <S/M/L/XL> | <low|medium|high> | <keep|split|defer> | <reason> | <n> |

Decision rules:

- `keep` means the story is already small enough to map to one executable slice.
- `split` means the story fans out into multiple execution-ready slices.
- `defer` means the story is not ready and should not be executed yet.
- split any `XL` story before slice bootstrap
- `S`/`M`/`L` stories may also split when risk, validation shape, coupling, or handoff complexity would make one packet brittle
- record the main reason for the decision, not just the size label

Risk rubric:

- `low`: one cohesive packet with one clear validation path
- `medium`: some coupling, multiple touchpoints, or moderate sequencing/handoff risk
- `high`: cross-subsystem impact, migration/reconciliation, compatibility risk, or materially different validation paths

## 3. Increment Plan

Use increments to group related slices into small, demonstrable outcomes. Increment 1 should usually be the simplest end-to-end usable path.

| Increment | Goal / User-Visible Value | Included Story IDs | Planned Slice IDs | Demo / Verification Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | First usable refresh flow | AUTH-03 | auth-api, auth-tests | User can refresh a token successfully in an end-to-end test run | Simplest end-to-end path |
| I2 | Operational hardening for refresh flow | AUTH-03 | auth-rate-limit | Refresh path enforces retry or abuse limits | Optional follow-on increment |
| <I1/I2/...> | <small demonstrable outcome> | <story-id[, ...]> | <slice-id[, ...]> | <demo, test command, or artifact check> | <ordering, scope, or risk note> |

Rules:

- keep increments feature-scoped planning artifacts, not execution slices
- each increment should be demonstrable without requiring the full project to be complete
- an increment can include one or many execution-ready slices
- planned slices and execution slices remain slice-scoped even when they belong to the same increment

## 4. Execution Slice Backlog

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| auth-api | AUTH-03 | Implement refresh token endpoint | Add refresh endpoint and token rotation logic | `auth/api` | primary | `pytest tests/auth/test_refresh.py` | create slice |  | yes |
| auth-tests | AUTH-03 | Add refresh token integration tests | Cover refresh flow end-to-end | `tests/auth` | primary | `pytest tests/auth/test_refresh.py` | create slice | auth-api | yes |
| <slice-id> | <story-id> | <slice title> | <short summary> | <module/path> | <lane name or primary> | <command or manual check> | <create slice | defer> | <slice-id[, ...] or blank> | <yes|no> |

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

- This file is feature-scoped planning, not slice-scoped execution.
- Keep increment definitions here, not in execution-slice artifacts.
- Once planned slices are created, record the actual slice IDs in `slice-traceability.md`.
- Keep slice IDs stable enough that they can be cross-referenced from traceability notes and planning discussion.
