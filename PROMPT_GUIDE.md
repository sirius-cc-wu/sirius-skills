# Prompt Guide

This guide helps developers prompt the `sirius-skills` workflow effectively.

Use it together with:

- `README.md` for repository layout and managed skill list
- `SKILLS_METHODOLOGY.md` for the full planning and execution workflow

## Core idea

Good prompts do three things clearly:

1. name the workflow stage or skill
2. identify the feature, subfeature, slice, or path
3. say what outcome you want the agent to produce

When in doubt, prefer the **shortest happy-path prompt** first:

- use `autoplan` when you want planning to continue to the next explicit boundary
- use `ship` when reviewed planning is already committed and you want to work the remaining backlog one planned slice at a time
- use `guide-scope` when the repository may have multiple scopes
- use `guide-planning` when you need manual planning-layer routing
- use `guide-execution` when you need manual execution-layer routing
- use `archive-artifacts` when you want to summarize and archive closed slices without losing durable history
- use `governance-update` when repeated drift means the real fix is a durable
  repo rule, not only a one-off artifact rewrite

## Start with the simplest useful prompt

If planning is already in progress and you want the default accelerator path:

```text
Use `autoplan` for `checkout-redesign` and continue until the next planning boundary.
```

If you are not sure which planning skill should run next and need manual routing:

```text
Use `guide-planning` to decide the next step for `checkout-redesign`.
```

If you are not sure whether the next step is planning, execution, or bootstrap:

```text
Use `guide-scope` to resolve the active scope and route this request.
```

If you already know the exact skill and target:

```text
Use `design` for `docs/features/checkout-redesign/`.
```

```text
Use `research` for `docs/features/checkout/subfeatures/replace-legacy-flow/` and record the chosen borrowing path from checked-in references.
```

## Prompt patterns that work well

### 1. New feature planning

Use this when the work should become canonical planning under `docs/features/`.

```text
Use `discover` for `checkout-redesign` and frame the problem, goals, constraints, and initial stories.
```

```text
Use `design` for `checkout-redesign` and produce `system-design.md` with architecture, interfaces, risks, and validation.
```

```text
Use `breakdown` for `docs/features/checkout-redesign/` and create execution-ready slices.
```

### 2. Prompt-first design without `discover.md`

Use this when engineers want to start directly from requirements or chat context.

```text
Use `design` for `checkout-redesign`. There is no `discover.md` yet. Use this prompt as the source of truth and write the feature design from it.
```

Add the most important context in the prompt:

- the problem to solve
- the constraints
- the affected systems
- the expected output or review goal

### 3. Reverse-engineered current-state design

Use this when implementation already exists and you want a reviewable design document.

```text
Use `design` for `docs/features/checkout-redesign/` and document the current implemented design from the code for review.
```

Useful additions:

- name the implementation area to inspect
- say whether the goal is review, onboarding, or drift detection
- ask for implementation-vs-intended-design deltas when needed

Example:

```text
Use `design` for `docs/features/checkout-redesign/` and reverse engineer the current implementation under `src/checkout/` into a reviewable `system-design.md`. Call out design drift explicitly.
```

### 4. Existing feature evolution

Use this when a canonical feature already exists and you need a durable child change.

```text
Use `add-subfeature` to create `replace-legacy-flow` under `checkout`.
```

```text
Use `assess` for subfeature `replace-legacy-flow` under `checkout`.
```

```text
Use `research` for `docs/features/checkout/subfeatures/replace-legacy-flow/` when upstream reference comparison should be captured durably before discovery or design continues.
```

```text
Use `design` for `docs/features/checkout/subfeatures/replace-legacy-flow/`.
```

### 5. Speculative work that should not be canonical yet

Use this when the idea is exploratory or still needs acceptance.

```text
Use `propose` to create a proposal for automated review handoff, but keep it out of canonical planning for now.
```

### 6. Planning review and approval boundary

Use this when discovery, design, and breakdown are complete enough for review.

```text
Use `review-planning` for `docs/features/checkout-redesign/`.
```

Remember the workflow boundary:

- `review-planning` stops at readiness review
- a human approves
- approved planning is committed
- only then should execution bootstrap begin

If accelerator mode is enabled and the planning target already exists, prefer:

```text
Use `autoplan` for `checkout-redesign` and continue until the approval boundary.
```

### 7. Execution-layer prompts

Use these only after planning is approved and committed.

For the default accelerator path, use:

```text
Use `ship` for `docs/features/checkout/subfeatures/replace-legacy-flow/` and continue until a blocker, preflight stop, or per-slice commit checkpoint stops the run.
```

```text
Use `slice` to bootstrap the next execution slice for `checkout-redesign`.
```

`slice` is the planning-to-execution bridge. When it bootstraps a slice for a
reviewed feature or subfeature, it should also sync the planning metadata to
`slice_ready` and record the bootstrapped slice ID.

Use `ship` when a reviewed and committed feature or subfeature has
multiple planned slices and the goal is to keep progressing through them without
manually reselecting the next slice after each closure or commit.

```text
Use `ship` for `docs/features/checkout/subfeatures/replace-legacy-flow/` and work the remaining planned slices one at a time.
```

```text
Use `ship` for `replace-legacy-flow` under `checkout` and resume from the current durable slice state.
```

Keep the boundary explicit:

- `ship` resolves backlog state from planning and execution artifacts
- it resumes an active mapped slice or bootstraps the next ready one
- it reports the next concrete owner for the active slice instead of forcing you to re-decide that handoff
- it stops when the backlog is blocked or when a completed slice still needs its own commit checkpoint
- it routes through the existing execution owners instead of replacing them

If you need manual execution routing for one active slice:

```text
Use `guide-execution` to decide the next step for slice `CHK-12-form-state-refactor`.
```

```text
Use `brief` for slice `CHK-12-form-state-refactor`.
```

```text
Use `blueprint` for slice `CHK-12-form-state-refactor`.
```

```text
Use `review-execution` for slice `CHK-12-form-state-refactor`.
```

```text
Use `close-slice` for slice `CHK-12-form-state-refactor`.
```

`close-slice` is non-destructive. It closes the slice and preserves its working
context. Use `archive-artifacts` later if you want to move closed slices out of
the active execution area.

### 8. Archive and summarize closed slices

Use this when closed slices should leave the active slice area, but their work
items and design should still be visible in planning docs.

```text
Use `archive-artifacts` with `--artifact-type feature --artifact-id checkout --apply` to summarize and archive all closed planned slices for `checkout`.
```

```text
Use `archive-artifacts` with `--artifact-type subfeature --artifact-id replace-legacy-flow --apply` to summarize and archive all closed planned slices for that subfeature.
```

In scope apply mode, the skill:

- reads planned slice IDs from `slice-planning.md`
- finds closed, not-yet-archived slices
- summarizes `brief.md` and `blueprint.md` into the target `system-design.md`
- carries over embedded PlantUML figures directly into `system-design.md`
- archives the slice folders through the execution archive helper

### 9. Tighten repo governance after repeated drift

Use this when the problem is recurring enough that the repository should gain a
durable rule in `AGENTS.md`, `.skills/*.json`, or another top-level governance
surface.

```text
Use `governance-update` to add a repo rule in `AGENTS.md` so UI design artifacts default to a simpler MVP interaction model instead of expanding into mini-apps.
```

```text
Use `governance-update` to review repeated config-surface drift across `AGENTS.md`, `.skills/conventions.json`, and recent planning docs, then tighten the narrowest governance surface that should own the rule.
```

Good additions to the prompt:

- the repeated problem pattern
- 1-3 concrete examples that show the drift
- the preferred governance surface when you already know it
- whether the rule should stay generic-first or become explicitly repo-local
- the non-goals, so the governance update does not sprawl into unrelated policy

## What to include in a strong prompt

Include whichever of these matter:

- the exact skill name, if you know it
- the feature slug, subfeature ID, or slice ID
- the repository path when the target is ambiguous
- whether the work is new planning, current-state documentation, or review
- important constraints such as compatibility, validation needs, or non-goals
- whether the agent should stop at planning output or continue into the next workflow handoff

Good:

```text
Use `design` for `docs/features/routing-cache/` and produce a reviewable `system-design.md` for the current implementation under `src/routing/`. Make failure and reconnect behavior explicit.
```

Weak:

```text
Help me with routing.
```

## When to fall back to a guide skill

Use a guide skill when the accelerator path is not the right fit and you know
the layer but not the exact next operation.

### Prefer `guide-scope`

When:

- the repo may contain multiple scopes
- you are unsure whether the task belongs to planning, execution, or bootstrap

### Prefer `guide-planning`

When:

- the work is feature planning
- you want the agent to pick among `propose`, `research`, `discover`, `design`, `breakdown`, or review-oriented planning skills

### Prefer `guide-execution`

When:

- a slice already exists
- you want the agent to choose among `brief`, `blueprint`, `review-execution`, and closure work

## Common prompt mistakes

- asking for implementation when planning is not reviewed yet
- naming no feature, path, or slice when several are plausible
- asking for `breakdown` before discovery or design is concrete
- asking for `slice` bootstrap before planning approval and commit
- asking for `ship` before the reviewed planning artifacts are committed
- assuming closed slices are deleted automatically
- writing a vague prompt that omits the desired artifact or stop point

## Practical recipes

### “I already have a planning target and want it advanced”

```text
Use `autoplan` for `checkout-redesign` and continue until the next planning boundary.
```

### “I want design first, no discover doc”

```text
Use `design` for `checkout-redesign`. There is no `discover.md`; use this prompt as the planning input and create `system-design.md`.
```

### “This feature overlaps checked-in references; capture the borrowing path first”

```text
Use `research` for `docs/features/checkout-redesign/` and write `reference-research.md` from the relevant checked-in references before design continues.
```

### “I already implemented it; document it for review”

```text
Use `design` for `docs/features/checkout-redesign/` and reverse engineer the implementation into a current-state `system-design.md` for review.
```

### “I need a change under an existing feature”

```text
Use `guide-planning` for feature `checkout` and route this request as subfeature work if needed.
```

### “Planning is reviewed and committed; start execution”

```text
Use `slice` to bootstrap the next approved slice for `checkout-redesign`.
```

### “Planning is reviewed and committed; work the full backlog one slice at a time”

```text
Use `ship` for `checkout-redesign` and continue through the planned slices until a blocker or per-slice commit checkpoint stops the run.
```

### “Move closed slices out of the active area but keep their design history”

```text
Use `archive-artifacts` with `--artifact-type feature --artifact-id checkout --apply` and summarize the archived slices into the feature `system-design.md`.
```

### “This keeps happening; add a durable repo rule instead of fixing one artifact”

```text
Use `governance-update` to review the repeated UI-design drift in `docs/features/terminal-ui/` and tighten `AGENTS.md` with a simple MVP-first UI design rule.
```

## Short rule of thumb

If you know the exact artifact you want, prompt the specific skill.

If accelerator flow is not the right fit and you know only the workflow layer,
prompt the corresponding guide skill.
