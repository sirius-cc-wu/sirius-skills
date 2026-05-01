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
| HSS-01 | M | Keep the repository root as a valid planning scope | I1 | hss-root-fallback | Scope runtime, Root fallback |  | hss-root-fallback | Bootstrapped as `slices/hss-root-fallback-add-scope-runtime-with-root-fallback/`; establishes the compatibility baseline that later nested-scope behavior builds on. |
| HSS-02 | M | Give nested directories local planning and proposal workspaces | I1 | hss-local-registries | Planning registry, Proposal registry | hss-root-fallback | hss-local-registries | Keeps feature and proposal registries local to the resolved scope. |
| HSS-03 | M | Default to the nearest enclosing scope from the working directory | I1 | hss-nearest-scope | CLI scope resolution | hss-root-fallback, hss-local-registries | hss-nearest-scope | Depends on both the shared resolver and local registry ownership semantics. |
| HSS-04 | M | Stop for explicit scope selection when multi-scope lookups are ambiguous | I2 | hss-scope-selection | Ambiguity guards | hss-nearest-scope | hss-scope-selection | Generic ambiguity handling lands first and establishes the safe multi-scope lookup boundary. |
| HSS-04 | M | Stop for explicit scope selection when multi-scope lookups are ambiguous | I2 | hss-promotion-targeting | Promotion routing | hss-scope-selection | hss-promotion-targeting | Cross-scope promotion targeting is the second half of the same story and depends on explicit scope-selection behavior. |
| HSS-05 | L | Add one scope-entry skill instead of duplicating workflows | I4 | hss-guide-scope | Scope routing, Skill docs | hss-promotion-targeting, hss-scoped-execution | hss-guide-scope | Depends on stable planning and execution scope contracts before documenting user-facing routing. |
| HSS-06 | L | Let child scopes override parent config and keep execution local | I2 | hss-config-inheritance | Config merge | hss-nearest-scope | hss-config-inheritance | Config inheritance lands before scoped execution so nested scope behavior is deterministic. |
| HSS-06 | L | Let child scopes override parent config and keep execution local | I3 | hss-scoped-execution | Execution and slices | hss-config-inheritance | hss-scoped-execution | Scope-local execution builds on the inherited config contract and validates separately. |

## Notes

- `Blocked By` should use execution-slice relationships, not story relationships.
- `Planned Slice IDs` records the planned identifiers before slice bootstrap.
- `Execution Slice IDs` records the actual bootstrapped slice IDs after `slice` runs.
- `Increments` records planning-level grouping only; do not treat it as an execution state.
- If a story fans out into multiple executable slices, keep the fan-out here instead of inventing story-state outside the planning artifacts.
