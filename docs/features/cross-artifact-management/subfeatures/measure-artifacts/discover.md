# Discover: Measure Artifacts

## Parent Feature

- Feature: `cross-artifact-management`
- Subfeature ID: `measure-artifacts`
- Subfeature Type: `additive`

## Problem

The cross-artifact management layer can already audit, trace, report, repair,
and archive durable workflow packets, but it still lacks one important kind of
signal: implementation evidence.

Today a maintainer can inspect whether a feature or subfeature exists and what
state it is in, but cannot easily answer questions such as:

- how much implementation work landed for this feature or subfeature
- how many planned slices it actually needed
- whether the work used `guide-execution` or was implemented directly
- whether smaller, localized work really benefited from the full execution
  workflow

Without those metrics, workflow decisions stay anecdotal. That makes it harder
to calibrate when `guide-execution` is worth the overhead and harder to prepare
for a future agent-level improvement loop that can propose better `guide-*`
skill behavior from real repository history.

## Requested Subfeature

- Add a reusable `measure-artifacts` capability that computes and records
  durable implementation metrics for completed features and subfeatures.
- Keep the first version focused on evidence capture and reporting inputs, not
  automatic workflow changes.
- Preserve generic-first behavior so repositories can define local thresholds or
  decision rules without hardcoding them into the base skills.

## Baseline Artifacts To Assess

- parent feature discovery and story artifacts under
  `docs/features/cross-artifact-management/`
- feature and subfeature planning packets, especially:
  - `discover.md`
  - `system-design.md`
  - `user-stories.md`
  - `slice-planning.md`
  - `slice-traceability.md`
- subfeature metadata and feature planning metadata
- execution slice registries and metadata under `slices/`
- Git history or other durable implementation signals when calculating line
  count or churn

## Subfeature Execution Planning

- Add or update `slice-planning.md` and `slice-traceability.md` inside this subfeature folder for any new execution work.
- Treat the parent feature docs as baseline context unless impact analysis explicitly narrows or supersedes them.

## Goals

- Record reusable implementation metrics such as:
  - story-size sum (`S=1`, `M=3`, `L=5`; reject `XL`)
  - total slice count
  - implementation line count or churn
  - execution mode (`guide-execution` vs direct)
- Make those metrics available to artifact reporting and later archival or
  workflow-analysis flows.
- Keep the evidence tied to canonical repository artifacts rather than hidden
  session memory.
- Support later workflow evaluation without assuming that metrics alone decide
  the right process.

## Non-Goals

- Silent self-modification of workflow skills.
- Replacing human review with automatic process policy.
- Project-specific scoring heuristics baked into the generic core.
- Treating raw code size as the only signal for workflow quality.

## Success Criteria

- A maintainer can retrieve durable implementation metrics for completed
  features and subfeatures.
- The stored metrics are generic enough to support later reporting and
  evaluation.
- The capability helps compare direct implementation against guided execution
  without mutating the workflow automatically.

## Risks and Open Questions

- Which definition of "line count" is the most useful: final LOC, diff churn, or
  slice-scoped added+deleted lines?
- Where should the metrics live so they stay durable without duplicating too
  much owner state?
- Which outcome signals beyond raw size are worth capturing in the first
  version, such as review findings, follow-up fixes, or planning drift?
