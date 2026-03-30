---
name: reconcile-feature
description: Reconciles an approved feature change packet back into canonical feature docs, records backlinks, and closes the change with retained history.
---

# Reconcile Feature

Use this skill after a feature change packet has been reviewed and the approved
delta needs to be folded back into the canonical feature docs without deleting
the original change packet.

## Responsibilities

1. Resolve the canonical feature and selected change packet.
2. Reconcile approved change-local planning docs back into canonical feature docs.
3. Record durable backlinks from the canonical docs to the retained change packet.
4. Publish optional feature-local change history.
5. Close the change packet cleanly through the existing feature-change state model.

## Required Output

- updates to canonical planning docs under `<planning_dir>/<feature-slug>/`
- `<change_path>/reconciliation.md`
- optional `<feature_path>/changes/history.md`
- updated `<change_path>/.feature-change-meta.json`

## Workflow

1. Confirm the selected change packet is already `reviewed`.
2. Select the change-local planning docs that should reconcile into the canonical feature.
3. Append or refresh stable reconciliation blocks inside the canonical docs with backlinks to the change packet.
4. Write `reconciliation.md` in the change packet with the canonical targets and review note.
5. Publish retained history when configured or requested.
6. Advance the change through `reconciled` and `closed`.

## Tooling

```bash
# Reconcile all supported change-local planning docs and close the change
python3 skills/reconcile-feature/scripts/reconcile_feature_change.py \
  "checkout" "replace-legacy-flow"

# Reconcile only selected canonical docs
python3 skills/reconcile-feature/scripts/reconcile_feature_change.py \
  "checkout" "replace-legacy-flow" \
  --canonical-file system-design.md \
  --canonical-file slice-planning.md

# Reconcile without publishing feature-local history
python3 skills/reconcile-feature/scripts/reconcile_feature_change.py \
  "checkout" "replace-legacy-flow" \
  --no-history
```

## Guardrails

- Do not use this skill before planning review has marked the change packet `reviewed`, unless you are deliberately repairing state with `--force`.
- Do not delete or move the original change packet; reconciliation is additive and keeps the retained change history in place.
- Do not silently overwrite canonical docs with hidden merges; keep stable reconciliation blocks and explicit backlinks.
- Publish history as a retained rollup, not as a destructive archive.
