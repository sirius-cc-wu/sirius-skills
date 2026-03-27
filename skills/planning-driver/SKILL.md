---
name: planning-driver
description: Deprecated alias for guide-planning.
---

# Planning Driver

`planning-driver` remains available as a backward-compatible alias for `guide-planning`.

## Status

- Deprecated for new workflows
- Supported for existing prompts, automation, and repositories

## What to use now

Use `guide-planning` as the canonical planning-layer entrypoint.

Recommended migration:

- prefer the `guide-planning` skill name in prompts and workflow docs
- prefer `skills/guide-planning/scripts/manage_planning.py` in examples and automation
- keep `planning-driver` only when you need compatibility with older instructions

## Scope

This alias still represents the same planning-layer responsibility:

- resolve or initialize the active feature planning folder
- verify planning files, registry state, and metadata
- route work to `discover`, `design`, `ui-flow`, `breakdown`, `review-planning`, or `slice`
- maintain planning readiness state in repository metadata

For the canonical guidance, use `skills/guide-planning/SKILL.md`.
