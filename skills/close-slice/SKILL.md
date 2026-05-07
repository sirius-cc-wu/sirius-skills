---
name: close-slice
description: Closes the active execution slice with validation and records durable closure metadata while invoking shared owner-completion reconciliation.
---

# Close Slice

Use this skill when implementation is complete and you want to close an execution slice cleanly.

## Responsibilities

1. Resolve the target slice through `guide-execution`.
2. Validate that the slice is ready to close.
3. Close the slice without deleting the original artifacts.
4. Optionally record explicit invalidation or supersession relations as part of closure.

## Source of Truth Rules

- Keep the original slice artifacts intact. `close-slice` records closure only; any later cleanup or archival is a separate explicit maintenance step.
- Treat `<slice_dir>/README.md`, `<slice_dir>/registry.json`, and `<slice_path>/.slice-meta.json` as the canonical closure records.

## Artifact Ownership

`close-slice` owns closure metadata updates and relation-bearing slice closure.
After closure, it invokes the shared `workflow_state.owner_completion` hook so
feature and subfeature completion can be reconciled from traceability plus
closed execution slices.

`guide-execution` should route into closure only after execution review is complete; it should not replace `close-slice` by mutating closure state directly outside normal registry/status tooling.

## Workflow

1. Resolve the target slice explicitly, or use the active slice.
2. Run `manage_execution.py validate-slice`.
3. If the slice is not already `closed`, close it through tooling.
4. Run shared owner-completion reconciliation for planning owners linked to the closed slice.
5. If relation-bearing closure is requested:
    - record explicit slice relations such as `supersedes` or `replaces_partially`
    - require explicit impact confirmation unless forced
    - run relation auditing through the execution registry tooling
6. Return the closed slice outcome, owner-sync results, and the retained source artifacts.

## Tooling

```bash
# Close the active slice
python3 <path-to-close-slice>/scripts/close_slice.py

# Close a slice while explicitly confirming that it supersedes an older one
python3 <path-to-close-slice>/scripts/close_slice.py --slice "<slice-id-or-path>" --relate supersedes "<old-slice-id-or-path>" --confirm-impact

# Close a slice with a partial replacement relation scoped to one story/requirement
python3 <path-to-close-slice>/scripts/close_slice.py --slice "<slice-id-or-path>" --relate replaces_partially "<old-slice-id-or-path>" --story-title "Story 2 - Legacy flow" --requirement-id FR-002 --selector "legacy checkout path" --confirm-impact

# Output JSON for downstream tooling
python3 <path-to-close-slice>/scripts/close_slice.py --json
```

Use `--confirm-impact` when closure also changes the semantic validity of older execution slices. Use `--force` only for deliberate repair when the slice lifecycle is temporarily inconsistent and you have already verified the intent with the user.

If a repository later wants to archive or prune closed slices, treat that as a separate explicit maintenance workflow rather than part of slice closure.
