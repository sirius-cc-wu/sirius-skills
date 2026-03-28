---
name: breakdown
description: Converts repo stories and planning docs into directly executable, dependency-aware work items with traceability and execution handoff.
---

# Breakdown

Use this skill after feature-level discovery and design to turn repo stories into directly executable work.

If you need a starting folder for a new feature, scaffold the default breakdown files with:

```bash
python3 skills/breakdown/scripts/scaffold_breakdown.py <feature-slug>
```

By default this creates:

```text
docs/features/<feature-slug>/slice-planning.md
docs/features/<feature-slug>/slice-traceability.md
```

If `.skills/planning.json` defines `planning_dir`, the scaffold uses
`<planning_dir>/<feature-slug>/` instead unless `--base-dir` is passed.

## Responsibilities

1. Validate that stories are concrete, scoped, and ready for decomposition.
2. Split oversized work into smaller, independently verifiable execution packets.
3. Produce planning artifacts that preserve story-to-slice traceability, increment grouping, sequencing, and execution mode assumptions.
4. Create executable work items, dependency links, and explicit parallel-safe lanes where appropriate.
5. Hand off ready work to `review-planning` and then `slice` for execution-slice bootstrap.

## Required Output

- `<feature_path>/slice-planning.md`
- `<feature_path>/slice-traceability.md`

Resolve `<feature_path>` as `<planning_dir>/<feature-slug>/`.

- If `.skills/planning.json` defines `planning_dir`, use that as `<planning_dir>`.
- Otherwise default to `docs/features`.

Preferred execution output when available:

- planned slices and dependency links

Use `assets/slice-planning-template.md` as the default starting point for `<feature_path>/slice-planning.md`.
Use `assets/slice-traceability-template.md` as the default starting point for `<feature_path>/slice-traceability.md`.
Use `scripts/scaffold_breakdown.py` when you want both files scaffolded together from a feature slug.

## Breakdown Rules

- Keep stories and design in repo docs; keep executable slices in the repository's planning artifacts.
- Prefer repository story sizes such as `S`, `M`, `L`, and `XL`.
- Record an explicit story risk for decomposition decisions, using `low`, `medium`, or `high`.
- Split any `XL` item before creating execution-ready slices.
- Do not assume only `XL` stories may split. A smaller `S`/`M`/`L` story may still split when risk, coupling, or validation shape would make one packet brittle.
- Every executable slice should be small enough to fit one slice-scoped execution slice.
- Group related slices into small, demonstrable increments before bootstrapping slices.
- Prefer execution packets that stay within one subsystem or a small set of files.
- Every execution-ready slice should have concrete acceptance notes and a validation command or artifact check.
- Preserve stable story identifiers so slice traceability is durable.

## Sizing and Risk Heuristics

Use size as the default signal and risk as the override signal.

- `S` and `M` stories usually stay as one planned slice unless there is a clear reason to split.
- `L` stories may stay whole when the work is cohesive and low-risk, but may split when the work naturally falls into independently verifiable packets.
- `XL` stories should be split before they become execution-ready.
- `high` risk can justify splitting even when the story is not `XL`.

Treat risk as elevated when one or more of these are true:

- the work crosses multiple subsystems or ownership boundaries
- the work mixes separate validation paths that would be clearer in separate packets
- the work includes migration, reconciliation, replacement, or compatibility impact
- the work has high coupling, fragile sequencing, or non-trivial handoff risk
- the acceptance path is ambiguous unless the work is decomposed further

When you choose `keep`, `split`, or `defer`, record both the size and the risk and explain the primary reason in `slice-planning.md`.

## Increment Planning

Use increments to bridge repo-level planning and slice-level execution:

- an increment is a small, demonstrable outcome made from one or more execution-ready slices
- Increment 1 should usually be the simplest end-to-end usable path
- increments belong in `slice-planning.md` and `slice-traceability.md`, not in spec-slice state
- one increment can contain multiple planned slices, but each slice still gets its own execution slice later
- if a story spans multiple increments, record that explicitly instead of hiding it in notes

## Execution Mode and Packet Design

Default to `single-agent` execution when:

- work has a tight critical path
- slice coupling is high and handoff risk is non-trivial
- codebase context is concentrated in one subsystem

Prefer `multi-agent` execution only when:

- there are clear parallel lanes with minimal overlap
- integration points can be validated with deterministic checks
- ownership and handoff boundaries can be documented explicitly

When a story becomes execution-ready:

- split it into small packets when size or risk indicates the story would be brittle as one execution item
- mark blockers and sequencing constraints explicitly
- label only genuinely independent slices as parallel-safe
- if using `multi-agent`, record lane ownership, handoff targets, and an integration checkpoint after each lane

## Execution Backlog Guidance

Use `slice-planning.md` as the execution backlog:

- create one planned slice per directly executable work item
- group those slices under increment headings in `slice-planning.md`
- use parent-child relationships when a larger story needs grouped sub-slices
- record blockers as explicit dependency links in `slice-planning.md`
- reflect safe parallel lanes and integration checkpoints in `slice-planning.md`
- keep mapping from repo story IDs to planned slice IDs in `slice-traceability.md`

Record slices and dependencies directly in `slice-planning.md` and use it as the primary execution backlog.

## Story-to-Slice Mapping

Treat repo story IDs as the planning-system identifiers and planned slice IDs as the execution identifiers.

Default mapping:

- one repo story can map to one or many planned slices
- each execution-ready work item becomes one planned slice
- preserve the repo story ID in:
  - `slice-traceability.md`
  - the planned slice description
- use dependency links only for real execution blockers, not for narrative grouping

Preferred description shape for a new slice:

```text
Story: <story-id>
Increment: <increment-id>
Slice: <short slice name>
Acceptance:
- ...
Validation:
- ...
```

If one repo story splits into multiple executable work items:

- keep the story as a repo concept in `user-stories.md`
- create multiple planned slices
- optionally create a non-executable parent item only when it helps grouped review
- record the story-to-slice fan-out in `slice-traceability.md`

Only reuse the repo story ID as the planned slice ID when **all** of the following are true:

- the repo story maps to exactly one executable work item
- the team wants the story ID preserved end-to-end
- that ID will not collide with another execution item

Otherwise, use an opaque slice ID and keep the repo story ID in traceability metadata.

## Workflow

1. Read `discover.md`, `system-design.md`, optional `ui-design.md`, and `user-stories.md`.
2. Validate that each story has scope, acceptance notes, an explicit size, and an explicit risk rating.
3. Split oversized work into smaller execution packets and group them into increments with clear demo outcomes.
4. Choose `single-agent` or `multi-agent` handling where relevant and record lane assumptions.
5. Write `slice-planning.md` and `slice-traceability.md` with increment groupings, dependency notes, parallel-safe lanes, and integration checkpoints as needed.
6. Create planned slices and dependency links for execution-ready work, keeping packet validation explicit.
7. Stop when each slice is ready for `review-planning` and subsequent bootstrap by `slice`.

When generating `slice-planning.md`, start from `assets/slice-planning-template.md` and replace placeholders rather than inventing a new structure each time.
When generating `slice-traceability.md`, start from `assets/slice-traceability-template.md` and replace placeholders rather than inventing a new table shape each time.

## Guardrails

- Do not create execution slices directly from vague stories.
- Do not mirror external execution states inside feature planning docs.
- Do not turn increments into execution states or spec-slice containers.
- Do not turn `slice-planning.md` into a slice-scoped execution checklist; that belongs to `guide-execution` and `blueprint` later.
- Do not mark work as parallel-safe unless overlap and integration risk are genuinely low.
- If a slice still needs major replanning, split it again before handoff.
