# Impact Analysis: Change To Subfeature Migration

## Parent Feature

- Feature: `planning-workflow`
- Subfeature: `change-to-subfeature-migration`

## Why This Subfeature Exists

The repository has already replaced the live planning model from legacy
`changes/` packets to durable `subfeatures/`. Projects that were bootstrapped
before that migration can still contain old change packets, so the planning
workflow now needs a supported conversion path.

## Affected Baseline Artifacts

- `docs/features/planning-workflow/discover.md`
- `docs/features/planning-workflow/system-design.md`
- `docs/features/planning-workflow/slice-planning.md`
- `docs/features/planning-workflow/subfeatures/subfeature-workflow/discover.md`
- `docs/features/planning-workflow/subfeatures/subfeature-workflow/system-design.md`
- `skills/add-subfeature/scripts/manage_subfeatures.py`
- `skills/guide-planning/scripts/manage_planning.py`
- `README.md`
- `Makefile`

## Affected Behavior

### 1. Planning migration path

Projects need a supported way to move from:

```text
docs/features/<feature>/changes/<change-id>/
```

to:

```text
docs/features/<feature>/subfeatures/<subfeature-id>/
```

without rebuilding planning artifacts by hand.

### 2. Metadata conversion

Legacy change metadata must be mapped into the new durable subfeature model:

- `.feature-change-meta.json` -> `.subfeature-meta.json`
- old change statuses -> current subfeature statuses
- legacy change type -> current subfeature type

### 3. Registry repair

The migration needs to regenerate:

- feature-local `subfeatures/README.md`
- feature-local `subfeatures/registry.json`
- top-level planning registry via `guide-planning`

## Candidate Story and Slice Impact

### Story IDs

- `CTSM-01`
- `CTSM-02`
- `CTSM-03`
- `CTSM-04`

### Planned Slice IDs

- `CTSM-01-scan-legacy-layout`
- `CTSM-02-migrate-change-packets`
- `CTSM-03-docs-and-install`

## Risks

- Legacy repositories may have partially migrated or manually edited `changes/`
  folders.
- Some change packets may be structurally inconsistent with the old workflow.
- Conflicts must stop migration cleanly instead of overwriting existing
  subfeatures.

## Recommended MVP Boundary

- Support one feature or the full planning tree.
- Add `--dry-run` before making changes.
- Refuse to overwrite existing subfeature folders.
- Preserve change content and only rewrite the structural metadata required by
  the new model.
