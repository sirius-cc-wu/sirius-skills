---
name: guide-planning
description: Resolves feature planning state, promotes accepted proposals into canonical planning, and routes to the right planning skill.
---

# Guide Planning

Use this skill as the planning-layer canonical entrypoint when you need to decide the next planning step for one feature planning folder.

## Responsibilities

1. Resolve or initialize the active feature planning folder.
2. Promote accepted proposals into canonical feature planning folders when the user explicitly asks for planning to begin.
3. Verify required planning files, registry state, and feature metadata.
4. Route feature-scoped work to `propose`, `add-subfeature`, `assess`, `research`, `discover`, `design`, `ui-flow`, `breakdown`, or `review-planning`, then stop for approval/commit before execution begins.
5. Persist planning readiness state when a phase is complete.
6. Keep planning handoff decisions durable in the repository instead of transient chat state.
7. When planning surface is consolidated, keep one canonical planning route and treat superseded surfaces as historical context instead of parallel entrypoints.
8. Treat new issues against implemented or archived features as follow-on delta work, not as a reason to mutate or archive the old packet in place.

## Entry Decision Guide

Use `guide-planning` when you need to decide the next planning step before slice-scoped execution begins.

- If no feature planning folder exists yet, initialize one with its default
  `subfeatures/` registry and route to `discover`.
  In short: initialize one and route to `discover`.
- If the work is still speculative, exploratory, or not yet accepted as a canonical feature, route to `propose`.
- If the user wants an accepted proposal promoted into canonical planning, perform that promotion here and then route to `discover`.
- If the request adds or reshapes a durable child capability under an existing feature, route to `add-subfeature`.
- If the user reports a bug, regression, missing behavior, or concrete runtime failure against an existing canonical feature, especially one already marked `implemented` or already archived, treat that as follow-on delta work and route to `add-subfeature` before editing the old packet further.
- If an active subfeature exists and the parent-feature impact is not yet explicit, route to `assess`.
- If the user explicitly asks for reference-project research or wiki synthesis, if the target overlaps checked-in `references/` patterns and has no durable `reference-research.md` yet, or if discovery/design depends on choosing between multiple upstream patterns, route to `research`.
- If the work is a small repo-local change whose shape does not depend on upstream comparison, skip `research` and continue directly into the normal planning path.
- If the user supplied a concrete error message, failing command, or missing runtime path, verify the current code/runtime seam first before deciding the request is only a planning-doc update.
- If the problem, outcomes, or constraints are still being framed, if only
  `draft.md` exists, or if `discover.md` is a bootstrap scaffold, route to
  `discover`.
- If the architecture, interfaces, or validation strategy are still unresolved, route to `design`.
- If UI or interaction flow remains material, route to `ui-flow`.
- If the work is still too large for execution or slices are not explicit, route to `breakdown`.
- If planning artifacts need a readiness pass before approval and execution bootstrap, route to `review-planning`.
  For workflow-shaping changes, expect the review pass to verify any declared
  consolidation story before the packet can become `planning_reviewed`.
- If planning has been reviewed but not yet explicitly approved, stop for human approval instead of advancing into execution.
- If implementation planning is needed for a canonical feature, create or select
  a subfeature first; subfeatures are the default execution-planning unit.
- If planning has been approved and committed and the selected subfeature or
  compatibility feature packet already has execution-ready work items with
  explicit slice IDs, hand off to the execution layer through `slice`.
- If a slice-scoped execution slice already exists, hand off to `guide-execution`.

## Workflow Boundary

`guide-planning` owns feature-planning readiness and routing only.

- Own the transition from accepted proposal to canonical feature planning.
- Keep feature-planning readiness in planning metadata.
- For subfeatures, treat `.subfeature-meta.json` as the writable lifecycle source and only use `guide-planning`'s metadata view as a derived projection. That derived view should stay `planning_reviewed` until explicit approval is recorded in subfeature metadata, and only become `slice_ready` once approved reviewed work also has ready slice IDs recorded.
- Treat the top-level planning registry as feature-only. Subfeature lookup is
  derived from feature-local `subfeatures/registry.json` and `.subfeature-meta.json`.
- Keep `research` advisory within the existing planning lifecycle instead of introducing a new readiness state.
- Do not duplicate execution-slice lifecycle state here.
- Stop at reviewed planning until the user approves the planning artifacts.
- Treat planning commits as the durable checkpoint between planning and execution.
- Keep any normalized `consolidation` summary in the existing planning or
  subfeature metadata instead of introducing a second planning sidecar.
- Do not treat an implemented or archived feature packet as the active home for new delta work; open or continue a subfeature instead.
- Do not suggest `archive-artifacts` as the next step while handling a newly reported fix or follow-on capability request for the same feature.
- When reviewed planning narrows or supersedes older workflow surface, route
  maintainers through this entrypoint and describe older surfaces as
  historical, migration-only, or archival context unless an explicit
  transition plan says both remain active temporarily.
- Hand off execution-layer work to `slice` or `guide-execution` instead of absorbing it into planning.

Typical handoff:

```text
guide-planning -> propose/add-subfeature/assess/research/discover -> design -> ui-flow -> breakdown -> review-planning -> human approval -> commit -> slice -> guide-execution
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

- `discovery_pending` means discovery has not been authored yet. A planning
  folder may have `draft.md` rough input in this state, but `draft.md` is not a
  readiness artifact.
- `discovery_ready` means `discover` has authored a real `discover.md`; draft
  notes or scaffold-marked `discover.md` files do not qualify.
- `planning_reviewed` means the planning packet has passed readiness review and is waiting for explicit human approval.
- `slice_ready` means the approved planning artifacts are committed and at least one execution-ready work item is selected for execution bootstrap. For subfeatures, derive this from reviewed status plus approval metadata and recorded ready slice IDs in `.subfeature-meta.json`.

## Preflight

1. Resolve the active planning scope from the nearest `.skills/planning.json`; if none exists in ancestor directories, fall back to the repository root when inside a Git worktree, then default `<planning_dir>` to `docs/features`.
2. Resolve any planning-layer artifact conventions from `.skills/planning.json`, including `design_diagram_mode` for `system-design.md` diagram layout.
3. Ensure the planning registry exists.
4. Resolve the active feature using tooling or a user-provided slug/path.
5. Confirm the folder represents one coherent feature or capability.
6. Check optional `reference-research.md`, `draft.md`, `discover.md`, `system-design.md`, optional `ui-design.md`, `slice-planning.md`, `slice-traceability.md`, and `.planning-meta.json` as appropriate for the current state. For subfeatures, rely on the derived planning view rather than editing a nested `.planning-meta.json` file directly.
7. If the target feature is already `implemented`, has archived slices, or the request is framed as a new bugfix/follow-on issue, decide first whether the right durable target is a new or existing subfeature rather than in-place edits to the parent packet.
8. When the user provided a concrete runtime failure or missing-path report, inspect the current implementation seam before choosing between subfeature planning, execution handoff, or archival.
9. When the packet materially reshapes existing workflow surface, confirm any
   durable consolidation summary in metadata matches the planning docs before
   treating the packet as review-ready.

## Tooling

Always use `sirius manage-planning` for initialization, proposal promotion, registry synchronization, state transitions, and validation.

- Use `sync-status` after `discover`, `design`, `ui-flow`, `breakdown`, and successful `review-planning` passes so metadata advances through the normal adjacent planning states instead of drifting behind the authored artifacts.
- Use `--consolidation-json` with `set-status` or `sync-status` when the
  reviewed packet needs a metadata-carried consolidation summary; keep that
  summary aligned with the narrative planning docs.
- Use `set-status` for explicit manual overrides, terminal execution states, or deliberate repair that should not be inferred from current artifacts alone.
