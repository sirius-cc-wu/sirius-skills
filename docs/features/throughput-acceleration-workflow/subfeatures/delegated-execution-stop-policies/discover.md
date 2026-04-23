# Discover: Delegated Execution Stop Policies

## Parent Feature

- Feature: `throughput-acceleration-workflow`
- Subfeature ID: `delegated-execution-stop-policies`
- Subfeature Type: `additive`

## Problem

Add operator policy controls for when delegated execution continues or stops at review and commit boundaries.

## Requested Subfeature

- Add explicit policy controls for delegated `ship` -> `ship-slice` execution so
  operators can choose which boundaries are advisory and which remain hard
  stops.
- Cover at least review and commit-checkpoint boundaries, with room for later
  extension to other deterministic stop reasons.
- Keep the policy layer additive to readiness reporting; it should influence
  whether the accelerator continues, not hide why a boundary was encountered.
- Preserve safe defaults so repositories that do not opt in still stop at the
  current review and commit boundaries.

## Why This Is Separate

- This is operator-policy work, not terminal owner execution itself.
- It affects both delegated backlog mode in `ship` and one-slice finishing in
  `ship-slice`, so it is broader than the close/commit control packet.
- The roadmap lists this as the step after close/commit automation, which makes
  it easier to reason about separately.

## Candidate Scope

- `.skills/execution.json` policy toggles for delegated continuation behavior
- `skills/ship/scripts/ship.py`
- `skills/ship-slice/scripts/ship_slice.py`
- readiness payload and stop-reason handling
- accelerator tests covering delegated continuation behavior

## Baseline Artifacts To Assess

- `discover.md`
- `system-design.md`
- `user-stories.md`
- `docs/wiki/concepts/two-step-autonomy-roadmap.md`
- `subfeatures/ship-slice-owner-chain/discover.md`
- `subfeatures/two-step-approval-gate/discover.md`
- `subfeatures/accelerator-readiness-dashboard/discover.md`

## Subfeature Execution Planning

- Add or update `slice-planning.md` and `slice-traceability.md` inside this subfeature folder for any new execution work.
- Treat the parent feature docs as baseline context unless impact analysis explicitly narrows or supersedes them.

## Resolved Defaults

- First-rollout policy is config-only; one-off CLI overrides are deferred.
- Only `review_boundary` and `commit_checkpoint` are policy-driven in the first
  implementation.
- `approval_required`, dirty-worktree safety, verification failure, and
  transition-guardrail failures remain unconditional hard stops.
- Readiness output should expose both the encountered boundary and the policy
  action that was applied.
- Policy should remain additive to stop reporting; it changes whether the run
  continues, not whether the boundary is visible.

## Remaining Risks

- Policy and terminal automation must stay coherent so continuation never jumps
  past a required owner that has not actually run.
- Readiness output can become harder to interpret if policy metadata is bolted
  on inconsistently between `ship` and `ship-slice`.
