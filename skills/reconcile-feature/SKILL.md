---
name: reconcile-feature
description: Reconciles an approved feature change packet back into canonical feature docs, verifies the planned slices are complete, removes completed execution slices, and removes the completed change packet.
---

# Reconcile Feature

Use this skill after a feature change packet has been reviewed and the approved
delta needs to be folded back into the canonical feature docs and a human has
explicitly requested final reconcile/cleanup.

## Responsibilities

1. Resolve the canonical feature and selected change packet.
2. Reconcile approved change-local discovery, design, or UI docs back into canonical feature docs.
3. Copy any durable figures needed by the canonical feature docs.
4. Verify that all slices planned for the change are closed before cleanup.
5. Remove completed execution slices for that reviewed change.
6. Close the change packet cleanly through the existing feature-change state model.
7. Remove the completed change packet after canonical reconciliation is done.

## Required Output

- updates to canonical feature docs under `<planning_dir>/<feature-slug>/`
- optional updates to `<feature_path>/figures/`
- updated `<feature_path>/.planning-meta.json`

## Workflow

1. Confirm a human explicitly requested `reconcile-feature` for the selected reviewed change packet.
2. Verify that all slices listed in the change packet's `slice-planning.md` are closed, unless force is explicitly used for repair.
3. Select the supported change-local docs that should reconcile into the canonical feature.
4. Rewrite the canonical docs directly with the approved change content; do not keep surviving change-packet markers or backlinks.
5. Copy any durable `figures/` assets needed by the rewritten canonical docs.
6. Advance the change through `reconciled` and `closed`.
7. Remove the closed execution slices from the execution registry and filesystem.
8. Remove the completed change packet from the feature-change registry and filesystem.

## Tooling

```bash
# Reconcile the supported change-local docs and close the feature change
python3 skills/reconcile-feature/scripts/reconcile_feature_change.py \
  "checkout" "replace-legacy-flow"

# Reconcile only selected canonical docs
python3 skills/reconcile-feature/scripts/reconcile_feature_change.py \
  "checkout" "replace-legacy-flow" \
  --canonical-file discover.md \
  --canonical-file system-design.md \
  --canonical-file ui-design.md
```

## Guardrails

- Do not invoke this skill autonomously after review or closure; `reconcile-feature` is human-owned and should run only when a human explicitly requests it.
- Do not use this skill before planning review has marked the change packet `reviewed`, unless you are deliberately repairing state with `--force`.
- Do not reconcile a feature change as complete while planned slices are still open unless you are deliberately repairing state with `--force`.
- Do not keep surviving change-packet backlinks, `reconciliation.md`, or feature-local history files after cleanup.
- Cleanup belongs to reviewed change completion here, not to per-slice closure.
- Do not reconcile change-local `slice-planning.md` or `slice-traceability.md` back into canonical feature planning.
