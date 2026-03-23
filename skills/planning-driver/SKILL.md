---
name: planning-driver
description: Orchestrates planning-layer workflow by resolving feature planning state and routing to the right planning skill.
---

# Planning Driver

Use this skill as the planning-layer entrypoint when you need to decide the next step for one feature planning folder.

## Responsibilities

1. Resolve or initialize the active feature planning folder.
2. Verify required planning files, registry state, and feature metadata.
3. Route feature-scoped work to `discover`, `design`, `ui-flow`, `breakdown`, `review-planning`, or `track` as appropriate.
4. Update planning readiness state when a phase is complete.
5. Keep planning handoff decisions durable in the repository instead of in transient chat.

## Entry Decision Guide

Use `planning-driver` when you need to decide the next planning step for a feature before task-scoped execution begins.

Before routing planning work, classify the request:

1. If no feature planning folder exists yet:
   - initialize one with `manage_planning.py add <feature-slug>`
   - route to `discover`
2. If the problem, outcomes, or constraints are still being framed:
   - route to `discover`
3. If the architecture, interfaces, or validation strategy are still unresolved:
   - route to `design`
4. If UI or interaction flow is still a material part of scope:
   - route to `ui-flow`
5. If the work is still too large for execution or tracker tasks are not yet defined:
   - route to `breakdown`
6. If the planning artifacts need a readiness pass before task bootstrap:
   - route to `review-planning`
7. If the feature already has one or more execution-ready work items with explicit task IDs:
   - route to `track`
8. If a task-scoped execution track already exists:
   - route to `spec-driver`

`planning-driver` should not absorb discovery, architecture, decomposition, or execution bootstrap work just because it was invoked first. Route to the owning skill and keep readiness state separate from the artifact authoring skill.

## Upstream and Downstream Handoff

`planning-driver` sits between feature-scoped planning artifacts and task-scoped execution tracks.

In repositories that use the planning-layer skills, the usual flow is:

```text
planning-driver -> discover -> design -> ui-flow -> breakdown -> review-planning -> track -> spec-driver
```

- `planning-driver` owns feature planning readiness and routing.
- `discover`, `design`, `ui-flow`, and `breakdown` own the planning artifacts.
- `review-planning` owns the readiness review pass.
- `track` bootstraps one task-scoped execution track for one ready work item.
- `spec-driver` then manages task-scoped execution readiness.

## Lifecycle States

- `discovery_pending`
- `discovery_ready`
- `design_ready`
- `breakdown_ready`
- `planning_reviewed`
- `track_ready`

Allowed transitions:

1. `discovery_pending -> discovery_ready`
2. `discovery_ready -> design_ready`
3. `design_ready -> breakdown_ready`
4. `breakdown_ready -> planning_reviewed`
5. `planning_reviewed -> track_ready`

Do not skip states without explicit user approval. Adjacent transitions are the default; use tooling overrides only for deliberate repair.

## State Ownership

`planning-driver` owns **planning readiness** only:

- `discovery_pending`
- `discovery_ready`
- `design_ready`
- `breakdown_ready`
- `planning_reviewed`
- `track_ready`

Do not duplicate task tracker lifecycle states in planning metadata. Keep task execution state in the tracker and task-scoped execution readiness in `spec-driver`.

## Preflight

1. Resolve `<planning_dir>` from `.skills/planning.json`; if the file is missing, default to `docs/features`.
2. Ensure the planning registry exists (`<planning_dir>/README.md` and `<planning_dir>/registry.json`).
3. Resolve the active feature using tooling or user-provided slug/path.
4. Confirm the feature planning folder exists and represents one coherent feature or capability.
5. Check presence of:
   - `discover.md`
   - `system-design.md`
   - optional `ui-design.md`
   - `task-planning.md`
   - `task-traceability.md`
6. Verify feature planning metadata exists at `<feature_path>/.planning-meta.json`.
7. If no feature can be resolved, initialize one before routing further work.

## Routing Rules

1. If no `discover.md` exists or intent is still unresolved:
   - use `discover`
   - set status to `discovery_ready` when framing is concrete enough to design
2. If `discover.md` is complete but architecture or validation strategy is still unresolved:
   - use `design`
   - if UI flow is material, route to `ui-flow` before marking design complete
   - set status to `design_ready` when system design is concrete enough for decomposition
3. If design is complete but no breakdown artifacts exist or slices are still too large:
   - use `breakdown`
   - set status to `breakdown_ready` when `task-planning.md` and `task-traceability.md` make the execution-ready slices explicit
4. If breakdown is complete but planning has not yet been reviewed:
   - use `review-planning`
   - record a durable readiness note
   - set status to `planning_reviewed` when blocking issues are resolved
5. If planning has been reviewed and there is at least one execution-ready task ID:
   - route to `track`
   - set status to `track_ready` when the handoff to task-scoped execution is explicit
6. If task-scoped execution tracks already exist:
   - route to `spec-driver`

## Completion Checks

A feature is `discovery_ready` when:

- `discover.md` exists and is non-empty
- the problem, outcomes, constraints, and open questions are durable enough for design

A feature is `design_ready` when:

- `system-design.md` exists and is non-empty
- `ui-design.md` also exists when UI flow is required for the feature
- the next step is decomposition, not more architecture framing

A feature is `breakdown_ready` when:

- `task-planning.md` and `task-traceability.md` exist and are non-empty
- execution-ready slices and validation paths are explicit enough for review

A feature is `planning_reviewed` when:

- the planning artifacts have passed `review-planning`
- a non-empty review note is recorded in planning metadata
- blocking planning issues have been resolved or explicitly forced for repair

A feature is `track_ready` when:

- planning review is complete
- one or more ready task IDs are recorded for bootstrap
- the next lifecycle owner is `track` and then `spec-driver`

## Tooling

Always use `scripts/manage_planning.py` for initialization, active feature resolution, status updates, validation, and registry synchronization.

`manage_planning.py` maintains:

- a human-readable registry at `<planning_dir>/README.md`
- a machine-readable registry at `<planning_dir>/registry.json`
- per-feature lifecycle metadata at `<feature_path>/.planning-meta.json`

The configured planning directory is stored in `.skills/planning.json` under `planning_dir`.

Example:

```json
{
  "planning_dir": "docs/features"
}
```

```bash
# Initialize the planning registry/config:
python3 <path-to-planning-driver>/scripts/manage_planning.py init [planning-dir]

# Add a feature planning folder:
python3 <path-to-planning-driver>/scripts/manage_planning.py add "feature-slug"

# Add a feature that requires ui-flow before design is ready:
python3 <path-to-planning-driver>/scripts/manage_planning.py add "feature-slug" --require-ui-flow

# Mark discovery complete:
python3 <path-to-planning-driver>/scripts/manage_planning.py set-status "feature-slug" discovery_ready

# Record planning review completion:
python3 <path-to-planning-driver>/scripts/manage_planning.py set-status "feature-slug" planning_reviewed --review-note "Reviewed for scope, sequencing, and validation readiness."

# Mark the feature ready to bootstrap one or more tracks:
python3 <path-to-planning-driver>/scripts/manage_planning.py set-status "feature-slug" track_ready --task-id ABC-101 --task-id ABC-102

# Resolve the active planning feature:
python3 <path-to-planning-driver>/scripts/manage_planning.py get-active

# Validate planning feature consistency:
python3 <path-to-planning-driver>/scripts/manage_planning.py validate-feature "feature-slug"
```
