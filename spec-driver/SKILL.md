---
name: spec-driver
description: High-level orchestrator for the spec-driven lifecycle. Use this when starting a new specification, planning, or implementation.
---

# Spec-driver Skill (Orchestrator)

This skill manages the transition between Specification, Planning, and Implementation. It now supports a two-stage specification process: high-level user stories followed by optional, detailed use cases for complex features.

## Workflow & Responsibilities

1.  **Discovery**: Look at `specs/README.md` to identify the active track.
2.  **Lifecycle Gatekeeping**:
    -   **If no `spec.md` exists**:
        1.  Redirect to the `specify` skill to create a `spec.md` with user stories.
        2.  After the user stories are defined, ask the user if any of the stories are complex enough to require a detailed use case.
        3.  If so, redirect to the `use-case` skill to elaborate on the `spec.md`.
    -   **If `spec.md` is complete but no `plan.md` exists**: Redirect to the `plan` skill.
    -   **If both exist**: Facilitate the `implement` loop.
3.  **State Management**:
    -   Update the status in `specs/README.md` after each major milestone.
    -   **CRITICAL**: During the implementation loop, ensure that checkboxes in the active `plan.md` are marked as completed (`[x]`) immediately after the corresponding work is verified.

## Tooling
Always use `scripts/manage_specs.py` for registry updates to ensure cross-platform compatibility. The script supports automatic ID generation or extraction from the branch name.

```bash
# Auto-detect ID from branch name or generate timestamp:
python3 <path-to-spec-driver>/scripts/manage_specs.py add "feature-name"

# To specify an ID manually:
python3 <path-to-spec-driver>/scripts/manage_specs.py add "ID" "feature-name"
```
