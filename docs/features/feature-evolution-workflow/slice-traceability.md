# Slice Traceability

## Conventions

- Keep story IDs stable across planning docs.
- Use provisional slice IDs because these planning docs model work before slice bootstrap.
- Leave `Slice IDs` blank until future slice bootstrap actually occurs.
- Treat feature-change packets as planning-layer deltas; do not treat them as execution slices.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Slice IDs | Slice Slices | Blocked By | Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FEW-01 | M | Initiate a change against an existing canonical feature | I1 | FEW-201, FEW-202 | Registry, Change bootstrap |  |  | Split between registry lifecycle and per-change initialization |
| FEW-02 | M | Produce explicit impact analysis before new work is bootstrapped | I2 | FEW-203 | Impact analysis | FEW-202 |  | Single coherent packet centered on `impact-analysis.md` |
| FEW-03 | L | Support change-local planning artifacts and state transitions | I1, I2 | FEW-204, FEW-205 | State model, Change-local artifact support | FEW-202, FEW-203 |  | Separates metadata/state enforcement from path-aware artifact reuse |
| FEW-04 | L | Reconcile approved changes into canonical feature docs | I3 | FEW-206, FEW-207 | Change breakdown, Reconciliation | FEW-205 |  | Keeps change-local decomposition separate from canonical update logic |
| FEW-05 | L | Close feature changes with cleanup and clear routing | I4 | FEW-208, FEW-209 | Cleanup closure, Routing docs | FEW-207 |  | Reconciliation should leave only canonical feature artifacts as the durable record |

## Notes

- `Blocked By` uses execution-slice style dependencies between the planned slices.
- The planned slices intentionally preserve a strict order because change routing, reconciliation, and history semantics share the same feature model.
- If the repository later supports multiple simultaneous feature changes robustly, this file should be extended with explicit change-selection policy notes.
