---
name: slice
description: Validates approved, committed execution-ready work, bootstraps a slice-scoped execution slice, and hands off to guide-execution.
---

# Slice

Use this skill when a work item is small enough to execute, has passed planning review, has explicit human approval, and its planning artifacts have been committed.

## Responsibilities

1. Validate that the selected work item is ready for execution.
2. Ensure execution bootstrap prerequisites exist, including `.skills/execution.json`, the slice registry, and a durable approved planning checkpoint.
3. Bootstrap one execution slice for that work item.
4. Confirm the slice exists and is aligned with the repository's execution layout.
5. Hand off to `guide-execution` for `brief.md` and `blueprint.md`.

## Preferred Input

- a work item ID from repository planning (for example, one created by `breakdown`)

## Bootstrap Rules

- One executable work item should map to one slice.
- Prefer preserving the planned ID as the slice ID when available.
- Do not create a slice for work that still needs major decomposition.
- If execution config does not exist yet, initialize it with a repository-specific slice directory when known, otherwise use the generic default `slices/`.
- Keep slice readiness and registry state in `guide-execution`.

## Preflight

Before bootstrapping, confirm:

1. The input represents exactly one execution-ready work item rather than a feature-sized batch.
2. Dependencies, sequencing notes, and expected verification are already clear in the planning artifacts.
3. The work item does not still need major decomposition, architecture discovery, or planning review.
4. The chosen slice ID, if provided, should be preserved exactly.
5. The planning artifacts were explicitly approved and committed before bootstrap.
6. For subfeatures, explicit approval must already be recorded in `.subfeature-meta.json`; `reviewed` alone is not enough.

## Workflow

1. Inspect the target work item and confirm dependencies, scope, and acceptance notes are clear.
2. Bootstrap the slice with:

```bash
sirius bootstrap-slice "<slice-id>" "<feature-name>"
```

3. If the repository has not configured execution yet and the default `slices/` location is not appropriate, pass an explicit directory during first bootstrap:

```bash
sirius bootstrap-slice --slice-dir "team-slices" "<slice-id>" "<feature-name>"
```

4. Confirm the new slice path exists and registry state is consistent.
5. Hand off to `guide-execution` to author `brief.md` and `blueprint.md`.

`bootstrap_slice.py` keeps the ownership boundary intact by delegating registry creation, slice creation, and validation to `sirius manage-execution`.
For reviewed subfeatures, it also expects approval metadata to be present already and records the chosen ready slice ID back into `.subfeature-meta.json` so the derived planning view becomes `slice_ready`.

## Guardrails

- Do not invent extra slice states to mirror external execution lifecycles.
- Do not skip `guide-execution`; this skill prepares and bootstraps the slice, but `guide-execution` still owns execution readiness and routing.
- Do not bootstrap directly from uncommitted planning output.
- Treat the "planning output is committed" check as target-scoped to the active
  feature or subfeature packet so unrelated repository dirt does not block the
  execution handoff.
- If the input work item is still too large, send it back to `guide-planning` or `breakdown`.
