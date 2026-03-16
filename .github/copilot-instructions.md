# Copilot Instructions for `sirius-skills`

This repository is a monorepo containing:
1.  **`sb-tracker`**: A Python-based, standalone local task tracker using SQLite.
2.  **AI Skills**: A collection of skill definitions (`SKILL.md`) for AI agents.

## 1. `sb-tracker` Development

Located in the `sb-tracker/` directory.

### Build and Install
- **Install from source**:
  ```bash
  cd sb-tracker
  pip install -e .
  ```
- **CLI Usage**: The entry point is `sb`.
  ```bash
  sb --help
  sb init          # Initialize DB
  sb list --all    # List tasks
  ```

### Testing and Linting
- **Run Tests**:
  ```bash
  cd sb-tracker
  PYTHONPATH=src pytest -q
  ```
  - **Coverage**: Enforces >90% coverage.
  - **Single Test**: `PYTHONPATH=src pytest tests/test_cli_context.py`

### Architecture and Data
- **Storage**: SQLite database (default `~/.sb.sqlite`, override with `SB_DB_PATH`).
- **Schema**: Stores normalized `issues`, `issue_dependencies`, `issue_events`.
- **Repo Awareness**: Tracks `repo_path` and `repo_commit` to provide context.
- **Workflow**: `Backlog` -> `Ready` -> `Doing` -> `Review` -> `Done`.

## 2. AI Skills Development

Located in `skills/` and `sb-tracker/skills/`.

### Structure
Each skill is a directory containing:
- **`SKILL.md`**: The definition file with YAML frontmatter (name, description, tools) and Markdown body (instructions).
- **Scripts/Assets**: Helper scripts or templates referenced by the skill.

### Installation
- Use the provided script to install skills into the AI agent configuration:
  ```bash
  ./scripts/install-skills.sh
  ```
  - This utilizes `npx skills add` to register skills.

## 3. Workflow Conventions (Spec-Driven Development)

This project follows a **Spec-Driven Development (SDD)** lifecycle:

1.  **Discover & Design**: Articulate intent and architecture before coding.
2.  **Plan**: Create a `plan.md` file.
    - **Ingest**: `sb import plan.md` to convert the plan into tracked tasks.
3.  **Execute (The Autonomous Loop)**:
    - **Pick**: `sb ready` to find unblocked tasks.
    - **Start**: `sb begin <id>` to capture context.
    - **Verify**: `sb verify <id> --cmd "pytest ..."` to run tests and auto-advance status.
    - **Finish**: `sb finish <id>` (or `sb promote` for documentation).

### PR Guidelines
- **Title Format**: `<ID/Scope>: <summary>` (e.g., `sb-tracker: Add verify command`).
- **Validation**: PRs should not be created if `plan.md` has unchecked items.
