---
name: guide-planning
description: Resolves feature planning state, promotes accepted proposals into canonical planning, and routes to the right planning skill.
---

# Guide Planning

Use this skill as the planning-layer entrypoint when you need to decide the next planning step for one feature planning folder.

## Responsibilities

1. Resolve or initialize the active feature planning folder.
2. Promote accepted proposals into canonical feature planning folders when the user explicitly asks for planning to begin.
3. Verify required planning files, registry state, and feature metadata.
4. Route feature-scoped work to `propose`, `add-subfeature`, `assess`, `discover`, `design`, `ui-flow`, `breakdown`, or `review-planning`, then stop for approval/commit before execution begins.
5. Update planning readiness state when a phase is complete.
6. Keep planning handoff decisions durable in the repository instead of transient chat state.

## Entry Decision Guide

Use `guide-planning` when you need to decide the next planning step before slice-scoped execution begins.

- If no feature planning folder exists yet, initialize one and route to `discover`.
- If the work is still speculative, exploratory, or not yet accepted as a canonical feature, route to `propose`.
- If the user wants an accepted proposal promoted into canonical planning, perform that promotion here and then route to `discover`.
- If the request adds or reshapes a durable child capability under an existing feature, route to `add-subfeature`.
- If an active subfeature exists and the parent-feature impact is not yet explicit, route to `assess`.
- If the problem, outcomes, or constraints are still being framed, route to `discover`.
- If the architecture, interfaces, or validation strategy are still unresolved, route to `design`.
- If UI or interaction flow remains material, route to `ui-flow`.
- If the work is still too large for execution or slices are not explicit, route to `breakdown`.
- If planning artifacts need a readiness pass before approval and execution bootstrap, route to `review-planning`.
- If planning has been reviewed but not yet explicitly approved, stop for human approval instead of advancing into execution.
- If planning has been approved and committed and the feature already has execution-ready work items with explicit slice IDs, hand off to the execution layer through `slice`.
- If a slice-scoped execution slice already exists, hand off to `guide-execution`.

## Workflow Boundary

`guide-planning` owns feature-planning readiness and routing only.

- Own the transition from accepted proposal to canonical feature planning.
- Keep feature-planning readiness in planning metadata.
- Do not duplicate execution-slice lifecycle state here.
- Stop at reviewed planning until the user approves the planning artifacts.
- Treat planning commits as the durable checkpoint between planning and execution.
- Hand off execution-layer work to `slice` or `guide-execution` instead of absorbing it into planning.

Typical handoff:

```text
guide-planning -> propose/add-subfeature/assess/discover -> design -> ui-flow -> breakdown -> review-planning -> human approval -> commit -> slice -> guide-execution
```

## Lifecycle States

- `discovery_pending`
- `discovery_ready`
- `design_ready`
- `breakdown_ready`
- `planning_reviewed`
- `slice_ready`
- `implemented`

Use adjacent transitions by default and repair skipped states only deliberately.

- `planning_reviewed` means the planning packet has passed readiness review and is waiting for explicit human approval.
- `slice_ready` means the approved planning artifacts are committed and at least one execution-ready work item is selected for execution bootstrap.

## Preflight

1. Resolve the active planning scope from the nearest `.skills/planning.json`; if none exists in ancestor directories, fall back to the repository root when inside a Git worktree, then default `<planning_dir>` to `docs/features`.
2. Resolve any planning-layer artifact conventions from `.skills/planning.json`, including `design_diagram_mode` for `system-design.md` diagram layout.
3. Ensure the planning registry exists.
4. Resolve the active feature using tooling or a user-provided slug/path.
5. Confirm the folder represents one coherent feature or capability.
6. Check `discover.md`, `system-design.md`, optional `ui-design.md`, `slice-planning.md`, `slice-traceability.md`, and `.planning-meta.json` as appropriate for the current state.

## Tooling

Always use `scripts/manage_planning.py` in this skill directory for initialization, proposal promotion, registry synchronization, state transitions, and validation.
