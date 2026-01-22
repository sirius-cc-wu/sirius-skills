---
name: design
description: Architecture and prototyping expert (Design-Driven Development).
---

# Design Skill (DDD)

Use this skill to produce `design.md` artifacts focused on architecture, prototypes, and implementation strategy. `design` supports iterative exploration and should be used when the work is not interface-critical or when architecture-first prototyping is preferred.

## Goals
- Capture architecture diagrams, decision records, tradeoffs, and incremental prototypes.
- Produce a `design.md` that documents choices, alternatives considered, and migration or compatibility notes.

## Workflow
1. Create or update `design.md` in the track folder.
2. Iterate via prototypes and recorded design decisions.
3. If the track later becomes interface-critical, add a `spec.md` (use `specify`) and run `scripts/manage_specs.py validate-spec`.

## Handoff
- When ready, hand to `plan` for TDD mapping; `conductor` will enforce spec validation if required for implementation.
