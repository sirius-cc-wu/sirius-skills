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

## Terminal Completion Reconciliation

Recent repo usage exposed a practical drift class: a feature or subfeature could
have all planned slices backed by closed execution slices while durable planning
state stayed `slice_ready` / `reviewed` instead of `implemented` / `finalized`.

### What the current code already does

- `lib/workflow_state/owner_completion.py` is now the shared terminal
  reconciliation hook.
- `close-slice` invokes that hook after slice closure.
- `ship --finalize` invokes that hook for the target before requiring terminal
  `implemented` planning state.
- The hook promotes a feature to `implemented` or a subfeature to `finalized`
  only when traceability shows every planned slice has a closed mapped execution
  slice.

### Remaining boundaries

- Direct repository implementation bypasses the execution slice system
  entirely.
  - If a maintainer or agent edits the repo against planned slice IDs and makes
    one commit per slice without bootstrapping and closing execution slices,
    the shared hook still has no execution-slice evidence to use.
- A dedicated “semantic reconcile” maintenance command could still be useful
  for applying previewed repairs outside `close-slice` and `ship --finalize`.
- Add guardrails so agent-led “work all slices” flows either:
  - bootstrap real execution slices and route through `close-slice`, or
  - refuse to claim backlog completion while the planning owner state still
    says `reviewed`.

### Practical takeaway

The system still preserves separate planning and execution owners, but terminal
status promotion no longer lives only in `close-slice`. It is centralized in the
shared semantic layer and reused by both slice closure and finalization.

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
