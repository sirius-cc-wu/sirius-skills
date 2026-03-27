---
name: close-slice
description: Closes the active execution slice with validation, records durable closure metadata, and can optionally publish a non-destructive rollout entry to a project-local history or changelog document.
---

# Close Slice

Use this skill when implementation is complete and you want to close an execution slice cleanly.

## Responsibilities

1. Resolve the target slice through `guide-execution`.
2. Validate that the slice is ready to close.
3. Close the slice without moving or deleting the original artifacts.
4. Optionally publish a summary entry into a project-local canonical doc such as `docs/slice-history.md` or `CHANGELOG.md`.
5. Optionally record explicit invalidation or supersession relations as part of closure.

## Source of Truth Rules

- Keep the original slice folder in place.
- Treat `<slice_dir>/README.md`, `<slice_dir>/registry.json`, and `<slice_path>/.slice-meta.json` as the canonical closure records.
- Publishing is additive. It creates or updates a rollup entry with backlinks; it does not merge or erase the original `brief.md` / `blueprint.md` artifacts, and it may also reference legacy `slices.md` files when present.

## Artifact Ownership

`close-slice` owns closure metadata updates and any optional publication outputs.

`guide-execution` should route into closure only after execution review is complete; it should not replace `close-slice` by mutating closure state directly outside normal registry/status tooling.

## Project-Local Publishing Configuration

This skill may optionally read `.skills/plugins/spec-publish.json`.

Example:

```json
{
  "target_file": "docs/slice-history.md",
  "document_title": "Execution Slice History",
  "section_title": "Closed Slices"
}
```

See also `assets/spec-publish.example.json`.

If the config file is absent, the skill still works for closing slices. Publishing can also be directed explicitly by command argument.

## Workflow

1. Resolve the target slice explicitly, or use the active slice.
2. Run `manage_execution.py validate-slice`.
3. If the slice is not already `closed`, close it through tooling.
4. If publishing is requested or configured:
    - generate a concise summary from `brief.md`, `blueprint.md`, any legacy `slices.md`, and metadata
    - include explicit slice relations such as `supersedes` or `replaces_partially` when they are confirmed at close time
    - include source issue links when slice metadata and `.skills/conventions.json` provide them
    - include implementation verification highlights when they can be inferred from `blueprint.md` and any legacy `slices.md`
    - write or update the configured rollup document using stable markers
    - record publication metadata back into `.slice-meta.json`
5. Return the outcome, published target if any, and the retained source artifacts.

## Tooling

```bash
# Close the active slice and publish using local config if present
python3 <path-to-close-slice>/scripts/close_slice.py

# Close a specific slice and publish to an explicit file
python3 <path-to-close-slice>/scripts/close_slice.py --slice "<slice-id-or-path>" --publish docs/slice-history.md

# Close a slice while explicitly confirming that it supersedes an older one
python3 <path-to-close-slice>/scripts/close_slice.py --slice "<slice-id-or-path>" --relate supersedes "<old-slice-id-or-path>" --confirm-impact

# Close a slice with a partial replacement relation scoped to one story/requirement
python3 <path-to-close-slice>/scripts/close_slice.py --slice "<slice-id-or-path>" --relate replaces_partially "<old-slice-id-or-path>" --story-title "Story 2 - Legacy flow" --requirement-id FR-002 --selector "legacy checkout path" --confirm-impact

# Close only, without publishing
python3 <path-to-close-slice>/scripts/close_slice.py --slice "<slice-id-or-path>" --no-publish

# Output JSON for downstream tooling
python3 <path-to-close-slice>/scripts/close_slice.py --json
```

Use `--confirm-impact` when closure also changes the semantic validity of older execution slices. Use `--force` only for deliberate repair when the slice lifecycle is temporarily inconsistent and you have already verified the intent with the user.
