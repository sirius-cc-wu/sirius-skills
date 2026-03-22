# Copilot Instructions for `sirius-skills`

This repository contains:
1.  **AI Skills**: A collection of skill definitions (`SKILL.md`) for AI agents.
2.  **Repository guidance**: Top-level docs and installation helpers for the spec-driven workflow.

## 1. AI Skills Development

Located in `skills/`.

### Structure
Each skill is a directory containing:
- **`SKILL.md`**: The definition file with YAML frontmatter (name, description, tools) and Markdown body (instructions).
- **Scripts/Assets**: Helper scripts or templates referenced by the skill.

### Installation
- Use the repository `Makefile` to install skills into the AI agent configuration:
  ```bash
  make install
  ```
  - This uses `npx skills add` to register the managed skills.
- To remove the same managed skill set:
  ```bash
  make uninstall
  ```

## 2. Workflow Conventions (Spec-Driven Development)

This project follows a **Spec-Driven Development (SDD)** lifecycle:

1.  **Discover & Design**: Articulate intent, scope, and architecture before coding.
2.  **Break Down**: Turn stories into execution-ready work items and increments.
3.  **Review Planning**: Use `review-planning` to review planning artifacts before track bootstrap.
4.  **Track**: Bootstrap one task-scoped spec track per implementation-ready work item.
5.  **Execute**: Use `spec-driver`, `define`, and `plan` to create task-scoped execution artifacts, including PlantUML detailed design when it clarifies implementation.
6.  **Review Execution**: Use `review-execution` to compare implementation against task-scoped execution artifacts before closure.
7.  **Close**: Use `close-track` after implementation review and verification are complete.

### PR Guidelines
- **Title Format**: `<ID/Scope>: <summary>`.
- **Validation**: PRs should not be created if `plan.md` has unchecked items.
