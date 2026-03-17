---
name: spec-driver
description: Orchestrates the spec-driven workflow by resolving the active track and routing to the right skill.
---

# Spec Driver

Use this skill to manage workflow state for track readiness.

## Responsibilities

1. Resolve or initialize the active track.
2. Verify required files, registry state, and track metadata.
3. Route work to `specify`, `plan`, and optionally `tasks`.
4. Update track status when a phase is complete.

## Lifecycle States

- `draft`
- `spec_ready`
- `plan_ready`
- `execution_ready`
- `closed`

Allowed transitions:

1. `draft -> spec_ready`
2. `spec_ready -> plan_ready`
3. `plan_ready -> execution_ready`
4. `execution_ready -> closed`

Do not skip states without explicit user approval. Adjacent transitions are the default; use tooling overrides only for deliberate repair.

## State Ownership

`spec-driver` owns **track/document readiness** only:

- `draft`
- `spec_ready`
- `plan_ready`
- `execution_ready`
- `closed`

If you also use `sb-tracker`, let `sb` own **execution/task lifecycle** such as `Backlog`, `Ready`, `Doing`, `Review`, `Done`, and `Blocked`.

Do not duplicate task-execution states like `implementing`, `in progress`, or `blocked` in the track registry.

## Preflight

1. If `.specs/config.json` is missing, ask the user where specs should be created, then initialize via tooling with that path.
2. Ensure the configured registry exists (`<spec_dir>/README.md` and `<spec_dir>/registry.json`).
3. Resolve the active track using tooling (or by user-provided ID/path).
4. Confirm track path exists.
5. Check presence of:
    - `spec.md`
    - `plan.md`
    - `tasks.md` (optional)
6. Verify registry status is consistent with file reality. If inconsistent, repair status first.
7. For closed tracks, verify closure metadata exists in `<track_path>/.track-meta.json`.

## Routing Rules

1. If no `spec.md` or spec is incomplete:
    - Use `specify` to create or update `spec.md`.
    - Set status to `draft` during authoring and `spec_ready` when complete.
2. If `spec.md` is complete and no `plan.md`:
    - Use `plan` to produce `plan.md`.
    - Set status to `plan_ready` when complete.
3. If `spec.md` and `plan.md` are complete:
    - Optionally use `tasks` to produce `tasks.md` or an execution checklist when it helps execution.
    - Set status to `execution_ready` when the plan is actionable and execution can begin.
4. Once execution is finished and verified:
    - Set status to `closed`.
    - Record closure metadata and keep the original track artifacts in place.

## Completion Checks

A track is `spec_ready` when:
- required sections in `spec.md` are filled
- requirements are testable
- success criteria are measurable
- unresolved clarifications are zero or minimal and critical only

A track is `plan_ready` when:
- `plan.md` is actionable
- requirements map to implementation and validation steps
- the next task is generating `tasks.md`
- gates are passed or explicitly waived

A track is `execution_ready` when:
- `plan.md` is actionable
- execution can begin without major replanning
- any optional `tasks.md` or execution checklist is aligned with the plan
- the next lifecycle owner is the active coding agent or task tracker

A track is `closed` when:
- the execution work is complete
- verification has passed or been explicitly waived
- any follow-up execution tracking lives in the task system rather than the track state
- closure metadata has been recorded in `.track-meta.json`

## Tooling
Always use `scripts/manage_specs.py` for initialization, active track resolution, status updates, validation, and registry synchronization.

`manage_specs.py` maintains:

- a human-readable registry at `<spec_dir>/README.md`
- a machine-readable registry at `<spec_dir>/registry.json`
- per-track lifecycle metadata at `<track_path>/.track-meta.json`

Track metadata may also contain explicit relation records such as:

- `supersedes` / `superseded_by`
- `invalidates` / `invalidated_by`
- `narrows` / `narrowed_by`
- `replaces_partially` / `replaced_partially_by`

Partial invalidation is represented with soft selectors in relation scope, for example story title, requirement IDs, or a freeform selector string.

Closed tracks are non-destructive: the original `spec.md`, `plan.md`, and optional `tasks.md` stay in place, while the metadata and registry record that the track is closed.

The configured specs directory is stored in `.specs/config.json` under `spec_dir`. If `.specs/config.json` does not exist yet, ask the user where specs should be created before running `init`.

Track IDs are treated as opaque identifiers. Manual IDs may include letters, numbers, `.`, `_`, and `-`, so IDs like `BNC-lg2fwe` are valid. Auto-generated standalone track IDs use an `sb`-style hash format such as `SPC-a3f8e9` or `CLAW-a3f8e9`.

### Optional Identity Configuration

Projects may define `.skills/identity.json` to describe issue-tracker or branch naming conventions without changing the base workflow.

Supported Phase 1 fields:

- `branch_extract_pattern`: regex used by `manage_specs.py add "<feature-name>"` to infer an ID from the current branch
- `id_pattern`: project-level documentation for what a valid ID looks like
- `commit_format`: convention for the `commit` skill
- `pr_title_format`: convention for the `create-pr` skill
- `issue_url_template`: optional documentation hook for linking IDs to a tracker

If `.skills/identity.json` is absent:

- `manage_specs.py add "<feature-name>"` keeps the generic default behavior
- it generates an `sb`-style hash ID
- it uses the repo-specific `sb` prefix when `sb config get prefix` reports `(from repo)`
- otherwise it falls back to the standalone `SPC` prefix

If `.skills/identity.json` is present and defines `branch_extract_pattern`, `manage_specs.py add "<feature-name>"` uses that pattern before falling back to hash generation. Manual IDs always override auto-detection. Tracks created via `add-from-sb` preserve the exact `sb` issue ID.

Example:

```json
{
  "issue_tracker": "jira",
  "id_pattern": "^[A-Z][A-Z0-9]*-[0-9]+$",
  "branch_extract_pattern": "^([A-Z][A-Z0-9]*-[0-9]+)-(.+)$",
  "commit_format": "{ID}: {summary}",
  "pr_title_format": "{ID}: {summary}",
  "issue_url_template": "https://jira.example.com/browse/{ID}"
}
```

```bash
# Initialize registry/config:
python3 <path-to-spec-driver>/scripts/manage_specs.py init [spec-dir]

# Example with a custom specs directory:
python3 <path-to-spec-driver>/scripts/manage_specs.py init docs/specs

# Add track (use branch_extract_pattern from .skills/identity.json when present,
# otherwise generate an sb-style hash ID with a repo prefix or SPC fallback):
python3 <path-to-spec-driver>/scripts/manage_specs.py add "feature-name"

# To specify an ID manually:
python3 <path-to-spec-driver>/scripts/manage_specs.py add "ID" "feature-name"

# Example with an sb-style ID:
python3 <path-to-spec-driver>/scripts/manage_specs.py add "BNC-lg2fwe" "feature-name"

# Create a track directly from an sb issue:
python3 <path-to-spec-driver>/scripts/manage_specs.py add-from-sb "BNC-lg2fwe"

# Update track status:
python3 <path-to-spec-driver>/scripts/manage_specs.py set-status "<track-id-or-path>" "spec_ready"

# Mark a track ready for execution:
python3 <path-to-spec-driver>/scripts/manage_specs.py set-status "<track-id-or-path>" "execution_ready"

# Close a track after execution is complete:
python3 <path-to-spec-driver>/scripts/manage_specs.py set-status "<track-id-or-path>" "closed"

# Use --force only for deliberate repair when the registry/file state is temporarily inconsistent:
python3 <path-to-spec-driver>/scripts/manage_specs.py set-status "<track-id-or-path>" "plan_ready" --force

# Record that one track supersedes another:
python3 <path-to-spec-driver>/scripts/manage_specs.py add-relation "<track-id-or-path>" supersedes "<target-track-id-or-path>"

# Record a partial replacement scoped to one story or requirement:
python3 <path-to-spec-driver>/scripts/manage_specs.py add-relation "<track-id-or-path>" replaces_partially "<target-track-id-or-path>" --story-title "Story 2 - Legacy flow" --requirement-id FR-002 --selector "legacy checkout path"

# Resolve active track:
python3 <path-to-spec-driver>/scripts/manage_specs.py get-active

# Validate track consistency:
python3 <path-to-spec-driver>/scripts/manage_specs.py validate-track "<track-id-or-path>"

# Audit relation consistency:
python3 <path-to-spec-driver>/scripts/manage_specs.py audit-relations --json
```

`add-from-sb` shells out to `sb show <id> --json`, uses the issue title as the feature name, and writes source metadata to a per-track sidecar file.

For backward compatibility, `manage_specs.py` still accepts legacy status inputs such as `draft_spec`, `tasks_ready`, `implementing`, `done`, `approved`, and `completed`, but it normalizes them to the canonical track states above.
