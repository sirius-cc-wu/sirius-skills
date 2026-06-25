# Slice Traceability

Use this file to map repo story IDs to execution slices without moving story ownership outside repository planning artifacts.

## Conventions

- Keep repo story IDs exactly as they appear in `user-stories.md`.
- Use planned slice IDs that begin with a feature or subfeature prefix rather
  than bare `slice-*` placeholders unless a repository-specific convention says
  otherwise.
- Use one primary row per repo story. When one story fans out into multiple
  planned slices, add additional rows for that same story so each row keeps
  exactly one planned slice ID.
- List increment IDs as a comma-separated list when a story spans multiple increments.
- List multiple execution slice IDs as a comma-separated list only when a
  single planned slice genuinely maps to more than one execution slice.
- Record only real execution blockers in `Blocked By`.
- Leave `Execution Slice IDs` blank until `slice` bootstraps execution slices.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DALC-01 | M | Markdown file repository | I3 | dalc-repo-markdown | Library | dalc-repo-metadata |  | Consolidates markdown reads/writes |
| DALC-02 | M | Schema-validated metadata | I2 | dalc-repo-metadata | Library | dalc-foundation-guardrail | dalc-repo-metadata | Enforces metadata schemas in repos |
| DALC-03 | M | Relocate scope_runtime & thin commands | I1 | dalc-foundation-storage | Library |  | dalc-foundation-storage | Move scope_runtime and setup storage/models |
| DALC-03 | M | Relocate scope_runtime & thin commands | I2 | dalc-repo-metadata | Commands, Library | dalc-foundation-guardrail |  | Thin command metadata writes |
| DALC-03 | M | Relocate scope_runtime & thin commands | I3 | dalc-repo-markdown | Commands, Library | dalc-repo-metadata |  | Thin command markdown writes |
| DALC-04 | S | Direct filesystem writes guardrail | I1 | dalc-foundation-guardrail | Tests | dalc-foundation-storage | dalc-foundation-guardrail | AST analysis test checking commands |

## Notes

- `Blocked By` should use execution-slice relationships, not story relationships.
- `Planned Slice IDs` records the planned identifiers before slice bootstrap.
- `Execution Slice IDs` records the actual bootstrapped slice IDs after `slice` runs.
- `Increments` records planning-level grouping only; do not treat it as an execution state.
- If a story fans out into multiple executable slices, keep the fan-out here by
  repeating the story row once per planned slice instead of inventing
  story-state outside the planning artifacts.
