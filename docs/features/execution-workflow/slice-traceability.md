# Slice Traceability

## Conventions

- Use stable story IDs from `user-stories.md`.
- Use provisional slice IDs because no external execution tracker is configured for this reverse-engineered planning set.
- Leave `Slice IDs` blank until actual slice bootstrap occurs.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Slice IDs | Slice Slices | Blocked By | Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Bootstrap execution registry and slices | I1 | EW-101 | Bootstrap |  |  | Covers config, registry, metadata, and slice creation |
| EW-02 | L | Define slice brief and checklist readiness | I1 | EW-102, EW-103 | Brief, Checklist | EW-101 |  | Split between artifact authoring and readiness enforcement |
| EW-03 | L | Plan execution with gates and validation | I2 | EW-104, EW-105 | Plan, Gates | EW-103 |  | Keeps plan content separate from status-gate behavior |
| EW-04 | L | Review, relate, and close slices | I3 | EW-106, EW-107, EW-108 | Review, Relations, Close | EW-105 |  | Closure depends on prior review and relation integrity |

## Notes

- `Blocked By` shows execution-slice sequencing rather than story ownership.
- These mappings are intended to seed later tracker and slice bootstrap work.
