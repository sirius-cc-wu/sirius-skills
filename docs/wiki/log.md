## [2026-05-16] implementation-synthesis | audit stale approval-note drift

- Extended `skills/audit-artifacts/scripts/audit_artifacts.py` so subfeature audits flag approval notes that still mention already-closed traced execution slices.
- Added a regression test in `skills/audit-artifacts/tests/test_audit_artifacts.py` covering stale `.approval-gate.json` slice references after closure.
- Updated `docs/wiki/features/cross-artifact-management.md` and `docs/wiki/index.md` so the synthesized maintenance-layer docs describe the new stale approval-note detection behavior.

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

## [2026-04-23] implementation-synthesis | accelerator readiness dashboard

- Added a normalized `readiness` payload to `autoplan`, `ship`, and `ship-slice` JSON outputs with `can_proceed`, `next_owner`, `blocked_by`, `stop_reason`, `approval_gate`, and `commit_checkpoint`.
- Kept gate ownership explicit: approval and commit remain hard boundaries, now surfaced in one machine-readable contract.
- Added focused test assertions across autoplan/ship-slice/ship suites for approval boundaries, review boundaries, commit checkpoints, and happy-path readiness.
- Updated skill docs and throughput/two-step/gstack wiki synthesis pages to mark readiness-dashboard work as implemented.

## [2026-04-23] docs-synthesis | two-step UX cleanup entrypoints

- Updated `docs/wiki/concepts/two-step-autonomy-roadmap.md` with an explicit operator command flow:
  `autoplan --execute-owner-chain` -> human review -> `ship --approve` -> `ship --resume`.
- Clarified guide-path positioning: `guide-scope`, `guide-planning`, and `guide-execution` remain advanced/manual entrypoints rather than the default happy path.
- Updated throughput synthesis, wiki index summary text, and `README.md` to reflect the same two-step entrypoint guidance consistently.

## [2026-04-23] implementation-synthesis | accelerator transition guardrails

- Added shared accelerator guardrail runtime in `lib/workflow_runtime/accelerator_guardrails.py` to centralize stop-reason classification, reason normalization, and readiness invariant construction.
- Updated `autoplan`, `ship-slice`, and `ship` scripts to consume shared guardrail helpers instead of maintaining duplicated local classification/deduplication logic.
- Synced shared `workflow_runtime` into packaged skill copies via `scripts/sync_shared_skill_runtime.py`.
- Added focused shared guardrail tests (`skills/autoplan/tests/test_accelerator_guardrails.py`) and revalidated accelerator suites.
- Updated roadmap/feature synthesis and skill guardrail docs to reflect implemented cross-accelerator transition normalization.

## [2026-04-23] implementation-synthesis | ship-slice terminal automation

- Implemented delegated owned-change-set tracking in `skills/ship-slice/scripts/ship_slice.py` so resumed runs can distinguish owned dirty files from unrelated baseline dirtiness and stop on same-file ownership conflicts.
- Added optional terminal automation controls under `accelerators.ship_slice`: `auto_format`, `auto_close`, `auto_commit`, plus path-scoped `format_command`; `auto_commit` now requires `auto_close`.
- Delegated terminal automation now supports owned-file formatting, close-slice handoff, owned-only commit staging, formatter spillover detection, and explicit close-success / commit-failure partial-success reporting.
- Added focused `ship-slice` tests for owned-change tracking, formatter spillover, full format-close-commit happy path, invalid config, and commit-failure partial success.
- Closed slices `scc-owned-change-set` and `scc-terminal-automation`, finalized subfeature `ship-slice-close-commit-controls`, and updated throughput/two-step/skill docs to reflect the implemented execution tail.

## [2026-04-24] implementation-synthesis | delegated execution stop policies

- Implemented typed delegated continuation-policy parsing in `skills/ship-slice/scripts/ship_slice.py` with config-only controls under `accelerators.ship_slice.continuation_policy` for `review_boundary` and `commit_checkpoint`.
- Updated delegated execution behavior so `auto_close`/`auto_commit` respect continuation policy defaults and config overrides instead of bypassing boundaries implicitly.
- Extended `ship-slice` readiness output with `policy_action` and `policy_source`, while preserving boundary visibility in `blocked_by` and stop reporting.
- Propagated delegated policy readiness metadata through `skills/ship/scripts/ship.py` so `ship --resume` surfaces the same policy context from delegated runs.
- Added and updated focused tests in `skills/ship-slice/tests/test_ship_slice.py` and `skills/ship/tests/test_ship.py`, then validated with `python3 -m pytest -q skills/ship/tests/test_ship.py skills/ship-slice/tests/test_ship_slice.py`.
- Closed slices `dsp-policy-contract` and `dsp-boundary-enforcement`, finalized subfeature `delegated-execution-stop-policies`, and updated throughput roadmap/wiki synthesis to mark continuation policy delivery as implemented.

## [2026-04-24] analysis-synthesis | subfeature completion drift

- Analyzed why completed subfeature work can still remain `planning_reviewed` / `reviewed` in durable metadata.
- Documented the key finding in `docs/wiki/features/workflow-state-consistency.md`: terminal subfeature sync already exists in `close-slice`, but `ship` is orchestration-only and direct repo implementation can bypass that owner-sync path entirely.
- Captured candidate follow-up directions for later repair: terminal reconciliation in `ship`, a semantic reconcile maintenance command, stronger guardrails for agent-led multi-slice work, and documentation cleanup around subfeature completion semantics.

## [2026-05-01] docs-repair | audit inconsistency cleanup

- Ran `audit-artifacts --json` and identified structural/documentation inconsistencies across the parent cross-artifact feature packet, hierarchical scope traceability, split-install subfeature metadata, and one closed slice missing a core doc artifact.
- Repaired the cross-artifact-management parent packet by adding `system-design.md`, `slice-planning.md`, and `slice-traceability.md` so feature validation matches the implemented child maintenance stack.
- Split grouped planned-slice rows in `docs/features/hierarchical-scope-support/slice-traceability.md` into one row per planned slice so audit mapping is deterministic.
- Updated `docs/features/installation-and-configuration/subfeatures/split-install-modes/.subfeature-meta.json` so `affected_slice_ids` matches the actual closed `sim-*` execution slices.
- Restored a minimal `README.md` for the closed `sim-parity-scope` slice so closed-slice validation has the expected core artifact surface.
- Updated synthesized wiki feature pages to reflect the repaired planning/doc state.
