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
- Subfeature ID: `ship-slice-close-commit-controls`
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

- Feature: ship-slice-close-commit-controls
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
  - This is subfeature-local breakdown for terminal automation on top of the
    existing `ship-slice` owner chain.
  - Plan only the new or amended slices required by this child capability.
  - Use `scc-` as the subfeature slice prefix.
  - Keep parent slice IDs such as `taw-ship-slice-loop` in dependencies or
    notes only; do not reuse them as new subfeature-local slice IDs.

## 2. Story Decisions

| Story ID | Story Size | Story Risk | Decision | Reason | Output Slice Count |
| --- | --- | --- | --- | --- | --- |
| TAW-02 | L | high | split | Owned-file tracking and formatter safety are a distinct correctness boundary from close/commit orchestration, and they should validate separately. | 2 |

Decision rules:

- `keep` means the story is already small enough to map to one executable slice.
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
| I1 | Delegated terminal automation knows exactly which files it owns | TAW-02 | scc-owned-change-set | `ship-slice` can distinguish owned versus unrelated dirty files, scope formatting to owned files, and stop safely on spillover or same-file conflicts. | Establish safety guardrails first |
| I2 | Delegated runs can optionally format, close, and commit on the happy path | TAW-02 | scc-terminal-automation | With automation enabled, `ship-slice` can format owned files, close the slice, and commit owned changes while preserving partial-success reporting. | Depends on I1 |

## 4. Execution Slice Backlog

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| scc-owned-change-set | TAW-02 | Track owned changes and formatter scope | Snapshot pre-run dirtiness, derive the delegated run's owned file set, scope formatting to owned files, and stop safely on formatter spillover or same-file ownership conflicts. | `skills/ship-slice/` | primary | `pytest -q skills/ship-slice/tests/test_ship_slice.py` | create slice | taw-ship-slice-loop | yes |
| scc-terminal-automation | TAW-02 | Auto-format, close, and commit owned changes | Add `auto_format`, `auto_close`, and `auto_commit`; require `auto_commit` to imply `auto_close`; delegate slice closure and commit creation to existing owners while staging only owned changed files. | `.skills/execution.json`, `skills/ship-slice/`, `skills/close-slice/` | primary | `pytest -q skills/ship-slice/tests/test_ship_slice.py skills/close-slice/tests/test_close_slice.py` | create slice | scc-owned-change-set, taw-ship-backlog-integration | yes |

## 5. Dependency Notes

- Critical path: `scc-owned-change-set` -> `scc-terminal-automation`.
- Explicit blockers:
  - owned-file tracking must exist before terminal automation can safely format
    or commit in a dirty workspace
  - parent delegation semantics from `taw-ship-backlog-integration` remain a
    prerequisite for the final delegated happy path
- Parallel-safe slices: none recommended; both slices touch the same
  `ship-slice` control surface and stop semantics.
- Increment ordering: `I1` -> `I2`.
- Integration checkpoints:
  - after `I1`, verify spillover/conflict detection and unrelated-worktree
    tolerance
  - after `I2`, verify happy-path formatting, closure, owned-file commit, and
    close-then-commit partial success handling

## 6. Bootstrap Order

1. `scc-owned-change-set`
2. `scc-terminal-automation`

## 7. Open Questions / Stop-and-Ask Items

- Resolved for MVP: `auto_commit` implies `auto_close`.
- Resolved for MVP: owned-file staging is mandatory delegated-run behavior,
  not an optional toggle.
- Resolved for MVP: formatter spillover outside the owned file set is a hard
  stop rather than an auto-absorbed side effect.

## 8. Review Notes

- Review outcome: Ready for human approval, planning commit, and later `slice`
  bootstrap.
- Blocking findings: none. The packet keeps format/close/commit behavior behind
  explicit execution config, preserves current owner boundaries, and makes
  owned-file safety the first execution checkpoint.
- Handoff note: prove owned-file safety first, then layer terminal automation on
  top of that contract.
