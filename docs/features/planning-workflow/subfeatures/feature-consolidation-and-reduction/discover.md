# Discover: Feature Consolidation And Reduction

## Parent Feature

- Feature: `planning-workflow`
- Subfeature ID: `feature-consolidation-and-reduction`
- Subfeature Type: `superseding`

## Problem

`sirius-skills` can add new planning capabilities over time, but the planning
workflow does not yet require maintainers to account for what a new capability
should simplify, narrow, retire, or supersede.

Without an explicit consolidation rule, the planning surface can drift toward
additive-only growth:

- new skills can overlap existing planning responsibilities without naming the
  boundary change,
- new planning artifacts can appear without a durable retirement path for older
  ones,
- new command surfaces can accumulate while older entrypoints remain
  effectively supported in parallel,
- reviews can approve a useful new capability while still increasing total
  workflow complexity.

For a planning system that aims to stay repository-centric and durable, growth
without reduction makes the workflow harder to learn, review, and maintain.

## Goals

- Require net-new planning capabilities to declare what existing workflow
  surface they supersede, narrow, or remove.
- Make reduction decisions durable in planning artifacts instead of leaving them
  implied in chat or code review.
- Teach planning review to reject additive-only expansion when a credible
  consolidation path exists.
- Track which artifacts move from active workflow use to historical or archived
  status when a new capability lands.
- Push the planning workflow toward fewer overlapping entrypoints and clearer
  ownership boundaries over time.

## Non-Goals

- Ban all additive change. Some genuinely new capabilities will still be
  additive when no valid consolidation target exists.
- Delete historical planning artifacts automatically during discovery.
- Force execution-layer slices or execution metadata to absorb planning-layer
  consolidation decisions.
- Redesign the entire planning workflow in one pass instead of creating a
  durable rule for future changes.

## Primary Actors

- Planner proposing a new planning capability or subfeature.
- Reviewer deciding whether the proposed capability simplifies the overall
  planning workflow or only adds parallel complexity.
- Maintainer updating feature docs, subfeature docs, and registries to reflect
  what is now active versus historical.
- Repository adopter trying to understand the current command surface and which
  planning path is canonical.

## Constraints

- Discovery must stay feature-scoped and repository-first; it should not create
  execution slices.
- The parent `planning-workflow` feature remains the baseline context unless a
  later impact-analysis or design artifact narrows that scope explicitly.
- Consolidation decisions must be durable in repo artifacts, not only in chat
  explanations or code comments.
- The workflow must support `additive`, `narrowing`, `superseding`, and
  `replacement` subfeature types without collapsing them into one vague review
  rule.
- Review guidance should be strict enough to prevent redundant planning
  surfaces, but not so rigid that it blocks clearly justified net-new
  capabilities.

## Desired Outcomes

- Every new planning capability states its reduction story up front.
- Reviewers can see whether a proposal removes complexity or merely shifts it.
- Parent features, subfeatures, and later execution planning can trace what
  capability or artifact became historical.
- The user-facing planning command surface becomes simpler over time instead of
  accumulating parallel entrypoints.

## Candidate Capability Areas

- **Reduction declaration**
  - Require discovery and/or impact-analysis artifacts to name what existing
    capability, skill, artifact, or command surface is being narrowed or
    superseded.
  - Distinguish between "no valid consolidation target exists" and "this is a
    justified superseding change."

- **Artifact lifecycle accounting**
  - Record which planning artifacts remain active, which become historical, and
    which should later be archived.
  - Keep those decisions durable enough for cross-artifact maintenance and wiki
    reporting workflows to consume.

- **Planning review enforcement**
  - Add review checks that identify additive-only expansion when overlapping
    planning responsibilities already exist.
  - Require explicit justification when a reviewer accepts a net-new capability
    without corresponding reduction.

- **Surface-area simplification**
  - Capture how a proposed capability simplifies the visible workflow for a
    maintainer or repository adopter.
  - Prefer one clearer command path over several overlapping skill entrypoints
    when the repo can support that simplification safely.

## Confirmed Signals in Repo

- `subfeature-workflow` already distinguishes additive, narrowing,
  superseding, and replacement changes, which means this repository recognizes
  change-shape categories but does not yet require capability-reduction
  accounting for new planning work.
- `review-planning` already asks reviewers to guard against ownership drift and
  brittle planning, which provides the right enforcement point for a
  consolidation rule.
- `cross-artifact-management` and its archive/trace/report maintenance
  subfeatures already assume artifacts can become historical or superseded,
  which means planning-layer reduction decisions should be recorded durably
  enough for those workflows to use.
- `execution-workflow` already treats relations such as `supersedes` as durable
  metadata, which suggests planning should offer an equally explicit model for
  feature-level or subfeature-level supersession.

## Baseline Artifacts To Assess

- parent feature `discover.md`, `system-design.md`, `user-stories.md`,
  `slice-planning.md`, and `slice-traceability.md`
- `subfeature-workflow` discovery and later impact-analysis/design guidance
- `review-planning` guidance and any checks that currently allow additive-only
  expansion
- maintenance-oriented artifacts or wiki pages that should eventually reflect
  whether a capability is active, superseded, or historical

## Candidate Story Seeds

- Define a durable way for new planning capabilities to declare what they
  simplify or retire.
- Make planning review block redundant capability growth when a valid
  consolidation path exists.
- Record active-versus-historical artifact movement so maintenance tooling can
  reason about consolidation outcomes later.
- Explain simplification in user-facing terms rather than only in internal
  planning notes.

## Subfeature Execution Planning

- Add or update `slice-planning.md` and `slice-traceability.md` inside this
  subfeature folder for any new execution work.
- Keep planned slices scoped to the new consolidation behavior and review
  enforcement, not to redoing the whole parent feature backlog.
- Treat the parent feature docs as baseline context unless impact analysis
  explicitly narrows or supersedes them.

## Success Criteria

- A maintainer adding a new planning capability can state what existing
  capability, artifact, or command surface is reduced as a result.
- A reviewer can distinguish between a justified net-new capability and
  redundant parallel workflow growth.
- Planning artifacts record what becomes active, historical, archived, or
  superseded in a way that later maintenance workflows can inspect.
- The resulting planning packet is concrete enough to move into design without
  re-framing the problem in chat.

## Risks and Open Questions

- How strict should the first review gate be: warning-oriented, blocking, or
  configurable by capability type?
- What minimum evidence proves a proposal truly reduces workflow surface area
  rather than simply renaming or relocating complexity?
- Which artifact should own the canonical active-versus-historical declaration:
  discovery, impact analysis, design, or review output?
- Should user-facing simplification be evaluated in terms of skill count,
  command count, artifact count, or reviewer burden?
