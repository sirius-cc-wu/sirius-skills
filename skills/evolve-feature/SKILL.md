---
name: evolve-feature
description: Starts and manages repo-native change packets for an existing feature without replacing the canonical feature folder.
---

# Evolve Feature

Use this skill when an existing canonical feature needs to change and you want a durable, reviewable change packet instead of ad hoc edits to the baseline planning docs.

## Responsibilities

1. Resolve the canonical feature planning folder under the repository planning layout.
2. Initialize the feature-local `changes/` registry when it does not exist yet.
3. Create one change packet under `docs/features/<feature-slug>/changes/<change-id>/`.
4. Maintain machine-readable metadata for change lifecycle state.
5. Enforce the MVP rule that one canonical feature has at most one active open change at a time.

## Preferred Input

- a canonical feature slug, folder name, or path
- a change ID or short slug
- an optional change type such as `additive`, `narrowing`, `superseding`, or `replacement`
- an optional summary of why the feature is changing

## Required Output

- `<feature_path>/changes/README.md`
- `<feature_path>/changes/registry.json`
- `<feature_path>/changes/<change-id>/discover.md`
- `<feature_path>/changes/<change-id>/.feature-change-meta.json`

## MVP Workflow

1. Resolve the canonical feature with `manage_feature_changes.py init-feature <feature>` or by creating a change directly.
2. Create the change packet with `manage_feature_changes.py add <feature> <change-id>`.
3. Write the changed intent in the change-local `discover.md`.
4. Advance state only when the required artifacts exist.
5. Hand off to `impact-analysis`, `design`, `breakdown`, and `review-planning` using the selected change packet.

## Source of Truth Rules

- Keep `docs/features/<feature-slug>/` as the canonical feature planning folder.
- Treat `docs/features/<feature-slug>/changes/<change-id>/` as a planning-scoped delta, not an execution slice.
- Do not silently merge change-packet content back into canonical feature docs.
- Do not allow a second active open change for the same feature in the MVP path unless the user explicitly repairs state.

## Tooling

```bash
# Initialize the change registry for a canonical feature
python3 skills/evolve-feature/scripts/manage_feature_changes.py init-feature "<feature-slug>"

# Create a new additive change packet
python3 skills/evolve-feature/scripts/manage_feature_changes.py add "<feature-slug>" "<change-id>"

# Create a superseding change packet with a short summary
python3 skills/evolve-feature/scripts/manage_feature_changes.py add "<feature-slug>" "<change-id>" --type superseding --summary "Replace legacy checkout path"

# Return the active open change for a feature
python3 skills/evolve-feature/scripts/manage_feature_changes.py get-active "<feature-slug>"

# Advance change state once required artifacts exist
python3 skills/evolve-feature/scripts/manage_feature_changes.py set-status "<feature-slug>" "<change-id>" impact_ready

# Validate one change packet
python3 skills/evolve-feature/scripts/manage_feature_changes.py validate "<feature-slug>" "<change-id>"
```

## Guardrails

- Do not use this skill for net-new feature discovery; use `guide-planning` and `discover` for that.
- Do not treat change packets as execution slices.
- Do not overwrite canonical feature docs during change bootstrap.
- If the feature already has an active open change, stop and resolve that state before creating another one.
