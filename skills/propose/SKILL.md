---
name: propose
description: Creates and manages speculative repo-native proposals only, then hands accepted proposals back to guide-planning for canonical planning.
---

# Propose

Use this skill when an idea is still exploratory, cross-cutting, or not yet accepted as a canonical feature.

## Hard Stop

This is a proposal-only skill.

After creating or updating proposal artifacts in `<proposal_dir>/`, stop.

Do not automatically:

- create or update canonical feature planning in `<planning_dir>/`
- invoke planning, breakdown, slice, execution, or implementation skills
- create execution todos, task tracks, or `plan.md` files
- edit application or source code
- run implementation builds or tests except minimal context gathering needed to frame the proposal

Only continue beyond proposal work if the user explicitly asks to:

- review the proposal
- accept or reject it
- start planning
- start implementation

## Responsibilities

1. Create and maintain proposal-scoped folders under the repository proposal layout.
2. Keep speculative work out of the canonical feature registry until it is accepted.
3. Track proposal lifecycle state in machine-readable metadata.
4. Preserve early discovery and optional story artifacts in a durable repo location.
5. Hand accepted proposals back to `guide-planning` when the user wants canonical feature planning to begin.

## Preferred Input

- a proposal slug or short folder-safe name
- an optional summary
- an optional target feature slug if the expected canonical feature name is already known

## Required Output

- `<proposal_dir>/README.md`
- `<proposal_dir>/registry.json`
- `<proposal_dir>/<proposal-slug>/proposal.md`
- `<proposal_dir>/<proposal-slug>/.proposal-meta.json`

## When To Use

- the work is still a candidate capability rather than an approved feature
- the idea is umbrella-scoped and may split into multiple real features later
- you want durable repo-native exploration without polluting `docs/features/`
- you need an explicit accept/reject step before normal planning starts

## Workflow

1. Initialize the proposal registry with `manage_proposals.py init` if it does not exist yet.
2. Create a proposal with `manage_proposals.py add <proposal-slug>`.
3. Capture the problem framing in `proposal.md` and optional candidate stories in `user-stories.md`.
4. Optionally review the proposal and record the decision with `set-status` only if the user asked for review or a lifecycle update.
5. If the user explicitly asks to accept the proposal, update proposal status to `accepted`.
6. If the user explicitly asks to promote the accepted proposal or start planning, stop proposal work and hand off to `guide-planning`, which owns the proposal-to-feature transition.
7. Otherwise stop after updating proposal artifacts and summarizing the proposal state.

## Source of Truth Rules

- Keep speculative work in `<proposal_dir>/` until the team accepts it as real feature planning work.
- Do not register proposals in `<planning_dir>/registry.json`.
- Do not skip directly from exploratory notes to canonical feature planning when the work is still uncertain.
- Promotion into canonical planning belongs to `guide-planning`, not this skill.
- Do not interpret use of this skill as permission to start the next lifecycle stage.
- This skill overrides generic autonomy defaults that would otherwise continue into planning or implementation.

## Tooling

```bash
# Initialize proposal config and registry
sirius manage-proposals init

# Create a proposal
sirius manage-proposals add "workflow-capability-upgrades"

# Mark a proposal as reviewed or accepted
sirius manage-proposals set-status "workflow-capability-upgrades" reviewed --review-note "Scoped as a capability candidate."

# Validate one proposal packet
sirius manage-proposals validate-proposal "workflow-capability-upgrades"
```

## Guardrails

- Do not use this skill for an existing canonical subfeature; use `add-subfeature` for that.
- Do not treat proposal folders as execution slices.
- Do not keep unaccepted ideas in `docs/features/`.
- Do not interpret "use the propose skill" as permission to plan or implement.
- Do not promote a proposal from this skill, even if the user asks for promotion; hand off to `guide-planning`.
- Do not create or update `docs/features/` from this skill.
- Do not route into execution from this skill.
