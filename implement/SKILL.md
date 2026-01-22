---
name: implement
description: Code implementation expert. Follows the Design-Driven Development lifecycle to execute implementation plans.
---

# Code Implementation Skill

This skill governs the execution phase of the Design-Driven Development lifecycle. It ensures that code matches the `spec.md` and fulfills the atomic steps in `plan.md`.

## Mandatory TDD Implementation Loop

For every task in the implementation phase, follow these steps:

1. **State Synchronization**:
   - Read the current `specs/<ID>-<name>/plan.md`.
   - Identify the next available task (`[ ]`).
   - Sync the `manage_todo_list` tool with the current step.

2. **The Red-Green-Refactor Cycle**:
   - **Step A: Red (Fail)**: Write or update a test case capturing the requirement. Verify it fails.
   - **Step B: Green (Pass)**: Write minimal code required to pass the test. Follow project coding standards (no panics, explicit results).
   - **Step C: Refactor & Verify**: Optimize and run all tests to ensure no regressions.
   - **Step D: Atomic Commit**: Commit the change using the `commit` skill.

3. **Checklist Maintenance**:
   - Mark the task as completed (`[x]`) in `plan.md` IMMEDIATELY after verification.

## Integration with the Lifecycle
- **Conductor**: `implement` is triggered only when `conductor` confirms a valid plan is ready.
- **Commit**: Uses `commit` to ensure project-standard Git messages.
- **Completion**: Once the plan is fully checked, report back to `conductor` for final track closure.
