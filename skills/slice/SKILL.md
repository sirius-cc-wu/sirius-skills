---
name: slice
description: Bootstraps a slice-scoped execution slice from a ready work item and hands off to execution-driver.
---

# Slice

Use this skill when a work item is small enough to execute, has passed planning review, and needs a execution slice.

## Responsibilities

1. Validate that the selected work item is ready for execution.
2. Bootstrap one execution slice for that work item.
3. Confirm the slice exists and is aligned with the repository's spec layout.
4. Hand off to `execution-driver` for `brief.md` and `blueprint.md`.

## Preferred Input

- a work item ID from repository planning (for example, one created by `breakdown`)

## Bootstrap Rules

- One executable work item should map to one slice.
- Prefer preserving the planned ID as the slice ID when available.
- Do not create a slice for work that still needs major decomposition.
- Keep slice readiness and registry state in `execution-driver`.

## Workflow

1. Inspect the target work item and confirm dependencies, scope, and acceptance notes are clear.
2. Bootstrap the slice with:

```bash
python3 skills/execution-driver/scripts/manage_execution.py add "<slice-id>" "<feature-name>"
```

3. Confirm the new slice path exists and registry state is consistent.
4. Hand off to `execution-driver` to author `brief.md` and `blueprint.md`.

## Guardrails

- Do not invent extra slice states to mirror external execution lifecycles.
- Do not skip `execution-driver`; this skill only bootstraps and hands off.
- If the input work item is still too large, send it back to `planning-driver` or `breakdown`.
