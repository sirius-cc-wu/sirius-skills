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
docs/features/<project-slug>/task-planning.md
docs/features/<project-slug>/task-traceability.md
```

## Responsibilities

1. Validate that stories are concrete, scoped, and ready for decomposition.
2. Split oversized work into smaller, independently verifiable execution packets.
3. Produce planning artifacts that preserve story-to-task traceability, increment grouping, sequencing, and execution mode assumptions.
4. Create executable tracker items, dependency links, and explicit parallel-safe lanes where appropriate.
5. Hand off ready work to `track` for spec-track bootstrap.

## Required Output

- `<project_path>/task-planning.md`
- `<project_path>/task-traceability.md`

Preferred tracker output when available:

- tracker tasks and dependency links

Use `assets/task-planning-template.md` as the default starting point for `<project_path>/task-planning.md`.
Use `assets/task-traceability-template.md` as the default starting point for `<project_path>/task-traceability.md`.
Use `scripts/scaffold_breakdown.py` when you want both files scaffolded together from a project slug.

## Breakdown Rules

- Keep stories and design in repo docs; keep executable tasks in the tracker.
- Prefer repository story sizes such as `S`, `M`, `L`, and `XL`.
- Split any `XL` item before creating execution-ready tasks.
- Every executable task should be small enough to fit one task-scoped spec track.
- Group related slices into small, demonstrable increments before bootstrapping tracks.
- Prefer execution packets that stay within one subsystem or a small set of files.
- Every execution-ready slice should have concrete acceptance notes and a validation command or artifact check.
- Preserve stable story identifiers so task traceability is durable.

## Increment Planning

Use increments to bridge repo-level planning and task-level execution:

- an increment is a small, demonstrable outcome made from one or more execution-ready slices
- Increment 1 should usually be the simplest end-to-end usable path
- increments belong in `task-planning.md` and `task-traceability.md`, not in spec-track state
- one increment can contain multiple tracker tasks, but each task still gets its own track later
- if a story spans multiple increments, record that explicitly instead of hiding it in notes

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

When a task tracker is available, use it as the execution tracker:

- create one tracker task per directly executable task
- group those tasks under increment headings in `task-planning.md` before creating them in the tracker
- use parent-child relationships when a larger story needs grouped subtasks
- record blockers as explicit dependency links in the tracker
- reflect safe parallel lanes and integration checkpoints in `task-planning.md`
- keep mapping from repo story IDs to tracker task IDs in `task-traceability.md`

If no tracker is configured, record tasks and dependencies directly in `task-planning.md` and use it as the execution backlog.

## Story-to-Task Mapping

Treat repo story IDs as the planning-system identifiers and tracker task IDs as the execution identifiers.

Default mapping:

- one repo story can map to one or many tracker tasks
- each execution-ready slice becomes one tracker task
- preserve the repo story ID in:
  - `task-traceability.md`
  - the tracker task description
- use dependency links only for real execution blockers, not for narrative grouping

Preferred description shape for a new task:

```text
Story: <story-id>
Increment: <increment-id>
Slice: <short slice name>
Acceptance:
- ...
Validation:
- ...
```

If one repo story splits into multiple executable tasks:

- keep the story as a repo concept in `user-stories.md`
- create multiple tracker tasks for the slices
- optionally create a non-executable parent task only when it helps grouped review
- record the story-to-task fan-out in `task-traceability.md`

Only reuse the repo story ID as the tracker task ID when **all** of the following are true:

- the repo story maps to exactly one executable task
- the team wants the story ID preserved end-to-end
- that ID will not collide with another execution item

Otherwise, let the tracker generate the task ID and keep the repo story ID in traceability metadata.

## Workflow

1. Read `discover.md`, `system-design.md`, optional `ui-design.md`, and `user-stories.md`.
2. Validate that each story has scope, acceptance notes, and an explicit size.
3. Split oversized work into smaller execution packets and group them into increments with clear demo outcomes.
4. Choose `single-agent` or `multi-agent` handling where relevant and record lane assumptions.
5. Write `task-planning.md` and `task-traceability.md` with increment groupings, dependency notes, parallel-safe lanes, and integration checkpoints as needed.
6. Create tracker tasks and dependency links for execution-ready work, keeping packet validation explicit.
7. Stop when each task is ready to be bootstrapped by `track`.

When generating `task-planning.md`, start from `assets/task-planning-template.md` and replace placeholders rather than inventing a new structure each time.
When generating `task-traceability.md`, start from `assets/task-traceability-template.md` and replace placeholders rather than inventing a new table shape each time.

## Guardrails

- Do not create execution tracks directly from vague stories.
- Do not mirror tracker execution states inside project planning docs.
- Do not turn increments into tracker states or spec-track containers.
- Do not turn `task-planning.md` into a task-scoped `tasks.md`; that belongs to `spec-driver` later.
- Do not mark work as parallel-safe unless overlap and integration risk are genuinely low.
- If a task still needs major replanning, split it again before handoff.
