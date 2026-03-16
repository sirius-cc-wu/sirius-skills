---
name: tasks
description: Generates an actionable tasks.md from a completed plan.
---

# Tasks

Use this skill to convert `spec.md` and `plan.md` into an execution-ready `tasks.md`.

## Responsibilities

1. Read the active track's `spec.md` and `plan.md`.
2. Produce `<track_path>/tasks.md`.
3. Turn plan packets into concrete, dependency-aware work items.
4. Make execution order, parallel-safe work, and validation explicit.

## Required Output

- `<track_path>/tasks.md`

Resolve `<track_path>` through `spec-driver`.

## Task Authoring Rules

- Use the existing codebase and target module as context.
- Prefer exact file paths when the plan makes them identifiable.
- Keep tasks concrete enough that a coding agent can execute them without replanning.
- Organize work by execution phase or user story so progress can be verified incrementally.
- Mark only genuinely independent work as parallel-safe.
- Include validation tasks when the spec or plan requires tests, checks, or manual verification.
- Do not repeat planning prose; convert it into executable checklist items.

## `tasks.md` Requirements

`<track_path>/tasks.md` must include:

1. Execution phases or story groupings
2. Concrete task IDs and checklist items
3. Explicit file paths or target modules where practical
4. Dependency notes and parallelization opportunities
5. Validation checkpoints
6. MVP or sequencing guidance for implementation

## Workflow

1. Resolve the active track with `spec-driver`.
2. Read `spec.md`, `plan.md`, and scan the target codebase as needed.
3. Fill `templates/tasks-template.md`.
4. Validate that every planned packet or requirement has execution coverage.
5. Stop when `tasks.md` is actionable and ready for implementation.
