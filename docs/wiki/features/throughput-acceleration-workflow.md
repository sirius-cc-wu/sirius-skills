# Throughput Acceleration Workflow

## Snapshot

- Feature: `throughput-acceleration-workflow`
- Status: `implemented` (updated `2026-04-22`)

## What This Feature Establishes

This feature adds an optional accelerator layer above the baseline planning and
execution workflows.

Implemented direction:

- `autoplan` composes planning steps while preserving approval boundaries.
- `ship` remains backlog orchestrator and can emit handoff payloads.
- `ship-slice` is a one-slice finisher for implementation through close/commit.
- `learn` manages durable workflow learnings.
- supplemental runtime artifacts (`.skills/runtime/*`, learnings JSONL) support
  resume/event logging without replacing repository artifacts as source of truth.

## Key Tradeoffs

- Strength: faster end-to-end flow without collapsing ownership boundaries.
- Cost: runtime/checkpoint state adds operational complexity and requires clear
  stale-state reconciliation.
- Strength: all accelerator behavior is optional and config-driven.

## Design Boundary To Preserve

The feature explicitly keeps `ship` independent for core backlog resolution and
positions `ship-slice` as optional delegation, not a required dependency.

## gstack Reference Comparison (`ship`)

Compared against `gstack` local clone commit `656df0e3`
(`https://github.com/garrytan/gstack`).

| Dimension | `gstack /ship` | `sirius-skills ship` |
|---|---|---|
| Primary intent | End-to-end ship pipeline to push branch and produce PR URL. | Resolve one planning backlog into next executable slice ownership step. |
| Interaction model | Fully automated, non-interactive by default; broad gate set. | Deterministic orchestration with explicit stop boundaries and owner handoff. |
| Unit of progress | Branch-level release/PR checklist. | Planned-slice backlog entry plus one active execution slice. |
| Source of truth | Git branch diff, review logs, version/changelog/docs artifacts. | Planning + execution registries, traceability docs, and slice metadata. |
| Output artifact | Updated branch, PR/MR body, metrics log. | Backlog state, next-owner routing, optional `ship-slice` handoff payload. |

Reference takeaway: `sirius-skills` should keep its repo-artifact-first
ownership model while selectively borrowing `gstack`'s stronger ship-readiness
reporting and explicit idempotency documentation.

## Reference-Guided Improvements

High-value improvements inferred from the comparison:

1. Add a formal "ship readiness summary" surface in `ship` output that mirrors
   current gates (active slice, increment readiness, commit checkpoint, owner
   handoff) in one quick dashboard.
2. Document idempotency contracts in `skills/ship/SKILL.md` as explicit rerun
   guarantees (what is always recomputed vs what is mutation-only).
3. Add an optional preflight branch-freshness check (config-driven, non-default)
   before `--bootstrap-next`, without turning `ship` into PR/deploy automation.
4. Keep PR creation, release, and changelog ownership external to `ship`; do not
   import `gstack`'s branch-release responsibilities into this backlog resolver.

## Two-Step UX Fit

Desired UX:

1. one planning command (`autoplan`) drives discover/design/breakdown/review
2. after approval, one execution command drives brief/blueprint/implementation/review-execution

Current status:

- partially implemented (routing and checkpointing exist)
- not yet implemented as full owner-chain execution

Roadmap link:

- see `docs/wiki/concepts/two-step-autonomy-roadmap.md`

## Main Sources

- `docs/features/throughput-acceleration-workflow/discover.md`
- `docs/features/throughput-acceleration-workflow/system-design.md`
- `docs/features/throughput-acceleration-workflow/.planning-meta.json`
- `skills/ship/SKILL.md`
- `skills/ship/scripts/ship.py`
- `skills/ship-slice/SKILL.md`
- `skills/ship-slice/scripts/ship_slice.py`
- `gstack/ship/SKILL.md` (sibling local reference clone)
