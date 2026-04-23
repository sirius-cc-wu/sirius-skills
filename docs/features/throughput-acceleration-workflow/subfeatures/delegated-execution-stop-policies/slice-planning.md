# Slice Planning

Use this file to decompose repo stories into execution-ready slices before
bootstrapping execution slices.

## Slice ID Naming

- Default naming: `<scope-prefix>-<capability-slug>`
- Use a short lowercase alias derived from the owning feature slug for
  feature-scoped breakdown.
- Use a short lowercase alias derived from the owning subfeature ID for
  subfeature-scoped breakdown.
- Avoid meaningless generic prefixes such as bare `slice-*` unless a
  repository-specific convention explicitly requires them.

## 0. Subfeature Context

- Parent feature: `throughput-acceleration-workflow`
- Parent feature path: `docs/features/throughput-acceleration-workflow`
- Subfeature ID: `delegated-execution-stop-policies`
- Subfeature type: `additive`
- Current subfeature status: `draft`
- Impact input: `impact-analysis.md` is present and should drive the
  subfeature-local slice plan.

### Affected Story IDs

- `TAW-02`

### Affected Canonical Slice IDs

- `taw-ship-slice-loop`
- `taw-ship-backlog-integration`

### Affected Baseline Artifacts

- `docs/features/throughput-acceleration-workflow/discover.md`
- `docs/features/throughput-acceleration-workflow/system-design.md`
- `docs/features/throughput-acceleration-workflow/user-stories.md`
- `docs/features/throughput-acceleration-workflow/slice-planning.md`
- `docs/features/throughput-acceleration-workflow/slice-traceability.md`

## 1. Planning Scope

- Feature: delegated-execution-stop-policies
- Planning sources:
  - `discover.md`
  - `impact-analysis.md`
  - `system-design.md`
  - parent `docs/features/throughput-acceleration-workflow/user-stories.md`
  - parent `docs/features/throughput-acceleration-workflow/slice-planning.md`
  - parent `docs/features/throughput-acceleration-workflow/slice-traceability.md`
- Execution system: repository-managed slices
- Execution mode: `single-agent`
- Notes:
  - This is subfeature-local breakdown for delegated continuation policy on top
    of the existing accelerator readiness contract.
  - Use `dsp-` as the subfeature slice prefix.
  - Keep parent and sibling planned slice IDs in dependencies or notes only;
    do not reuse them as new subfeature-local slice IDs.

## 2. Story Decisions

| Story ID | Story Size | Story Risk | Decision | Reason | Output Slice Count |
| --- | --- | --- | --- | --- | --- |
| TAW-02 | M | high | split | The config/readiness contract is a separate validation path from delegated continuation behavior, and the second packet depends on the first contract being stable. | 2 |

## 3. Increment Plan

| Increment | Goal / User-Visible Value | Included Story IDs | Planned Slice IDs | Demo / Verification Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | Delegated runs expose one durable continuation-policy contract | TAW-02 | dsp-policy-contract | `ship` and `ship-slice` surface policy-aware readiness with explicit default-stop behavior at review and commit boundaries. | Establish the policy surface first |
| I2 | Delegated runs can continue past selected terminal boundaries | TAW-02 | dsp-boundary-enforcement | With policy enabled, delegated execution continues or stops deterministically at review and commit boundaries without weakening hard-stop guardrails. | Depends on I1 and terminal automation support |

## 4. Execution Slice Backlog

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dsp-policy-contract | TAW-02 | Add continuation policy config and readiness metadata | Extend execution config with a typed `continuation_policy` object and expose policy action/source alongside the existing readiness boundary reporting. | `.skills/execution.json`, `skills/ship/`, `skills/ship-slice/` | primary | `pytest -q skills/ship/tests/test_ship.py skills/ship-slice/tests/test_ship_slice.py` | create slice | taw-ship-backlog-integration | yes |
| dsp-boundary-enforcement | TAW-02 | Apply continuation policy to delegated review and commit boundaries | Teach delegated execution to continue or stop at `review_boundary` and `commit_checkpoint` according to policy while preserving hard-stop behavior for approval, verification, dirty-worktree, and guardrail failures. | `skills/ship/`, `skills/ship-slice/` | primary | `pytest -q skills/ship/tests/test_ship.py skills/ship-slice/tests/test_ship_slice.py` | create slice | dsp-policy-contract, scc-terminal-automation | yes |

## 5. Dependency Notes

- Critical path: `dsp-policy-contract` -> `dsp-boundary-enforcement`.
- Explicit blockers:
  - the policy contract must exist before delegated execution can explain why it
    continued or stopped
  - commit-checkpoint continuation depends on the sibling
    `ship-slice-close-commit-controls` packet providing terminal automation
- Parallel-safe slices: none recommended; both slices touch the same readiness
  and delegated-control surfaces.
- Increment ordering: `I1` -> `I2`.
- Integration checkpoints:
  - after `I1`, verify readiness output exposes both the boundary and the
    policy decision
  - after `I2`, verify review and commit continuation obey policy while hard
    stops still ignore it

## 6. Bootstrap Order

1. `dsp-policy-contract`
2. `dsp-boundary-enforcement`

## 7. Open Questions / Stop-and-Ask Items

- Resolved for MVP: policy is config-only; CLI overrides are deferred.
- Resolved for MVP: only `review_boundary` and `commit_checkpoint` are
  policy-driven in the first rollout.
- Resolved for MVP: approval and dirty-worktree guarantees remain hard stops.

## 8. Review Notes

- Review outcome: Ready for human approval, planning commit, and later `slice`
  bootstrap.
- Blocking findings: none. The packet keeps the first rollout config-driven,
  limits policy to review and commit boundaries, and preserves approval and
  dirty-worktree guarantees as hard stops.
- Handoff note: land the policy contract first, then wire delegated continuation
  behavior on top of it and the sibling terminal-automation packet.
