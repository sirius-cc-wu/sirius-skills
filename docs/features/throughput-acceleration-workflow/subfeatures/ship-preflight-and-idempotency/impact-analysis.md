# Impact Analysis: Ship Preflight And Idempotency

## Target Subfeature

- Parent Feature: `throughput-acceleration-workflow`
- Subfeature ID: `ship-preflight-and-idempotency`
- Subfeature Type: `additive`
- Current Subfeature Status: `impact_ready`

## Subfeature Summary

Add ship idempotency contracts and optional preflight freshness checks for the two-step accelerator path.

## Parent Baseline Reviewed

- `docs/features/throughput-acceleration-workflow/discover.md`
- `docs/features/throughput-acceleration-workflow/system-design.md`
- `docs/features/throughput-acceleration-workflow/user-stories.md`
- `docs/features/throughput-acceleration-workflow/slice-planning.md`
- `docs/features/throughput-acceleration-workflow/slice-traceability.md`
- `docs/wiki/concepts/two-step-autonomy-roadmap.md`
- `docs/wiki/features/throughput-acceleration-workflow.md`
- `docs/shared/config-surface-governance.md`
- `skills/ship/SKILL.md`

## Candidate Affected Story IDs

- `TAW-02`
- `TAW-03`

## Candidate Affected Increment IDs

- `I2`
- `I3`

## Candidate Affected Slice IDs

- `taw-runtime-foundation`
- `taw-ship-handoff`
- `taw-ship-slice-loop`
- `taw-ship-backlog-integration`

## Candidate Affected Implementation Areas

- `.skills/execution.json`
- `skills/ship/SKILL.md`
- `skills/ship/scripts/ship.py`
- `skills/ship/tests/test_ship.py`
- `skills/ship-slice/SKILL.md`
- `skills/ship-slice/scripts/ship_slice.py`
- `skills/ship-slice/tests/test_ship_slice.py`

## Inherited Constraints

- `ship` stays a backlog resolver and optional delegator rather than taking on
  broader release automation responsibilities.
- Any new preflight surface must remain additive to the existing readiness and
  guardrail model instead of creating a second status/control plane.
- Configuration should reuse the existing typed execution-config surface rather
  than introducing ad hoc flags or global process inputs.
- Approval, commit-checkpoint, dirty-worktree, and owned-file safety
  guarantees remain hard boundaries; this subfeature should clarify and front
  load them, not relax them.
- The first rollout should prefer deterministic local evidence over remote or
  host-specific freshness checks.

## Resolved Defaults For Design

- Preflight v1 should stay local-only.
- Preflight should run before execution-state mutation on both
  `ship --bootstrap-next` and `ship --resume`.
- Idempotency guarantees should be phrased as typed rerun contracts:
  what `ship` recomputes, what is mutation-only, and which boundaries still
  intentionally stop progress.

## Impact Notes

- This packet is mostly a `ship` boundary and operator-contract refinement, but
  delegated execution is still affected because `ship --resume` can hand work
  to `ship-slice`.
- The primary parent lineage is `TAW-02` plus the checkpoint/runtime
  expectations from `TAW-03`; this work should stay out of proposal/learn
  scope and should not broaden into workflow-state consistency repair.
- The design should decide whether preflight results become part of the
  existing `readiness` payload, a sibling machine-readable section, or both,
  but should avoid duplicating stop-reason semantics.
- Use this analysis to drive subfeature-local `system-design.md` and later
  `slice-planning.md`.
