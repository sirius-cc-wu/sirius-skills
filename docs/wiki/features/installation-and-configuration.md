# Installation And Configuration

## Snapshot

- Feature: `installation-and-configuration`
- Status: `planning_reviewed` (updated `2026-03-24`)
- Canonical scope: install entrypoints in `Makefile` and config under `.skills/`

## What This Feature Establishes

This feature defines integration boundaries for adopting `sirius-skills`:

- Managed install and uninstall entrypoints live in `Makefile`.
- Config ownership is split across:
  - `.skills/planning.json` (planning layout)
  - `.skills/execution.json` (execution layout and behavior)
  - `.skills/conventions.json` (naming/convention policy)
- Plugin/extensions are opt-in and explicit, not auto-loaded.

## Current Child Capability Map

| Subfeature | Status | Synthesis |
|---|---|---|
| `split-install-modes` | `implemented` | Splits source-linked local install from packaged install so repo-local development can run directly from checked-in skills while preserving packaged distribution mode. |

## Key Tradeoffs

- Strength: clear config ownership prevents workflow responsibilities from
  collapsing into one file.
- Cost: maintainers must keep install targets and managed skill lists aligned.
- Strength: split install modes reduce local drift risk from stale copied
  installs while keeping packaged compatibility paths.

## Notable Delta

The split-install subfeature is implemented and its execution lineage is now
aligned with the actual `sim-*` slices recorded in subfeature traceability and
closed slice history. The parent packet can still lag the child in lifecycle
status, but the documented execution mapping is consistent again.

## Main Sources

- `docs/features/installation-and-configuration/discover.md`
- `docs/features/installation-and-configuration/system-design.md`
- `docs/features/installation-and-configuration/.planning-meta.json`
- `docs/features/installation-and-configuration/subfeatures/split-install-modes/discover.md`
- `docs/features/installation-and-configuration/subfeatures/split-install-modes/system-design.md`
