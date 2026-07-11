# Planning Model Simplification Plan

## Goal

Simplify `sirius-skills` toward a clearer planning hierarchy:

```text
feature = story and product context container
subfeature = executable planning and delivery unit
execution slice = implementation unit
```

Stories live at the feature level. Every feature has subfeatures. Execution
planning happens through subfeatures.

Target structure:

```text
docs/features/<feature>/
  discover.md
  user-stories.md
  .planning-meta.json
  subfeatures/
    README.md
    registry.json
    <subfeature>/
      discover.md
      .subfeature-meta.json
      system-design.md
      slice-planning.md
      slice-traceability.md
```

## Phase 1: Document The Target Model

Update methodology and skill docs first so behavior has a clear destination.

| Area | Change |
|---|---|
| `SKILLS_METHODOLOGY.md` | Define feature container, mandatory subfeatures, and feature-owned stories. |
| `skills/discover/SKILL.md` | Say canonical features own `user-stories.md`; subfeatures reference parent story IDs. |
| `skills/add-subfeature/SKILL.md` | Make story linkage part of subfeature creation. |
| `skills/breakdown/SKILL.md` | Prefer subfeature-local breakdown only. |
| `skills/guide-planning/SKILL.md` | Route implementation planning to subfeatures. |

Deliverable: docs clearly describe the new model while current behavior still
works.

## Phase 2: Make Subfeatures Default

Change feature creation so every feature gets a subfeature registry
automatically.

Target scaffold:

```text
docs/features/<feature>/
  discover.md
  user-stories.md
  .planning-meta.json
  subfeatures/
    README.md
    registry.json
```

| File | Change |
|---|---|
| `manage_planning.py` | Ensure `subfeatures/` registry during feature creation. |
| `manage_subfeatures.py` | Keep explicit `init-feature`, but make it idempotent compatibility. |
| `bootstrap.py` | Generated examples should include subfeatures. |
| Tests | Add assertions that new features include `subfeatures/`. |

## Phase 3: Move Story Ownership To Features

Deprecate subfeature-local `user-stories.md`.

New rule:

```text
docs/features/<feature>/user-stories.md = only story catalog
docs/features/<feature>/subfeatures/<subfeature>/discover.md = references parent story IDs
```

Prefer explicit subfeature metadata for parent story linkage:

```json
{
  "story_ids": ["MD-001", "MD-002"]
}
```

| File | Change |
|---|---|
| `manage_subfeatures.py` | Add `story_ids` or replace `affected_story_ids` with clearer parent story linkage. |
| `analyze_impact.py` | Populate subfeature story refs from parent stories. |
| `discover/SKILL.md` | Do not create `user-stories.md` for subfeatures. |
| `breakdown/SKILL.md` | Read parent feature stories for subfeature breakdown. |
| Tests | Cover story refs without subfeature-local story files. |

Compatibility: warn when subfeature-local `user-stories.md` exists, but do not
delete it automatically.

## Phase 4: Make Subfeatures The Delivery Unit

Execution planning should target subfeatures, not parent features.

| Target | Allowed Role |
|---|---|
| Feature | Discovery, user stories, capability grouping. |
| Subfeature | Design, breakdown, review, approval, shipping. |
| Slice | Implementation. |

| File | Change |
|---|---|
| `design/SKILL.md` | Prefer subfeature target for implementation design. |
| `breakdown/SKILL.md` | Prefer subfeature target for slice planning. |
| `review-planning/SKILL.md` | Review subfeatures as normal execution-ready packets. |
| `slice/SKILL.md` | Warn or block direct feature bootstrap unless compatibility mode applies. |
| `ship/SKILL.md` | Prefer subfeatures; feature shipping means shipping all child subfeatures. |

Compatibility: allow direct feature execution temporarily, but emit deprecation
warnings.

## Phase 5: Separate Registries Clearly

Stop mixing feature and subfeature rows in the top-level planning registry.

Current behavior: `docs/features/registry.json` can contain both feature rows
and nested subfeature rows.

Target behavior:

```text
docs/features/registry.json = features only
docs/features/<feature>/subfeatures/registry.json = child subfeatures only
```

| File | Change |
|---|---|
| `manage_planning.py` | Discover only `.planning-meta.json` for top-level registry. |
| `manage_subfeatures.py` | Own subfeature registry fully. |
| `report_data.py` | Build combined views from both registries. |
| `trace_data.py` | Preserve feature -> subfeature -> slice lineage. |
| `repair_data.py` | Repair each registry at its proper level. |

## Phase 6: Simplify Lifecycle State

Collapse feature/subfeature lifecycle confusion.

Recommended ownership:

```text
feature status = discovery/story container status plus derived completion summary
subfeature status = executable planning status
```

Subfeature states can remain close to today:

```text
draft
design_ready
breakdown_ready
reviewed
approved
slice_ready
implemented
```

Key simplification: remove the need to project subfeature state into
`manage-planning` as if it were a feature row.

## Phase 7: Migration Tooling

Add a migration or repair mode before removing compatibility.

Possible command:

```bash
sirius migrate-planning-model
sirius migrate-planning-model --apply
```

| Existing Shape | Migration |
|---|---|
| Feature without `subfeatures/` | Add empty subfeature registry. |
| Subfeature-local `user-stories.md` | Report and optionally merge into parent stories. |
| Feature-level `slice-planning.md` | Report as direct-feature execution legacy. |
| Top-level registry with subfeature rows | Rebuild top-level registry feature-only. |
| Subfeature missing story refs | Infer from discover/impact docs when safe. |

## Phase 8: Update Maintenance Tools

Maintenance commands should still report all artifacts, but from the simplified
hierarchy.

Update:

```text
report-artifacts
audit-artifacts
repair-artifacts
trace-artifacts
archive-artifacts
measure-artifacts
```

Desired hierarchy in output:

```text
feature
  subfeature
    planned slice
      execution slice
```

Avoid treating proposals, features, subfeatures, and slices as flat peers unless
the command explicitly asks for a flat inventory.

## Phase 9: Tests And Rollout

Add tests in stages.

| Test Area | Coverage |
|---|---|
| Feature creation | Always creates subfeature registry. |
| Story ownership | Subfeatures reference parent story IDs. |
| Registry sync | Top-level registry excludes subfeatures. |
| Breakdown | Subfeature uses parent stories. |
| Ship/slice | Subfeature-first routing. |
| Migration | Dry-run reports legacy shapes safely. |
| Audit/report/trace | New hierarchy renders correctly. |

## Recommended Rollout Order

1. Docs and tests for target model.
2. New scaffold behavior.
3. Story reference metadata.
4. Subfeature-first routing.
5. Registry separation.
6. Lifecycle simplification.
7. Migration and compatibility cleanup.

## Definition Of Done

The simplification is complete when a new feature naturally produces this flow:

```text
discover feature
write feature user stories
create one or more subfeatures
design/breakdown/review subfeatures
ship subfeature slices
derive feature progress from child subfeatures
```

No new workflow path should create subfeature-local `user-stories.md` or direct
feature-level execution planning by default.
