# Discover: Cross-Artifact Management

## Problem

This repository now creates and maintains durable workflow artifacts across
multiple layers:

- proposal packets under `docs/proposals/`
- canonical feature packets under `docs/features/`
- feature-local subfeatures under `subfeatures/`
- execution slices under `slices/`
- registries and metadata files such as `registry.json`, `.planning-meta.json`,
  `.proposal-meta.json`, `.subfeature-meta.json`, and `.slice-meta.json`

That structure is strong enough to support repo-native planning and execution,
but the repo still lacks a coherent cross-artifact management layer.

Today, artifact health checks, lineage tracing, drift detection, reporting, and
cleanup are spread across individual workflow skills or left to manual
inspection. As the number of proposals, features, subfeatures, and slices
grows, teams need a supported way to understand the whole artifact graph and
keep it healthy over time.

## Goals

- Add a canonical feature for managing artifacts created by the planning and
  execution workflows.
- Treat proposals, features, subfeatures, and slices as one connected durable
  graph rather than isolated folders.
- Provide a clear place for cross-artifact operations such as auditing, tracing,
  reporting, repair, and archival policy.
- Preserve existing ownership boundaries while making their outputs easier to
  inspect and maintain together.

## Non-Goals

- Replace `guide-planning`, `propose`, `add-subfeature`, `guide-execution`, or
  `close-slice` with one monolithic manager.
- Move day-to-day implementation state into planning metadata or planning state
  into execution metadata.
- Delete durable planning packets automatically as part of routine artifact
  hygiene.
- Hardcode project-specific retention or reporting rules into the generic core
  workflow.

## Primary Actors

- Repository maintainer keeping planning and execution artifacts healthy.
- Planning owner reviewing proposal and feature packet readiness.
- Execution owner tracing slices back to their parent planning artifacts.
- Reporting or release owner needing summaries of active, stale, and completed
  workflow packets.

## Requested Capability

- Audit artifact trees for missing required files, stale states, broken
  references, and registry drift.
- Trace lineage across proposal, feature, subfeature, and slice artifacts.
- Report queues, status summaries, stale packets, and recent activity in a
  reusable form.
- Repair README/registry/metadata drift caused by merges, manual edits, or
  partial runs.
- Archive or retire superseded artifacts without losing traceability.

## Implemented v1 Capability Stack

- `audit-artifacts` provides read-only artifact health checks and shared
  inventory discovery.
- `trace-artifacts` provides read-only lineage tracing across proposals,
  features, subfeatures, planned slices, and execution slices.
- `report-artifacts` provides read-only operational summaries grouped by type,
  status, and parent feature.
- `repair-artifacts` provides conservative dry-run/apply regeneration of active
  registries and READMEs from durable directories plus valid metadata.
- `archive-artifacts` provides read-only archive candidate discovery across
  relevant artifact layers plus explicit closed-slice archival in v1 through the
  execution owner helper.

## Confirmed Signals in Repo

- `skills/propose/scripts/manage_proposals.py` already owns proposal registry
  state and validation.
- `skills/guide-planning/scripts/manage_planning.py` already owns feature
  registry state and proposal promotion.
- `skills/add-subfeature/scripts/manage_subfeatures.py` already owns feature
  child packets and subfeature metadata.
- `skills/guide-execution/scripts/manage_execution.py` already owns slice
  registry state and relation metadata, including `audit-relations`.
- Closed slices and durable subfeature planning folders are retained by default,
  so cross-artifact maintenance should stay explicit rather than piggybacking on
  execution closure.

## Constraints

- Keep the source-of-truth files where they already belong: proposal, planning,
  subfeature, and execution tooling should continue to own their own lifecycle
  metadata.
- Prefer additive cross-artifact tooling that reads and reconciles existing
  registries over introducing parallel state stores.
- Keep the management layer generic-first and configurable through
  `.skills/conventions.json` or project-local extensions when needed.
- Preserve non-destructive history by default; archival or cleanup operations
  should be explicit and reviewable.

## Success Criteria

- A maintainer can inspect artifact health across proposal, planning, and
  execution layers without manually opening every folder.
- The repository has a coherent feature home for the cross-artifact management
  capabilities discussed so far.
- Future design and breakdown work can treat audit, trace, report, repair, and
  archive operations as explicit child capabilities instead of scattered ideas.

## Risks and Open Questions

- Some cross-artifact checks may overlap with existing feature-local validation,
  so boundaries must stay explicit.
- Repair and archival operations can become risky if they mutate durable
  artifacts too aggressively.
- Reporting needs may vary by project, which argues for a generic core plus
  configurable local overlays.
