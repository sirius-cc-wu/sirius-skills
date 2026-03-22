---
name: review-execution
description: Reviews implementation against task-scoped specs and plans, then feeds durable fixes back into execution artifacts before closure.
---

# Review Execution

Use this skill after implementation and validation, and before `close-track`, when a task-scoped track needs an explicit review against `spec.md` and `plan.md`.

## Responsibilities

1. Review implementation and validation evidence against the active track's `spec.md` and `plan.md`.
2. Distinguish specification-to-implementation gaps from intent-to-specification gaps.
3. Feed durable fixes back into task-scoped artifacts or upstream planning guidance so the next execution starts from improved context.
4. Confirm whether the track is ready for `close-track` or needs more execution work first.

## Preferred Input

- `<track_path>/spec.md`
- `<track_path>/plan.md`
- optional `<track_path>/tasks.md` for legacy tracks
- the implementation diff or changed files
- validation results, tracker notes, or PR context when available

Resolve `<track_path>` through `spec-driver`.

## Required Output

- updated task-scoped execution artifacts when the review exposes durable gaps
- explicit review outcome recorded in the tracker, PR, or closure context used by the team

## Review Rules

- Check that requirements, acceptance notes, and validation steps still match the implementation.
- Classify findings explicitly:
  - specification-to-implementation gap
  - intent-to-specification gap
  - follow-up improvement outside the active track
- Prefer fixing the spec or plan when the issue reflects missing or ambiguous execution context.
- Capture any follow-up work in the team's execution tracker instead of overloading track readiness state.

## Workflow

1. Resolve the active track with `spec-driver`.
2. Read `spec.md`, `plan.md`, changed code, and available validation evidence.
3. Compare the implementation with the task-scoped requirements and validation plan.
4. Update `spec.md`, `plan.md`, or upstream planning guidance when the review reveals a durable context gap.
5. Stop when the track is ready for `close-track` or return the work to execution with explicit findings.

## Guardrails

- Do not close the track while blocking review findings remain unresolved.
- Do not treat code-only fixes as complete if the underlying spec or plan is still wrong.
- Do not use track metadata to mirror execution lifecycle states owned by the tracker.
