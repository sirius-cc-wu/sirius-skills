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
- Make the feature/subfeature `system-design.md` summary the durable retained
  history for closed slices once a maintainer decides the archived slice folders
  no longer add value.

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
- archived slice summaries already copied into `system-design.md`

## Success Criteria

- A maintainer can archive old artifacts without losing discoverability or
  lineage.
- Archival remains explicit and reviewable rather than implicit side effects.
- The capability fits cleanly with finalization and non-destructive closure.
- A later prune step can remove archived slice folders without making the
  feature-level history unreadable or turning audit/report output into false
  breakage.

## Risks and Open Questions

- Which artifact states should remain visible in active registries vs archived
  surfaces?
- Should archival move folders, mark metadata, generate reports, or some
  combination of those?
- What minimal retained signal should remain after an archived slice folder is
  pruned: summary block only, registry tombstone, or explicit history sidecar?
