# Impact Analysis: Feature Consolidation And Reduction

## Target Subfeature

- Parent Feature: `planning-workflow`
- Subfeature ID: `feature-consolidation-and-reduction`
- Subfeature Type: `superseding`
- Current Subfeature Status: `reviewed`

## Subfeature Summary

Require new planning-workflow capabilities to declare what they simplify,
supersede, narrow, or retire, then make that declaration enforceable during
planning review and reusable by downstream maintenance/reporting workflows.

## Parent Baseline Reviewed

- `docs/features/planning-workflow/discover.md`
- `docs/features/planning-workflow/system-design.md`
- `docs/features/planning-workflow/user-stories.md`
- `docs/features/planning-workflow/slice-planning.md`
- `docs/features/planning-workflow/slice-traceability.md`

## Candidate Affected Story IDs

- `PW-01`
- `PW-02`
- `PW-03`
- `PW-04`

## Candidate Affected Increment IDs

- `I1`
- `I2`
- `I3`

## Candidate Affected Slice IDs

- `pw-registry`
- `pw-gates`
- `pw-routing`
- `pw-breakdown-guidance`
- `pw-review-readiness`

## Inherited Constraints

- Keep the planning workflow repository-first and feature-scoped; do not create
  a new readiness state or execution-owned control plane for consolidation.
- Reuse existing metadata carriers such as `.planning-meta.json` and
  `.subfeature-meta.json` before introducing any new durable artifact type.
- Keep parent planning docs as the baseline source of truth; this subfeature may
  narrow or supersede behavior but should not silently replace the parent packet.
- Preserve the boundary that `review-planning` is the planning gate and
  `slice`/execution begin only after approval and planning commit.

## Impact Notes

- This subfeature primarily reshapes the planning contract around the parent
  feature's readiness, routing, and breakdown guidance rather than replacing the
  parent planning workflow wholesale.
- The most directly affected parent slices are the readiness and routing paths:
  `pw-gates`, `pw-routing`, and `pw-review-readiness`.
- The child backlog should contain only the new or amended work needed to add
  consolidation declarations, metadata summaries, review enforcement, canonical
  surface guidance, and maintenance-skill consumers.
- Superseded or narrowed parent slice IDs should remain contextual references in
  notes or dependencies; they should not be reused as subfeature-local slice IDs.
