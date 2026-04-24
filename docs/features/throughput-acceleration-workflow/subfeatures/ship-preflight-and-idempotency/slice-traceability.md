# Slice Traceability

Use this file to map repo story IDs to execution slices without moving story
ownership outside repository planning artifacts.

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
| SPI-01 | M | Document a typed rerun contract for `ship` | I3 | spi-operator-contracts | `skills/ship/SKILL.md`, `docs/wiki/` | spi-mutation-gating | spi-operator-contracts | Docs should reflect the final implemented behavior, not just the design |
| SPI-02 | M | Add optional preflight before mutation-capable `ship` operations | I1 | spi-preflight-contract | `.skills/execution.json`, `skills/ship/` | taw-ship-backlog-integration, taw-runtime-foundation | spi-preflight-contract | Establish config and readiness shape before enforcing blocks |
| SPI-02 | M | Add optional preflight before mutation-capable `ship` operations | I2 | spi-mutation-gating | `skills/ship/`, `skills/ship-slice/` | spi-preflight-contract, taw-ship-slice-loop | spi-mutation-gating | Uses existing approval and commit guardrails as canonical blocker reasons |
| SPI-03 | S | Keep preflight opt-in and repo-owned through typed config | I1 | spi-preflight-contract | `.skills/execution.json`, `skills/ship/` | taw-runtime-foundation |  | Typed ownership is satisfied by the same contract slice as SPI-02 |
| SPI-04 | S | Reflect rerun and preflight behavior in operator guidance | I3 | spi-operator-contracts | `skills/ship/SKILL.md`, `docs/wiki/` | spi-mutation-gating |  | Roadmap and feature wiki should match the shipped operator contract |

## Notes

- `Blocked By` should use execution-slice relationships, not story
  relationships.
- `Planned Slice IDs` records the planned identifiers before slice bootstrap.
- `Execution Slice IDs` records the actual bootstrapped slice IDs after `slice`
  runs.
- `Increments` records planning-level grouping only; do not treat it as an
  execution state.
- The parent feature stories `TAW-02` and `TAW-03` remain lineage context, but
  this subfeature tracks the new child stories `SPI-01` through `SPI-04`
  directly.
