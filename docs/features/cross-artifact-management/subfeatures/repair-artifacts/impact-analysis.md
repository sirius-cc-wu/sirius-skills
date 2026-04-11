# Impact Analysis: Repair Artifacts

## Why this subfeature exists

Audit can now surface registry and metadata drift, but maintainers still need a
supported way to recover from broken active registries after merges, manual
edits, or partial automation. `repair-artifacts` provides that remediation path.

## Expected user-visible outcome

- Maintainers can preview and apply active registry regeneration across
  proposals, features, subfeatures, and slices.
- Repair flows stay conservative, explicit, and reviewable by default.
- The first version focuses on derived registry/readme reconstruction from
  durable directories plus valid metadata, not on rewriting planning content.

## Affected existing artifacts

- `skills/audit-artifacts/scripts/artifact_inventory.py`
- `skills/propose/scripts/manage_proposals.py`
- `skills/guide-planning/scripts/manage_planning.py`
- `skills/add-subfeature/scripts/manage_subfeatures.py`
- `skills/guide-execution/scripts/manage_execution.py`
- `docs/features/cross-artifact-management/discover.md`
- `docs/features/cross-artifact-management/user-stories.md`

## New artifacts likely required

- `skills/repair-artifacts/SKILL.md`
- `skills/repair-artifacts/scripts/repair_data.py`
- `skills/repair-artifacts/scripts/repair_artifacts.py`
- `skills/repair-artifacts/tests/test_repair_artifacts.py`

## Risks and constraints

- Repair must not silently overwrite semantic planning docs.
- Invalid metadata should remain manual follow-up items instead of being
  normalized into potentially incorrect registry rows.
- Dry-run output should clearly describe intended changes before any apply mode.

## Story and slice framing

- Parent story: `CAM-04` — repair artifact drift
- Planned slice: `CAM-04-registry-drift-repair`
