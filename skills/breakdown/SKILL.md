---
name: breakdown
description: Converts repo stories and planning docs into directly executable, dependency-aware work items with traceability and tracker handoff.
---

# Breakdown

Use this skill after project-level discovery and design to turn repo stories into directly executable work.

If you need a starting folder for a new project, scaffold the default breakdown files with:

```bash
python3 skills/breakdown/scripts/scaffold_breakdown.py <project-slug>
```

By default this creates:

```text
doc/specs/projects/<project-slug>/task-planning.md
doc/specs/projects/<project-slug>/task-traceability.md
```

## Responsibilities

1. Validate that stories are concrete, scoped, and ready for decomposition.
2. Split oversized work into smaller, independently verifiable execution packets.
3. Produce planning artifacts that preserve story-to-task traceability, sequencing, and execution mode assumptions.
4. Create executable tracker items, dependency links, and explicit parallel-safe lanes where appropriate.
5. Hand off ready work to `track` for spec-track bootstrap.

## Required Output

- `<project_path>/task-planning.md`
- `<project_path>/task-traceability.md`

Preferred tracker output when available:

- `sb` tasks and dependencies

Use `assets/task-planning-template.md` as the default starting point for `<project_path>/task-planning.md`.
Use `assets/task-traceability-template.md` as the default starting point for `<project_path>/task-traceability.md`.
Use `scripts/scaffold_breakdown.py` when you want both files scaffolded together from a project slug.

## Breakdown Rules

- Keep stories and design in repo docs; keep executable tasks in the tracker.
- Prefer repository story sizes such as `S`, `M`, `L`, and `XL`.
- Split any `XL` item before creating execution-ready tasks.
- Every executable task should be small enough to fit one task-scoped spec track.
- Prefer execution packets that stay within one subsystem or a small set of files.
- Every execution-ready slice should have concrete acceptance notes and a validation command or artifact check.
- Preserve stable story identifiers so task traceability is durable.

## Execution Mode and Packet Design

Default to `single-agent` execution when:

- work has a tight critical path
- task coupling is high and handoff risk is non-trivial
- codebase context is concentrated in one subsystem

Prefer `multi-agent` execution only when:

- there are clear parallel lanes with minimal overlap
- integration points can be validated with deterministic checks
- ownership and handoff boundaries can be documented explicitly

When a story becomes execution-ready:

- split it into small packets that can be executed without broad repo-wide context
- mark blockers and sequencing constraints explicitly
- label only genuinely independent slices as parallel-safe
- if using `multi-agent`, record lane ownership, handoff targets, and an integration checkpoint after each lane

## Tracker Guidance

When `sb-tracker` is available, use it as the default execution tracker:

- create one `sb` task per directly executable task
- use parent-child relationships when a larger story needs grouped subtasks
- record blockers with `sb dep`
- reflect safe parallel lanes and integration checkpoints in `task-planning.md`
- keep mapping from repo story IDs to `sb` task IDs in `task-traceability.md`

If another tracker is configured, keep the same boundary and map these concepts to the local tracker.

## Story-to-`sb` Mapping

Treat repo story IDs as the planning-system identifiers and `sb` task IDs as the execution identifiers.

Default mapping:

- one repo story can map to one or many `sb` tasks
- each execution-ready slice becomes one `sb` task
- preserve the repo story ID in:
  - `task-traceability.md`
  - the `sb` task description
- use `sb dep <child_id> <parent_id>` only for real execution blockers, not for narrative grouping

Preferred description shape for `sb add`:

```text
Story: <story-id>
Slice: <short slice name>
Acceptance:
- ...
Validation:
- ...
```

If one repo story splits into multiple executable tasks:

- keep the story as a repo concept in `user-stories.md`
- create multiple `sb` tasks for the slices
- optionally create a non-executable parent `sb` task only when it helps grouped review
- record the story-to-task fan-out in `task-traceability.md`

Only use `sb add --id <story-id>` when **all** of the following are true:

- the repo story maps to exactly one executable task
- the team wants the story ID preserved end-to-end
- that ID will not collide with another execution item

Otherwise, let `sb` generate the task ID and keep the repo story ID in traceability metadata.

## Recommended `sb` Command Pattern

Example for a story `AUTH-03` that splits into two executable tasks:

```bash
sb add "Implement refresh token endpoint" \
  --desc $'Story: AUTH-03\nSlice: API\nAcceptance:\n- POST /refresh rotates tokens\nValidation:\n- pytest tests/auth/test_refresh.py'

sb add "Add refresh token integration tests" \
  --desc $'Story: AUTH-03\nSlice: Tests\nAcceptance:\n- refresh flow covered end-to-end\nValidation:\n- pytest tests/auth/test_refresh.py'

sb dep <tests-task-id> <api-task-id>
```

In `task-traceability.md`, record the mapping explicitly, for example:

```text
| Story ID | Story Size | Story Summary | sb Task IDs | Task Slices | Blocked By | Track IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AUTH-03 | L | Refresh token support | BNC-a1b2c3, BNC-d4e5f6 | API, Tests | BNC-d4e5f6 -> BNC-a1b2c3 | BNC-a1b2c3, BNC-d4e5f6 | Split into API and tests |
```

## Workflow

1. Read `discover.md`, `system-design.md`, optional `ui-design.md`, and `user-stories.md`.
2. Validate that each story has scope, acceptance notes, and an explicit size.
3. Split oversized work into smaller execution packets and choose `single-agent` or `multi-agent` handling where relevant.
4. Write `task-planning.md` and `task-traceability.md` with dependency notes, parallel-safe lanes, and integration checkpoints as needed.
5. Create tracker tasks and dependency links for execution-ready work, keeping packet validation explicit.
6. Stop when each task is ready to be bootstrapped by `track`.

When generating `task-planning.md`, start from `assets/task-planning-template.md` and replace placeholders rather than inventing a new structure each time.
When generating `task-traceability.md`, start from `assets/task-traceability-template.md` and replace placeholders rather than inventing a new table shape each time.

## Guardrails

- Do not create execution tracks directly from vague stories.
- Do not mirror tracker execution states inside project planning docs.
- Do not turn `task-planning.md` into a task-scoped `tasks.md`; that belongs to `spec-driver` later.
- Do not mark work as parallel-safe unless overlap and integration risk are genuinely low.
- If a task still needs major replanning, split it again before handoff.
