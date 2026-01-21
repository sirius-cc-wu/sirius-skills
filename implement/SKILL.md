---
name: implement
description: Guide for executing a technical implementation plan iteratively, following TDD practices and updating the plan status.
---

# Implementation Skill

This skill guides the execution of a `plan.md` created by the `plan` skill. It focuses on iterative, test-driven development (TDD) to ensure high-quality code delivery.

## Core Philosophy

-   **Atomic Execution**: Focus on one plan item at a time.
-   **Test-Driven**: Write tests before implementation whenever possible (Red-Green-Refactor).
-   **Continuous Verification**: Verify functionality after every step.
-   **Living Document**: The `plan.md` reflects the current state of reality.

## Workflow

### 1. Select & Analyze
1.  Read the active `plan.md`.
2.  Find the first unchecked item (`- [ ]`). This is your **Current Task**.
3.  Read the relevant context (files, previous steps, `spec.md` if needed).

### 2. Implementation Loop (The "Current Task")

#### A. Test (Red)
If the task involves logic or behavior changes:
1.  Create or modify a test case that replicates the requirement.
2.  Run the test to confirm it fails (or fails to compile if new types are needed).

#### B. Implement (Green)
1.  Write the minimal code necessary to satisfy the test or requirements.
2.  **Constraint**: Do not implement future steps yet.

#### C. Verify
1.  Run the tests.
2.  Run the build/check command (e.g., `cargo check`, `npm run lint`).
3.  Fix any errors.

#### D. Refactor
1.  Review the code for cleanliness, naming, and duplication.
2.  Ensure existing tests still pass.

### 3. Update Status
1.  **IMMEDIATELY** mark the task as completed in `plan.md`: change `- [ ]` to `- [x]`.
2.  Commit the changes (code + plan update) using the `commit` skill standards.

## Handling Blockers
If a step cannot be completed as planned:
1.  **Diverge**: Propose a modification to the plan.
2.  **Report**: Explain why the original plan was insufficient or incorrect.
3.  **Refine**: Update `plan.md` with new sub-steps if the task was too large.
