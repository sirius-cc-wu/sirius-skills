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
| `audit-artifacts` | `implemented` | Read-only health checks across artifact inventory, validation, link integrity, and registry drift. |
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

The parent packet has now been structurally reconciled with the implemented
child capability stack. The main remaining nuance is that most concrete
execution history still lives in the finalized child subfeatures rather than in
this umbrella packet.

## Main Sources

- `docs/features/cross-artifact-management/discover.md`
- `docs/features/cross-artifact-management/.planning-meta.json`
- `docs/features/cross-artifact-management/subfeatures/README.md`
- `docs/features/cross-artifact-management/subfeatures/*/{discover.md,system-design.md,.planning-meta.json}`
