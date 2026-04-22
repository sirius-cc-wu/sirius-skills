# Discover: Autoplan Owner Chain

## Parent Feature

- Feature: `throughput-acceleration-workflow`
- Subfeature ID: `autoplan-owner-chain`
- Subfeature Type: `additive`

## Problem

Execute discover/design/breakdown/review-planning as one owner chain behind autoplan.

## Requested Subfeature

- Add an optional owner-chain execution mode for `autoplan` that can run
  `discover`, `design`, `breakdown`, and `review-planning` in sequence.
- Keep planning artifacts and planning status transitions owned by the existing
  planning-layer skills.
- Stop with structured handoff context whenever a hard boundary is hit
  (approval boundary, ambiguity, missing required input, or validation failure).

## Baseline Artifacts To Assess

- `discover.md`
- `system-design.md`
- `user-stories.md`

## Subfeature Execution Planning

- Add or update `slice-planning.md` and `slice-traceability.md` inside this subfeature folder for any new execution work.
- Treat the parent feature docs as baseline context unless impact analysis explicitly narrows or supersedes them.

## Risks and Open Questions

- How should `autoplan` surface partial completion when one owner in the chain
  fails after earlier owners already wrote artifacts?
- Which stop boundaries should be default hard stops versus config-driven
  optional stops?
