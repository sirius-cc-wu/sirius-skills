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

## Main Sources

- `docs/features/workflow-state-consistency/discover.md`
- `docs/features/workflow-state-consistency/system-design.md`
- `docs/features/workflow-state-consistency/.planning-meta.json`
