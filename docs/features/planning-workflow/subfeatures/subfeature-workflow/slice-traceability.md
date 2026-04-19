# Slice Traceability

## Conventions

- Keep story IDs stable across planning docs.
- Use provisional slice IDs because these planning docs model work before slice bootstrap.
- Leave `Slice IDs` blank until future slice bootstrap actually occurs.
- Treat subfeatures as child planning folders; do not treat them as execution slices.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Slice IDs | Slice Slices | Blocked By | Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FEW-01 | M | Initiate a durable subfeature under an existing feature | I1 | sfw-registry, sfw-initiate-change | Registry, Subfeature bootstrap |  |  | Split between registry lifecycle and child-folder initialization |
| FEW-02 | M | Produce explicit impact analysis before new work is bootstrapped | I2 | sfw-impact-analysis | Impact analysis | sfw-initiate-change |  | Single coherent packet centered on `impact-analysis.md` |
| FEW-03 | L | Support subfeature-local planning artifacts and state transitions | I1, I2 | sfw-change-metadata, sfw-change-artifacts | State model, Subfeature-local artifact support | sfw-initiate-change, sfw-impact-analysis |  | Separates metadata/state enforcement from path-aware artifact reuse |
| FEW-04 | L | Finalize reviewed subfeatures after execution | I3 | sfw-change-breakdown, sfw-finalization-workflow | Breakdown, Finalization | sfw-change-artifacts |  | Keeps subfeature-local decomposition separate from feature-level cleanup |
| FEW-05 | L | Close subfeatures with cleanup and clear routing | I4 | sfw-history-closure, sfw-routing-docs | Cleanup closure, Routing docs | sfw-finalization-workflow |  | Finalization should preserve the durable subfeature folder as the history record |

## Notes

- `Blocked By` uses execution-slice style dependencies between the planned slices.
- The planned slices intentionally preserve a strict order because subfeature routing, finalization, and history semantics share the same feature model.
- If the repository later supports multiple simultaneous subfeatures robustly, this file should be extended with explicit active-subfeature selection notes.
