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
| SIM-01 | M | Add a source-linked local install path | I1 | SIM-01-local-helper | Helper |  | SIM-01-local-helper | Establishes the deterministic local symlink helper before other install-mode work depends on it |
| SIM-01 | M | Add a source-linked local install path | I1 | SIM-01-local-docs | Docs | SIM-01-local-helper | SIM-01-local-docs | Documents the local workflow only after helper behavior is concrete |
| SIM-02 | L | Separate packaged install from local install | I2 | SIM-02-packaged-targets | Make targets | SIM-01-local-helper |  | Splits the command surface once the local helper contract exists |
| SIM-02 | L | Separate packaged install from local install | I2 | SIM-02-packaged-compat | Compatibility policy | SIM-02-packaged-targets |  | Preserves the old packaged behavior while the new target split lands |
| SIM-03 | L | Scope runtime sync and parity to packaging boundaries | I3 | SIM-03-runtime-scope | Runtime sync | SIM-02-packaged-compat |  | Keeps copied-runtime sync behind the explicit packaged boundary |
| SIM-03 | L | Scope runtime sync and parity to packaging boundaries | I3 | SIM-03-parity-scope | Maintenance reporting | SIM-03-runtime-scope |  | Narrows parity defaults only after packaged-runtime scoping is in place |
| SIM-04 | M | Publish migration and operator guidance | I3 | SIM-04-migration-guidance | Docs, Migration notes | SIM-03-parity-scope |  | Guidance should reflect the final install target names and parity semantics |

## Notes

- `Blocked By` records planned execution ordering, not story hierarchy.
- The main design boundary in this subfeature is local source-linked install
  versus packaged standalone install; every planned slice should reinforce that
  split rather than blur it again.
