# Discover: Subfeature Workflow

## Problem

`sirius-skills` already supports net-new feature planning and slice-scoped
execution, but it also needs a durable way to extend or reshape an existing
feature over time.

Without a dedicated subfeature workflow, teams either overwrite parent feature
docs in place with weak traceability or keep ad hoc side documents that never
become first-class planning artifacts.

## Goals

- Add a repo-native workflow for evolving an existing feature through durable
  child planning folders.
- Keep parent feature docs durable while allowing reviewed subfeature planning
  to happen in parallel.
- Make impact analysis explicit before new execution slices are bootstrapped.
- Preserve traceability between parent artifacts, subfeature artifacts, planned
  slices, and closed work.
- Finalize reviewed subfeatures explicitly once all planned slices are closed.

## Non-Goals

- Replace the current workflow for net-new feature planning.
- Replace the slice-scoped execution workflow.
- Automatically rewrite parent feature docs as part of ordinary planning.
- Delete durable subfeature folders after implementation.

## Primary Actors

- Product or feature owner requesting an extension to an existing capability.
- Planner creating a durable child planning folder under the parent feature.
- Reviewer assessing impact on parent docs, stories, and slices.
- Designer or breakdown owner producing subfeature-local design and slice plans.
- Maintainer finalizing a reviewed subfeature after its planned slices are
  closed.

## Constraints

- Parent feature planning remains rooted in `docs/features/<feature-slug>/`.
- Durable child planning lives under
  `docs/features/<feature-slug>/subfeatures/<subfeature-id>/`.
- The workflow remains skill-first and repository-centric.
- Execution still flows through slices, not through subfeatures.
- Finalization must be explicit and human-invoked.

## Desired Outcomes

- Teams can add durable subfeatures without replacing the parent feature folder.
- Reviewers can inspect changed intent, impacted artifacts, and planned slices
  before execution starts.
- Closed work can be traced back to a reviewed subfeature and its impact
  analysis.
- Implemented subfeatures remain part of the planning hierarchy as durable
  history.

## Candidate Capability Areas

- **Subfeature creation**
  - Start a durable child planning folder under an existing feature.
  - Record parent-child metadata and the reason for the new capability.

- **Subfeature-local planning artifacts**
  - Author `discover.md`, `system-design.md`, `slice-planning.md`, and
    `slice-traceability.md` inside the selected subfeature folder.
  - Use `discover.md` and `.subfeature-meta.json` to record affected parent
    artifacts, user stories, planned slices, and whether the change is additive,
    narrowing, superseding, or replacement.
  - Keep those artifacts linked to the parent feature without overwriting the
    parent baseline.

- **Finalization**
  - Verify that every planned slice for a reviewed subfeature is closed.
  - Remove completed execution slices and mark the durable subfeature
    implemented.

## Confirmed Signals in Repo

- `guide-planning` already manages planning readiness and registry state.
- `add-subfeature` creates durable child planning folders and subfeature
  metadata.
- `discover` writes subfeature-local context from parent feature context.
- `design` and `breakdown` can target a selected subfeature path.
- Subfeature execution remains non-destructive after closure; any later cleanup
  or archival should be handled by explicit maintenance tooling.

## Success Criteria

- A maintainer can create a durable subfeature under an existing feature and
  route it through planning review.
- Reviewers can see what is affected before new execution slices are created.
- Execution slices can be closed independently, then finalized back at the
  reviewed subfeature level.
- The resulting history is durable, inspectable, and nested within the feature
  hierarchy.

## Risks and Open Questions

- Parent and child planning artifacts need clear ownership so traceability stays
  obvious.
- Nested planning paths require registry syncing to remain recursive and stable.
- If multiple active open subfeatures under one parent become common, the repo
  may need stronger coordination rules.
