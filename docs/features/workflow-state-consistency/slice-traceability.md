# Slice Traceability

Use this file to map repo story IDs to execution slices without moving story ownership outside repository planning artifacts.

## Conventions

- Keep repo story IDs exactly as they appear in `user-stories.md`.
- Use one primary row per repo story.
- List increment IDs as a comma-separated list when a story spans multiple increments.
- List multiple slice IDs as a comma-separated list.
- Record only real execution blockers in `Blocked By`.
- Leave `Execution Slice IDs` blank until `slice` bootstraps execution slices.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WSC-01 | M | Run high-confidence consistency checks around important transitions | I2 | WSC-01-transition-guardrails | Planning, subfeature, and execution transition owners | WSC-03-semantic-preview |  | Reuses the same normalized findings shape established by the preview path before owner scripts warn or block. |
| WSC-02 | M | Share one reconciliation model across maintenance workflows | I1 | WSC-02-shared-library, WSC-02-maintenance-adoption | Shared library, Audit, Trace, Repair, Report | WSC-02-maintenance-adoption -> WSC-02-shared-library |  | Split between canonical library extraction and wrapper adoption so validation stays targeted. |
| WSC-03 | M | Preview semantic workflow drift separately from derived repair | I2 | WSC-03-semantic-preview | Repair preview, Report summaries | WSC-02-maintenance-adoption |  | Keeps semantic drift preview read-only and distinct from owner-mediated repair paths. |
| WSC-04 | S | Detect installed maintenance-skill drift against the repo source | I3 | WSC-04-installed-parity | Parity inspection, Install checks | WSC-02-shared-library |  | Depends only on the shared parity primitives, but is scheduled after I2 so the parity contract reflects stabilized invariants. |
| WSC-05 | M | Fail repeatable validation when durable workflow artifacts disagree | I3 | WSC-05-validation-hooks | Read-only validation entrypoint, CI hooks | WSC-01-transition-guardrails, WSC-04-installed-parity |  | Turns the stabilized guardrails and parity surfaces into automation-friendly validation. |

## Notes

- `Blocked By` should use execution-slice relationships, not story relationships.
- `Planned Slice IDs` records the planned identifiers before slice bootstrap.
- `Execution Slice IDs` records the actual bootstrapped slice IDs after `slice` runs.
- `Increments` records planning-level grouping only; do not treat it as an execution state.
- If a story fans out into multiple executable slices, keep the fan-out here instead of inventing story-state outside the planning artifacts.
