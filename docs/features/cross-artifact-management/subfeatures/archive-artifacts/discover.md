# Discover: Archive Artifacts

## Parent Feature

- Feature: `cross-artifact-management`
- Subfeature ID: `archive-artifacts`
- Subfeature Type: `additive`

## Problem

Durable workflow artifacts are valuable, but active registries can become noisy
over time as proposals are rejected, packets are superseded, and slices are
closed. The repo already prefers non-destructive history, so any archive
capability must reduce active clutter without breaking lineage or deleting
important context.

## Goals

- Define a supported way to retire or archive artifacts that are no longer part
  of the active workflow surface.
- Preserve traceability from archived artifacts back to their original context.
- Keep active registries readable while retaining durable history.
- Respect the repo’s existing preference for explicit, human-invoked cleanup.

## Non-Goals

- Automatically purge planning packets or slices as part of normal closure.
- Treat archival as an explicit maintenance workflow rather than something that
  happens automatically during slice closure.
- Treat archival as a substitute for audit or repair.

## Baseline Artifacts To Assess

- proposal lifecycle states such as rejected, superseded, accepted, and promoted
- reviewed and finalized subfeatures
- closed or superseded execution slices and their relation metadata
- any registry entries or folder layout that would need archive-aware handling

## Success Criteria

- A maintainer can archive old artifacts without losing discoverability or
  lineage.
- Archival remains explicit and reviewable rather than implicit side effects.
- The capability fits cleanly with finalization and non-destructive closure.

## Risks and Open Questions

- Which artifact states should remain visible in active registries vs archived
  surfaces?
- Should archival move folders, mark metadata, generate reports, or some
  combination of those?
