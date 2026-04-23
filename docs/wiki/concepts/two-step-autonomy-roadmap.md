# Two-Step Autonomy Roadmap

## Goal

Reduce orchestration friction from many manual commands to two high-level steps:

1. `autoplan` drives planning owners end-to-end.
2. After approval, `ship`/`ship-slice` drives execution owners end-to-end.

## Primary Operator Flow

Use this as the default happy-path UX when accelerators are enabled:

1. Run `autoplan` until planning reaches approval boundary:
   `python3 skills/autoplan/scripts/autoplan.py <target> --execute-owner-chain --json`
2. Review planning artifacts, then approve explicitly.
3. Record approval:
   `python3 skills/ship/scripts/ship.py <target> --approve --approval-note "<note>" --json`
4. Start execution autopilot:
   `python3 skills/ship/scripts/ship.py <target> --resume --json`
5. Re-run `ship --resume` until `readiness.blocked_by` reports a boundary
   requiring manual action (for example `commit_checkpoint`).

Guide-path positioning:

- `guide-scope`, `guide-planning`, and `guide-execution` remain available, but
  should be treated as advanced/manual entrypoints for ambiguous scopes,
  recovery, and fine-grained control.
- The primary operator path should prefer `autoplan` and `ship` for normal
  two-step execution.

## Current State

Current accelerator skills now support owner-chain orchestration in both layers:

- `autoplan` can now optionally execute the planning owner chain and stop with
  structured boundary context.
- `ship` resolves backlog and can bootstrap/delegate.
- `ship-slice` can now optionally execute one-slice execution owner-chain
  routing and stop with structured boundary context.
- `ship-slice` can now optionally continue through owned-file formatting,
  slice closure, and owned-only commit creation with deterministic partial
  success reporting.

Continuation-policy controls are now implemented for delegated execution
boundaries:

- `accelerators.ship_slice.continuation_policy.review_boundary`
- `accelerators.ship_slice.continuation_policy.commit_checkpoint`

Readiness now surfaces both boundary stop context and policy metadata
(`policy_action`, `policy_source`) so continuation behavior stays explicit.

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
into continuing through owned-file `auto_format`, `close-slice`, and
`commit`.

## Suggested Configuration Surface

Use additive flags under existing typed configs:

- `.skills/planning.json`:
  - `accelerators.autoplan.execute_owner_chain` (bool)
  - `accelerators.autoplan.stop_on_owner` (optional list)
- `.skills/execution.json`:
  - `accelerators.ship.delegate_to_ship_slice` (existing)
  - `accelerators.ship_slice.execute_owner_chain` (bool)
  - `accelerators.ship_slice.stop_on_owner` (optional list)
  - `accelerators.ship_slice.continuation_policy.review_boundary` (`stop` or `continue`)
  - `accelerators.ship_slice.continuation_policy.commit_checkpoint` (`stop` or `continue`)
  - `accelerators.ship_slice.auto_format` (bool, default false)
  - `accelerators.ship_slice.format_command` (string or string list, required when `auto_format=true`)
  - `accelerators.ship_slice.auto_close` (bool, default false)
  - `accelerators.ship_slice.auto_commit` (bool, default false)

## Guardrails To Keep

1. Planning/execution artifacts remain source of truth.
2. Approval stays explicit between planning and execution.
3. Any owner failure returns structured stop context instead of fallback
   guessing.
4. Unrelated dirty worktree state remains tolerated, but owned-file conflicts,
   formatter spillover, and owned commit checkpoints remain enforced.

## Incremental Delivery Notes

1. Policy toggles for delegated stop-vs-continue at review/commit boundaries
   are implemented.

## Main Sources

- `skills/autoplan/SKILL.md`
- `skills/autoplan/scripts/autoplan.py`
- `skills/ship/SKILL.md`
- `skills/ship/scripts/ship.py`
- `skills/ship-slice/SKILL.md`
- `skills/ship-slice/scripts/ship_slice.py`
- `docs/wiki/concepts/gstack-ship-reference.md`
