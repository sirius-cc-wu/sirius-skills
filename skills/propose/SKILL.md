---
name: propose
description: Creates and manages speculative repo-native proposals before they become canonical feature planning folders.
---

# Propose

Use this skill when an idea is still exploratory, cross-cutting, or not yet accepted as a canonical feature.

## Responsibilities

1. Create and maintain proposal-scoped folders under the repository proposal layout.
2. Keep speculative work out of the canonical feature registry until it is accepted.
3. Track proposal lifecycle state in machine-readable metadata.
4. Preserve early discovery and optional story artifacts in a durable repo location.
5. Promote accepted proposals into canonical feature planning folders when the work is ready.

## Preferred Input

- a proposal slug or short folder-safe name
- an optional summary
- an optional target feature slug if the expected canonical feature name is already known

## Required Output

- `<proposal_dir>/README.md`
- `<proposal_dir>/registry.json`
- `<proposal_dir>/<proposal-slug>/discover.md`
- `<proposal_dir>/<proposal-slug>/.proposal-meta.json`

## When To Use

- the work is still a candidate capability rather than an approved feature
- the idea is umbrella-scoped and may split into multiple real features later
- you want durable repo-native exploration without polluting `docs/features/`
- you need an explicit accept/reject/promote step before normal planning starts

## Workflow

1. Initialize the proposal registry with `manage_proposals.py init` if it does not exist yet.
2. Create a proposal with `manage_proposals.py add <proposal-slug>`.
3. Capture the problem framing in `discover.md` and optional candidate stories in `user-stories.md`.
4. Review the proposal and record the decision with `set-status`.
5. When the proposal is accepted, run `promote` to create the canonical feature planning folder.

## Source of Truth Rules

- Keep speculative work in `<proposal_dir>/` until the team accepts it as real feature planning work.
- Do not register proposals in `<planning_dir>/registry.json`.
- Do not skip directly from exploratory notes to canonical feature planning when the work is still uncertain.
- Promotion should create a feature planning folder, not silently overwrite one that already exists.

## Tooling

```bash
# Initialize proposal config and registry
python3 skills/propose/scripts/manage_proposals.py init

# Create a proposal
python3 skills/propose/scripts/manage_proposals.py add "workflow-capability-upgrades"

# Mark a proposal as reviewed or accepted
python3 skills/propose/scripts/manage_proposals.py set-status "workflow-capability-upgrades" reviewed --review-note "Scoped as a capability candidate."

# Promote an accepted proposal into feature planning
python3 skills/propose/scripts/manage_proposals.py promote "workflow-capability-upgrades" --feature-slug "workflow-capability-upgrades"

# Validate one proposal packet
python3 skills/propose/scripts/manage_proposals.py validate-proposal "workflow-capability-upgrades"
```

## Guardrails

- Do not use this skill for an existing canonical feature change; use `evolve-feature` for that.
- Do not treat proposal folders as execution slices.
- Do not promote a proposal into an already-existing feature folder unless the user is explicitly repairing state.
- Do not keep unaccepted ideas in `docs/features/`.
