---
name: tasks
description: Generates an actionable, machine-checkable tasks.md from a completed plan.
---

# Tasks

Use this skill to convert `spec.md` and `plan.md` into an execution-ready `tasks.md`.

## Responsibilities

1. Read the active track's `spec.md` and `plan.md`.
2. Produce `<track_path>/tasks.md`.
3. Turn plan packets into concrete, dependency-aware work items.
4. Make execution order, parallel-safe work, validation, and stop gates explicit.

## Required Output

- `<track_path>/tasks.md`

Resolve `<track_path>` through `spec-driver`.

## Task Authoring Rules

- Use the existing codebase and target module as context.
- Prefer exact file paths when the plan makes them identifiable.
- Keep tasks concrete enough that a coding agent can execute them without major replanning.
- Prefer small, context-local tasks over broad implementation buckets.
- Organize work by execution phase or user story so progress can be verified incrementally.
- Mark only genuinely independent work as parallel-safe.
- Every implementation task should have an exact validation command or a concrete artifact check.
- Include validation tasks when the spec or plan requires tests, checks, or manual verification.
- Add stop-and-ask gates for destructive or high-risk work such as schema/data migrations, auth or permission changes, public API or contract breaks, and production config or infrastructure changes.
- If the track uses multiple execution lanes, include handoff notes and an integration checkpoint for each lane.
- Do not repeat planning prose; convert it into executable checklist items.

## Definition of Done Standard

A task or packet is complete only if all are true:

1. Required code or artifact changes are present.
2. Verification commands pass exactly as specified.
3. Non-functional checks pass when applicable, such as lint, type, security, or performance checks.
4. Required supporting artifacts are updated, such as docs, changelog, or migration notes.
5. Medium-risk or high-risk tasks include rollback or mitigation notes when the plan calls for them.
6. Multi-agent handoffs include notes for downstream work when applicable.

## `tasks.md` Requirements

`<track_path>/tasks.md` must include:

1. Execution phases or story groupings
2. Concrete task IDs and checklist items
3. Explicit file paths or target modules where practical
4. Dependency notes and parallelization opportunities
5. Exact verification commands or artifact checks
6. Validation checkpoints
7. MVP or sequencing guidance for implementation
8. Risk stop gates and integration checkpoints where applicable

## Re-planning Rules

- If a task still requires major design work, push that back to planning instead of encoding vague implementation steps.
- If a task fails repeatedly, exceeds context budget, or spans too many modules, split it into smaller tasks before execution continues.
- Do not treat "looks good" or review-only language as sufficient validation.

## Workflow

1. Resolve the active track with `spec-driver`.
2. Read `spec.md`, `plan.md`, and scan the target codebase as needed.
3. Fill `templates/tasks-template.md`.
4. Validate that every planned packet or requirement has execution coverage, a verification path, and any required stop gates.
5. Stop when `tasks.md` is actionable, machine-checkable, and ready for implementation.
