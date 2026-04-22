# Slice Traceability

## Conventions

- Use stable story IDs from `user-stories.md`.
- Use planned slice IDs from this feature's `slice-planning.md`.
- Leave `Execution Slice IDs` blank until actual slice bootstrap occurs.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TAW-01 | L | Add one planning entrypoint that can run the reviewed planning stack end to end | I3 | taw-autoplan | planning-layer orchestration, review boundary preservation | taw-runtime-foundation |  | Keeps planning acceleration separate from execution finishing semantics |
| TAW-02 | XL | Finish one active slice end to end without replacing existing owners | I2 | taw-ship-handoff | backlog handoff contract, `ship` JSON output | taw-runtime-foundation |  | Preserves `ship` as a standalone backlog resolver while making later delegation possible |
| TAW-02 | XL | Finish one active slice end to end without replacing existing owners | I2 | taw-ship-slice-loop | one-slice finishing, checkpoint-aware resume, execution-owner orchestration | taw-ship-handoff |  | Adds the narrow finisher without absorbing backlog traversal |
| TAW-02 | XL | Finish one active slice end to end without replacing existing owners | I3 | taw-ship-backlog-integration | optional backlog delegation, execution config, one-active-slice enforcement | taw-ship-slice-loop |  | Reuses the validated finisher instead of expanding `ship` into a monolith |
| TAW-03 | L | Resume interrupted accelerator runs from durable checkpoint context | I1 | taw-runtime-foundation | shared runtime stores, locking, packaged runtime sync |  | taw-runtime-foundation | Establishes supplemental runtime support without changing workflow truth ownership |
| TAW-03 | L | Resume interrupted accelerator runs from durable checkpoint context | I2 | taw-ship-slice-loop | checkpoint reconciliation, stop-boundary resume semantics | taw-ship-handoff |  | Couples resume behavior to one-slice finishing so the state model stays consistent |
| TAW-04 | M | Persist repo-scoped workflow learnings across sessions | I1 | taw-learn-skill | learnings store access, promotion/pruning flows, learn skill CLI | taw-runtime-foundation |  | Makes learnings durable and inspectable before accelerators begin consuming them widely |

## Notes

- `Blocked By` records planned-slice execution dependencies, not story dependencies.
- Story fan-out is recorded by repeating the story row once per planned slice.
- `Execution Slice IDs` stays blank until planning is reviewed, approved, committed, and bootstrapped with `slice`.
