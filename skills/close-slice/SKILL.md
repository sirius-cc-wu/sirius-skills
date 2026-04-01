---
name: close-slice
description: Closes the active execution slice with validation, records durable closure metadata, and can optionally publish a non-destructive rollout entry to a project-local history or changelog document.
---

# Close Slice

Use this skill when implementation is complete and you want to close an execution slice cleanly.

## Responsibilities

1. Resolve the target slice through `guide-execution`.
2. Validate that the slice is ready to close.
3. Close the slice without deleting the original artifacts.
4. Optionally move the closed slice into a hidden archive directory.
5. Optionally publish a summary entry into a project-local canonical doc such as `docs/slice-history.md` or `CHANGELOG.md`.
6. Optionally record explicit invalidation or supersession relations as part of closure.

## Source of Truth Rules

- Keep the original slice artifacts intact. Archiving may relocate the closed slice folder, but it must not merge or delete `brief.md`, `blueprint.md`, legacy `slices.md`, or `.slice-meta.json`.
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

## Project-Local Archiving Configuration

This skill may optionally read `.skills/plugins/spec-archive.json`.

Example:

```json
{
  "target_dir": "slices/.archived"
}
```

See also `assets/spec-archive.example.json`.

If the config file is absent, archiving can still be requested explicitly with `--archive`, which defaults to a hidden directory under the configured slice root.

## Workflow

1. Resolve the target slice explicitly, or use the active slice.
2. Run `manage_execution.py validate-slice`.
3. If the slice is not already `closed`, close it through tooling.
4. If archiving is requested or configured:
    - move the closed slice into the configured archive directory, defaulting to a hidden folder under `<slice_dir>/`
    - update the registry and slice metadata so the archived path remains resolvable
    - preserve durable backlinks and closure metadata after the move
5. If publishing is requested or configured:
    - generate a concise summary from `brief.md`, `blueprint.md`, any legacy `slices.md`, and metadata
    - include explicit slice relations such as `supersedes` or `replaces_partially` when they are confirmed at close time
    - include source issue links when slice metadata and `.skills/conventions.json` provide them
    - include implementation verification highlights when they can be inferred from `blueprint.md` and any legacy `slices.md`
    - write or update the configured rollup document using stable markers
    - record publication metadata back into `.slice-meta.json`
6. Return the outcome, archive target if any, published target if any, and the retained source artifacts.

## Tooling

```bash
# Close the active slice and publish using local config if present
python3 <path-to-close-slice>/scripts/close_slice.py

# Close and archive a specific slice into the default hidden archive directory
python3 <path-to-close-slice>/scripts/close_slice.py --slice "<slice-id-or-path>" --archive

# Close and archive a slice into an explicit directory
python3 <path-to-close-slice>/scripts/close_slice.py --slice "<slice-id-or-path>" --archive-dir slices/.retired

# Close a specific slice and publish to an explicit file
python3 <path-to-close-slice>/scripts/close_slice.py --slice "<slice-id-or-path>" --publish docs/slice-history.md

# Close a slice while explicitly confirming that it supersedes an older one
python3 <path-to-close-slice>/scripts/close_slice.py --slice "<slice-id-or-path>" --relate supersedes "<old-slice-id-or-path>" --confirm-impact

# Close a slice with a partial replacement relation scoped to one story/requirement
python3 <path-to-close-slice>/scripts/close_slice.py --slice "<slice-id-or-path>" --relate replaces_partially "<old-slice-id-or-path>" --story-title "Story 2 - Legacy flow" --requirement-id FR-002 --selector "legacy checkout path" --confirm-impact

# Close only, without publishing
python3 <path-to-close-slice>/scripts/close_slice.py --slice "<slice-id-or-path>" --no-publish

# Close only, without archiving even when archive config is present
python3 <path-to-close-slice>/scripts/close_slice.py --slice "<slice-id-or-path>" --no-archive

# Output JSON for downstream tooling
python3 <path-to-close-slice>/scripts/close_slice.py --json
```

Use `--confirm-impact` when closure also changes the semantic validity of older execution slices. Use `--force` only for deliberate repair when the slice lifecycle is temporarily inconsistent and you have already verified the intent with the user.
