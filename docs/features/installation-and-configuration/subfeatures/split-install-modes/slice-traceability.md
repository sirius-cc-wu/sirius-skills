# Slice Traceability

## Conventions

- Keep story IDs stable across this subfeature packet.
- Use planned slice IDs for planning-level decomposition and leave execution
  slice IDs blank until `slice` bootstraps real execution work.
- Record blockers only when the later slice truly depends on the earlier
  boundary decision or implementation packet.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SIM-01 | M | Add a source-linked local install path | I1 | SIM-01-local-helper, SIM-01-local-docs | Helper, Docs |  |  | Split between helper behavior and published local install guidance |
| SIM-02 | L | Separate packaged install from local install | I2 | SIM-02-packaged-targets, SIM-02-packaged-compat | Make targets, Compatibility policy | SIM-01-local-helper |  | Install-mode split depends on a working local helper first |
| SIM-03 | L | Scope runtime sync and parity to packaging boundaries | I3 | SIM-03-runtime-scope, SIM-03-parity-scope | Runtime sync, Maintenance reporting | SIM-02-packaged-compat |  | Keeps copied-runtime and parity assumptions behind the explicit packaged boundary |
| SIM-04 | M | Publish migration and operator guidance | I3 | SIM-04-migration-guidance | Docs, Migration notes | SIM-03-parity-scope |  | Guidance should reflect the final install target names and parity semantics |

## Notes

- `Blocked By` records planned execution ordering, not story hierarchy.
- The main design boundary in this subfeature is local source-linked install
  versus packaged standalone install; every planned slice should reinforce that
  split rather than blur it again.
