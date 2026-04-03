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
| HSS-01 | M | Keep the repository root as a valid planning scope | I1 | HSS-01-root-fallback | Scope runtime, Root fallback |  | HSS-01-root-fallback | Bootstrapped as `slices/HSS-01-root-fallback-add-scope-runtime-with-root-fallback/`; establishes the compatibility baseline that later nested-scope behavior builds on. |
| HSS-02 | M | Give nested directories local planning and proposal workspaces | I1 | HSS-02-local-registries | Planning registry, Proposal registry | HSS-01-root-fallback | HSS-02-local-registries | Keeps feature and proposal registries local to the resolved scope. |
| HSS-03 | M | Default to the nearest enclosing scope from the working directory | I1 | HSS-03-nearest-scope | CLI scope resolution | HSS-01-root-fallback, HSS-02-local-registries | HSS-03-nearest-scope | Depends on both the shared resolver and local registry ownership semantics. |
| HSS-04 | M | Stop for explicit scope selection when multi-scope lookups are ambiguous | I2 | HSS-04-scope-selection, HSS-04-promotion-targeting | Ambiguity guards, Promotion routing | HSS-03-nearest-scope | HSS-04-scope-selection | Split between generic lookup ambiguity and the explicit cross-scope promotion contract. |
| HSS-05 | L | Add one scope-entry skill instead of duplicating workflows | I4 | HSS-05-guide-scope | Scope routing, Skill docs | HSS-04-promotion-targeting, HSS-06-scoped-execution |  | Depends on stable planning and execution scope contracts before documenting user-facing routing. |
| HSS-06 | L | Let child scopes override parent config and keep execution local | I2, I3 | HSS-06-config-inheritance, HSS-06-scoped-execution | Config merge, Execution and slices | HSS-03-nearest-scope |  | Separates config precedence from scope-local execution integration because the validation paths differ materially. |

## Notes

- `Blocked By` should use execution-slice relationships, not story relationships.
- `Planned Slice IDs` records the planned identifiers before slice bootstrap.
- `Execution Slice IDs` records the actual bootstrapped slice IDs after `slice` runs.
- `Increments` records planning-level grouping only; do not treat it as an execution state.
- If a story fans out into multiple executable slices, keep the fan-out here instead of inventing story-state outside the planning artifacts.
