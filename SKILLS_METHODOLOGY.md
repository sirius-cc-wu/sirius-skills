# Skills Methodology

This document explains **how to use the skills together**.

`README.md` already covers the repository direction, the planning-layer skill names, and the generic-first boundary. This file is the operational guide: what to do first, what each phase should produce, and when to hand off to the next skill.


## Core Idea

Use a **two-layer workflow**:

1. **Planning layer**
   - `guide-scope` (optional scope-aware entrypoint)
   - `guide-planning`
    - `propose`
    - `add-subfeature`
    - `migrate-subfeatures` (for legacy change packets)
    - `migrate-planning-model` (for simplified feature/subfeature layout repair)
    - `migrate-slices` (for co-locating execution slices)
   - `research` (when upstream comparison materially affects planning shape)
   - `discover`
   - `design`
   - `ui-flow` (optional)
   - `breakdown`
   - `review-planning`
2. **Execution layer**
   - `slice`
   - `guide-execution`
   - `ship` (optional backlog orchestrator)
   - `ship-worktree` (optional dedicated-worktree wrapper around `ship`)
   - `brief` (legacy/optional clarification)
   - `blueprint`
   - `review-execution`
   - `close-slice`

The planning layer keeps scope, design, decomposition, increment planning, and
optional durable reference comparison in repo documents, and `guide-planning`
owns readiness and routing across those artifacts.

`migrate-slices` is the migration helper for execution artifacts that still live
in a root-level `slices/` tree.

When planning work consolidates, narrows, or supersedes older workflow
surface, keep the user-facing route singular: `guide-scope` stays the optional
scope resolver, `guide-planning` stays the canonical planning entrypoint, and
older surfaces should be described as historical or migration-only unless a
planning packet explicitly documents a temporary parallel transition.

After each planning phase writes or updates its repository artifacts, persist the matching metadata transition with the owner script for that planning scope. Canonical features should use `sirius manage-planning sync-status <feature-selector> --through <expected-status>`. Subfeatures should use `sirius manage-subfeatures set-status <feature-selector> <subfeature-id> <expected-status>` through `reviewed`, then `sirius manage-subfeatures approve ...` to record explicit approval and any ready slice IDs. Use adjacent advancement by default and reserve explicit overrides for deliberate repair or terminal execution states.

The execution layer works one implementation-ready slice at a time, starting with `slice` bootstrap from approved committed planning artifacts. For reviewed subfeatures, that approval must be recorded in `.subfeature-meta.json` before bootstrap, and new execution slices are created under the owning subfeature's local `slices/` root. `ship` can sit above that flow when an approved and committed subfeature should be worked as one dependency-aware backlog; direct feature targets remain compatibility for existing packets. It should follow increment order first, then slice dependencies within the current increment, while still handing each concrete slice to the next existing single-slice owner such as `blueprint`, optional legacy `brief`, repository implementation, `review-execution`, `close-slice`, or `commit`. When the same backlog should execute on its own git branch and checkout, `ship-worktree` can sit one layer above `ship` to create or reuse a dedicated worktree, run `ship` there, and later hand the branch off to PR creation. For faster manual local work, use the shared `sirius worktree get` / `return` / `status` pool rooted at the owning repo's sibling `<repo>.worktrees` directory.

When accelerators are enabled, the default operator path compresses to one
planning accelerator surface and one execution accelerator surface, with an
explicit approval-and-commit checkpoint between them:

1. `autoplan --execute-owner-chain` drives planning to review-ready state.
2. After human approval, `autoplan --approve` records approval and hands the
   packet back to `commit` until the approved planning artifacts are committed.
3. Once that checkpoint is clear, `ship --resume` drives execution until the
   next manual boundary.
4. When the target should execute on its own branch and checkout,
   `ship-worktree --resume` can wrap that same execution path inside a
   dedicated worktree and later hand the branch off to PR creation.
5. For ad hoc manual work, use `sirius worktree get` to lease a reusable
   checkout in the owning repo's sibling `<repo>.worktrees`, `sirius worktree
   status` to inspect the shared pool, and `sirius worktree return <path>` to
   hand it back.

`guide-scope`, `guide-planning`, and `guide-execution` remain the canonical
manual fallback surfaces for ambiguous scope, recovery, and fine-grained
intervention.

## Manual Workflow

Use this path when the accelerator flow is unavailable, intentionally disabled,
or needs explicit operator intervention.

### 0. Resolve scope with guide-scope when needed

Use `guide-scope` as the optional entrypoint when the repository may contain
multiple explicit scopes and the user should not have to remember whether the
next handoff belongs to planning, execution, or bootstrap.

Its job is to:

- resolve the active scope from the current working directory
- stop for explicit selection when multiple scopes are plausible
- route to `guide-planning`, `guide-execution`, or `bootstrap`
- keep downstream ownership boundaries intact instead of duplicating their state

Recommended handoff:

```text
guide-scope -> guide-planning/guide-execution/bootstrap
```

If the repository effectively has one scope, `guide-scope` remains optional and
you can still enter directly through `guide-planning` or `guide-execution`.

### 1. Route planning with guide-planning

Use `guide-planning` as the manual planning-layer entrypoint when you need to
decide what should happen next for a feature.

Its job is to:

- resolve or initialize the feature planning folder
- verify the current planning artifacts and metadata
- decide whether the next step is `propose`, `add-subfeature`, `research`, `discover`, `design`, `ui-flow`, `breakdown`, `review-planning`, or an approval/commit stop before execution begins
- keep planning handoff decisions durable through explicit readiness states
- keep the canonical planning surface explicit when reviewed work narrows or supersedes older workflow paths

Expected planning states:

- `discovery_pending`
- `discovery_ready`
- `design_ready`
- `breakdown_ready`
- `planning_reviewed`
- `slice_ready`
- `implemented`

Recommended handoff:

```text
guide-scope -> guide-planning -> propose/add-subfeature/research/discover/design/ui-flow/breakdown/review-planning -> human approval -> commit -> slice/ship -> guide-execution
```

When the repository prefers one feature or subfeature per worktree branch,
substitute `ship-worktree` for direct `ship` entry after the planning commit
checkpoint.

Accelerator fast path:

```text
autoplan --execute-owner-chain -> human approval -> autoplan --approve -> commit -> ship --resume
```

If the request is still speculative, cross-cutting, or not yet accepted as a canonical feature, route to `propose` first. That keeps early exploration under `docs/proposals/` instead of polluting the canonical `docs/features/` registry too early.

If the request is changing an existing canonical feature instead of starting net-new planning work, route to `add-subfeature` first. That skill creates a feature-local subfeature and keeps the canonical feature folder as the durable source of truth.

Treat bug reports, regressions, and missing-runtime-path issues on an already
implemented or archived feature as the same kind of follow-on work: verify the
current seam, then open or continue a subfeature instead of mutating the parent
packet in place or jumping to archive flow.

When the user provides a concrete failure message, failing command, or missing
runtime path, check the live implementation before deciding the request is only
planning drift. If the user wording is ambiguous between "plan this" and "fix
this now", ask one clarifying question instead of assuming planning-only work.

For cross-agent transient routing state, prefer structured files under
`.skills/runtime/` over agent-local markdown scratch plans. Keep durable truth
in feature/subfeature artifacts, but use runtime files such as checkpoints,
event logs, and `request-handoff.json` when another agent or later run needs to
pick up the latest request-level route decision.

After a subfeature exists, author the real subfeature-local `discover.md` before design. Bootstrap `draft.md` is rough input only and should disappear once discovery is complete.

Use `research` only when upstream comparison can materially change the planning
shape: explicit user requests for reference-project research or wiki synthesis,
missing durable research for a feature or subfeature that overlaps checked-in
`references/` patterns, or discovery/design work that depends on choosing
between multiple upstream patterns. Skip `research` for small repo-local edits
whose shape does not depend on external comparison.

### 0b. Capture reference-project comparison only when it matters

Use `research` after `guide-planning` or `discover` when durable upstream
comparison is needed before discovery or design should continue.

Its job is to:

- compare relevant checked-in references against the local planning target
- write `reference-research.md` into the feature or subfeature packet
- record the chosen borrowing path and lower-priority alternatives durably
- note whether reusable wiki synthesis was written, skipped, or deferred

Expected outputs:

- `reference-research.md`

Recommended handoff:

```text
guide-planning -> research -> discover/design
guide-planning -> add-subfeature -> discover -> research -> design/breakdown
```

Skip `research` when the work is repo-local and does not depend on external
comparison, or when an existing `reference-research.md` already covers the same
decision scope without a material change.

When `reference-research.md` exists, later planning phases should reuse it as
the durable source for borrowing-path decisions instead of re-deriving the same
comparison from memory or transient chat context.

### 0a. Capture speculative ideas with propose

Use `propose` when the request is still exploratory and should not become a real feature planning folder yet.

Its job is to:

- create and maintain proposal-scoped docs under `docs/proposals/<proposal-slug>/`
- track proposal lifecycle state separately from canonical feature planning
- keep speculative capability ideas out of the feature registry until accepted
- stop at accepted proposal state and hand accepted proposals back to `guide-planning` for canonical promotion

Expected outputs:

- `proposal.md`
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

In the simplified planning model, canonical features own the stable story
catalog and subfeatures reference those parent story IDs. Do not create a
subfeature-local `user-stories.md` for new work.

Expected outputs:

- `discover.md`
- feature-level `user-stories.md` when stable story IDs are needed

If `reference-research.md` exists, use it to inform discovery framing,
constraints, and upstream-influenced goals. If it does not exist, discovery can
still proceed normally when research was never required.

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

If `reference-research.md` exists and affects the approach, carry the chosen
borrowing path and tradeoffs into `system-design.md` instead of silently
re-deriving them.

Diagram layout is configurable through `.skills/planning.json`:

- `design_diagram_mode: "embedded"` keeps fenced `plantuml` blocks in `system-design.md`
- `design_diagram_mode: "linked_svg"` writes `.puml` and `.svg` files under `<feature_path>/figures/` and links the SVGs from `system-design.md`; keep those diagrams on an explicit white background with `skinparam backgroundColor white` and a white SVG canvas rect

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
- create execution-ready planned slices
- group slices into small demonstrable increments
- map stories to planned slices

Expected outputs:

- `slice-planning.md`
- `slice-traceability.md`

In this workflow, an increment is a small, demonstrable system outcome made from one or more execution-ready slices. A slice maps to one executable slice; an increment groups related slices so the team can target the smallest useful demo or handoff. As a rule of thumb, Increment 1 should be the simplest end-to-end usable path.

Use the built-in helper when starting a new planning folder:

```bash
sirius scaffold-breakdown <feature-slug>
```

The helper uses `.skills/planning.json` field `planning_dir` when present and
otherwise defaults to `docs/features`.

For an existing subfeature, scaffold directly into the selected delivery-unit
path instead:

```bash
sirius scaffold-breakdown \
  docs/features/<feature-slug>/subfeatures/<change-id>
```

When the target is a real subfeature, the scaffold seeds subfeature context from
`.subfeature-meta.json` so the breakdown artifacts stay tied to the affected
canonical stories, slices, and baseline docs.
Those breakdown artifacts remain subfeature-local; they are not default
finalization targets for the canonical feature's `slice-planning.md` or
`slice-traceability.md`. New executable planning should prefer this subfeature
path; direct feature-level breakdown remains a compatibility path for existing
packets.

Review checkpoint:

- review the slices and increments for scope, sequencing, ownership, and demonstrability before asking for approval and bootstrapping execution
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
- for subfeatures, keep superseded canonical slice IDs in notes or dependency
  fields instead of reusing them as new subfeature-local slice IDs

Review checkpoint:

- confirm each planned slice has clear scope, dependencies, and expected verification before bootstrapping
- add any role-specific review expectations that matter for execution, such as architecture, security, or platform input, in the planning docs

### 5. Review planning outputs

Use `review-planning` after the discovery, design, and breakdown artifacts are concrete enough to support execution handoff, typically when `guide-planning` routes the feature into readiness review.

Its job is to:

- review the planning artifacts and slice definitions together rather than in isolation
- identify blocking scope, design, sequencing, or validation gaps before slice bootstrap
- record durable findings in the planning docs already used by the team
- confirm whether the work is ready for human approval and later `slice` bootstrap or needs another planning pass

When `reference-research.md` exists, review-planning should check that the
relevant borrowing-path decisions still line up with `discover.md`,
`system-design.md`, and `slice-planning.md`.

It can review either canonical feature planning or a selected feature subfeature.
For subfeatures, the review should center on the subfeature-local `discover.md`,
`system-design.md`, `slice-planning.md`, and `slice-traceability.md`, while using
the canonical feature docs only as baseline context for the delta.

When the review target is a subfeature, write findings back into the
subfeature-local docs and confirm the planned slices represent only the new or
amended work required by that change.

Recommended handoff:

```text
guide-planning -> propose/discover -> design -> breakdown -> review-planning -> human approval -> commit -> slice
```

### 6. Bootstrap one execution slice per approved planned slice

Once a planned slice is implementation-ready, has passed `review-planning`, and its approved planning artifacts are committed, use `slice`.

Preferred handoff:

```text
guide-planning -> breakdown -> review-planning -> human approval -> commit -> slice/ship -> guide-execution
```

`slice` should bootstrap a slice-scoped execution slice from the execution-ready work item, typically with:

```bash
sirius bootstrap-slice "<slice-id>" "<slice-name>"
```

If the active execution scope has no registry-owning `slice_dir` and the default `slices/` location is not the right fit, bootstrap the first slice with an explicit directory:

```bash
sirius bootstrap-slice --slice-dir "team-slices" "<slice-id>" "<slice-name>"
```

Do not jump directly from `review-planning` to `slice`; stop for explicit human approval and commit the planning artifacts first. For subfeatures, record that approval through `manage_subfeatures.py approve ...` before slice bootstrap so the derived planning view can become `slice_ready`.

When a reviewed and committed feature or subfeature has multiple planned slices
and the goal is to keep progressing through the backlog, `ship`
can resolve the remaining planned slices, resume an active mapped slice, or
bootstrap the next ready one. It stays orchestration-only: `guide-execution`,
`blueprint`, optional legacy `brief`, `review-execution`, `close-slice`, and `commit` still own
their existing steps.

When `.skills/execution.json` enables delegated owner-chain execution,
re-running `ship --resume` becomes the normal execution autopilot loop: `ship`
handles backlog readiness and preflight, then `ship-slice` owns downstream
review, formatting, close, and commit boundaries according to its configured
continuation policy.

### 7. Execute with guide-execution

After a slice exists, use the manual execution layer:

1. `guide-execution`
2. `blueprint`
3. optional legacy `brief` only when standalone clarification is needed

This is where slice-scoped execution artifacts are created:

- `blueprint.md`
- optional legacy `brief.md`

Within that execution layer:

- `guide-execution` owns routing, readiness checks, and registry state
- `ship` owns backlog traversal across multiple planned slices for one reviewed and committed feature or subfeature
- `blueprint` creates the slice-scoped contract and final implementation packets, technical decisions, traceability, validation steps, and PlantUML detailed design needed for execution
- `brief` remains available only for legacy slices or explicit standalone clarification before blueprint authoring
- when `.skills/execution.json` sets `auto_start_implementation` to `true`, marking the blueprint ready should immediately advance the slice into `execution_ready` and continue into repository implementation work
- `review-execution` owns the explicit implementation-versus-blueprint review outcome
- `close-slice` owns slice closure metadata
Keep the boundary explicit:

- `breakdown` owns repo-story decomposition and execution-ready slices
- `breakdown` also owns increment grouping at the repo-planning level
- `blueprint` owns the slice contract, requirement mapping, validation gates, and final slice-scoped execution checklist for new slices
- `brief_ready`, `brief.md`, and `checklists/requirements.md` are legacy-only unless a slice explicitly needs standalone clarification
- `guide-execution` should validate handoffs and route work, not take over artifact authoring from the other execution skills
- `ship` should stop at blockers or per-slice commit checkpoints instead of silently rolling work into the next slice

Execution review loop:

- review the slice-scoped `blueprint.md` before implementation starts if the slice carries meaningful risk or ambiguity
- review blueprint-to-implementation alignment during execution, not only at final handoff
- when validation or review finds a gap, update the slice-scoped execution artifacts or surrounding guidance so the fix persists at the blueprint level

### 8. Manage slice execution

Use the repository and `guide-execution` for the actual slice lifecycle:

- track slice readiness and state transitions
- record blockers or pauses in slice metadata
- request or record implementation review as required by your team
- capture review findings that affect execution or acceptance in `blueprint.md`, or in legacy `brief.md` when that artifact exists
- verify the implementation against the slice-scoped artifacts
- mark work complete using `close-slice`

If review uncovers an intent gap or blueprint gap, feed that back into the relevant blueprint or planning artifact before considering the slice fully done.

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

There is no dedicated subfeature-finalization skill. Once all slices listed in a
reviewed subfeature are closed, keep the durable subfeature folder and the
closed slices in place by default. If later cleanup or archival is needed, use
explicit maintenance tooling rather than bundling deletion into slice closure.

## Recommended Repository Layout

### Feature-local planning

```text
<planning_dir>/<feature-slug>/
  discover.md
  user-stories.md
  .planning-meta.json
  subfeatures/
    README.md
    registry.json
```

Keep discovery and stable story context in a feature-local planning folder so
the product context stays together. Every feature should have a `subfeatures/`
registry. The parent feature folder is still a repository document area; it is
not a slice-execution slice. By default, `planning_dir` is `docs/features`;
projects can override it in `.skills/planning.json`.

### Subfeature delivery planning

```text
<planning_dir>/<feature-slug>/subfeatures/<subfeature-id>/
  discover.md
  .subfeature-meta.json
  system-design.md
  ui-design.md              # optional
  slice-planning.md
  slice-traceability.md
```

Use subfeatures as the normal executable planning and delivery unit. Subfeature
metadata should carry parent feature `story_ids`; subfeatures should not create
their own `user-stories.md` catalogs.

### Proposal staging

```text
<proposal_dir>/<proposal-slug>/
  proposal.md
  user-stories.md          # optional
```

Use proposal folders for speculative or not-yet-accepted work. By default, `proposal_dir` is `docs/proposals`; projects can override that in `.skills/planning.json`.

### Slice-level execution

```text
<feature_dir>/subfeatures/<subfeature-id>/slices/<slice-id>-<slice-slug>/
  blueprint.md
  brief.md                 # optional legacy/clarification artifact
```

For new subfeature work, execution slices live under the owning subfeature's
local `slices/` root. Root-level or feature-level slice roots are compatibility
or migration-only locations. The important rule is that execution slices are
**slice-scoped** and stay tied to the subfeature delivery unit that owns the
planned slice backlog.

Direct feature or legacy work can still use a configured `slice_dir` in
`.skills/execution.json`. A root execution config without `slice_dir` is
defaults-only and does not own or implicitly recreate a root-level `slices/`
registry.

## Diagram Conventions

- Use **PlantUML** as the standard UML language in both layers.
- In the planning layer, keep UML diagrams feature-scoped and embed them in `system-design.md` unless a separate adjacent `.puml` file is clearly easier to maintain.
- In the execution layer, keep UML diagrams slice-scoped and place detailed design diagrams in `blueprint.md`.
- Require at least one diagram in both layers, and choose the simplest diagram set that answers the key question for the current phase without diagramming everything.

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
        user-stories.md
        subfeatures/
          registry.json
          habit-storage/
            discover.md
            system-design.md
            slice-planning.md
            slice-traceability.md
            slices/
              HAB-101-create-schema/
                blueprint.md
          habit-interactions/
            discover.md
            system-design.md
            slice-planning.md
            slice-traceability.md
            slices/
              HAB-102-add-habit-form/
                blueprint.md
              HAB-103-mark-habit-done/
                blueprint.md
```

In this example, the default planning layout `docs/features/habit-tracker/` holds the feature-level discovery and story catalog, subfeatures hold executable planning, and each executable slice lives under the owning subfeature's local `slices/` root.

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
