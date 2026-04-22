# Discover: Two Step Approval Gate

## Parent Feature

- Feature: `throughput-acceleration-workflow`
- Subfeature ID: `two-step-approval-gate`
- Subfeature Type: `additive`

## Problem

Enforce explicit approval boundary between planning autoplan and execution autopilot.

## Requested Subfeature

- Define one explicit approval gate between planning autoplan completion and
  execution autopilot start.
- Record approval decisions durably so resume/retry flows can distinguish
  "waiting for approval" from "approved and ready to execute".
- Keep approval semantics additive to current planning/execution state models
  without introducing parallel lifecycle registries.

## Baseline Artifacts To Assess

- `discover.md`
- `system-design.md`
- `user-stories.md`

## Subfeature Execution Planning

- Add or update `slice-planning.md` and `slice-traceability.md` inside this subfeature folder for any new execution work.
- Treat the parent feature docs as baseline context unless impact analysis explicitly narrows or supersedes them.

## Risks and Open Questions

- Where should approval evidence live so it is durable and auditable without
  duplicating planning metadata ownership?
- How should the gate behave when planning artifacts change after approval was
  granted (invalidate approval versus allow execution with warning)?
