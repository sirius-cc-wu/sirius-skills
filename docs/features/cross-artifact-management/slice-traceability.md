# Slice Traceability

Use this file to map the parent feature stories to the finalized child
capabilities that actually delivered them.

## Conventions

- Keep feature story IDs exactly as they appear in `user-stories.md`.
- Use one row per parent feature story in this umbrella packet.
- `Planned Slice IDs` here are parent-level traceability placeholders, not a
  second execution backlog.
- `Execution Slice IDs` should point at the already-closed execution slices that
  implemented the corresponding child capability.
- Use `Notes` to clarify when delivery happened through a child subfeature.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CAM-01 | M | Audit artifact health | I1 | cam-audit | audit-artifacts subfeature |  | aat-cross-artifact-audit | Implemented through finalized `docs/features/cross-artifact-management/subfeatures/audit-artifacts/`. |
| CAM-02 | M | Trace artifact lineage | I1 | cam-trace | trace-artifacts subfeature | cam-audit | tat-trace-artifact-lineage | Implemented through finalized `docs/features/cross-artifact-management/subfeatures/trace-artifacts/`. |
| CAM-03 | M | Report artifact state | I1 | cam-report | report-artifacts subfeature | cam-audit | rpt-artifact-state-report | Implemented through finalized `docs/features/cross-artifact-management/subfeatures/report-artifacts/`. |
| CAM-04 | M | Repair artifact drift | I1 | cam-repair | repair-artifacts subfeature | cam-audit | rpr-registry-drift-repair | Implemented through finalized `docs/features/cross-artifact-management/subfeatures/repair-artifacts/`. |
| CAM-05 | M | Archive durable history safely | I1 | cam-archive | archive-artifacts subfeature | cam-report | arc-safe-slice-archival | Implemented through finalized `docs/features/cross-artifact-management/subfeatures/archive-artifacts/`. |
| CAM-06 | M | Measure workflow evidence | I1 | cam-measure | measure-artifacts subfeature | cam-report | mea-metrics-foundation, mea-metrics-consumers | Implemented through finalized `docs/features/cross-artifact-management/subfeatures/measure-artifacts/`; delivery used two execution slices. |

## Notes

- This parent traceability file records umbrella lineage only.
- The child subfeature packets remain the canonical planning surface for their
  own breakdown and execution history.
- Keeping these rows here allows feature-level audits and wiki synthesis to
  reason about the parent capability without pretending the implementation never
  fanned out into child scopes.
