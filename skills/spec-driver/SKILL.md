---
name: spec-driver
description: Orchestrates the spec-driven workflow by resolving the active track and routing to the right skill.
---

# Spec Driver

Use this skill to manage workflow state for specification and planning.

## Responsibilities

1. Resolve or initialize the active track.
2. Verify required files and registry status.
3. Route work to `specify` or `plan`.
4. Update track status when a phase is complete.

## Lifecycle States

- `draft_spec`
- `spec_ready`
- `plan_ready`
- `implementation_ready`
- `implementing`
- `done`

Allowed transitions:

1. `draft_spec -> spec_ready`
2. `spec_ready -> plan_ready`
3. `plan_ready -> implementation_ready`
4. `implementation_ready -> implementing`
5. `implementing -> done`

Do not skip states without explicit user approval.

## Preflight

1. If `.specs/config.json` is missing, ask the user where specs should be created, then initialize via tooling with that path.
2. Ensure the configured registry exists (`<spec_dir>/README.md`).
3. Resolve the active track using tooling (or by user-provided ID/path).
4. Confirm track path exists.
5. Check presence of:
    - `spec.md`
    - `plan.md`
    - `tasks.md` (optional)
6. Verify registry status is consistent with file reality. If inconsistent, repair status first.

## Routing Rules

1. If no `spec.md` or spec is incomplete:
    - Use `specify` to create or update `spec.md`.
    - Set status to `draft_spec` during authoring and `spec_ready` when complete.
2. If `spec.md` is complete and no `plan.md`:
    - Use `plan` to produce `plan.md`.
    - Set status to `plan_ready` when complete.
3. If `spec.md` and `plan.md` are complete:
    - Set status to `implementation_ready`.
    - Proceed to implementation with the active coding agent.

## Completion Checks

A track is `spec_ready` when:
- required sections in `spec.md` are filled
- requirements are testable
- success criteria are measurable
- unresolved clarifications are zero or minimal and critical only

A track is `plan_ready` when:
- `plan.md` is actionable
- requirements map to implementation and validation steps
- gates are passed or explicitly waived

## Tooling
Always use `scripts/manage_specs.py` for initialization, active track resolution, status updates, and validation.

The configured specs directory is stored in `.specs/config.json` under `spec_dir`. If `.specs/config.json` does not exist yet, ask the user where specs should be created before running `init`.

Track IDs are treated as opaque identifiers. Manual IDs may include letters, numbers, `.`, `_`, and `-`, so IDs like `BNC-lg2fwe` are valid.

```bash
# Initialize registry/config:
python3 <path-to-spec-driver>/scripts/manage_specs.py init [spec-dir]

# Example with a custom specs directory:
python3 <path-to-spec-driver>/scripts/manage_specs.py init docs/specs

# Add track (auto-detect ID from branch or use timestamp):
python3 <path-to-spec-driver>/scripts/manage_specs.py add "feature-name"

# To specify an ID manually:
python3 <path-to-spec-driver>/scripts/manage_specs.py add "ID" "feature-name"

# Example with an sb-style ID:
python3 <path-to-spec-driver>/scripts/manage_specs.py add "BNC-lg2fwe" "feature-name"

# Create a track directly from an sb issue:
python3 <path-to-spec-driver>/scripts/manage_specs.py add-from-sb "BNC-lg2fwe"

# Update track status:
python3 <path-to-spec-driver>/scripts/manage_specs.py set-status "<track-id-or-path>" "spec_ready"

# Resolve active track:
python3 <path-to-spec-driver>/scripts/manage_specs.py get-active

# Validate track consistency:
python3 <path-to-spec-driver>/scripts/manage_specs.py validate-track "<track-id-or-path>"
```

`add-from-sb` shells out to `sb show <id> --json`, uses the issue title as the feature name, and writes source metadata to a per-track sidecar file without changing the registry table format.
