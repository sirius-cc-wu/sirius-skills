---
name: conductor
description: High-level orchestrator for the design-driven lifecycle. Use this when starting a new specification, planning, or implementation.
---

# Conductor Skill (Orchestrator)

This skill manages the transition between Specification, Planning, and Implementation.

## Responsibilities
1. **Discovery**: Look at `specs/README.md` to identify the active track.
2. **Lifecycle Gatekeeping**:
   - If no `spec.md` exists: Redirect to `specify`.
   - If `spec.md` is complete but no `plan.md` exists: Redirect to `plan`.
   - If both exist: Facilitate the `implement` loop.
3. **State Management**:
   - Update the status in `specs/README.md` after each major milestone.
   - **CRITICAL**: During the implementation loop, ensure that checkboxes in the active `plan.md` are marked as completed (`[x]`) immediately after the corresponding work is verified.

## Tooling
Always use `scripts/manage_specs.py` for registry updates to ensure cross-platform compatibility. The script supports automatic ID generation or extraction from the branch name.

```bash
# Auto-detect ID from branch name or generate timestamp:
python3 <path-to-conductor>/scripts/manage_specs.py add "feature-name"

# To specify an ID manually:
python3 <path-to-conductor>/scripts/manage_specs.py add "ID" "feature-name"
```
