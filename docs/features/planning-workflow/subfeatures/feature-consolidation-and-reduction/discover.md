# Discover: Feature Consolidation And Reduction

## Parent Feature

- Feature: `planning-workflow`
- Subfeature ID: `feature-consolidation-and-reduction`
- Subfeature Type: `superseding`

## Problem

Require explicit capability reduction and supersession accounting when adding planning capabilities.

## Requested Subfeature

- Require every net-new planning capability proposal to declare:
  - what existing capability/subfeature it supersedes, narrows, or removes
  - what artifacts move from active to historical/archived status
  - what user-facing command surface is simplified as a result
- Add review-planning checks that reject additive-only expansion when a valid
  consolidation path exists.
- Keep reduction decisions durable in planning artifacts so wiki and execution
  flows can track consolidation outcomes.

## Baseline Artifacts To Assess

- `discover.md`
- `system-design.md`
- `user-stories.md`

## Subfeature Execution Planning

- Add or update `slice-planning.md` and `slice-traceability.md` inside this subfeature folder for any new execution work.
- Treat the parent feature docs as baseline context unless impact analysis explicitly narrows or supersedes them.

## Risks and Open Questions

- How strict should the gate be for first rollout (warning-only vs blocking)?
- What minimum evidence should prove that a claimed supersession actually
  removed workflow surface area rather than adding parallel complexity?
