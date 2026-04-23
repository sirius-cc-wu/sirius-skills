# Impact Analysis: Delegated Execution Stop Policies

## Scope

Plan the policy layer that decides whether delegated execution continues or
stops when `ship-slice` reaches review and commit boundaries.

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
- `docs/features/throughput-acceleration-workflow/subfeatures/two-step-approval-gate/discover.md`
- `docs/features/throughput-acceleration-workflow/subfeatures/accelerator-readiness-dashboard/discover.md`
- `docs/features/throughput-acceleration-workflow/subfeatures/ship-slice-close-commit-controls/discover.md`

## Candidate Affected Implementation Areas

- `.skills/execution.json`
- `skills/ship/scripts/ship.py`
- `skills/ship/tests/test_ship.py`
- `skills/ship-slice/scripts/ship_slice.py`
- `skills/ship-slice/tests/test_ship_slice.py`

## Inherited Constraints

- Policy must not create a second hidden control plane; it should extend the
  existing typed execution config only.
- Approval and dirty-worktree guarantees stay non-optional.
- Policy decisions must remain visible in readiness output so operators can see
  both the encountered boundary and the continuation choice.
- Commit-checkpoint continuation depends on the terminal automation contract from
  `ship-slice-close-commit-controls`.

## Impact Notes

- This packet is broader than terminal owner execution alone because it affects
  both `ship` backlog delegation and `ship-slice` one-slice finishing.
- The design should be config-first for the first rollout to keep delegated runs
  reproducible and reviewable.
- The shared readiness contract already exists, so the policy layer should reuse
  that surface instead of inventing a parallel status payload.
