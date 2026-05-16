# Cross-Artifact Management

## Snapshot

- Feature: `cross-artifact-management`
- Parent status: `implemented` (updated `2026-04-23`)
- Child capability statuses: six implemented/finalized subfeatures

## What This Feature Establishes

The parent packet defines a repository-wide maintenance layer across proposals,
features, subfeatures, and slices. It frames artifacts as one connected graph
and keeps lifecycle ownership with existing planning/execution owners.

Implemented child capabilities provide the operational stack:

| Subfeature | Status | Synthesis |
|---|---|---|
| `audit-artifacts` | `implemented` | Read-only health checks across artifact inventory, validation, link integrity, registry drift, and stale approval-note detection after slice closure. |
| `trace-artifacts` | `implemented` | Typed lineage graph across proposal, feature, subfeature, planned slice, and execution slice links. |
| `report-artifacts` | `implemented` | Operational summaries by type/status/parent with stale detection and active-vs-historical distinction. |
| `repair-artifacts` | `implemented` | Conservative dry-run/apply rebuild of derived registries and README tables from durable metadata. |
| `archive-artifacts` | `implemented` | Archive candidate discovery plus explicit closed-slice archival through execution-owner helpers. |
| `measure-artifacts` | `implemented` | Durable implementation evidence sidecar (`implementation-metrics.json`) for completed work. |

## Key Tradeoffs

- Strength: shared cross-artifact maintenance surface improves operational
  visibility without centralizing ownership.
- Cost: semantic repairs are intentionally conservative; some drift remains
  manual follow-up.
- Strength: retention model separates durable planning summaries from optional
  archived slice packet retention.

## Notable Delta

The maintenance layer now explicitly treats stale approval-gate notes as
cross-layer drift when a subfeature's traced execution slices are already
closed. That closes a blind spot where execution truth had advanced, but the
remaining approval note still advertised obsolete next-slice guidance.

## Main Sources

- `docs/features/cross-artifact-management/discover.md`
- `docs/features/cross-artifact-management/.planning-meta.json`
- `docs/features/cross-artifact-management/subfeatures/README.md`
- `docs/features/cross-artifact-management/subfeatures/*/{discover.md,system-design.md,.planning-meta.json}`
