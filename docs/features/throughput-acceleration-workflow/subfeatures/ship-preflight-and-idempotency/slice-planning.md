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
- Subfeature ID: `ship-preflight-and-idempotency`
- Subfeature type: `additive`
- Current subfeature status: `impact_ready`
- Impact input: `impact-analysis.md` is present and should drive the
  subfeature-local slice plan.

### Affected Story IDs

- `TAW-02`
- `TAW-03`
- `SPI-01`
- `SPI-02`
- `SPI-03`
- `SPI-04`

### Affected Canonical Slice IDs

- `taw-runtime-foundation`
- `taw-ship-handoff`
- `taw-ship-slice-loop`
- `taw-ship-backlog-integration`

### Affected Baseline Artifacts

- `docs/features/throughput-acceleration-workflow/discover.md`
- `docs/features/throughput-acceleration-workflow/system-design.md`
- `docs/features/throughput-acceleration-workflow/user-stories.md`
- `docs/features/throughput-acceleration-workflow/slice-planning.md`
- `docs/features/throughput-acceleration-workflow/slice-traceability.md`
- `docs/wiki/concepts/two-step-autonomy-roadmap.md`
- `docs/wiki/features/throughput-acceleration-workflow.md`
- `docs/shared/config-surface-governance.md`
- `skills/ship/SKILL.md`

## 1. Planning Scope

- Feature: ship-preflight-and-idempotency
- Planning sources:
  - `discover.md`
  - `impact-analysis.md`
  - `system-design.md`
  - `user-stories.md`
  - parent `docs/features/throughput-acceleration-workflow/user-stories.md`
  - parent `docs/features/throughput-acceleration-workflow/slice-planning.md`
  - parent `docs/features/throughput-acceleration-workflow/slice-traceability.md`
- Execution system: repository-managed slices
- Execution mode: `single-agent`
- Notes:
  - This is subfeature-local breakdown for `ship` rerun contracts and
    preflight gating on top of the existing accelerator readiness model.
  - Use `spi-` as the subfeature slice prefix.
  - Keep parent slice IDs in dependencies or notes only; do not reuse them as
    new subfeature-local slice IDs.
  - Land the typed preflight contract before mutation gating, then update
    operator docs once behavior is stable.

## 2. Story Decisions

| Story ID | Story Size | Story Risk | Decision | Reason | Output Slice Count |
| --- | --- | --- | --- | --- | --- |
| SPI-01 | M | medium | keep | The rerun contract stays cohesive once the implementation and documentation are phrased by operation class. | 1 |
| SPI-02 | M | high | split | Config plus readiness metadata should stabilize before `ship` starts blocking mutation paths, and the two steps validate differently. | 2 |
| SPI-03 | S | medium | keep | Typed config ownership is part of the first preflight-contract slice and should not drift into a separate control plane. | 1 |
| SPI-04 | S | low | keep | Operator docs can land as one follow-on packet after the contract and gating behavior are in place. | 1 |

Decision rules:

- `keep` means the story is already small enough to map to one executable
  slice.
- `split` means the story fans out into multiple execution-ready slices.
- `defer` means the story is not ready and should not be executed yet.
- split any `XL` story before slice bootstrap
- `S`/`M`/`L` stories may also split when risk, validation shape, coupling, or
  handoff complexity would make one packet brittle
- record the main reason for the decision, not just the size label

Risk rubric:

- `low`: one cohesive packet with one clear validation path
- `medium`: some coupling, multiple touchpoints, or moderate sequencing/handoff
  risk
- `high`: cross-subsystem impact, migration/reconciliation, compatibility risk,
  or materially different validation paths

## 3. Increment Plan

| Increment | Goal / User-Visible Value | Included Story IDs | Planned Slice IDs | Demo / Verification Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | `ship` exposes one typed rerun and preflight contract | SPI-02, SPI-03 | spi-preflight-contract | `ship --json`, `--bootstrap-next`, and `--resume` expose consistent `readiness.preflight` metadata when preflight config is off or local-only. | Establish config and machine-readable contract first |
| I2 | `ship` blocks unsafe mutation before bootstrap or delegated resume | SPI-02 | spi-mutation-gating | With local-only preflight enabled, `ship` stops before bootstrap or delegated resume when approval or commit guardrails fail, and the readiness payload marks the block as preflight. | Depends on I1 |
| I3 | Operators can understand reruns and preflight without reading code | SPI-01, SPI-04 | spi-operator-contracts | Skill and wiki docs explain read-only recomputation, guarded mutation, delegated side effects, and preflight timing. | Depends on I1 and should reflect I2 behavior |

## 4. Execution Slice Backlog

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| spi-preflight-contract | SPI-02 | Add typed `ship` preflight contract and readiness metadata | Parse `accelerators.ship.preflight.mode`, classify mutation-capable operations, and add nested preflight status to `ship` readiness output without changing existing blocker codes. | `.skills/execution.json`, `skills/ship/` | primary | `pytest -q skills/ship/tests/test_ship.py` | create slice | taw-ship-backlog-integration, taw-runtime-foundation | yes |
| spi-mutation-gating | SPI-02 | Gate bootstrap and delegated resume with local-only preflight | Evaluate local preflight before `--bootstrap-next` and mutation-capable `--resume`, reuse approval and commit guardrails as canonical blocker reasons, and mark stop-reason phase as preflight. | `skills/ship/`, `skills/ship-slice/` | primary | `pytest -q skills/ship/tests/test_ship.py skills/ship-slice/tests/test_ship_slice.py` | create slice | spi-preflight-contract, taw-ship-slice-loop | yes |
| spi-operator-contracts | SPI-01 | Document rerun semantics and preflight behavior | Update `skills/ship/SKILL.md` and roadmap/wiki docs so operators know what `ship` recomputes, what mutates, when preflight runs, and why it can block. | `skills/ship/SKILL.md`, `docs/wiki/` | primary | artifact review: `skills/ship/SKILL.md`, `docs/wiki/concepts/two-step-autonomy-roadmap.md`, and `docs/wiki/features/throughput-acceleration-workflow.md` match the implemented contract | create slice | spi-preflight-contract, spi-mutation-gating | yes |

## 5. Dependency Notes

- Critical path:
  `spi-preflight-contract` -> `spi-mutation-gating` -> `spi-operator-contracts`.
- Explicit blockers:
  - the preflight config and readiness contract must exist before mutation
    gating can be made deterministic
  - delegated resume gating depends on the parent `ship-slice` stop-policy and
    handoff behavior already implemented in `taw-ship-slice-loop`
- Parallel-safe slices: none recommended; all three slices touch the same
  `ship` operator contract and should land in sequence
- Increment ordering: `I1` -> `I2` -> `I3`
- Integration checkpoints:
  - after `I1`, verify readiness carries stable nested preflight metadata while
    existing blocker codes stay unchanged
  - after `I2`, verify bootstrap and delegated resume stop before mutation when
    local guardrails fail
  - after `I3`, verify docs match the implemented rerun and preflight contract

## 6. Bootstrap Order

1. `spi-preflight-contract`
2. `spi-mutation-gating`
3. `spi-operator-contracts`

## 7. Open Questions / Stop-and-Ask Items

- Resolved for MVP: preflight mode is `off` or `local_only`; remote freshness
  stays out of scope.
- Resolved for MVP: `--approve` is not part of preflight and keeps its own
  durable write contract.
- Resolved for MVP: preflight reuses existing blocker codes instead of adding a
  new preflight-specific reason taxonomy.

## 8. Review Notes

- Review outcome: Ready for human approval, planning commit, and later `slice`
  bootstrap.
- Blocking findings: none. The packet keeps preflight under the existing
  execution-config owner, reuses the shared readiness model, and limits v1 to
  local evidence before mutation.
- Handoff note: land the machine-readable preflight contract first, then gate
  mutation paths, then update operator docs to match the implemented behavior.
