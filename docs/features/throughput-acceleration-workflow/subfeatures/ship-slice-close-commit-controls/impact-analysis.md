# Impact Analysis: Ship Slice Close Commit Controls

## Scope

Plan the next `ship-slice` increment that extends the delegated execution path
through optional formatting, closure, and commit without weakening ownership or
workspace safety rules.

## Affected Story IDs

- `TAW-02`

## Affected Canonical Slice IDs

- `taw-ship-slice-loop`
- `taw-ship-backlog-integration`

## Affected Baseline Artifacts

- `docs/features/throughput-acceleration-workflow/discover.md`
- `docs/features/throughput-acceleration-workflow/system-design.md`
- `docs/features/throughput-acceleration-workflow/user-stories.md`
- `docs/features/throughput-acceleration-workflow/slice-planning.md`
- `docs/features/throughput-acceleration-workflow/slice-traceability.md`
- `docs/wiki/concepts/two-step-autonomy-roadmap.md`
- `docs/shared/config-surface-governance.md`
- `docs/features/throughput-acceleration-workflow/subfeatures/ship-slice-owner-chain/discover.md`
- `docs/features/throughput-acceleration-workflow/subfeatures/ship-slice-owner-chain/system-design.md`

## Candidate Affected Implementation Areas

- `.skills/execution.json`
- `skills/ship-slice/scripts/ship_slice.py`
- `skills/ship-slice/tests/test_ship_slice.py`
- `skills/close-slice/scripts/close_slice.py`
- `skills/close-slice/tests/test_close_slice.py`
- `skills/commit/SKILL.md`

## Inherited Constraints

- `ship-slice` may orchestrate `close-slice` and `commit`, but those skills keep
  ownership of slice closure semantics and commit-format/convention handling.
- New configuration must stay under the existing typed execution config instead
  of creating a second control plane.
- The two-step workflow keeps approval, invariant failures, and same-file
  ownership conflicts as hard stops even when terminal automation is enabled.
- Formatting must be scoped to the delegated run's owned file set; repo-wide
  formatting is out of scope for the first rollout.

## Impact Notes

- This packet narrows the remaining terminal handoff gap after
  `ship-slice-owner-chain`.
- It introduces Git-mutating behavior after review passes, so partial-success
  reporting and resume semantics matter as much as the happy path.
- The implementation should reuse current readiness and stop-reason reporting so
  delegated runs stay inspectable when formatting, close, or commit stop.
