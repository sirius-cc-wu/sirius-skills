# Skills Methodology

This document explains **how to use the skills together**.

`README.md` already covers the repository direction, the planning-layer skill names, and the generic-first boundary. This file is the operational guide: what to do first, what each phase should produce, and when to hand off to the next skill.

## Core Idea

Use a **two-layer workflow**:

1. **Planning layer**
   - `discover`
   - `design`
   - `ui-flow` (optional)
   - `breakdown`
   - `review-planning`
   - `track`
2. **Execution layer**
   - `spec-driver`
   - `define`
   - `plan`
   - `review-execution`
   - `close-track`
   - your execution tracker

The planning layer keeps scope, design, decomposition, and increment planning in repo documents.

The execution layer works one implementation-ready task at a time.

## Recommended Workflow

### 1. Discover the work

Use `discover` to define:

- the problem
- the desired outcomes
- the constraints
- the first set of user stories or capabilities

Expected outputs:

- `discover.md`
- optional early `user-stories.md`

Review checkpoint:

- confirm the business intent, scope, constraints, and success criteria with the relevant stakeholders before moving into design
- update the discovery artifacts with that feedback so the next phase starts from reviewed intent rather than side-channel notes

### 2. Design the solution

Use `design` to define:

- architecture
- interfaces
- data flow
- risks
- validation approach
- PlantUML system-design diagrams

Expected output:

- `system-design.md`

If the work has meaningful UI or interaction design, also use `ui-flow` to create:

- `ui-design.md`

Review checkpoint:

- review the proposed architecture, interfaces, repository boundaries, and major risks before starting breakdown
- fold design feedback back into `system-design.md` and `ui-design.md` so decomposition starts from an approved technical direction

### 3. Break stories into executable work

Use `breakdown` after discovery and design are concrete enough.

Its job is to:

- validate story scope and size
- split oversized work
- create execution-ready slices
- group slices into small demonstrable increments
- map stories to tracker work

Expected outputs:

- `task-planning.md`
- `task-traceability.md`

In this workflow, an increment is a small, demonstrable system outcome made from one or more execution-ready slices. A slice maps to one executable task; an increment groups related tasks so the team can target the smallest useful demo or handoff. As a rule of thumb, Increment 1 should be the simplest end-to-end usable path.

Use the built-in helper when starting a new planning folder:

```bash
python3 skills/breakdown/scripts/scaffold_breakdown.py <project-slug>
```

Review checkpoint:

- review the slices and increments for scope, sequencing, ownership, and demonstrability before creating tracker tasks
- make sure the planned validation approach is clear enough that each slice can be checked independently during execution

### 4. Create tracker tasks

Use `breakdown` with your task system to create the executable work items.

Use `task-planning.md` to record the increment structure before bootstrapping tracks. For each increment, capture:

- the increment goal or user-visible value
- the included story IDs and planned tracker task IDs
- the expected demo or verification outcome
- any sequencing constraints between tasks or increments

Recommended rule:

- one execution-ready slice = one tracker task
- one increment = one or more related tracker tasks

Recommended tracker usage:

- create one task per execution-ready slice
- record real execution blockers as tracker dependencies
- keep repo story IDs in `task-traceability.md`
- keep tracker task IDs as execution identifiers

Review checkpoint:

- confirm each tracker task has clear scope, dependencies, and expected verification before bootstrapping a track
- add any role-specific review expectations that matter for execution, such as architecture, security, or platform input, in the tracker task or linked planning docs

### 5. Review planning outputs

Use `review-planning` after the discovery, design, and breakdown artifacts are concrete enough to support execution handoff.

Its job is to:

- review the planning artifacts and task definitions together rather than in isolation
- identify blocking scope, design, sequencing, or validation gaps before track bootstrap
- record durable findings in the planning docs or tracker context already used by the team
- confirm whether the work is ready for `track` or needs another planning pass

Recommended handoff:

```text
discover -> design -> breakdown -> execution tracker -> review-planning -> track
```

### 6. Bootstrap one execution track per task

Once a tracker task is implementation-ready, use `track`.

Preferred handoff:

```text
breakdown -> execution tracker -> review-planning -> track -> spec-driver
```

`track` should bootstrap a task-scoped spec track from the execution-ready work item, typically with:

```bash
python3 skills/spec-driver/scripts/manage_specs.py add "<task-id>" "<task-name>"
```

### 7. Execute with spec-driver

After a track exists, use the execution layer:

1. `spec-driver`
2. `define`
3. `plan`

This is where task-scoped execution artifacts are created:

- `spec.md`
- `plan.md`

Within that execution layer:

- `define` creates the task-scoped `spec.md` for one execution-ready work item, including acceptance and requirement context
- `plan` converts that task-scoped spec into the final implementation packets, traceability, validation steps, and PlantUML detailed design needed for execution

Keep the boundary explicit:

- `breakdown` owns repo-story decomposition and tracker-ready slices
- `breakdown` also owns increment grouping at the repo-planning level
- `plan` owns the final task-scoped execution checklist for new tracks

Execution review loop:

- review the task-scoped `spec.md` and `plan.md` before implementation starts if the task carries meaningful risk or ambiguity
- review spec-to-implementation alignment during execution, not only at final handoff
- when validation or review finds a gap, update the task-scoped execution artifacts or surrounding guidance so the fix persists at the spec level

### 8. Track execution in the execution tracker

Use your task system for the actual task lifecycle:

- start or claim work
- record blockers or pauses
- request or record implementation review as required by your team
- capture review findings that affect execution or acceptance
- verify the implementation
- mark work complete

If review uncovers an intent gap or spec gap, feed that back into the relevant spec or planning artifact before considering the task fully done.

Keep the responsibility boundary clear:

- `spec-driver` owns **track readiness**
- the execution tracker owns **execution state**

### 9. Review execution outcomes

Use `review-execution` after implementation and validation, and before closing the track.

Its job is to:

- compare the implementation and validation evidence with the task-scoped `spec.md` and `plan.md`
- classify whether a finding is an intent-to-spec gap, a spec-to-implementation gap, or a follow-up outside the active track
- feed durable fixes back into `spec.md`, `plan.md`, or upstream planning guidance when the issue reflects missing context
- confirm whether the work is actually ready for `close-track`

Recommended handoff:

```text
implementation complete -> review-execution -> close-track
```

### 10. Close the spec track

After implementation is complete and the execution task is finished, use `close-track` to close the spec track cleanly.

Its job is to:

- validate that the track is ready to close
- record durable closure metadata without moving or deleting the original artifacts
- optionally publish a project-local summary entry such as `docs/spec-history.md` or `CHANGELOG.md`
- capture durable feedback that should improve future specs, prompts, or validation harnesses

Recommended handoff:

```text
review-execution complete -> close-track
```

Important closure rules:

- closing a track should happen after required review, validation, and spec feedback loops are complete
- closing a track does not merge or delete the original `spec.md` or `plan.md`; older tracks may also retain `tasks.md`
- publishing is optional and project-local
- closure metadata belongs in the spec system, not in the execution tracker

## Recommended Repository Layout

### Feature-local planning

```text
docs/features/<project-slug>/
  discover.md
  system-design.md
  ui-design.md              # optional
  user-stories.md
  task-planning.md
  task-traceability.md
```

Keep discovery, design, and breakdown artifacts in a feature-local planning folder so the project context stays together. The planning folder is still a repository document area; it is not a task-execution track.

### Task-level execution

```text
<spec_dir>/<task-id>-<task-slug>/
  spec.md
  plan.md
```

The exact execution-track path depends on `spec-driver` configuration. The important rule is that execution tracks are **task-scoped**, not feature-scoped, and remain centrally managed separately from the feature-local planning docs.

## Diagram Conventions

- Use **PlantUML** as the standard UML language in both layers.
- In the planning layer, keep UML diagrams feature-scoped and embed them in `system-design.md` unless a separate adjacent `.puml` file is clearly easier to maintain.
- In the execution layer, keep UML diagrams task-scoped and place detailed design diagrams in `plan.md`.
- Prefer diagrams that answer a concrete question for the current phase rather than diagramming everything by default.

### Example layout

For a small feature such as a habit tracker, the resulting repository shape could look like:

```text
my-app/
  src/
  tests/
  docs/
    features/
      habit-tracker/
        discover.md
        system-design.md
        ui-design.md
        user-stories.md
        task-planning.md
        task-traceability.md
  tracks/
    HAB-101-create-schema/
      spec.md
      plan.md
    HAB-102-add-habit-form/
      spec.md
      plan.md
    HAB-103-mark-habit-done/
      spec.md
      plan.md
```

In this example, `docs/features/habit-tracker/` holds the feature-level planning artifacts, while each executable task gets its own centralized execution track under `tracks/`.

## Operating Rules

- Keep stories and design in repo docs.
- Keep increment plans in repo docs.
- Keep executable work in your task system.
- Do not use `spec-driver` for feature-level discovery or decomposition.
- Do not use spec tracks as increment containers; keep tracks task-scoped.
- Do not use execution lifecycle states as spec-track states.
- Split work before bootstrapping a track, not after.
- Preserve story-to-task traceability from planning through execution.

## When to Use This Methodology

Use this methodology when:

- the work is larger than a one-off coding task
- design or decomposition matters
- multiple implementation tasks will come out of one project or feature
- you want resumable execution with a separate task system

For small one-shot changes, you may skip most of the planning layer and go directly to `spec-driver` or straight implementation if no spec workflow is needed.
