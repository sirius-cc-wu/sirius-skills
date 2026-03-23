# Discover: Execution Workflow

## Problem

The repository provides a task-scoped execution workflow, but that workflow spans registry tooling, templates, review rules, and closure behavior. Teams need a durable execution model that keeps task readiness explicit, preserves traceability from intent to implementation, and closes work without destroying historical context.

## Goals

- Bootstrap one track per execution-ready work item.
- Capture task intent in `brief.md` and make execution sequencing explicit in `plan.md`.
- Keep track readiness separate from external task execution state.
- Preserve non-destructive closure and relation metadata for auditing and historical publishing.

## Non-Goals

- Replace the planning layer with task-scoped execution docs.
- Make the execution registry own tracker lifecycle states such as in-progress or blocked.
- Force project-specific tracker behavior into the core execution skills.

## Primary Actors

- Task definer capturing acceptance and requirements.
- Task planner producing implementation packets and validation.
- Implementation agent executing a ready track.
- Reviewer checking brief-to-implementation alignment.
- Closure owner publishing or recording track closure.

## Constraints

- Track layout defaults to `tracks/` unless `.skills/execution.json` overrides `track_dir`.
- Execution state machine is `draft -> brief_ready -> plan_ready -> execution_ready -> closed`.
- `execution-driver` owns readiness only; execution tracker owns task progress.
- Closed tracks retain `brief.md`, `plan.md`, and any legacy `tasks.md`.
- Relations such as `supersedes` and `replaces_partially` are durable metadata, not transient notes.

## Confirmed Signals in Repo

- `skills/execution-driver/scripts/manage_execution.py` manages registry, status updates, and relations.
- `skills/define/templates/brief-template.md` defines the task brief structure.
- `skills/plan/templates/plan-template.md` defines implementation packets and validation mapping.
- `skills/close-track/scripts/close_track.py` publishes non-destructive closure summaries.
- `skills/commit/` and `skills/create-pr/` enforce conventions and checklist completion around execution work.

## Success Criteria

- A maintainer can bootstrap, define, plan, review, and close a task-scoped track with durable metadata.
- Track artifacts remain sufficient for later audit or historical publication after closure.
- Execution workflow stays generic-first while allowing project-level conventions via config.

## Risks and Open Questions

- Track readiness can drift from actual implementation state if the external tracker is not updated.
- Checklist and validation completion rely on agent discipline plus PR checks rather than fully structured evidence.
- Relation recording is powerful but can become inconsistent if not reviewed carefully.
