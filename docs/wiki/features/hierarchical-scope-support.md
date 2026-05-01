# Hierarchical Scope Support

## Snapshot

- Feature: `hierarchical-scope-support`
- Status: `slice_ready` (updated `2026-04-04`)
- Ready slice IDs: `hss-root-fallback`

## What This Feature Establishes

`hierarchical-scope-support` introduces scope resolution ahead of planning and
execution operations:

- Explicit scope roots are directories containing `.skills/`.
- Resolver chooses nearest enclosing scope, with repository-root fallback.
- Config inheritance merges outer-to-inner scope values, with child overrides.
- Registries remain local to each scope; no global merged registry is added.
- `guide-scope` is a thin routing layer, not a replacement lifecycle.

## Key Tradeoffs

- Strength: supports monorepo and nested-subproject workflows while preserving
  backward compatibility for single-scope repos.
- Cost: scope ambiguity requires explicit selection and stronger CLI discipline.
- Strength: keeps ownership local and avoids cross-scope hidden writes.

## Current Planning State

The feature is implemented in practice, and its parent traceability now uses
one row per planned slice so audits can deterministically map each closed
hierarchical-scope execution slice back to planning without grouped-slice
ambiguity.

## Main Sources

- `docs/features/hierarchical-scope-support/discover.md`
- `docs/features/hierarchical-scope-support/system-design.md`
- `docs/features/hierarchical-scope-support/.planning-meta.json`
