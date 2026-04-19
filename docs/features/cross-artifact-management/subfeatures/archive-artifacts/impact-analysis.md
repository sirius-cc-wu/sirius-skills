# Impact Analysis: Archive Artifacts

## Why this subfeature exists

The repo now has audit, trace, report, and repair layers, but maintainers still
need an explicit way to reduce active workflow noise while preserving durable
history. `archive-artifacts` adds that next step conservatively.

## Expected user-visible outcome

- Maintainers can inspect archive candidates across proposals, finalized
  subfeatures, and closed slices.
- The first version can safely archive closed execution slices through the
  existing execution owner helper.
- Archive behavior stays explicit and reviewable; there is no implicit cleanup.
- Summarized slice history in `system-design.md` becomes the primary retained
  narrative, allowing archived slice folders to become optional later cleanup
  targets.

## Affected existing artifacts

- `skills/guide-execution/scripts/manage_execution.py`
- `skills/propose/scripts/manage_proposals.py`
- `skills/add-subfeature/scripts/manage_subfeatures.py`
- `skills/audit-artifacts/scripts/artifact_inventory.py`
- `docs/features/cross-artifact-management/discover.md`
- `docs/features/cross-artifact-management/user-stories.md`

## New artifacts likely required

- `skills/archive-artifacts/SKILL.md`
- `skills/archive-artifacts/scripts/archive_data.py`
- `skills/archive-artifacts/scripts/archive_artifacts.py`
- `skills/archive-artifacts/tests/test_archive_artifacts.py`

## Risks and constraints

- Cross-artifact archive writes are riskier than reporting or repair, so apply
  mode should stay narrow and explicit in v1.
- Execution slices already have an owner-supported archive path; reuse it.
- Proposal and subfeature candidate reporting must not imply unsupported apply
  flows.
- Any future prune step must coordinate with audit/report semantics so pruned
  archived slices are not mistaken for broken active registry state.

## Story and slice framing

- Parent story: `CAM-05` — archive durable history safely
- Planned slice: `arc-safe-slice-archival`
