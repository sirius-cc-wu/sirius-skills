---
name: migrate-slices
description: Migrates execution slices into co-located feature-scoped slice roots with versioned reports.
---

# Migrate Slices

Use this skill when a repository still keeps execution slices in a root-level
slice tree and those slices should be moved into the owning feature scope
without losing archived history.

## Responsibilities

1. Resolve one feature or the full execution tree.
2. Detect active and archived slice rows in the current slice registry.
3. Create or reuse feature-local scope files so the feature can own a local
   `slices/` tree.
4. Move slice directories and rewrite registry paths into the feature-local
   slice root.
5. Emit a versioned JSON migration report with planned, migrated, and blocked
   entries.

## Preferred Input

- a feature slug, folder name, or path when migrating one feature
- or `--all` for a repo-wide migration
- optional `--dry-run` before modifying files

## Required Output

- co-located slices under the owning feature scope
- preserved archived slices under that feature scope's archive subtree
- a versioned JSON report suitable for future migration runs

## Workflow

1. Run `scan` to inspect current slice rows and feature targets.
2. Run `migrate --dry-run` to preview target paths and feature-scope setup.
3. Run `migrate` for one feature or `--all` for the whole execution tree.
4. Review the JSON report for migrated items and any conflicts left behind.

## Guardrails

- Do not overwrite an existing target slice directory.
- Do not delete archived slice history unless it has already been pruned.
- Do not make repository-specific assumptions; resolve config from the current
  repo and active scope.
- Prefer `--dry-run` before repo-wide migration.
