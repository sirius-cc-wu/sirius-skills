# Discover: Ship Preflight And Idempotency

## Parent Feature

- Feature: `throughput-acceleration-workflow`
- Subfeature ID: `ship-preflight-and-idempotency`
- Subfeature Type: `additive`

## Problem

The two-step autonomy path is now mostly implemented, but `ship` still leaves
two operator-facing gaps in the execution handoff experience:

- rerun behavior is real but not explained as an explicit idempotency contract
- there is no optional preflight surface that can tell an operator whether
  bootstrap or resume should stop before mutating execution state

That creates avoidable uncertainty in the happy path described by
`docs/wiki/concepts/two-step-autonomy-roadmap.md`:

1. `autoplan --execute-owner-chain`
2. human review
3. `ship --approve`
4. `ship --resume`

Today, a maintainer can often rerun `ship`, but the repo does not clearly say
which parts are always recomputed, which parts are mutation-only, and which
conditions should block before bootstrap or delegated execution begins.

## Goals

- Make `ship` rerun and resume behavior explicit as a durable idempotency
  contract.
- Add an optional, config-driven preflight check before `ship` mutates
  execution state.
- Preserve the current design boundary where `ship` remains a backlog
  resolver and optional delegator rather than becoming release automation.
- Return deterministic stop context when preflight checks fail.
- Improve operator confidence in the two-step accelerator path without
  weakening approval, commit, or ownership boundaries.

## Non-Goals

- Turn `ship` into PR, deployment, or release automation.
- Make branch-freshness or remote-state checks mandatory for every repo.
- Replace existing `readiness` output with a second status model.
- Relax commit-checkpoint, approval, or dirty-worktree guardrails.
- Move execution ownership out of `ship-slice`, `close-slice`, or `commit`.

## Requested Subfeature

- Define explicit rerun guarantees for `ship` and delegated `ship-slice`
  handoff behavior.
- Add one optional preflight contract that can run before `--bootstrap-next`
  or `--resume`.
- Keep preflight additive to current backlog resolution, approval gating, and
  readiness reporting.
- Limit the first version to checks that improve execution confidence without
  introducing broad product-specific policy.

## Consolidation Expectations

- No valid consolidation target is required for this packet.
- This work is additive: it clarifies and strengthens the current
  accelerator/operator surface rather than superseding an existing skill.
- User-facing simplification:
  operators should be able to tell when rerunning `ship` is safe and when
  preflight wants them to stop before execution state changes.

## Primary Actors

- Maintainer using the two-step autonomy path as the default happy path.
- Reviewer who wants automation to stay explicit about what is safe to rerun.
- Repository author who may want stricter preflight checks in one repo without
  making them global defaults.

## Constraints

- Planning and execution artifacts remain source of truth.
- Any preflight surface must remain optional and configuration-driven.
- `ship` must keep standalone backlog-resolution ownership even when
  delegation is enabled.
- Stop reasons should fit the existing shared readiness/guardrail model rather
  than inventing a parallel classifier.
- Checks should prefer deterministic local evidence first; any stronger
  freshness policy must be explicit and non-default.

## Baseline Artifacts To Assess

- parent `discover.md`
- parent `system-design.md`
- parent `user-stories.md`
- `skills/ship/SKILL.md`
- `skills/ship/scripts/ship.py`
- `skills/ship-slice/SKILL.md`
- `docs/wiki/concepts/two-step-autonomy-roadmap.md`
- `docs/wiki/features/throughput-acceleration-workflow.md`

## Candidate Capability Areas

- **Idempotency contract**
  - document what `ship` always recomputes from repo artifacts
  - document which actions are mutation-only
  - make rerun guarantees explicit for backlog resolution, bootstrap,
    approval, and delegated resume

- **Preflight checks**
  - add an optional preflight surface before `--bootstrap-next` or `--resume`
  - report why a run should stop before mutating execution state
  - keep checks typed and compatible with existing readiness output

- **Config surface**
  - add execution config that enables or scopes preflight behavior
  - keep defaults conservative and non-blocking unless explicitly enabled

- **Operator docs**
  - update skill and wiki docs so the two-step happy path explains rerun and
    preflight behavior concretely

## Desired Outcomes

- Operators know whether rerunning `ship` is safe and what it will recompute.
- Repos that want extra safety can enable preflight checks before bootstrap or
  resume.
- Preflight failures show up as explicit, machine-readable stop context rather
  than ad hoc stderr-only guidance.
- The two-step roadmap becomes more operationally trustworthy without expanding
  `ship` into a broader automation product.

## Success Criteria

- Discovery is concrete enough for design to choose one preflight contract and
  config surface.
- The subfeature produces stable story IDs for idempotency, preflight, config,
  and operator documentation work.
- The planned work remains clearly outside the workflow-state consistency
  branch.

## Subfeature Execution Planning

- Add or update `slice-planning.md` and `slice-traceability.md` inside this
  subfeature folder for any new execution work.
- Treat the parent feature docs as baseline context unless impact analysis
  explicitly narrows or supersedes them.

## Risks and Resolved Design Defaults

- Resolved for the first rollout: preflight stays local-only and does not
  inspect remote branch state or host-specific freshness signals.
- Resolved for the first rollout: preflight runs on both
  `ship --bootstrap-next` and `ship --resume`, but only as a gate before
  mutation-capable behavior.
- Resolved for the first rollout: idempotency is phrased as a typed rerun
  contract that separates recomputation, guarded mutation, and delegated
  execution side effects.
- Remaining risk: if future repos want remote freshness checks, the extension
  should stay under the same typed `accelerators.ship.preflight` owner rather
  than adding a second control surface.
