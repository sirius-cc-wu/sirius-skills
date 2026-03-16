---
name: spec-driver
description: High-level orchestrator for the spec-driven lifecycle. Use this when starting a new specification, planning, or implementation.
---

# Spec-driver Skill (Orchestrator)

This skill manages deterministic transitions between Specification, Planning, and Implementation.

## Lifecycle State Machine

Use these statuses in the registry README at `<spec_dir>/README.md` (default: `specs/README.md`):

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

## Preflight (Required Before Routing)

1. If `.specs/config.json` is missing, ask the user where specs should be created, then initialize via tooling with that path.
2. Ensure the configured registry exists (`<spec_dir>/README.md`).
3. Resolve the active track using tooling (or by user-provided ID/path).
4. Confirm track path exists.
5. Check presence of:
   - `spec.md`
   - `plan.md`
   - `tasks.md` (optional, but required for strict task execution mode)
6. Verify registry status is consistent with file reality. If inconsistent, repair status first.

## Routing Rules

1. If no `spec.md` or spec is incomplete:
   - Activate `specify` to create/update `spec.md`.
   - Optionally activate `use-case` for complex stories.
   - Set status to `draft_spec` during authoring, then `spec_ready` when complete.
2. If `spec.md` is complete and no `plan.md`:
   - Activate `plan` to produce planning artifacts.
   - Set status to `plan_ready` when complete.
3. If `spec.md` and `plan.md` are complete:
   - Set status to `implementation_ready`.
   - Internal implementation capability is assumed for coding agents in this workflow.
   - Proceed directly to implementation (`implementing`) using the active coding agent.

## Completion Criteria Per State

1. `spec_ready`:
   - No unresolved placeholders.
   - At most 3 unresolved critical clarifications; preferably zero.
   - Requirements and success criteria are measurable.
2. `plan_ready`:
   - FR-to-steps traceability exists.
   - Paths and test strategy are concrete.
   - Planning gates are passed or explicitly waived with rationale.
3. `implementation_ready`:
   - Plan is actionable and ordered.
   - Acceptance scenarios are mapped to verification steps.
4. `done`:
   - Planned scope implemented and verified.
   - Plan/tasks checkboxes reflect actual completion.
   - Registry status updated.

## Tooling
Always use `scripts/manage_specs.py` for registry updates to ensure cross-platform compatibility.

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
