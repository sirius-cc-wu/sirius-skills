# Skills Methodology

This document explains **how to use the skills together**.

`README.md` already covers the repository direction, the planning-layer skill names, and the generic-first boundary. This file is the operational guide: what to do first, what each phase should produce, and when to hand off to the next skill.


## Core Idea

Use a **two-layer workflow**:

1. **Planning layer**
   - `guide-planning`
   - `propose`
   - `evolve-feature`
   - `assess`
   - `reconcile-feature`
   - `discover`
   - `design`
   - `ui-flow` (optional)
   - `breakdown`
   - `review-planning`
   - `slice`
2. **Execution layer**
   - `guide-execution`
   - `brief`
   - `blueprint`
   - `review-execution`
   - `close-slice`

The planning layer keeps scope, design, decomposition, and increment planning in repo documents, and `guide-planning` owns readiness and routing across those artifacts.

The execution layer works one implementation-ready slice at a time.

## Recommended Workflow

### 0. Route planning with guide-planning

Use `guide-planning` as the planning-layer entrypoint when you need to decide what should happen next for a feature.

Its job is to:

- resolve or initialize the feature planning folder
- verify the current planning artifacts and metadata
- decide whether the next step is `propose`, `evolve-feature`, `assess`, `reconcile-feature`, `discover`, `design`, `ui-flow`, `breakdown`, `review-planning`, or `slice`
- keep planning handoff decisions durable through explicit readiness states

Expected planning states:

- `discovery_pending`
- `discovery_ready`
- `design_ready`
- `breakdown_ready`
- `planning_reviewed`
- `slice_ready`

Recommended handoff:

```text
guide-planning -> propose/evolve-feature/assess/reconcile-feature/discover/design/ui-flow/breakdown/review-planning/slice
```

If the request is still speculative, cross-cutting, or not yet accepted as a canonical feature, route to `propose` first. That keeps early exploration under `docs/proposals/` instead of polluting the canonical `docs/features/` registry too early.

If the request is changing an existing canonical feature instead of starting net-new planning work, route to `evolve-feature` first. That skill creates a feature-local change packet and keeps the canonical feature folder as the durable source of truth.

After a change packet exists, use `assess` before change-local design when you need an explicit record of affected baseline artifacts, stories, increments, and slices.

### 0b. Assess existing-feature impact

Use `assess` after `evolve-feature` and before change-local design or breakdown.

Its job is to:

- inspect the canonical feature baseline
- write `impact-analysis.md` inside the selected change packet
- record affected artifacts, story IDs, and slice IDs in `.feature-change-meta.json`
- make the changed scope explicit before design starts

Recommended handoff:

```text
guide-planning -> evolve-feature -> assess -> design -> breakdown
```

### 0c. Reconcile approved feature changes

Use `reconcile-feature` after a reviewed feature change packet has been executed
and the approved delta needs to be folded back into the canonical feature docs.

Its job is to:

- update canonical feature docs with stable reconciliation blocks and backlinks
- write `reconciliation.md` inside the retained change packet
- keep change-local breakdown artifacts in the packet as the durable execution-planning record for that change
- optionally publish feature-local change history after planned slices are complete
- close the change packet through the existing feature-change lifecycle

Recommended handoff:

```text
review-planning -> slice -> guide-execution -> brief -> blueprint -> review-execution -> close-slice -> reconcile-feature
```

### 0a. Capture speculative ideas with propose

Use `propose` when the request is still exploratory and should not become a real feature planning folder yet.

Its job is to:

- create and maintain proposal-scoped docs under `docs/proposals/<proposal-slug>/`
- track proposal lifecycle state separately from canonical feature planning
- keep speculative capability ideas out of the feature registry until accepted
- stop at accepted proposal state and hand accepted proposals back to `guide-planning` for canonical promotion

Expected outputs:

- `discover.md`
- optional `user-stories.md`
- `.proposal-meta.json`

Recommended handoff:

```text
guide-planning -> propose -> guide-planning -> discover/design/breakdown
```

When a proposal is accepted and the user wants planning to continue, `guide-planning` should promote it into a canonical feature planning folder before continuing with the normal feature workflow.

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

Diagram layout is configurable through `.skills/planning.json`:

- `design_diagram_mode: "embedded"` keeps fenced `plantuml` blocks in `system-design.md`
- `design_diagram_mode: "linked_svg"` writes `.puml` and `.svg` files under `<feature_path>/figures/` and links the SVGs from `system-design.md`

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
- map stories to planned slices

Expected outputs:

- `slice-planning.md`
- `slice-traceability.md`

In this workflow, an increment is a small, demonstrable system outcome made from one or more execution-ready slices. A slice maps to one executable slice; an increment groups related slices so the team can target the smallest useful demo or handoff. As a rule of thumb, Increment 1 should be the simplest end-to-end usable path.

Use the built-in helper when starting a new planning folder:

```bash
python3 skills/breakdown/scripts/scaffold_breakdown.py <feature-slug>
```

The helper uses `.skills/planning.json` field `planning_dir` when present and
otherwise defaults to `docs/features`.

For an existing feature change, scaffold directly into the selected change
packet path instead:

```bash
python3 skills/breakdown/scripts/scaffold_breakdown.py \
  docs/features/<feature-slug>/changes/<change-id>
```

When the target is a real change packet, the scaffold seeds change context from
`.feature-change-meta.json` and `impact-analysis.md` so the breakdown artifacts
stay tied to the affected canonical stories, slices, and baseline docs.
Those breakdown artifacts remain change-local; they are not default reconciliation
targets for the canonical feature's `slice-planning.md` or `slice-traceability.md`.

Review checkpoint:

- review the slices and increments for scope, sequencing, ownership, and demonstrability before bootstrapping planned slices
- make sure the planned validation approach is clear enough that each slice can be checked independently during execution

### 4. Define executable slices

Use `breakdown` to define the directly executable slices.

Use `slice-planning.md` to record the increment structure before bootstrapping slices. For each increment, capture:

- the increment goal or user-visible value
- the included story IDs and planned slice IDs
- the expected demo or verification outcome
- any sequencing constraints between slices or increments

Recommended rule:

- one execution-ready slice = one repo-managed slice
- one increment = one or more related slices

Recommended slice usage:

- create one slice per execution-ready work item
- record real execution blockers as dependencies in `slice-planning.md`
- keep repo story IDs in `slice-traceability.md`
- keep slice IDs as the primary execution identifiers
- for change packets, keep superseded canonical slice IDs in notes or dependency
  fields instead of reusing them as new change-local slice IDs

Review checkpoint:

- confirm each planned slice has clear scope, dependencies, and expected verification before bootstrapping
- add any role-specific review expectations that matter for execution, such as architecture, security, or platform input, in the planning docs

### 5. Review planning outputs

Use `review-planning` after the discovery, design, and breakdown artifacts are concrete enough to support execution handoff, typically when `guide-planning` routes the feature into readiness review.

Its job is to:

- review the planning artifacts and slice definitions together rather than in isolation
- identify blocking scope, design, sequencing, or validation gaps before slice bootstrap
- record durable findings in the planning docs already used by the team
- confirm whether the work is ready for `slice` or needs another planning pass

Recommended handoff:

```text
guide-planning -> propose/discover -> design -> breakdown -> review-planning -> slice
```

### 6. Bootstrap one execution slice per planned slice

Once a planned slice is implementation-ready, use `slice`.

Preferred handoff:

```text
guide-planning -> breakdown -> review-planning -> slice -> guide-execution
```

`slice` should bootstrap a slice-scoped execution slice from the execution-ready work item, typically with:

```bash
python3 skills/slice/scripts/bootstrap_slice.py "<slice-id>" "<slice-name>"
```

If execution config has not been initialized yet and the default `slices/` location is not the right fit, bootstrap the first slice with an explicit directory:

```bash
python3 skills/slice/scripts/bootstrap_slice.py --slice-dir "team-slices" "<slice-id>" "<slice-name>"
```

### 7. Execute with guide-execution

After a slice exists, use the execution layer:

1. `guide-execution`
2. `brief`
3. `blueprint`

This is where slice-scoped execution artifacts are created:

- `brief.md`
- `blueprint.md`

Within that execution layer:

- `guide-execution` owns routing, readiness checks, and registry state
- `brief` creates the slice-scoped `brief.md` for one execution-ready work item, including acceptance and requirement context
- `blueprint` converts that slice-scoped brief into the final implementation packets, traceability, validation steps, and PlantUML detailed design needed for execution
- when `.skills/execution.json` sets `auto_start_implementation` to `true`, marking the blueprint ready should immediately advance the slice into `execution_ready` and continue into repository implementation work
- `review-execution` owns the explicit implementation-versus-brief review outcome
- `close-slice` owns slice closure metadata
- `reconcile-feature` owns feature-level archive/publish behavior after all planned slices are done

Keep the boundary explicit:

- `breakdown` owns repo-story decomposition and execution-ready slices
- `breakdown` also owns increment grouping at the repo-planning level
- `brief` owns `brief.md` and `checklists/requirements.md`
- `blueprint` owns the final slice-scoped execution checklist for new slices
- `guide-execution` should validate handoffs and route work, not take over artifact authoring from the other execution skills

Execution review loop:

- review the slice-scoped `brief.md` and `blueprint.md` before implementation starts if the slice carries meaningful risk or ambiguity
- review brief-to-implementation alignment during execution, not only at final handoff
- when validation or review finds a gap, update the slice-scoped execution artifacts or surrounding guidance so the fix persists at the brief level

### 8. Manage slice execution

Use the repository and `guide-execution` for the actual slice lifecycle:

- track slice readiness and state transitions
- record blockers or pauses in slice metadata
- request or record implementation review as required by your team
- capture review findings that affect execution or acceptance in `brief.md` or `blueprint.md`
- verify the implementation against the slice-scoped artifacts
- mark work complete using `close-slice`

If review uncovers an intent gap or brief gap, feed that back into the relevant brief or planning artifact before considering the slice fully done.

Keep the responsibility boundary clear:

- `guide-planning` owns **planning readiness**
- `guide-execution` owns **execution readiness and registry state**

### 9. Review execution outcomes

Use `review-execution` after implementation and validation, and before closing the slice.

Its job is to:

- compare the implementation and validation evidence with the slice-scoped `brief.md` and `blueprint.md`
- classify whether a finding is an intent-to-brief gap, a brief-to-implementation gap, or a follow-up outside the active slice
- feed durable fixes back into `brief.md`, `blueprint.md`, or upstream planning guidance when the issue reflects missing context
- confirm whether the work is actually ready for `close-slice`

Recommended handoff:

```text
implementation complete -> review-execution -> close-slice
```

### 10. Close the execution slice

After implementation is complete and the execution slice is finished, use `close-slice` to close the execution slice cleanly.

Its job is to:

- validate that the slice is ready to close
- record durable closure metadata without deleting the original artifacts
- capture durable feedback that should improve future briefs, prompts, or validation harnesses

Recommended handoff:

```text
review-execution complete -> close-slice
```

Important closure rules:

- closing a slice should happen after required review, validation, and brief feedback loops are complete
- closing a slice does not merge or delete the original `brief.md` or `blueprint.md`; older slices may also retain `slices.md`
- closure metadata belongs in the slice system itself

Feature-level cleanup happens later. Once all slices listed in a reviewed change packet are closed, `reconcile-feature` can archive those slices and publish retained feature history while leaving the change-local planning docs in place.

## Recommended Repository Layout

### Feature-local planning

```text
<planning_dir>/<feature-slug>/
  discover.md
  system-design.md
  ui-design.md              # optional
  user-stories.md
  slice-planning.md
  slice-traceability.md
```

Keep discovery, design, and breakdown artifacts in a feature-local planning folder so the project context stays together. The planning folder is still a repository document area; it is not a slice-execution slice. By default, `planning_dir` is `docs/features`; projects can override it in `.skills/planning.json`.

### Proposal staging

```text
<proposal_dir>/<proposal-slug>/
  discover.md
  user-stories.md          # optional
```

Use proposal folders for speculative or not-yet-accepted work. By default, `proposal_dir` is `docs/proposals`; projects can override that in `.skills/planning.json`.

### Slice-level execution

```text
<slice_dir>/<slice-id>-<slice-slug>/
  brief.md
  blueprint.md
```

The exact execution-slice path depends on `guide-execution` configuration. The important rule is that execution slices are **slice-scoped**, not feature-scoped, and remain centrally managed separately from the feature-local planning docs.

By default, `guide-execution` uses `slices/`; projects can override that by setting
`slice_dir` in `.skills/execution.json`.

## Diagram Conventions

- Use **PlantUML** as the standard UML language in both layers.
- In the planning layer, keep UML diagrams feature-scoped and embed them in `system-design.md` unless a separate adjacent `.puml` file is clearly easier to maintain.
- In the execution layer, keep UML diagrams slice-scoped and place detailed design diagrams in `blueprint.md`.
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
        slice-planning.md
        slice-traceability.md
  slices/
    HAB-101-create-schema/
      brief.md
      blueprint.md
    HAB-102-add-habit-form/
      brief.md
      blueprint.md
    HAB-103-mark-habit-done/
      brief.md
      blueprint.md
```

In this example, the default planning layout `docs/features/habit-tracker/` holds the feature-level planning artifacts, while each executable slice gets its own centralized execution slice under `slices/`.

## Operating Rules

- Keep stories and design in repo docs.
- Keep increment plans in repo docs.
- Keep executable work in the repository's slice system.
- Do not use `guide-execution` for feature-level discovery or decomposition.
- Do not use execution slices as increment containers; keep slices slice-scoped.
- Do not use execution lifecycle states as spec-slice states.
- Split work before bootstrapping a slice, not after.
- Preserve story-to-slice traceability from planning through execution.

## When to Use This Methodology

Use this methodology when:

- the work is larger than a one-off coding slice
- design or decomposition matters
- multiple implementation slices will come out of one project or feature
- you want resumable execution with a separate slice system

For small one-shot changes, you may skip most of the planning layer and go directly to `guide-execution` or straight implementation if no spec workflow is needed.
