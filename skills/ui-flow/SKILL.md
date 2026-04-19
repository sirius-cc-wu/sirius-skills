---
name: ui-flow
description: Captures optional UI and UX flows, screen-level requirements, and interaction notes before implementation.
---

# UI Flow

Use this skill when a project needs screen flows, interaction requirements, or UX notes before implementation work is decomposed.

## Responsibilities

1. Capture user journeys, states, and interaction boundaries.
2. Define screen-level requirements, transitions, and edge cases.
3. Record UX constraints that should influence system design or slice breakdown.
4. Keep UI decisions in repository documents instead of burying them in ad hoc execution notes.

## Required Output

- `<feature_path>/ui-design.md`

Optional companion output:

- updates to `<feature_path>/user-stories.md`
- links to mockups or external design references

## Feature Path Resolution

Resolve `<feature_path>` as `<planning_dir>/<feature-slug>/`.

- If `.skills/planning.json` defines `planning_dir`, use that as `<planning_dir>`.
- Otherwise default to `docs/features`.

## Workflow

1. Read `discover.md` and `system-design.md` when present.
2. Capture flows, states, and notable UX constraints.
3. Write `ui-design.md` with screen-level requirements and edge cases.
4. Refine story boundaries or acceptance notes if the UI changes scope.
5. Run `python3 skills/guide-planning/scripts/manage_planning.py sync-status <feature-selector> --through design_ready` when the feature requires UI flow so metadata catches up once the design packet is complete.
6. Stop when the UI work is concrete enough for `breakdown`.

## Guardrails

- Keep the output lightweight and implementation-relevant.
- Do not create implementation slices from UX notes alone.
- If the project has no meaningful UI surface, skip this skill.
