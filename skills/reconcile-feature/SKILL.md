---
name: reconcile-feature
description: Reconciles an approved feature change packet back into canonical feature docs, verifies the planned slices are complete, removes completed execution slices, and removes the completed change packet.
---

# Reconcile Feature

Use this skill after a feature change packet has been reviewed and the approved
delta needs to be folded back into the canonical feature docs and a human has
explicitly requested final reconcile/cleanup. It also supports canonical-only
repair when a feature has no change packet but all planned slices are already
closed and the remaining work is feature-level cleanup.

## Responsibilities

1. Resolve the canonical feature and selected change packet, or confirm the
   canonical-only repair path when no change packet exists.
2. Reconcile approved change-local discovery, design, or UI docs back into canonical feature docs.
3. Copy any durable figures needed by the canonical feature docs.
4. Verify that all slices planned for the change are closed before cleanup.
5. When no change packet exists, use the canonical feature's `slice-planning.md`
   or `ready_slice_ids` to verify remaining slices are closed before cleanup.
6. Remove completed execution slices for that reviewed change or canonical-only repair.
7. Close the change packet cleanly through the existing feature-change state model when a packet exists.
8. Remove the completed change packet after canonical reconciliation is done when applicable.

## Required Output

- updates to canonical feature docs under `<planning_dir>/<feature-slug>/`
- optional updates to `<feature_path>/figures/`
- updated `<feature_path>/.planning-meta.json`

## Workflow

1. Confirm a human explicitly requested `reconcile-feature` for the selected reviewed change packet or canonical-only repair.
2. If reconciling a change packet, verify that all slices listed in the change packet's `slice-planning.md` are closed, unless force is explicitly used for repair.
3. If no change packet exists, use canonical `slice-planning.md` or `ready_slice_ids` to identify the closed slices that still need cleanup.
4. Select the supported change-local docs that should reconcile into the canonical feature when a change packet exists.
5. Rewrite the canonical docs directly with the approved change content; do not keep surviving change-packet markers or backlinks.
6. Copy any durable `figures/` assets needed by the rewritten canonical docs.
7. Advance the change through `reconciled` and `closed` when a packet exists.
8. Remove the closed execution slices from the execution registry and filesystem.
9. Remove the completed change packet from the feature-change registry and filesystem when applicable.

## Tooling

```bash
# Reconcile the supported change-local docs and close the feature change
python3 skills/reconcile-feature/scripts/reconcile_feature_change.py \
  "checkout" "replace-legacy-flow"

# Repair a canonical feature that has no change packet
python3 skills/reconcile-feature/scripts/reconcile_feature_change.py \
  "checkout" --canonical-only

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
- When no change packet exists, use `--canonical-only` instead of inventing or backfilling a fake change packet.
- Do not keep surviving change-packet backlinks, `reconciliation.md`, or feature-local history files after cleanup.
- Cleanup belongs to reviewed change completion here, not to per-slice closure.
- Do not reconcile change-local `slice-planning.md` or `slice-traceability.md` back into canonical feature planning.
