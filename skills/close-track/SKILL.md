---
name: close-track
description: Closes the active spec track with validation, records durable closure metadata, and can optionally publish a non-destructive rollout entry to a project-local history or changelog document.
---

# Close Track

Use this skill when implementation is complete and you want to close a spec track cleanly.

## Responsibilities

1. Resolve the target track through `spec-driver`.
2. Validate that the track is ready to close.
3. Close the track without moving or deleting the original artifacts.
4. Optionally publish a summary entry into a project-local canonical doc such as `docs/spec-history.md` or `CHANGELOG.md`.
5. Optionally record explicit invalidation or supersession relations as part of closure.

## Source of Truth Rules

- Keep the original track folder in place.
- Treat `<spec_dir>/README.md`, `<spec_dir>/registry.json`, and `<track_path>/.track-meta.json` as the canonical closure records.
- Publishing is additive. It creates or updates a rollup entry with backlinks; it does not merge or erase the original `spec.md` / `plan.md` / `tasks.md`.

## Project-Local Publishing Configuration

This skill may optionally read `.skills/plugins/spec-publish.json`.

Example:

```json
{
  "target_file": "docs/spec-history.md",
  "document_title": "Specification History",
  "section_title": "Closed Tracks"
}
```

See also `assets/spec-publish.example.json`.

If the config file is absent, the skill still works for closing tracks. Publishing can also be directed explicitly by command argument.

## Workflow

1. Resolve the target track explicitly, or use the active track.
2. Run `manage_specs.py validate-track`.
3. If the track is not already `closed`, close it through tooling.
4. If publishing is requested or configured:
    - generate a concise summary from `spec.md`, `plan.md`, `tasks.md`, and metadata
   - include explicit spec relations such as `supersedes` or `replaces_partially` when they are confirmed at close time
   - include source issue links when track metadata and `.skills/identity.json` provide them
   - include implementation verification highlights when they can be inferred from the plan/tasks artifacts
    - write or update the configured rollup document using stable markers
    - record publication metadata back into `.track-meta.json`
5. Return the outcome, published target if any, and the retained source artifacts.

## Tooling

```bash
# Close the active track and publish using local config if present
python3 <path-to-close-track>/scripts/close_track.py

# Close a specific track and publish to an explicit file
python3 <path-to-close-track>/scripts/close_track.py --track "<track-id-or-path>" --publish docs/spec-history.md

# Close a track while explicitly confirming that it supersedes an older one
python3 <path-to-close-track>/scripts/close_track.py --track "<track-id-or-path>" --relate supersedes "<old-track-id-or-path>" --confirm-impact

# Close a track with a partial replacement relation scoped to one story/requirement
python3 <path-to-close-track>/scripts/close_track.py --track "<track-id-or-path>" --relate replaces_partially "<old-track-id-or-path>" --story-title "Story 2 - Legacy flow" --requirement-id FR-002 --selector "legacy checkout path" --confirm-impact

# Close only, without publishing
python3 <path-to-close-track>/scripts/close_track.py --track "<track-id-or-path>" --no-publish

# Output JSON for downstream tooling
python3 <path-to-close-track>/scripts/close_track.py --json
```

Use `--confirm-impact` when closure also changes the semantic validity of older specs. Use `--force` only for deliberate repair when the track lifecycle is temporarily inconsistent and you have already verified the intent with the user.
