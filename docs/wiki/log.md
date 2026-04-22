# Wiki Log

Append-only record of wiki maintenance.

Use entries like `## [YYYY-MM-DD] operation | subject` so the log stays
grep-friendly.

## [2026-04-23] synthesis | feature packet baseline

- Read canonical feature packets under `docs/features/` (top-level and subfeature packets).
- Added synthesized feature pages for planning, execution, installation/configuration,
  hierarchical scope support, cross-artifact management, workflow-state consistency,
  and throughput acceleration.
- Added one cross-cutting concept page for ownership boundaries.
- Updated wiki index entries to reflect current synthesized pages and source coverage.

## [2026-04-23] reference-synthesis | gstack ship comparison

- Compared `gstack` `ship` workflow (local clone commit `656df0e3`, upstream `https://github.com/garrytan/gstack`) against `sirius-skills` `ship` and `ship-slice`.
- Added `docs/wiki/concepts/gstack-ship-reference.md` with behavior delta and adoptable patterns.
- Updated `docs/wiki/features/throughput-acceleration-workflow.md` with a focused `gstack` comparison and concrete wiki-level improvement guidance.
- Updated wiki index concept listings for the new reference page.

## [2026-04-23] research-synthesis | two-step autonomy workflow

- Evaluated the requested two-step experience against current `sirius-skills` accelerators (`autoplan`, `ship`, `ship-slice`) and documented the current gap: routing/checkpointing exists, full owner-chain execution does not.
- Extended `docs/wiki/concepts/gstack-ship-reference.md` with explicit "does gstack already do this?" findings (`autoplan` + `ship` are strong pattern references but not a drop-in match for sirius planning/execution artifacts).
- Added `docs/wiki/concepts/two-step-autonomy-roadmap.md` with a concrete staged roadmap, config surface proposal, and guardrails for implementing the two-step flow.
- Updated throughput feature synthesis and wiki index to point to the roadmap.

## [2026-04-23] reference-synthesis | addy agent-skills comparison

- Compared Addy Osmani `agent-skills` (`https://github.com/addyosmani/agent-skills`) against `sirius-skills` using local clone commit `1f66d57` (matches upstream `HEAD` at research time).
- Added `docs/wiki/concepts/agent-skills-reference.md` with architecture-level deltas, adoptable command-UX patterns, and non-portable elements.
- Updated `docs/wiki/features/throughput-acceleration-workflow.md` with an additional external-reference section for `agent-skills`.
- Updated wiki index concept listings for the new reference page.

## [2026-04-23] implementation-synthesis | autoplan owner-chain

- Implemented optional owner-chain execution in `skills/autoplan/scripts/autoplan.py` with config/CLI controls (`execute_owner_chain`, `stop_on_owner`).
- Added structured owner-chain boundary reporting and checkpoint/event-log context for approval, explicit owner stops, and validation/missing-input stops.
- Added focused tests in `skills/autoplan/tests/test_autoplan.py` for owner-chain happy path and stop boundaries.
- Updated autoplan skill docs and throughput/two-step wiki pages to reflect planning-side owner-chain implementation status.

## [2026-04-23] implementation-synthesis | ship-slice owner-chain

- Implemented optional execution owner-chain routing in `skills/ship-slice/scripts/ship_slice.py` with config/CLI controls (`execute_owner_chain`, `stop_on_owner`).
- Added structured stop context for review boundaries, verification/missing-input failures, explicit owner stops, and commit checkpoints.
- Added focused tests in `skills/ship-slice/tests/test_ship_slice.py` covering owner-chain advancement, stop boundaries, and deterministic checkpoint behavior.
- Updated ship-slice skill docs and two-step throughput wiki pages to reflect execution-side owner-chain implementation status.

## [2026-04-23] implementation-synthesis | two-step approval gate

- Implemented durable approval-gate records in `skills/ship/scripts/ship.py` using per-target `.approval-gate.json` markers.
- Added `ship --approve [--approval-note]` to record explicit execution approval for `planning_reviewed` targets.
- Enforced approval before delegated execution autopilot (`ship` -> `ship-slice`) and invalidated prior approvals automatically when planning artifacts change.
- Added focused `ship` tests for approval-required delegation and post-approval invalidation behavior.
