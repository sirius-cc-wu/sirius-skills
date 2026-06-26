# src/ Use Cases (reverse-engineered)

This page summarises the primary use cases implemented by the src/ package in sirius-skills. Each entry lists actors, a short description, steps, and the modules most involved.

## Actors
- User (developer or automation invoking the CLI)
- CI / Automation (scripts, GitHub Actions)
- Skills subsystem (extensions in skills/)

## 1) Run CLI commands (primary entrypoint)
- Actors: User, CI
- Description: Invoke `sirius <command>` to run a command supplied by PACKAGE_COMMANDS.
- Steps: CLI discovers commands -> loads module -> calls main() -> command uses workflow_state and workflow_runtime -> returns exit code.
- Files/modules: src/sirius_skills/cli.py, src/sirius_skills/commands/*, src/sirius_skills/paths.py
- Examples: `sirius bootstrap`, `sirius autoplan`.

## 2) Manage planning registries and metadata
- Actors: CLI commands, repository maintainers
- Description: Create/read/write planning registries (README, registry.json) and per-feature metadata (.planning-meta.json).
- Steps: Command calls planning_repository.ensure_registry/read_registry_json/write_metadata_raw.
- Files/modules: lib/workflow_state/planning_repository.py, storage.py, markdown_repository.py
- Examples: register features, update registry after bootstrapping.

## 3) Bootstrap and scaffold features/slices
- Actors: User, scaffold commands
- Description: Create feature and slice scaffolding including README and registry entries.
- Steps: scaffold command generates files, updates registries, and initialises metadata.
- Files/modules: commands/bootstrap.py, commands/bootstrap_slice.py, commands/scaffold_design.py, lib/workflow_state/*

## 4) Autoplan & planning automation
- Actors: Automation, planner commands
- Description: Produce automated plans or suggestions for feature breakdown and slice assignments.
- Files/modules: commands/autoplan.py, lib/workflow_state/semantic_preview.py

## 5) Manage execution lifecycle (ship, ship-slice, ship-worktree)
- Actors: Release automation, users
- Description: Ship artifacts, move slices through execution, and manage worktrees/sessions.
- Files/modules: commands/ship.py, commands/ship_slice.py, commands/ship_worktree.py, lib/workflow_runtime/worktree_session.py

## 6) Traceability, metrics, and audits
- Actors: Reporting automation, maintainers
- Description: Trace artifacts, collect metrics, audit repositories and execution state.
- Files/modules: commands/trace_artifacts.py, commands/trace_data.py, commands/metrics_engine.py, commands/metrics_store.py

## 7) Repair, migrate, validate state
- Actors: Maintainers, automation
- Description: Repair corrupted registries, migrate subfeatures, validate workflow state and parity.
- Files/modules: commands/repair_data.py, commands/repair_artifacts.py, commands/migrate_subfeatures.py, commands/validate_workflow_state.py, lib/workflow_state/transitions.py

## 8) Learning & research utilities
- Actors: Users, researchers
- Description: Capture learnings, run research commands that produce semantic previews or drafts.
- Files/modules: commands/learn.py, commands/research.py, lib/workflow_runtime/learnings.py

## 9) Review recording and artifact measurement
- Actors: Reviewers, CI
- Description: Record code/design reviews and measure artifacts for quality/size.
- Files/modules: commands/record_review.py, commands/measure_artifacts.py

## 10) Extension and integration points
- CLI command discovery (PACKAGE_COMMANDS) allows adding commands via new modules.
- Files/modules: cli.py, commands/, paths.py.

## How to use this page
- Use the Component and Sequence diagrams (docs/wiki/concepts/src-architecture.md) to visualise interactions.
- For a specific command, open src/sirius_skills/commands/<command>.py to see concrete behavior.

## Next steps (recommended)
- Expand use cases with concrete examples per command (input/output, sample files changed).
- Auto-generate short sequence diagrams per command (e.g., bootstrap, ship) and attach to this page.

(Generated from source inspection of src/.)
