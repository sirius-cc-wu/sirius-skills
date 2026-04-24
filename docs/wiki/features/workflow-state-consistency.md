# Workflow State Consistency

## Snapshot

- Feature: `workflow-state-consistency`
- Status: `implemented` (updated `2026-04-19`)

## What This Feature Establishes

This feature hardens semantic consistency across planning and execution artifacts
without replacing the current workflow model.

Core design direction:

- shared repo-local `lib/workflow_state/` is the canonical semantic layer
- lifecycle owner scripts keep write authority for statuses and metadata
- maintenance skills (`audit`, `trace`, `report`, `repair`) consume shared
  reconciliation/parsing logic instead of diverging implementations
- parity checks surface installed-vs-repo drift for maintenance behavior

## Key Tradeoffs

- Strength: reduces drift by consolidating cross-artifact semantics in one
  shared library.
- Cost: installation/packaging flows must keep shared runtime sync correct.
- Strength: semantic drift preview remains separate from derived registry repair,
  reducing accidental destructive writes.

## Operational Outcome

The feature targets high-confidence invariants first (for example, subfeature
finalization and linked closed-slice consistency) while deferring broader
heuristic enforcement.

## Open Gap: Subfeatures Can Still Stay Unimplemented After Work Finishes

Recent repo usage still exposes a practical drift class: a subfeature can have
all planned slices implemented in the repository while its durable planning
state remains `planning_reviewed` / `reviewed` instead of
`implemented` / `finalized`.

### What the current code already does

- Subfeature lifecycle does have a terminal state.
  - `skills/add-subfeature/scripts/manage_subfeatures.py` maps
    `finalized -> implemented` into nested planning metadata.
- There is already an owner-sync path for completion.
  - `skills/close-slice/scripts/close_slice.py` calls
    `sync_owner_completion(...)` after slice closure.
  - That helper promotes a subfeature to `finalized` when every mapped
    execution slice is closed, and promotes the nested `.planning-meta.json`
    state to `implemented`.

### Why the drift still happens

The completion logic is present, but it is only attached to one narrow path:
`close-slice`.

The current execution stack makes it easy to finish work without traversing that
path:

- `ship` is explicitly orchestration-only.
  - Its skill contract says it routes to owners such as `brief`, `blueprint`,
    `implementation`, `review-execution`, `close-slice`, or `commit`, but it
    does not absorb closure logic itself.
- `ship` backlog resolution treats a planned slice as complete when the mapped
  execution slice is already `closed`, but it does not reconcile owner metadata
  when backlog completion is observed.
- Direct repository implementation bypasses the execution slice system
  entirely.
  - If a maintainer or agent edits the repo against planned slice IDs and makes
    one commit per slice without bootstrapping and closing execution slices,
    `close-slice` never runs, so the owner-sync hook never fires.
- Some older planning docs still describe subfeature completion as an explicit
  “finalization” concept, while the newer methodology says there is no
  dedicated subfeature-finalization skill and closure should happen through the
  slice system. That split makes the real completion trigger easier to miss.

### Root cause

This is primarily an ownership-gap problem, not a missing-state problem.

- The source of truth for “subfeature is implemented” currently depends on
  execution-slice closure.
- The repo has multiple practical ways to finish the implementation work
  without enforcing that closure handoff.
- No batch-orchestration or repair owner currently performs a final
  reconciliation pass when all planned slices are already satisfied.

### What should likely be fixed later

Any later fix should preserve explicit ownership boundaries but make terminal
reconciliation harder to miss.

Candidate directions:

- Add a terminal reconciliation step to `ship` when every planned slice for a
  feature or subfeature is already backed by closed execution slices.
- Add a dedicated “semantic reconcile” maintenance command that can safely
  promote `reviewed -> finalized` / `planning_reviewed -> implemented` when the
  traceability and execution evidence already prove completion.
- Add guardrails so agent-led “work all slices” flows either:
  - bootstrap real execution slices and route through `close-slice`, or
  - refuse to claim backlog completion while the planning owner state still
    says `reviewed`.
- Clean up documentation so all workflow surfaces say the same thing:
  subfeature implementation becomes durable through slice closure and owner
  sync, not through an implicit planning-side status guess.

### Practical takeaway

The current system does not “lack” implemented/finalized subfeature logic.
Instead, the logic is too easy to bypass because it lives at the
`close-slice` boundary while several common execution paths stop earlier or
work outside the execution-slice system entirely.

## Accelerator Guardrail Extension

The consistency layer now also backs accelerator transition guardrails:

- shared `lib/workflow_runtime/accelerator_guardrails.py` centralizes
  stop-reason classification, reason normalization, and readiness invariant
  construction.
- `autoplan`, `ship-slice`, and `ship` consume the same guardrail helper for
  deterministic `readiness.blocked_by` and normalized `stop_reason` payloads.
- this removes duplicated stop-reason parsing logic across accelerators and
  keeps approval/commit boundary semantics consistent in machine-readable output.

## Main Sources

- `docs/features/workflow-state-consistency/discover.md`
- `docs/features/workflow-state-consistency/system-design.md`
- `docs/features/workflow-state-consistency/.planning-meta.json`
