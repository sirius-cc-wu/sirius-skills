# Discover: Proposal Workflow

## Problem

`sirius-skills` now has a working `propose` skill and a proposal registry under
`docs/proposals/`, but the mechanism itself should also be tracked as a
canonical repository feature.

Without a canonical feature for the proposal system, the repo can use proposal
instances operationally while lacking a durable feature-level record for:

- why speculative work should stay out of `docs/features/`
- how proposal lifecycle state differs from feature lifecycle state
- how accepted proposals promote into canonical feature planning
- what routing rules `guide-planning` should use before discovery starts
- how configuration such as `proposal_dir` shapes proposal storage

That makes the capability harder to evolve intentionally over time.

## Goals

- Treat the proposal mechanism as a first-class feature of `sirius-skills`.
- Keep proposal instances under `docs/proposals/` until accepted.
- Define a durable boundary between proposal staging and canonical feature planning.
- Make promotion from proposal to feature explicit and reviewable.
- Capture routing, registry, metadata, and configuration expectations in one canonical place.

## Non-Goals

- Turn every individual proposal into a canonical feature.
- Replace `discover`, `design`, or `breakdown` for accepted features.
- Replace `evolve-feature` for changes to existing canonical features.
- Introduce a standalone CLI product.

## Primary Actors

- Repository maintainer shaping the planning workflow.
- Planner deciding whether an idea is speculative or already feature-ready.
- Reviewer checking whether a proposal should be accepted, rejected, or promoted.
- Project adopter configuring proposal storage with `.skills/planning.json`.

## Constraints

- Proposal instances remain proposal-scoped, not feature-scoped.
- Canonical features continue to live under `docs/features/<feature-slug>/`.
- Proposal storage remains configurable but defaults to `docs/proposals/`.
- Promotion must not silently overwrite an existing feature folder.
- Routing must stay repository-centric and skill-based.

## Desired Outcomes

- Users can separate speculative work from accepted feature planning cleanly.
- `guide-planning` can route early ideas to `propose` and accepted work to normal planning.
- The repository has a durable description of proposal states, artifacts, and promotion rules.
- Future improvements to proposal review or promotion have a canonical feature home.

## Success Criteria

- The repo contains a canonical feature describing the proposal workflow itself.
- Proposal instances remain outside the feature registry until they are promoted.
- Promotion rules, storage layout, and routing behavior are explicit enough for future design and review.
