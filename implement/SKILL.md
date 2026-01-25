---
name: implement
description: Executes a detailed implementation plan (plan.md) to build or modify code. This skill is typically activated by the spec-driver skill after a plan has been created by the plan skill. Use this to write code, run tests, and verify implementation against a spec.
---
# Skill: Implement

This skill provides a structured approach for implementing software engineering tasks such as adding features, fixing bugs, or refactoring code, based on a provided specification and plan.

## Core Mandates

- **Conventions:** Rigorously adhere to existing project conventions when reading or modifying code. Analyze surrounding code, tests, and configuration first.
- **Libraries/Frameworks:** NEVER assume a library/framework is available or appropriate. Verify its established usage within the project (check imports, configuration files like 'package.json', 'Cargo.toml', 'requirements.txt', 'build.gradle', etc., or observe neighboring files) before employing it.
- **Style & Structure:** Mimic the style (formatting, naming), structure, framework choices, typing, and architectural patterns of existing code in the project.
- **Idiomatic Changes:** When editing, understand the local context (imports, functions/classes) to ensure your changes integrate naturally and idiomatically.
- **Comments:** Add code comments sparingly. Focus on *why* something is done, especially for complex logic, rather than *what* is done.
- **Proactiveness:** Fulfill the user's request thoroughly. When adding features or fixing bugs, this includes adding tests to ensure quality.
- **Confirm Ambiguity/Expansion:** Do not take significant actions beyond the clear scope of the request without confirming with the user.

## Workflow

This skill is activated by the `spec-driver` when a `plan.md` is ready for implementation.

1.  **Understand**: Review the `plan.md` to fully grasp the implementation steps. Use the `spec.md` as a reference for the overall requirements.
2.  **Implement & Verify (Iteratively)**:
    *   Work through the `plan.md` task by task.
    *   Mark a task as `in_progress` in the `plan.md` before starting.
    *   Write code and unit/integration tests for the task.
    *   Verify the changes using the project's testing, linting, and build procedures.
    *   Once a task is fully verified, mark it as complete (`[x]`) in the `plan.md`.
3.  **Finalize**:
    *   After all tasks in the `plan.md` are complete, run all project verification steps (tests, lint, build) one last time.
    *   Use the `commit` skill to save the changes.
    *   Notify the `spec-driver` that implementation is complete.

## Resource Usage

- **`read_file`**: To understand existing code and the `plan.md`/`spec.md`.
- **`write_file` / `replace`**: For modifying code and creating new files (including tests).
- **`run_shell_command`**: For executing build, test, and linting commands.
- **`commit`**: To finalize changes.
