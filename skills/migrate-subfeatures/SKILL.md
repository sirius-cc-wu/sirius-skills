---
name: migrate-subfeatures
description: Migrates legacy feature-local change packets into durable subfeatures for repositories that still use the old changes/ layout.
---

# Migrate Subfeatures

Use this skill when a repository still contains legacy planning artifacts from
the old change-based workflow and those artifacts need to be converted into the
current durable `subfeatures/` model.

## Responsibilities

1. Resolve one feature or the full planning tree.
2. Detect legacy `changes/<change-id>/` packets.
3. Convert legacy `.feature-change-meta.json` into `.subfeature-meta.json`.
4. Create migrated subfeature folders whose lifecycle is stored in `.subfeature-meta.json`.
5. Rebuild feature-local subfeature registries and resync the planning registry.

## Preferred Input

- a feature slug, folder name, or path when migrating one feature
- or `--all` for a repo-wide migration
- optional `--dry-run` before modifying planning files

## Required Output

- migrated subfeatures under `docs/features/<feature>/subfeatures/<subfeature-id>/`
- rebuilt `subfeatures/README.md` and `subfeatures/registry.json`
- refreshed top-level planning registry via `guide-planning`
- a JSON migration report listing candidates, migrations, and blockers

## Workflow

1. Run `scan` to inspect legacy `changes/` packets and detect blockers.
2. Run `migrate --dry-run` to preview target paths and metadata mapping.
3. Run `migrate` for one feature or `--all` for the whole planning tree.
4. Review the JSON report for migrated items and any conflicts left behind.

## Tooling

```bash
# Scan one feature for legacy change packets
python3 skills/migrate-subfeatures/scripts/migrate_subfeatures.py scan "checkout"

# Scan the whole planning tree
python3 skills/migrate-subfeatures/scripts/migrate_subfeatures.py scan --all

# Preview migration without writing changes
python3 skills/migrate-subfeatures/scripts/migrate_subfeatures.py migrate \
  "checkout" \
  --dry-run

# Migrate every legacy feature in the planning tree
python3 skills/migrate-subfeatures/scripts/migrate_subfeatures.py migrate --all
```

## Guardrails

- Do not overwrite an existing target subfeature folder.
- Do not rewrite discovery, design, or breakdown contents beyond structural
  migration needs.
- Do not use this skill for net-new feature planning; use `guide-planning` and
  `add-subfeature` for those.
- Prefer `--dry-run` before repo-wide migration.
