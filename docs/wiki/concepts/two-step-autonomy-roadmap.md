# Two-Step Autonomy Roadmap

## Goal

Reduce orchestration friction from many manual commands to two high-level steps:

1. `autoplan` drives planning owners end-to-end.
2. After approval, `ship`/`ship-slice` drives execution owners end-to-end.

## Current Gap

Current accelerator skills mostly reconcile state and route to the next owner:

- `autoplan` returns `next_owner` from planning status and checkpoints runtime
  context.
- `ship` resolves backlog and can bootstrap/delegate.
- `ship-slice` resolves one active slice and checkpoints, but does not execute
  owner workflows itself.

This preserves strict boundaries but forces users to issue many follow-up
requests manually.

## Target Operating Model

### Step 1: Planning Autoplan

`autoplan` should optionally execute:

- `discover`
- `design`
- `breakdown`
- `review-planning`

Until:

- status reaches `planning_reviewed`, or
- an explicit stop boundary is hit (ambiguity, unresolved dependency, failing
  validation, missing required input).

### Step 2: Execution Autopilot (post-approval)

After explicit user approval, `ship` and delegated `ship-slice` should
optionally execute:

- `brief`
- `blueprint`
- repository implementation step
- `review-execution`

Then stop at existing closure/commit boundaries unless the user explicitly opts
into continuing through `close-slice` and `commit`.

## Suggested Configuration Surface

Use additive flags under existing typed configs:

- `.skills/planning.json`:
  - `accelerators.autoplan.execute_owner_chain` (bool)
  - `accelerators.autoplan.stop_on_owner` (optional list)
- `.skills/execution.json`:
  - `accelerators.ship.delegate_to_ship_slice` (existing)
  - `accelerators.ship_slice.execute_owner_chain` (bool)
  - `accelerators.ship_slice.stop_on_owner` (optional list)
  - `accelerators.ship_slice.auto_close` (bool, default false)
  - `accelerators.ship_slice.auto_commit` (bool, default false)

## Guardrails To Keep

1. Planning/execution artifacts remain source of truth.
2. Approval stays explicit between planning and execution.
3. Any owner failure returns structured stop context instead of fallback
   guessing.
4. Worktree cleanliness and commit checkpoint rules remain enforced.

## Incremental Delivery Plan

1. Extend `autoplan` with owner-chain execution behind config flag.
2. Extend `ship-slice` with owner-chain execution behind config flag.
3. Add machine-readable "readiness dashboard" outputs for both steps.
4. Add tests for happy path, stop boundaries, resume semantics, and stale
   checkpoint reconciliation.

## Main Sources

- `skills/autoplan/SKILL.md`
- `skills/autoplan/scripts/autoplan.py`
- `skills/ship/SKILL.md`
- `skills/ship/scripts/ship.py`
- `skills/ship-slice/SKILL.md`
- `skills/ship-slice/scripts/ship_slice.py`
- `docs/wiki/concepts/gstack-ship-reference.md`
