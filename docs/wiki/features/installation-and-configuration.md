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

The parent packet still reports `planning_reviewed`, but the split-install child
is `implemented`, indicating implementation has advanced beyond the original
baseline packet.

## Main Sources

- `docs/features/installation-and-configuration/discover.md`
- `docs/features/installation-and-configuration/system-design.md`
- `docs/features/installation-and-configuration/.planning-meta.json`
- `docs/features/installation-and-configuration/subfeatures/split-install-modes/discover.md`
- `docs/features/installation-and-configuration/subfeatures/split-install-modes/system-design.md`
