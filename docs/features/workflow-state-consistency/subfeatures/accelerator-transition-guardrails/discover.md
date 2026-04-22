# Discover: Accelerator Transition Guardrails

## Parent Feature

- Feature: `workflow-state-consistency`
- Subfeature ID: `accelerator-transition-guardrails`
- Subfeature Type: `additive`

## Problem

Harden owner-chain transitions with invariant checks and deterministic stop reasons.

## Requested Subfeature

- Add transition guardrails for accelerator owner-chain execution to prevent
  inconsistent cross-artifact states.
- Validate high-confidence invariants before and after owner transitions, and
  return deterministic stop reasons when a guardrail fails.
- Reuse shared consistency/reconciliation logic rather than duplicating checks
  independently in each accelerator entrypoint.

## Baseline Artifacts To Assess

- `discover.md`
- `system-design.md`
- `user-stories.md`

## Subfeature Execution Planning

- Add or update `slice-planning.md` and `slice-traceability.md` inside this subfeature folder for any new execution work.
- Treat the parent feature docs as baseline context unless impact analysis explicitly narrows or supersedes them.

## Risks and Open Questions

- Which guardrails should be blocking by default versus warning-only to avoid
  noisy false positives in normal workflows?
- How should guardrail findings be serialized so `autoplan`, `ship`, and
  `ship-slice` can all report them consistently?
