# Discover: Feature Evolution Workflow

## Problem

`sirius-skills` handles new feature planning and slice-scoped execution well,
but it does not yet provide a durable workflow for changing an already-planned
or already-implemented feature as product needs evolve.

Today, a team can create a feature folder, design it, break it into slices, and
execute those slices. The missing capability appears later, when the feature set
 changes:

- an existing feature needs new requirements or changed scope
- existing stories need to be superseded, narrowed, or replaced
- prior design decisions need amendment without losing history
- new slices must be created from changes to an existing canonical feature
- maintainers need a clear way to reconcile approved changes back into the
  feature's source-of-truth documents

Without a dedicated evolution workflow, teams risk either overwriting canonical
feature docs in place with weak traceability, or creating ad hoc side documents
that never reconcile back into the repository planning model.

## Goals

- Add a repo-native workflow for evolving an existing feature over time.
- Keep canonical feature docs durable while allowing scoped change proposals and
  deltas.
- Preserve traceability between baseline feature artifacts, change artifacts,
  updated slices, and closed work.
- Make impact analysis explicit before new execution slices are bootstrapped.
- Support reconciliation of approved changes back into canonical feature docs.

## Non-Goals

- Replace the current feature planning workflow for new greenfield features.
- Replace the current slice-scoped execution workflow.
- Introduce a standalone change-management CLI.
- Archive or delete canonical feature folders after a change closes.
- Automatically load arbitrary plugins or create a generalized workflow engine
  in the first iteration.

## Primary Actors

- Product or feature owner requesting a change to an existing capability.
- Planner assessing impact on existing feature docs, stories, and slices.
- Designer updating architecture or validation strategy for the changed scope.
- Breakdown owner creating new or revised execution-ready slices from the
  approved change.
- Reviewer confirming that approved changes have been reconciled into canonical
  feature artifacts.

## Constraints

- `docs/features/<feature-slug>/` remains the canonical feature planning area.
- The workflow must remain skill-first and repository-centric.
- The execution layer should still operate through slices, not through change
  folders as a parallel execution system.
- Evolution history must be durable, inspectable, and linkable from repo docs.
- Any new reconciliation step must be explicit; it should not silently mutate
  canonical planning artifacts without a visible workflow boundary.

## Desired Outcomes

- Teams can propose, analyze, approve, and reconcile changes to existing
  features without losing the original planning baseline.
- Existing stories, requirements, and slices can be marked as superseded,
  narrowed, expanded, or replaced with durable links.
- Planning reviewers can assess both the delta and the post-reconciliation
  canonical state before new slices are bootstrapped.
- Closed feature changes leave behind useful history instead of clutter or
  ambiguity.

## Candidate Capability Areas

- **Feature change initiation**
  - Add a way to start a scoped change against an existing feature.
  - Capture why the feature is changing and which baseline artifacts are
    affected.

- **Impact analysis**
  - Identify affected discovery/design/breakdown artifacts, user stories,
    planned increments, and slice IDs.
  - Distinguish additive changes from superseding or narrowing changes.

- **Delta artifacts**
  - Represent approved change intent separately from the canonical baseline long
    enough to review it clearly.
  - Keep delta artifacts explicitly linked to the feature they amend.

- **Reconciliation**
  - Provide an explicit step that merges approved changes back into canonical
    feature docs.
  - Remove temporary change artifacts after the canonical update is complete.

- **History and closure**
  - Keep canonical feature docs as the durable source of truth.
  - Use explicit reconciliation cleanup instead of archive-style retained
    history.

## Confirmed Signals in Repo

- Feature planning is already anchored in `docs/features/<feature-slug>/`.
- `guide-planning` already manages feature-scoped readiness and registry state.
- `breakdown` and `slice` already assume execution-ready work comes from
  repository planning artifacts.
- `guide-execution` and `close-slice` already support durable execution closure
  and relation tracking at the slice layer.
- `reconcile-feature` is the feature-level place where canonical updates and
  reviewed-change cleanup can happen, including deleting temporary source
  artifacts after reconciliation.

## Assumptions

- The best source of truth remains the canonical feature folder, not a separate
  global change registry.
- Feature evolution will likely need both new skills and small extensions to
  current planning metadata or conventions.
- The first version should focus on one changed feature at a time rather than
  multi-feature change batches.

## Success Criteria

- A maintainer can start a change against an existing feature without losing the
  canonical baseline.
- Reviewers can see what changed, what is impacted, and what must be reconciled
  before new slices are created.
- The workflow defines a clear boundary between "delta under review" and
  "reconciled canonical feature."
- The discovered scope is concrete enough for `design` to define artifact
  layouts, relationships, and validation rules.

## Risks and Open Questions

- The repository needs a clean distinction between feature-level change deltas
  and slice-level execution relations so the two do not compete.
- Reconciliation may become error-prone if artifact ownership is unclear.
- There may be more than one viable delta layout, for example:
  `docs/features/<feature>/changes/<change-id>/` versus a sibling
  `docs/feature-changes/` area.
- Archive-like history is useful, but the workflow should avoid making canonical
  feature docs feel disposable.
