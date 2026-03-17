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
   - `tasks`
   - `sb-tracker`

The planning layer keeps scope, design, and decomposition in repo documents.

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
- map stories to tracker work

Expected outputs:

- `task-planning.md`
- `task-traceability.md`

Use the built-in helper when starting a new planning folder:

```bash
python3 skills/breakdown/scripts/scaffold_breakdown.py <project-slug>
```

### 4. Create tracker tasks

Use `breakdown` with `sb-tracker` to create the executable work items.

Recommended rule:

- one execution-ready slice = one `sb` task

Recommended tracker usage:

- use `sb add` for executable tasks
- use `sb dep` for real execution blockers
- keep repo story IDs in `task-traceability.md`
- keep `sb` task IDs as execution identifiers

### 5. Bootstrap one execution track per task

Once an `sb` task is implementation-ready, use `track`.

Preferred handoff:

```text
breakdown -> sb-tracker -> track -> spec-driver
```

`track` should bootstrap a task-scoped spec track from the `sb` task, typically with:

```bash
python3 skills/spec-driver/scripts/manage_specs.py add-from-sb <id>
```

### 6. Execute with spec-driver

After a track exists, use the execution layer:

1. `spec-driver`
2. `specify`
3. `plan`
4. `tasks` (when helpful)

This is where task-scoped execution artifacts are created:

- `spec.md`
- `plan.md`
- `tasks.md`

### 7. Track execution in sb-tracker

Use `sb-tracker` for actual task lifecycle:

- `sb begin`
- `sb verify`
- `sb finish`
- `sb pause`

Keep the responsibility boundary clear:

- `spec-driver` owns **track readiness**
- `sb-tracker` owns **execution state**

## Recommended Repository Layout

### Project-level planning

```text
doc/specs/projects/<project-slug>/
  discover.md
  system-design.md
  ui-design.md              # optional
  user-stories.md
  task-planning.md
  task-traceability.md
```

### Task-level execution

```text
<spec_dir>/<task-id>-<task-slug>/
  spec.md
  plan.md
  tasks.md
```

The exact execution-track path depends on `spec-driver` configuration. The important rule is that execution tracks are **task-scoped**, not project-scoped.

## Operating Rules

- Keep stories and design in repo docs.
- Keep executable work in `sb-tracker`.
- Do not use `spec-driver` for project-level discovery or decomposition.
- Do not use `sb` lifecycle states as spec-track states.
- Split work before bootstrapping a track, not after.
- Preserve story-to-task traceability from planning through execution.

## When to Use This Methodology

Use this methodology when:

- the work is larger than a one-off coding task
- design or decomposition matters
- multiple implementation tasks will come out of one project or feature
- you want resumable execution with `sb-tracker`

For small one-shot changes, you may skip most of the planning layer and go directly to `spec-driver` or straight implementation if no spec workflow is needed.
