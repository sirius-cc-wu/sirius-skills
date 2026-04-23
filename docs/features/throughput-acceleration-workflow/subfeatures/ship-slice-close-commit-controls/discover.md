# Discover: Ship Slice Close Commit Controls

## Parent Feature

- Feature: `throughput-acceleration-workflow`
- Subfeature ID: `ship-slice-close-commit-controls`
- Subfeature Type: `additive`

## Problem

Add optional auto-close and auto-commit controls for ship-slice terminal execution.

## Requested Subfeature

- Add explicit `ship-slice` controls for continuing through `close-slice` and
  `commit` after the execution owner chain reaches a clean terminal boundary.
- Keep both controls opt-in and configuration-driven so the current explicit
  stop behavior remains the default.
- Preserve existing ownership boundaries:
  `ship-slice` may orchestrate `close-slice` and `commit`, but it must not
  absorb their state logic or rewrite their underlying invariants.
- Return deterministic stop context when auto-close or auto-commit is blocked by
  verification failures, approval requirements, dirty worktrees, or commit
  checkpoint rules.

## Why This Is Separate

- This extends the already-implemented `ship-slice-owner-chain` behavior rather
  than changing the meaning of the existing owner-chain packet.
- Closure and commit are the first execution boundaries that can mutate durable
  execution truth and Git state after review passes, so they deserve a dedicated
  planning packet.
- The roadmap already calls out `accelerators.ship_slice.auto_close` and
  `accelerators.ship_slice.auto_commit` as the next config surface.

## Candidate Scope

- `.skills/execution.json` flags for `auto_close` and `auto_commit`
- `.skills/execution.json` flag for `auto_format`
- `skills/ship-slice/scripts/ship_slice.py`
- `skills/close-slice/`
- `skills/commit/`
- `skills/ship-slice/tests/test_ship_slice.py`
- `skills/close-slice/tests/test_close_slice.py`

## Baseline Artifacts To Assess

- `discover.md`
- `system-design.md`
- `user-stories.md`
- `docs/wiki/concepts/two-step-autonomy-roadmap.md`
- `subfeatures/ship-slice-owner-chain/discover.md`
- `subfeatures/ship-slice-owner-chain/system-design.md`

## Subfeature Execution Planning

- Add or update `slice-planning.md` and `slice-traceability.md` inside this subfeature folder for any new execution work.
- Treat the parent feature docs as baseline context unless impact analysis explicitly narrows or supersedes them.

## Resolved Defaults

- `auto_format`, `auto_close`, and `auto_commit` all default to `false`.
- `auto_commit` requires `auto_close`; commit automation should not leave the
  execution slice open.
- Formatting runs before close/commit and only against the files owned by the
  delegated run.
- `ship-slice` should still commit when unrelated files elsewhere in the
  workspace are dirty, but it must stage only the files modified by the run
  itself.
- Formatter spillover outside the owned file set and mixed ownership on the
  same file remain hard stops.
- Commit-message construction stays owned by the existing `commit` skill and
  repo conventions rather than being reimplemented inside `ship-slice`.

## Remaining Risks

- Owned-file tracking must remain deterministic across resume and retry paths.
- Formatter behavior can still be surprising when language toolchains rewrite
  adjacent generated or imported files.
- Partial success reporting must keep `close-slice` and Git checkpoint truth
  aligned when close succeeds but commit stops.
