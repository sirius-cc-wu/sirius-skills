# Slice Traceability

## Conventions

- Keep story IDs stable across planning docs.
- Use provisional slice IDs because these planning docs model work before slice bootstrap.
- Leave `Slice IDs` blank until future slice bootstrap actually occurs.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Slice IDs | Slice Slices | Blocked By | Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PW-01 | M | Initialize planning registry and feature metadata | I1 | pw-registry | Registry bootstrap |  |  | Covers planning config, registry, and metadata creation |
| PW-02 | L | Enforce planning readiness and routing | I1 | pw-gates, pw-routing | Gates, Routing docs | pw-registry |  | Split between status validation and routing guidance |
| PW-03 | L | Decompose stories into increments and slices | I2 | pw-templates, pw-breakdown-guidance | Templates, Breakdown guidance | pw-routing |  | Keeps scaffold behavior separate from decomposition policy |
| PW-04 | M | Review planning output and hand off to execution | I3 | pw-review-readiness, pw-slice-handoff | Review readiness, Slice handoff | pw-breakdown-guidance |  | Requires reviewed planning state before handoff |

## Notes

- `Blocked By` uses execution-slice style dependencies between the planned slices.
- This mapping is reverse-engineered from current repo behavior and can seed later slice bootstrap work.
