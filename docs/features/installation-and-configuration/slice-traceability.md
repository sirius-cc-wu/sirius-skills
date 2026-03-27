# Slice Traceability

## Conventions

- Keep story IDs stable across planning docs.
- Use provisional slice IDs because these planning docs model work before slice bootstrap.
- Leave `Slice IDs` blank until real execution-slice bootstrap happens.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Slice IDs | Slice Slices | Blocked By | Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IC-01 | M | Install and uninstall the managed skill set | I1 | IC-101 | Install |  |  | Anchors the managed repo setup entrypoint |
| IC-02 | M | Configure planning and execution layout separately | I1 | IC-102, IC-103 | Planning config, Execution config | IC-101 |  | Split by config ownership surface |
| IC-03 | M | Configure naming and ID conventions | I2 | IC-104 | Conventions config | IC-103 |  | Cross-cutting config consumer story |
| IC-04 | L | Document project-local plugin and doc alignment behavior | I3 | IC-105, IC-106 | Plugin convention, Doc alignment | IC-104 |  | Keeps extension convention and docs in sync |

## Notes

- `Blocked By` reflects slice sequencing needed to keep config semantics coherent.
- These rows can seed future slice bootstrap work if the repo chooses to execute further integration work.
