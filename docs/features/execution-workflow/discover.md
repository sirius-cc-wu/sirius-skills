# Discover: Execution Workflow

## Problem

The repository provides a slice-scoped execution workflow, but that workflow spans registry tooling, templates, review rules, and closure behavior. Teams need a durable execution model that keeps slice readiness explicit, preserves traceability from intent to implementation, and closes work without destroying historical context.

## Goals

- Bootstrap one slice per execution-ready work item.
- Capture slice intent in `brief.md` and make execution sequencing explicit in `blueprint.md`.
- Keep slice readiness separate from external slice execution state.
- Preserve non-destructive closure and relation metadata for auditing and historical publishing.

## Non-Goals

- Replace the planning layer with slice-scoped execution docs.
- Make the execution registry own tracker lifecycle states such as in-progress or blocked.
- Force project-specific tracker behavior into the core execution skills.

## Primary Actors

- Slice definer capturing acceptance and requirements.
- Slice planner producing implementation packets and validation.
- Implementation agent executing a ready slice.
- Reviewer checking brief-to-implementation alignment.
- Closure owner publishing or recording slice closure.

## Constraints

- Slice layout defaults to `slices/` unless `.skills/execution.json` overrides `slice_dir`.
- Execution state machine is `draft -> brief_ready -> blueprint_ready -> execution_ready -> closed`.
- `execution-driver` owns readiness only; execution tracker owns slice progress.
- Closed slices retain `brief.md`, `blueprint.md`, and any legacy `slices.md`.
- Relations such as `supersedes` and `replaces_partially` are durable metadata, not transient notes.

## Confirmed Signals in Repo

- `skills/execution-driver/scripts/manage_execution.py` manages registry, status updates, and relations.
- `skills/define/templates/brief-template.md` defines the slice brief structure.
- `skills/blueprint/templates/plan-template.md` defines implementation packets and validation mapping.
- `skills/close-slice/scripts/close_slice.py` publishes non-destructive closure summaries.
- `skills/commit/` and `skills/create-pr/` enforce conventions and checklist completion around execution work.

## Success Criteria

- A maintainer can bootstrap, define, plan, review, and close a execution slice with durable metadata.
- Slice artifacts remain sufficient for later audit or historical publication after closure.
- Execution workflow stays generic-first while allowing project-level conventions via config.

## Risks and Open Questions

- Slice readiness can drift from actual implementation state if the external tracker is not updated.
- Checklist and validation completion rely on agent discipline plus PR checks rather than fully structured evidence.
- Relation recording is powerful but can become inconsistent if not reviewed carefully.
