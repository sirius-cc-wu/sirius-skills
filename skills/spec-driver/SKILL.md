---
name: spec-driver
description: High-level orchestrator for the spec-driven lifecycle. Use this when starting a new specification, planning, or implementation.
---

# Spec-driver Skill (Orchestrator)

This skill manages the transition between Specification, Planning, and Implementation.

## Workflow & Responsibilities

1.  **Discovery**: Look at `specs/README.md` to identify the active feature track.
2.  **Lifecycle Gatekeeping**:
    -   **If no `spec.md` exists or the spec is incomplete**:
        1.  Activate the `specify` skill to create or update a `spec.md` with user stories.
        2.  After user stories are defined, ask if any are complex enough for a detailed use case. If so, activate the `use-case` skill to elaborate.
    -   **If `spec.md` is complete but no `plan.md` exists**: Activate the `plan` skill to create a detailed implementation plan.
    -   **If both `spec.md` and `plan.md` exist and are complete**: Activate the `implement` skill to begin code implementation, using the `plan.md` as a guide.
3.  **State Management**:
    -   Update the status in `specs/README.md` after each major milestone (e.g., spec complete, plan complete).
    -   **CRITICAL**: During implementation, the `implement` skill is responsible for marking checkboxes in the active `plan.md` as completed (`[x]`) immediately after the corresponding work is verified.

## Tooling
Always use `scripts/manage_specs.py` for registry updates to ensure cross-platform compatibility. The script supports automatic ID generation or extraction from the branch name.

```bash
# Auto-detect ID from branch name or generate timestamp:
python3 <path-to-spec-driver>/scripts/manage_specs.py add "feature-name"

# To specify an ID manually:
python3 <path-to-spec-driver>/scripts/manage_specs.py add "ID" "feature-name"
```