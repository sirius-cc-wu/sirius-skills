---
name: guide-planning
description: Resolves feature planning state and routes to the right planning skill.
---

# Guide Planning

Use this skill as the planning-layer entrypoint when you need to decide the next planning step for one feature planning folder.

## Responsibilities

1. Resolve or initialize the active feature planning folder.
2. Verify required planning files, registry state, and feature metadata.
3. Route feature-scoped work to `evolve-feature`, `discover`, `design`, `ui-flow`, `breakdown`, `review-planning`, or `slice`.
4. Update planning readiness state when a phase is complete.
5. Keep planning handoff decisions durable in the repository instead of transient chat state.

## Entry Decision Guide

Use `guide-planning` when you need to decide the next planning step before slice-scoped execution begins.

- If no feature planning folder exists yet, initialize one and route to `discover`.
- If the request changes an existing feature rather than starting a net-new feature, route to `evolve-feature`.
- If the problem, outcomes, or constraints are still being framed, route to `discover`.
- If the architecture, interfaces, or validation strategy are still unresolved, route to `design`.
- If UI or interaction flow remains material, route to `ui-flow`.
- If the work is still too large for execution or slices are not explicit, route to `breakdown`.
- If planning artifacts need a readiness pass before slice bootstrap, route to `review-planning`.
- If the feature already has execution-ready work items with explicit slice IDs, route to `slice`.
- If a slice-scoped execution slice already exists, route to `guide-execution`.

## Workflow Boundary

`guide-planning` owns feature-planning readiness and routing only.

- Keep feature-planning readiness in planning metadata.
- Do not duplicate execution-slice lifecycle state here.
- Route execution-layer work to `guide-execution` instead of absorbing it into planning.

Typical handoff:

```text
guide-planning -> evolve-feature/discover -> design -> ui-flow -> breakdown -> review-planning -> slice -> guide-execution
```

## Lifecycle States

- `discovery_pending`
- `discovery_ready`
- `design_ready`
- `breakdown_ready`
- `planning_reviewed`
- `slice_ready`

Use adjacent transitions by default and repair skipped states only deliberately.

## Preflight

1. Resolve `<planning_dir>` from `.skills/planning.json`; default to `docs/features`.
2. Ensure the planning registry exists.
3. Resolve the active feature using tooling or a user-provided slug/path.
4. Confirm the folder represents one coherent feature or capability.
5. Check `discover.md`, `system-design.md`, optional `ui-design.md`, `slice-planning.md`, `slice-traceability.md`, and `.planning-meta.json` as appropriate for the current state.

## Tooling

Always use `scripts/manage_planning.py` in this skill directory for initialization, registry synchronization, state transitions, and validation.
