---
name: add-subfeature
description: Starts and manages durable subfeatures for an existing feature without replacing the parent feature folder.
---

# Add Subfeature

Use this skill when an existing canonical feature needs a durable child planning
folder instead of direct in-place edits to the parent feature plan.

## Responsibilities

1. Resolve the parent feature planning folder under the repository planning layout.
2. Initialize the feature-local `subfeatures/` registry when it does not exist yet.
3. Create one durable subfeature under `docs/features/<feature>/subfeatures/<subfeature-id>/`.
4. Maintain machine-readable subfeature metadata for parent-child and impact context.
5. Seed the subfeature as a real planning folder with its own `.planning-meta.json`.

## Preferred Input

- a parent feature slug, folder name, or path
- a subfeature ID or short slug
- an optional subfeature type such as `additive`, `narrowing`, `superseding`, or `replacement`
- an optional summary of why the feature needs the child capability

## Required Output

- `<feature_path>/subfeatures/README.md`
- `<feature_path>/subfeatures/registry.json`
- `<feature_path>/subfeatures/<subfeature-id>/discover.md`
- `<feature_path>/subfeatures/<subfeature-id>/.planning-meta.json`
- `<feature_path>/subfeatures/<subfeature-id>/.subfeature-meta.json`

## Workflow

1. Resolve the parent feature.
2. Initialize the feature-local subfeature registry with `manage_subfeatures.py init-feature <feature>` when needed.
3. Create the durable child planning folder with `manage_subfeatures.py add <feature> <subfeature-id>`.
4. Write the requested child capability in the subfeature-local `discover.md`.
5. Hand off to `assess`, `design`, `breakdown`, and `review-planning` using the selected subfeature folder.

## Source of Truth Rules

- Keep `docs/features/<feature-slug>/` as the parent feature planning folder.
- Treat `docs/features/<feature-slug>/subfeatures/<subfeature-id>/` as a durable planning folder, not a temporary delta and not an execution slice.
- Do not silently fold subfeature docs back into the parent feature docs.
- Let the subfeature folder keep its own planning lifecycle through `.planning-meta.json`.

## Tooling

```bash
# Initialize the subfeature registry for a canonical feature
python3 skills/add-subfeature/scripts/manage_subfeatures.py init-feature "<feature-slug>"

# Create a new additive subfeature
python3 skills/add-subfeature/scripts/manage_subfeatures.py add "<feature-slug>" "<subfeature-id>"

# Create a superseding subfeature with a short summary
python3 skills/add-subfeature/scripts/manage_subfeatures.py add \
  "<feature-slug>" "<subfeature-id>" \
  --type superseding \
  --summary "Replace legacy checkout path with a durable child capability"

# Advance subfeature state once required artifacts exist
python3 skills/add-subfeature/scripts/manage_subfeatures.py set-status \
  "<feature-slug>" "<subfeature-id>" impact_ready

# Validate one subfeature
python3 skills/add-subfeature/scripts/manage_subfeatures.py validate \
  "<feature-slug>" "<subfeature-id>"
```

## Guardrails

- Do not use this skill for net-new feature discovery; use `guide-planning` and `discover` for that.
- Do not treat subfeatures as execution slices.
- Do not overwrite parent feature docs during subfeature bootstrap.
- Do not use this skill to create speculative work that should stay under `docs/proposals/`.
