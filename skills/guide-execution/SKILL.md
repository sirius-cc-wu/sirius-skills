---
name: guide-execution
description: Resolves the active slice and routes execution-layer work to the right skill.
---

# Guide Execution

Use this skill as the execution-layer entrypoint when you need to decide the next step for one execution slice.

## Responsibilities

1. Resolve or initialize the active slice.
2. Verify required files, registry state, and slice metadata.
3. Decide whether work belongs in the planning layer or the slice-scoped execution layer.
4. Route slice-scoped work to `brief`, `blueprint`, active repository implementation, `review-execution`, or `close-slice`.
5. Update slice readiness status when a phase is complete.

`guide-execution` owns orchestration and readiness only. It should not absorb artifact authoring that belongs to `brief`, `blueprint`, `review-execution`, or `close-slice`.

When `.skills/execution.json` sets `auto_start_implementation` to `true`, treat `blueprint_ready` as an automatic handoff into implementation: once `blueprint.md` is complete, update the slice through `manage_execution.py set-status <slice> blueprint_ready`, let the tooling advance the slice to `execution_ready`, and continue directly into code changes instead of stopping for a second manual handoff.

## Entry Decision Guide

Use `guide-execution` when a slice already exists or you need to decide the next step for execution-layer work.

- If the work is still feature-scoped or story-scoped, send it back to `guide-planning`.
- If there is one execution-ready work item but no slice-scoped execution slice yet, route to `slice` after confirming the reviewed planning artifacts were approved and committed.
- If a slice exists or can be resolved, stay in `guide-execution` and route inside the execution layer.

## Workflow Boundary

Typical handoff:

```text
guide-planning -> discover -> design -> ui-flow -> breakdown -> review-planning -> human approval -> commit -> slice -> guide-execution
```

`guide-execution` owns slice/document readiness only:

- `draft`
- `brief_ready`
- `blueprint_ready`
- `execution_ready`
- `closed`

Do not duplicate day-to-day implementation states like `implementing` or `blocked` in the slice registry.

## Preflight

1. Resolve `.skills/execution.json` and the configured slice registry.
2. Resolve the active slice using `sirius manage-execution get-active` or a user-provided ID/path. Do not refer to a `resolve-active` command because the execution tool exposes `get-active`.
3. Confirm the slice path represents one execution-ready work item.
4. Check `brief.md`, `blueprint.md`, optional legacy `slices.md`, and `.slice-meta.json` as appropriate for the current state.
5. Check whether `auto_start_implementation` is enabled so the blueprint handoff behavior matches repository config.
6. Repair registry inconsistencies before routing deeper into execution.

## Tooling

Always use `sirius manage-execution` for initialization, active-slice resolution, status updates, validation, registry synchronization, and relation management. Use `get-active` when you need the current active slice from the CLI.
