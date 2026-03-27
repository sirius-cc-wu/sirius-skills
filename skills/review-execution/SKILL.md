---
name: review-execution
description: Reviews implementation against slice-scoped briefs and plans, then feeds durable fixes back into execution artifacts before closure.
---

# Review Execution

Use this skill after implementation and validation, and before `close-slice`, when a execution slice needs an explicit review against `brief.md` and `blueprint.md`.

## Responsibilities

1. Review implementation and validation evidence against the active slice's `brief.md` and `blueprint.md`.
2. Distinguish brief-to-implementation gaps from intent-to-brief gaps.
3. Feed durable fixes back into slice-scoped artifacts or upstream planning guidance so the next execution starts from improved context.
4. Confirm whether the slice is ready for `close-slice` or needs more execution work first.

## Preferred Input

- `<slice_path>/brief.md`
- `<slice_path>/blueprint.md`
- optional `<slice_path>/slices.md` for legacy slices
- the implementation diff or changed files
- validation results, tracker notes, or PR context when available

Resolve `<slice_path>` through `execution-driver`.

## Required Output

- updated slice-scoped execution artifacts when the review exposes durable gaps
- explicit review outcome recorded in the tracker, PR, or closure context used by the team

## Artifact Ownership

`review-execution` owns the review outcome and any durable updates needed in `brief.md`, `blueprint.md`, or upstream planning guidance when the review exposes context gaps.

`execution-driver` should route into execution review, but it should not absorb the review itself or silently close slices without that owning review step.

## Review Rules

- Check that requirements, acceptance notes, and validation steps still match the implementation.
- Classify findings explicitly:
  - brief-to-implementation gap
  - intent-to-brief gap
  - follow-up improvement outside the active slice
- Prefer fixing the brief or plan when the issue reflects missing or ambiguous execution context.
- Capture any follow-up work in the team's execution tracker instead of overloading slice readiness state.

## Workflow

1. Resolve the active slice with `execution-driver`.
2. Read `brief.md`, `blueprint.md`, changed code, and available validation evidence.
3. Compare the implementation with the slice-scoped requirements and validation plan.
4. Update `brief.md`, `blueprint.md`, or upstream planning guidance when the review reveals a durable context gap.
5. Stop when the slice is ready for `close-slice` or return the work to execution with explicit findings.

## Guardrails

- Do not close the slice while blocking review findings remain unresolved.
- Do not treat code-only fixes as complete if the underlying brief or plan is still wrong.
- Do not use slice metadata to mirror execution lifecycle states owned by the tracker.
