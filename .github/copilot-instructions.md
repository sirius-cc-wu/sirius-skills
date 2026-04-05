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

1.  **Route Planning**: Use `guide-planning` to resolve the feature planning folder and route to the right planning skill.
2.  **Discover & Design**: Articulate intent, scope, and architecture before coding.
3.  **Break Down**: Turn stories into execution-ready work items and increments.
4.  **Review Planning**: Use `review-planning` to review planning artifacts before track bootstrap.
5.  **Track**: Bootstrap one task-scoped spec track per implementation-ready work item.
6.  **Execute**: Use `spec-driver`, `define`, and `plan` to create task-scoped execution artifacts, including PlantUML detailed design when it clarifies implementation.
7.  **Review Execution**: Use `review-execution` to compare implementation against task-scoped execution artifacts before closure.
8.  **Close**: Use `close-track` after implementation review and verification are complete.

### Skill Boundary Rule

When a planning skill is active, do not advance to the next lifecycle stage unless the user explicitly requests the handoff.

- `propose` ends in `docs/proposals/` unless the user explicitly asks to review, accept, or reject the proposal.
- Promotion from an accepted proposal into `docs/features/` belongs to `guide-planning`, not `propose`.
- Proposal work must not automatically create or update canonical planning in `docs/features/`.
- Planning work must stop after `review-planning` until the user explicitly approves the planning artifacts.
- Approved planning artifacts should be committed before `slice` or any other execution bootstrap begins.
- Planning skills must not automatically bootstrap breakdown, slice, tracking, or execution work.
- Planning skills must not automatically commit planning artifacts without explicit approval.
- Execution or implementation must never start from a proposal-only request.
- If generic agent instructions encourage autonomy or "keep going," the active skill boundary wins.

### PR Guidelines
- **Title Format**: `<ID/Scope>: <summary>`.
- **Validation**: PRs should not be created if `plan.md` has unchecked items.
