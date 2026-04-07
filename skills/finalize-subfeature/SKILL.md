---
name: finalize-subfeature
description: Finalizes a reviewed subfeature by verifying planned slices are complete, cleaning completed execution slices, and marking the durable subfeature implemented.
---

# Finalize Subfeature

Use this skill after a subfeature has been reviewed, implemented through slices,
and a human explicitly requests final cleanup.

## Responsibilities

1. Resolve the parent feature and selected subfeature.
2. Verify that all slices planned for the subfeature are closed before cleanup.
3. Remove completed execution slices for that reviewed subfeature.
4. Mark the durable subfeature finalized and implemented.
5. Leave the subfeature planning folder in place as part of the durable feature hierarchy.

## Required Output

- updated `<subfeature_path>/.subfeature-meta.json`
- updated `<subfeature_path>/.planning-meta.json`
- execution registry cleanup for completed slices referenced by the subfeature

## Workflow

1. Confirm a human explicitly requested `finalize-subfeature` for the selected reviewed subfeature.
2. Verify that all slices listed in the subfeature's `slice-planning.md` are closed, unless force is explicitly used for repair.
3. Remove the closed execution slices from the execution registry and filesystem.
4. Advance the subfeature to `finalized` and mark the planning folder `implemented`.
5. Keep the subfeature folder and its planning artifacts intact.

## Tooling

```bash
# Finalize a reviewed subfeature and clean its completed slices
python3 skills/finalize-subfeature/scripts/finalize_subfeature.py \
  "checkout" "replace-legacy-flow"
```

## Guardrails

- Do not invoke this skill autonomously after review or closure; `finalize-subfeature` is human-owned and should run only when a human explicitly requests it.
- Do not use this skill before planning review has marked the subfeature `reviewed`, unless you are deliberately repairing state with `--force`.
- Do not finalize a subfeature while its planned slices are still open unless you are deliberately repairing state with `--force`.
- Do not delete the durable subfeature folder as part of finalization.
- Cleanup belongs to reviewed subfeature completion here, not to per-slice closure.
