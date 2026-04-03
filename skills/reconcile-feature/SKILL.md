---
name: reconcile-feature
description: Reconciles an approved feature change packet back into canonical feature docs, verifies the planned slices are complete, archives completed execution slices, and closes the change with retained history.
---

# Reconcile Feature

Use this skill after a feature change packet has been reviewed and the approved
delta needs to be folded back into the canonical feature docs without deleting
the original change packet.

## Responsibilities

1. Resolve the canonical feature and selected change packet.
2. Reconcile approved change-local discovery or design docs back into canonical feature docs.
3. Record durable backlinks from the canonical docs to the retained change packet.
4. Verify that all slices planned for the change are closed before feature-level archive/publish work.
5. Archive completed execution slices when the reviewed change is done.
6. Publish optional feature-local change history.
7. Close the change packet cleanly through the existing feature-change state model.

## Required Output

- updates to canonical feature docs under `<planning_dir>/<feature-slug>/`
- `<change_path>/reconciliation.md`
- retained change-local `slice-planning.md` / `slice-traceability.md` inside the change packet
- optional `<feature_path>/changes/history.md`
- updated `<change_path>/.feature-change-meta.json`

## Workflow

1. Confirm the selected change packet is already `reviewed`.
2. Verify that all slices listed in the change packet's `slice-planning.md` are closed, unless force is explicitly used for repair.
3. Select the supported change-local docs that should reconcile into the canonical feature.
4. Append or refresh stable reconciliation blocks inside the canonical docs with backlinks to the change packet.
5. Archive the closed execution slices into the hidden slice archive while leaving the change-local breakdown artifacts in the packet.
6. Write `reconciliation.md` in the change packet with the canonical targets and completion outputs.
7. Publish retained history when configured or requested.
8. Advance the change through `reconciled` and `closed`.

## Tooling

```bash
# Reconcile the supported change-local docs and close the feature change
python3 skills/reconcile-feature/scripts/reconcile_feature_change.py \
  "checkout" "replace-legacy-flow"

# Reconcile only selected canonical docs
python3 skills/reconcile-feature/scripts/reconcile_feature_change.py \
  "checkout" "replace-legacy-flow" \
  --canonical-file discover.md \
  --canonical-file system-design.md

# Reconcile without publishing feature-local history
python3 skills/reconcile-feature/scripts/reconcile_feature_change.py \
  "checkout" "replace-legacy-flow" \
  --no-history
```

## Guardrails

- Do not use this skill before planning review has marked the change packet `reviewed`, unless you are deliberately repairing state with `--force`.
- Do not delete or move the original change packet; reconciliation is additive and keeps the retained change history in place.
- Do not reconcile a feature change as complete while planned slices are still open unless you are deliberately repairing state with `--force`.
- Do not silently overwrite canonical docs with hidden merges; keep stable reconciliation blocks and explicit backlinks.
- Archive/publish belongs to reviewed change completion here, not to per-slice closure.
- Do not reconcile change-local `slice-planning.md` or `slice-traceability.md` back into canonical feature planning by default; keep them in the retained change packet.
