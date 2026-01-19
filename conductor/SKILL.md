---
name: conductor
description: High-level orchestrator for the design-driven lifecycle.
---

# Conductor Skill (Orchestrator)

This skill manages the transition between Specification, Planning, and Implementation.

## Responsibilities
1. **Discovery**: Look at `specs/README.md` to identify the active track.
2. **Lifecycle Gatekeeping**:
   - If no `spec.md` exists: Redirect to `specify`.
   - If `spec.md` is complete but no `plan.md` exists: Redirect to `plan`.
   - If both exist: Facilitate the `implement` loop.
3. **State Management**: Update the status in `specs/README.md` after each major milestone.

## Tooling
Always use `python3 .github/skills/conductor/scripts/manage_specs.py` for registry updates to ensure cross-platform compatibility.
