# Slice Traceability

## Conventions

- Keep story IDs stable across planning docs.
- Use provisional slice IDs because these planning docs model work before slice bootstrap.
- Leave `Slice IDs` blank until future slice bootstrap actually occurs.
- Treat subfeatures as child planning folders; do not treat them as execution slices.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Slice IDs | Slice Slices | Blocked By | Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FEW-01 | M | Initiate a durable subfeature under an existing feature | I1 | FEW-201, FEW-202 | Registry, Subfeature bootstrap |  |  | Split between registry lifecycle and child-folder initialization |
| FEW-02 | M | Produce explicit impact analysis before new work is bootstrapped | I2 | FEW-203 | Impact analysis | FEW-202 |  | Single coherent packet centered on `impact-analysis.md` |
| FEW-03 | L | Support subfeature-local planning artifacts and state transitions | I1, I2 | FEW-204, FEW-205 | State model, Subfeature-local artifact support | FEW-202, FEW-203 |  | Separates metadata/state enforcement from path-aware artifact reuse |
| FEW-04 | L | Finalize reviewed subfeatures after execution | I3 | FEW-206, FEW-207 | Breakdown, Finalization | FEW-205 |  | Keeps subfeature-local decomposition separate from feature-level cleanup |
| FEW-05 | L | Close subfeatures with cleanup and clear routing | I4 | FEW-208, FEW-209 | Cleanup closure, Routing docs | FEW-207 |  | Finalization should preserve the durable subfeature folder as the history record |

## Notes

- `Blocked By` uses execution-slice style dependencies between the planned slices.
- The planned slices intentionally preserve a strict order because subfeature routing, finalization, and history semantics share the same feature model.
- If the repository later supports multiple simultaneous subfeatures robustly, this file should be extended with explicit active-subfeature selection notes.
