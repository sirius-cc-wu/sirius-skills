---
name: execution-driver
description: Orchestrates the execution layer by resolving the active slice and routing to the right skill.
---

# Execution Driver

Use this skill to manage workflow state for slice readiness.

## Responsibilities

1. Resolve or initialize the active slice.
2. Verify required files, registry state, and slice metadata.
3. Decide whether the request belongs in the planning layer or the slice-scoped execution layer.
4. Route slice-scoped work to `define`, `plan`, `review-execution`, or `close-slice` as appropriate.
5. Update slice status when a phase is complete.

`execution-driver` owns orchestration only. It should not absorb artifact authoring that belongs to `define`, `plan`, `review-execution`, or `close-slice`.

## Entry Decision Guide

Use `execution-driver` as the execution-layer entrypoint when you need to decide the next step for one execution slice.

Before routing execution work, classify the request:

1. If the work is still feature-scoped, story-scoped, or needs planning-layer routing:
   - send the work to `planning-driver`
2. If there is one execution-ready work item but no slice-scoped execution slice yet:
   - send the work to `slice`
3. If a execution slice already exists or can be resolved:
   - stay in `execution-driver` and route inside the execution layer

`execution-driver` should not absorb feature-level discovery, design, or decomposition just because it was invoked first. Route back out to the planning layer instead.

## Upstream Handoff

`execution-driver` starts after planning has already produced one execution-ready work item.

In repositories that use the planning-layer skills, the usual handoff is:

```text
planning-driver -> discover -> design -> ui-flow -> breakdown -> review-planning -> slice -> execution-driver
```

- `planning-driver` owns feature-planning readiness and routes to the right planning skill.
- `breakdown` turns repo stories into directly executable work items.
- `slice` bootstraps one slice-scoped execution slice for one ready work item.
- `execution-driver` then manages slice readiness for that bootstrapped slice.

If the input is still feature-scoped, story-scoped, or too large for one execution slice, send it back to `planning-driver` instead of stretching `execution-driver` to own planning decomposition.

## Lifecycle States

- `draft`
- `brief_ready`
- `blueprint_ready`
- `execution_ready`
- `closed`

Allowed transitions:

1. `draft -> brief_ready`
2. `brief_ready -> blueprint_ready`
3. `blueprint_ready -> execution_ready`
4. `execution_ready -> closed`

Do not skip states without explicit user approval. Adjacent transitions are the default; use tooling overrides only for deliberate repair.

## State Ownership

`execution-driver` owns **slice/document readiness** only:

- `draft`
- `brief_ready`
- `blueprint_ready`
- `execution_ready`
- `closed`

Do not duplicate slice-execution states like `implementing`, `in progress`, or `blocked` in the slice registry. If you use an external slice tracker, let it own the execution lifecycle (slice start, progress, verification, and finish); keep `execution-driver` focused on slice readiness and artifact state.

## Preflight

1. If `.skills/execution.json` is missing, ask the user where slices should be created, then initialize via tooling with that path.
2. Ensure the configured registry exists (`<slice_dir>/README.md` and `<slice_dir>/registry.json`).
3. Resolve the active slice using tooling (or by user-provided ID/path).
4. Confirm slice path exists and represents one execution-ready work item.
5. Check presence of:
    - `brief.md`
    - `blueprint.md`
    - `slices.md` (legacy optional)
6. Verify registry status is consistent with file reality. If inconsistent, repair status first.
7. For closed slices, verify closure metadata exists in `<slice_path>/.slice-meta.json`.
8. If no slice can be resolved, do not invent feature-level planning inside `execution-driver`; route to `slice` or the planning layer based on scope.

## Routing Rules

1. If no `brief.md` or the slice brief is incomplete:
    - Use `define` to create or update `brief.md`.
    - Set status to `draft` during authoring and `brief_ready` when complete.
2. If `brief.md` is complete and no `blueprint.md`:
    - Use `plan` to produce `blueprint.md`.
    - Set status to `blueprint_ready` when complete.
3. If `brief.md` and `blueprint.md` are complete:
    - Use `blueprint.md` as the final execution artifact for sequencing, validation, and checklist coverage.
    - Legacy slices may still contain `slices.md`; if present, keep it aligned with the plan rather than regenerating it as a required step.
    - Set status to `execution_ready` when the plan is actionable and execution can begin.
4. While implementation is underway:
    - keep `execution-driver` focused on slice readiness and artifact state
    - delegate execution lifecycle events (begin, verify, finish, pause) to your slice tracker if one is in use
5. Once execution is finished and verified:
    - route to `review-execution` before final closure when an explicit implementation-versus-brief review is needed
    - route to `close-slice` after review is complete
    - close the slice non-destructively, record closure metadata, and optionally publish a project-local summary

## Completion Checks

A slice is `brief_ready` when:
- required sections in `brief.md` are filled
- requirements are testable
- success criteria are measurable
- unresolved clarifications are zero or minimal and critical only

A slice is `blueprint_ready` when:
- `blueprint.md` is actionable
- requirements map to implementation and validation steps
- the next step is final readiness review or beginning execution
- gates are passed or explicitly waived

A slice is `execution_ready` when:
- `blueprint.md` is actionable
- execution can begin without major replanning
- any legacy `slices.md` or execution checklist is aligned with the plan
- the next lifecycle owner is the active coding agent or slice tracker

A slice is `closed` when:
- the execution work is complete
- verification has passed or been explicitly waived
- any follow-up execution tracking lives in the slice system rather than the slice state
- closure metadata has been recorded in `.slice-meta.json`
- any closure or publication step has been handled through `close-slice` or equivalent tooling

## Tooling
Always use `scripts/manage_execution.py` for initialization, active slice resolution, status updates, validation, and registry synchronization.

`manage_execution.py` maintains:

- a human-readable registry at `<slice_dir>/README.md`
- a machine-readable registry at `<slice_dir>/registry.json`
- per-slice lifecycle metadata at `<slice_path>/.slice-meta.json`

`manage_execution.py` validates orchestration prerequisites such as:

- `.slice-meta.json` presence and status consistency
- `brief.md` plus `checklists/requirements.md` before a slice is treated as `brief_ready`
- `blueprint.md` before a slice is treated as `blueprint_ready` or `execution_ready`

Slice metadata may also contain explicit relation records such as:

- `supersedes` / `superseded_by`
- `invalidates` / `invalidated_by`
- `narrows` / `narrowed_by`
- `replaces_partially` / `replaced_partially_by`

Partial invalidation is represented with soft selectors in relation scope, for example story title, requirement IDs, or a freeform selector string.

Closed slices are non-destructive: the original `brief.md` and `blueprint.md` stay in place, and any legacy `slices.md` may remain as well, while the metadata and registry record that the slice is closed.

The configured slices directory is stored in `.skills/execution.json` under `slice_dir`. If `.skills/execution.json` does not exist yet, ask the user where slices should be created before running `init`.

Example:

```json
{
  "slice_dir": "slices",
  "preferred_workflow": "TDD"
}
```

Slice IDs are treated as opaque identifiers. Manual IDs may include letters, numbers, `.`, `_`, and `-`, so IDs like `BNC-lg2fwe` are valid. Auto-generated standalone slice IDs use a hash format such as `SPC-a3f8e9` or `CLAW-a3f8e9`.

### Optional Conventions Configuration

Projects may define `.skills/conventions.json` to describe issue-tracker or branch naming conventions without changing the base workflow.

Supported Phase 1 fields:

- `branch_extract_pattern`: regex used by `manage_execution.py add "<feature-name>"` to infer an ID from the current branch
- `id_pattern`: project-level documentation for what a valid ID looks like
- `commit_format`: convention for the `commit` skill
- `pr_title_format`: convention for the `create-pr` skill
- `issue_url_template`: optional documentation hook for linking IDs to a tracker

If `.skills/conventions.json` is absent:

- `manage_execution.py add "<feature-name>"` keeps the generic default behavior
- it generates a hash ID with the `SPC` prefix

If `.skills/conventions.json` is present and defines `branch_extract_pattern`, `manage_execution.py add "<feature-name>"` uses that pattern before falling back to hash generation. Manual IDs always override auto-detection.

Example:

```json
{
  "issue_sliceer": "jira",
  "id_pattern": "^[A-Z][A-Z0-9]*-[0-9]+$",
  "branch_extract_pattern": "^([A-Z][A-Z0-9]*-[0-9]+)-(.+)$",
  "commit_format": "{ID}: {summary}",
  "pr_title_format": "{ID}: {summary}",
  "issue_url_template": "https://jira.example.com/browse/{ID}"
}
```

```bash
# Initialize registry/config:
python3 <path-to-execution-driver>/scripts/manage_execution.py init [slice-dir]

# Example with a custom slices directory:
python3 <path-to-execution-driver>/scripts/manage_execution.py init docs/slices

# Add slice (use branch_extract_pattern from .skills/conventions.json when present,
# otherwise generate a hash ID with the SPC prefix):
python3 <path-to-execution-driver>/scripts/manage_execution.py add "feature-name"

# To specify an ID manually (e.g., to match your issue tracker):
python3 <path-to-execution-driver>/scripts/manage_execution.py add "ID" "feature-name"

# Example with a custom tracker ID:
python3 <path-to-execution-driver>/scripts/manage_execution.py add "BNC-lg2fwe" "feature-name"

# Update slice status:
python3 <path-to-execution-driver>/scripts/manage_execution.py set-status "<slice-id-or-path>" "brief_ready"

# Mark a slice ready for execution:
python3 <path-to-execution-driver>/scripts/manage_execution.py set-status "<slice-id-or-path>" "execution_ready"

# Preferred close path after execution is complete:
# use `close-slice` for normal closure and optional publication

# Low-level status repair only:
python3 <path-to-execution-driver>/scripts/manage_execution.py set-status "<slice-id-or-path>" "closed" --force

# Use --force only for deliberate repair when the registry/file state is temporarily inconsistent:
python3 <path-to-execution-driver>/scripts/manage_execution.py set-status "<slice-id-or-path>" "blueprint_ready" --force

# Record that one slice supersedes another:
python3 <path-to-execution-driver>/scripts/manage_execution.py add-relation "<slice-id-or-path>" supersedes "<target-slice-id-or-path>"

# Record a partial replacement scoped to one story or requirement:
python3 <path-to-execution-driver>/scripts/manage_execution.py add-relation "<slice-id-or-path>" replaces_partially "<target-slice-id-or-path>" --story-title "Story 2 - Legacy flow" --requirement-id FR-002 --selector "legacy checkout path"

# Resolve active slice:
python3 <path-to-execution-driver>/scripts/manage_execution.py get-active

# Validate slice consistency:
python3 <path-to-execution-driver>/scripts/manage_execution.py validate-slice "<slice-id-or-path>"

# Audit relation consistency:
python3 <path-to-execution-driver>/scripts/manage_execution.py audit-relations --json
```
