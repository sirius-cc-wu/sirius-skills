---
name: track
description: Bootstraps a task-scoped execution track from a ready work item and hands off to spec-driver.
---

# Track

Use this skill when a work item is small enough to execute, has passed planning review, and needs a task-scoped track.

## Responsibilities

1. Validate that the selected work item is ready for execution.
2. Bootstrap one task-scoped track for that work item.
3. Confirm the track exists and is aligned with the repository's spec layout.
4. Hand off to `spec-driver` for `spec.md` and `plan.md`.

## Preferred Input

- a work item ID from your execution tracker (for example, one created by `breakdown`)

If no tracker is in use, use the repository's configured issue ID and track bootstrap convention.

## Bootstrap Rules

- One executable work item should map to one track.
- Prefer preserving the tracker ID as the track ID when the tooling supports it.
- Do not create a track for work that still needs major decomposition.
- Keep task execution state in the tracker and track readiness in `spec-driver`.

## Workflow

1. Inspect the target work item and confirm dependencies, scope, and acceptance notes are clear.
2. Bootstrap the track with:

```bash
python3 skills/spec-driver/scripts/manage_specs.py add "<track-id>" "<feature-name>"
```

   If the tracker supports exporting issue metadata as JSON, you may pass `--id` manually to preserve the tracker ID as the track ID.

3. Confirm the new track path exists and registry state is consistent.
4. Hand off to `spec-driver` to author `spec.md` and `plan.md`.

## Guardrails

- Do not invent extra track states to mirror tracker execution lifecycle.
- Do not skip `spec-driver`; this skill only bootstraps and hands off.
- If the input work item is still too large, send it back to `breakdown`.
