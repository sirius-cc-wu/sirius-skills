# Discover: Accelerator Readiness Dashboard

## Parent Feature

- Feature: `throughput-acceleration-workflow`
- Subfeature ID: `accelerator-readiness-dashboard`
- Subfeature Type: `additive`

## Problem

Expose structured readiness dashboards for autoplan and ship/ship-slice gates.

## Requested Subfeature

- Add machine-readable readiness summaries for both planning (`autoplan`) and
  execution (`ship` / `ship-slice`) accelerators.
- Include current gate states such as next owner, active blockers, dependency
  readiness, approval requirement, and commit checkpoint requirement.
- Keep dashboards derived from durable artifacts plus explicit runtime context;
  do not create a new source-of-truth registry.

## Baseline Artifacts To Assess

- `discover.md`
- `system-design.md`
- `user-stories.md`

## Subfeature Execution Planning

- Add or update `slice-planning.md` and `slice-traceability.md` inside this subfeature folder for any new execution work.
- Treat the parent feature docs as baseline context unless impact analysis explicitly narrows or supersedes them.

## Risks and Open Questions

- Which readiness fields are stable enough to expose as a long-term JSON
  contract for downstream tooling?
- How should dashboard outputs represent stale checkpoint context versus current
  artifact truth without confusing operators?
