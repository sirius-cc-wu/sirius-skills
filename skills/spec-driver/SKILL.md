---
name: spec-driver
description: Orchestrates the spec-driven workflow by resolving the active track and routing to the right skill.
---

# Spec Driver

Use this skill to manage workflow state for track readiness.

## Responsibilities

1. Resolve or initialize the active track.
2. Verify required files, registry state, and track metadata.
3. Decide whether the request belongs in the planning layer or the task-scoped execution layer.
4. Route task-scoped work to `define`, `plan`, `review-execution`, or `close-track` as appropriate.
5. Update track status when a phase is complete.

## Entry Decision Guide

Use `spec-driver` as the execution-layer entrypoint when you need to decide the next step for one task-scoped track.

Before routing execution work, classify the request:

1. If the problem, outcomes, or constraints are still being framed:
   - send the work to `discover`
2. If the architecture, interfaces, or technical approach are still unresolved:
   - send the work to `design`
3. If UI or interaction flow is still a material part of scope:
   - send the work to `ui-flow`
4. If the work is still repo-scoped, story-scoped, or needs decomposition into tracker slices:
   - send the work to `breakdown`
5. If there is one execution-ready work item but no task-scoped spec track yet:
   - send the work to `track`
6. If a task-scoped track already exists or can be resolved:
   - stay in `spec-driver` and route inside the execution layer

`spec-driver` should not absorb feature-level discovery, design, or decomposition just because it was invoked first. Route back out to the planning layer instead.

## Upstream Handoff

`spec-driver` starts after planning has already produced one execution-ready work item.

In repositories that use the planning-layer skills, the usual handoff is:

```text
discover -> design -> ui-flow -> breakdown -> track -> spec-driver
```

- `breakdown` turns repo stories into directly executable work items.
- `track` bootstraps one task-scoped spec track for one ready work item.
- `spec-driver` then manages track readiness for that bootstrapped track.

If the input is still feature-scoped, story-scoped, or too large for one execution track, send it back to `breakdown` instead of stretching `spec-driver` to own decomposition.

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

Do not duplicate task-execution states like `implementing`, `in progress`, or `blocked` in the track registry. If you use an external task tracker, let it own the execution lifecycle (task start, progress, verification, and finish); keep `spec-driver` focused on track readiness and artifact state.

## Preflight

1. If `.skills/spec-driver.json` is missing, ask the user where tracks should be created, then initialize via tooling with that path.
2. Ensure the configured registry exists (`<spec_dir>/README.md` and `<spec_dir>/registry.json`).
3. Resolve the active track using tooling (or by user-provided ID/path).
4. Confirm track path exists and represents one execution-ready work item.
5. Check presence of:
    - `spec.md`
    - `plan.md`
    - `tasks.md` (legacy optional)
6. Verify registry status is consistent with file reality. If inconsistent, repair status first.
7. For closed tracks, verify closure metadata exists in `<track_path>/.track-meta.json`.
8. If no track can be resolved, do not invent feature-level planning inside `spec-driver`; route to `track` or the planning layer based on scope.

## Routing Rules

1. If no `spec.md` or spec is incomplete:
    - Use `define` to create or update `spec.md`.
    - Set status to `draft` during authoring and `spec_ready` when complete.
2. If `spec.md` is complete and no `plan.md`:
    - Use `plan` to produce `plan.md`.
    - Set status to `plan_ready` when complete.
3. If `spec.md` and `plan.md` are complete:
    - Use `plan.md` as the final execution artifact for sequencing, validation, and checklist coverage.
    - Legacy tracks may still contain `tasks.md`; if present, keep it aligned with the plan rather than regenerating it as a required step.
    - Set status to `execution_ready` when the plan is actionable and execution can begin.
4. While implementation is underway:
    - keep `spec-driver` focused on track readiness and artifact state
    - delegate execution lifecycle events (begin, verify, finish, pause) to your task tracker if one is in use
5. Once execution is finished and verified:
    - route to `review-execution` before final closure when an explicit implementation-versus-spec review is needed
    - route to `close-track` after review is complete
    - close the track non-destructively, record closure metadata, and optionally publish a project-local summary

## Completion Checks

A track is `spec_ready` when:
- required sections in `spec.md` are filled
- requirements are testable
- success criteria are measurable
- unresolved clarifications are zero or minimal and critical only

A track is `plan_ready` when:
- `plan.md` is actionable
- requirements map to implementation and validation steps
- the next step is final readiness review or beginning execution
- gates are passed or explicitly waived

A track is `execution_ready` when:
- `plan.md` is actionable
- execution can begin without major replanning
- any legacy `tasks.md` or execution checklist is aligned with the plan
- the next lifecycle owner is the active coding agent or task tracker

A track is `closed` when:
- the execution work is complete
- verification has passed or been explicitly waived
- any follow-up execution tracking lives in the task system rather than the track state
- closure metadata has been recorded in `.track-meta.json`
- any closure or publication step has been handled through `close-track` or equivalent tooling

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

Closed tracks are non-destructive: the original `spec.md` and `plan.md` stay in place, and any legacy `tasks.md` may remain as well, while the metadata and registry record that the track is closed.

The configured tracks directory is stored in `.skills/spec-driver.json` under `spec_dir`. If `.skills/spec-driver.json` does not exist yet, ask the user where tracks should be created before running `init`.

Example:

```json
{
  "spec_dir": "tracks",
  "preferred_workflow": "TDD"
}
```

Track IDs are treated as opaque identifiers. Manual IDs may include letters, numbers, `.`, `_`, and `-`, so IDs like `BNC-lg2fwe` are valid. Auto-generated standalone track IDs use a hash format such as `SPC-a3f8e9` or `CLAW-a3f8e9`.

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
- it generates a hash ID with the `SPC` prefix

If `.skills/identity.json` is present and defines `branch_extract_pattern`, `manage_specs.py add "<feature-name>"` uses that pattern before falling back to hash generation. Manual IDs always override auto-detection.

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
python3 <path-to-spec-driver>/scripts/manage_specs.py init [track-dir]

# Example with a custom tracks directory:
python3 <path-to-spec-driver>/scripts/manage_specs.py init docs/tracks

# Add track (use branch_extract_pattern from .skills/identity.json when present,
# otherwise generate a hash ID with the SPC prefix):
python3 <path-to-spec-driver>/scripts/manage_specs.py add "feature-name"

# To specify an ID manually (e.g., to match your issue tracker):
python3 <path-to-spec-driver>/scripts/manage_specs.py add "ID" "feature-name"

# Example with a custom tracker ID:
python3 <path-to-spec-driver>/scripts/manage_specs.py add "BNC-lg2fwe" "feature-name"

# Update track status:
python3 <path-to-spec-driver>/scripts/manage_specs.py set-status "<track-id-or-path>" "spec_ready"

# Mark a track ready for execution:
python3 <path-to-spec-driver>/scripts/manage_specs.py set-status "<track-id-or-path>" "execution_ready"

# Preferred close path after execution is complete:
# use `close-track` for normal closure and optional publication

# Low-level status repair only:
python3 <path-to-spec-driver>/scripts/manage_specs.py set-status "<track-id-or-path>" "closed" --force

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

For backward compatibility, `manage_specs.py` still accepts legacy status inputs such as `draft_spec`, `tasks_ready`, `implementing`, `done`, `approved`, and `completed`, but it normalizes them to the canonical track states above.
