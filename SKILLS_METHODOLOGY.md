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
   - `track`
2. **Execution layer**
   - `spec-driver`
   - `specify`
   - `plan`
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

### 2. Design the solution

Use `design` to define:

- architecture
- interfaces
- data flow
- risks
- validation approach

Expected output:

- `system-design.md`

If the work has meaningful UI or interaction design, also use `ui-flow` to create:

- `ui-design.md`

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

### 5. Bootstrap one execution track per task

Once a tracker task is implementation-ready, use `track`.

Preferred handoff:

```text
breakdown -> execution tracker -> track -> spec-driver
```

`track` should bootstrap a task-scoped spec track from the execution-ready work item, typically with:

```bash
python3 skills/spec-driver/scripts/manage_specs.py add "<task-id>" "<task-name>"
```

### 6. Execute with spec-driver

After a track exists, use the execution layer:

1. `spec-driver`
2. `specify`
3. `plan`

This is where task-scoped execution artifacts are created:

- `spec.md`
- `plan.md`

Within that execution layer:

- `specify` creates the task-scoped `spec.md` for one execution-ready work item, including acceptance and requirement context
- `plan` converts that task-scoped spec into the final implementation packets, traceability, and validation steps needed for execution

Keep the boundary explicit:

- `breakdown` owns repo-story decomposition and tracker-ready slices
- `breakdown` also owns increment grouping at the repo-planning level
- `plan` owns the final task-scoped execution checklist for new tracks

### 7. Track execution in the execution tracker

Use your task system for the actual task lifecycle:

- start or claim work
- record blockers or pauses
- verify the implementation
- mark work complete

Keep the responsibility boundary clear:

- `spec-driver` owns **track readiness**
- the execution tracker owns **execution state**

### 8. Close the spec track

After implementation is complete and the execution task is finished, use `close-track` to close the spec track cleanly.

Its job is to:

- validate that the track is ready to close
- record durable closure metadata without moving or deleting the original artifacts
- optionally publish a project-local summary entry such as `docs/spec-history.md` or `CHANGELOG.md`

Recommended handoff:

```text
task complete -> close-track
```

Important closure rules:

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
  specs/
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

In this example, `docs/features/habit-tracker/` holds the feature-level planning artifacts, while each executable task gets its own centralized execution track under `specs/`.

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
