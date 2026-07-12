# Slice Traceability

Use this file to map repo story IDs to execution slices without moving story
ownership outside repository planning artifacts.

## Subfeature Context

- Parent feature: `planning-workflow`
- Subfeature ID: `feature-consolidation-and-reduction`
- Subfeature type: `superseding`
- Use `Planned Slice IDs` for the new or amended slices defined by this
  subfeature.
- Keep subfeature-local traceability in this folder instead of folding it back
  into parent feature breakdown docs.
- Record affected canonical slice IDs such as `pw-registry`,
  `pw-breakdown-guidance`, and `pw-review-readiness` in `Notes`, not
  `Execution Slice IDs`.

## Conventions

- Keep repo story IDs exactly as they appear in `user-stories.md`.
- Use planned slice IDs that begin with a feature or subfeature prefix rather
  than bare `slice-*` placeholders unless a repository-specific convention says
  otherwise.
- Use one primary row per repo story. When one story fans out into multiple
  planned slices, add additional rows for that same story so each row keeps
  exactly one planned slice ID.
- List increment IDs as a comma-separated list when a story spans multiple
  increments.
- List multiple execution slice IDs as a comma-separated list only when a
  single planned slice genuinely maps to more than one execution slice.
- Record only real execution blockers in `Blocked By`.
- Leave `Execution Slice IDs` blank until `slice` bootstraps execution slices.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FCR-01 | M | Require consolidation declarations in planning authoring | I1 | fcr-declaration-contract | discover and add-subfeature guidance |  |  | Seeds the durable declaration contract before review enforcement or maintenance consumption. |
| FCR-03 | M | Record active versus historical outcomes durably | I1 | fcr-metadata-summary | planning and subfeature metadata carriers | fcr-declaration-contract |  | Introduces one compact consolidation summary in existing metadata files rather than a new sidecar artifact. |
| FCR-02 | M | Flag additive-only expansion during planning review | I2 | fcr-review-gate | review-planning guidance, planning validation | fcr-metadata-summary |  | Makes missing or contradictory reduction stories blocking when overlap exists. |
| FCR-04 | S | Keep the user-facing planning surface canonical and simpler | I2 | fcr-canonical-surface | guide-planning, README, methodology docs | fcr-review-gate |  | Explains which planning path remains canonical after consolidation and which surfaces become historical. |
| FCR-03 | M | Record active versus historical outcomes durably | I3 | fcr-history-consumers | trace, report, archive inventory and outputs | fcr-metadata-summary, fcr-review-gate |  | Reuses the durable consolidation summary in maintenance skills without inventing a second workflow-state model. |

## Notes

- `Blocked By` uses execution-slice relationships between planned slices.
- `Planned Slice IDs` records the planned identifiers before slice bootstrap.
- `Execution Slice IDs` records the actual bootstrapped slice IDs after `slice`
  runs.
- `Increments` records planning-level grouping only; do not treat it as an
  execution state.
- Affected parent slices remain baseline context only; this subfeature does not
  reuse parent slice IDs as new planned slices.
