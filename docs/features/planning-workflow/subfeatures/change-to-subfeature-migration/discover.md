# Discover: Change To Subfeature Migration

## Parent Feature

- Feature: `planning-workflow`
- Subfeature ID: `change-to-subfeature-migration`
- Subfeature Type: `additive`

## Problem

Some repositories already contain planning artifacts produced by the old
change-based workflow:

- feature-local `changes/<change-id>/` folders
- change metadata such as `.feature-change-meta.json`
- reviewed or partially completed change packets that still need to remain
  usable after the repo adopts durable subfeatures

Once the planning model settles on `subfeatures/`, teams need a supported way to
convert those legacy change packets into the new structure without losing
history, links, or readiness state.

Without an explicit migration capability, users are forced to rename folders and
metadata by hand, which is risky and inconsistent across repositories.

## Goals

- Add a repo-native migration skill or helper that converts legacy
  `changes/<change-id>/` packets into durable
  `subfeatures/<subfeature-id>/` folders.
- Preserve meaningful planning history, including summaries, status, and
  affected-artifact context.
- Map old change metadata and lifecycle states into the new subfeature model.
- Detect conflicts early instead of silently overwriting existing subfeatures.
- Make migration idempotent or clearly restartable when a repository is only
  partially migrated.

## Non-Goals

- Re-plan migrated content from scratch.
- Automatically redesign or rewrite the semantic contents of discovery, design,
  or breakdown docs beyond what is needed for structural migration.
- Migrate execution slices themselves into a new execution model.
- Support arbitrary historical layouts unrelated to the old
  `evolve-feature` / `reconcile-feature` workflow.

## Requested Capability

- Scan one feature or an entire planning tree for legacy `changes/` folders.
- Convert each change packet into a subfeature folder under the same parent
  feature.
- Rename and translate legacy metadata fields into `.subfeature-meta.json`.
- Repair or regenerate feature-local registries after migration.
- Produce a clear migration report showing converted items, skipped items, and
  conflicts needing manual attention.

## Candidate Inputs

- a parent feature path or feature slug
- an optional repository-wide mode for bulk migration
- an optional dry-run mode before writing changes
- an optional explicit mapping override when a change ID should not become the
  final subfeature ID

## Baseline Artifacts To Assess

- legacy `changes/<change-id>/` folders under `docs/features/<feature>/`
- `.feature-change-meta.json`
- parent feature `discover.md`, `system-design.md`, `slice-planning.md`, and
  `slice-traceability.md`
- any feature-local change registry or references that still point at the old
  path layout

## Constraints

- Preserve the parent feature as the canonical anchor; only the child planning
  layout should move.
- Do not overwrite an existing `subfeatures/<subfeature-id>/` folder without an
  explicit repair path.
- Keep the migration auditable and deterministic.
- Prefer a repo-managed helper or skill over ad hoc shell instructions.
- Keep the migrated output compatible with `guide-planning`, `assess`,
  `breakdown`, and `finalize-subfeature`.

## Success Criteria

- A maintainer can migrate one legacy change packet into a valid durable
  subfeature with correct metadata and path layout.
- A maintainer can run the migration across a repo and then resync planning
  registries successfully.
- The migrated subfeature validates under the new subfeature lifecycle rules.
- Users get actionable errors when migration cannot proceed cleanly.

## Risks and Open Questions

- Which legacy change statuses should map directly to `draft`, `impact_ready`,
  `design_ready`, `breakdown_ready`, `reviewed`, or `finalized`?
- Should the first version migrate one selected feature at a time, or support
  whole-repo bulk migration immediately?
- Should migration write backlink notes into the migrated docs, or keep the
  change content untouched apart from structural updates?
- How should the tool behave when a repository has both old `changes/` folders
  and manually created `subfeatures/` for the same parent feature?
