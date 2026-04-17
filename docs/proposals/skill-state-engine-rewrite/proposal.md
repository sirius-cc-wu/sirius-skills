# Proposal: Skill State Engine Rewrite

## Problem

The current skillset spreads workflow semantics across many scripts. Each skill
owns a useful slice of the workflow, but over time the model has become
duplicated:

- status normalization lives in multiple places
- artifact linkage is inferred separately by different skills
- traceability parsing and interpretation can move without every dependent skill
  moving with it
- repair, audit, report, and trace operate on overlapping concepts without one
  canonical state engine

This makes incremental fixes possible, but it increases the chance of
cross-skill drift and creates repeated maintenance work whenever the workflow
model grows more sophisticated.

The architectural question is whether `sirius-skills` should consolidate
artifact semantics into one shared engine, with skills becoming thin interfaces
for inspect, mutate, report, and repair operations.

## Goals

- Define one canonical artifact model for proposals, features, subfeatures,
  planned slices, and execution slices.
- Centralize workflow invariants, relationship parsing, and reconciliation
  rules.
- Make state transitions transactional across the artifacts they own.
- Reduce duplicated semantic logic across maintenance and planning skills.
- Keep the external skill surface understandable even if internal state handling
  becomes more centralized.

## Non-Goals

- Rewrite the entire repository in one step without an incremental migration
  path.
- Remove durable repo artifacts in favor of hidden runtime state.
- Turn `sirius-skills` into a standalone CLI product as part of this proposal.
- Replace skills with a freeform agent-only workflow.

## Proposed Direction

- **Canonical model**
  - Define shared types and normalization rules for workflow artifacts and their
    relationships.
  - Make status progression and invariants explicit in one place.

- **Shared engine**
  - Move reconciliation, linkage, and validation logic under one common engine.
  - Let skills call engine operations instead of reimplementing semantic rules.

- **Thin skill interfaces**
  - Keep user-facing skills as operation-specific wrappers:
    - audit
    - trace
    - repair
    - report
    - planning/execution state transitions
  - Preserve existing workflow names where practical.

- **Transactional writes**
  - State-changing operations should update all owned artifacts together or fail
    clearly.
  - Derived registries and readmes should remain generated views, not parallel
    sources of truth.

- **Migration-first rollout**
  - Freeze current drift cases as regression tests first.
  - Migrate one skill family at a time onto the shared engine.

## Key Risks

- A rewrite can over-centralize logic and make the skillset harder to evolve if
  the canonical model is too rigid.
- Migration could temporarily increase complexity if old and new paths coexist
  too long.
- Thin wrappers still need clean boundaries so one engine does not erase the
  current workflow ownership model.

## Desired Outcomes

- Semantic drift fixes happen in one place instead of four or five scripts.
- New workflow capabilities can be added by extending the shared model rather
  than repeating logic across maintenance skills.
- State transitions become more reliable without relying on chat context or
  human memory.

## Success Criteria

- The repository can point to one shared engine or library as the canonical home
  for workflow state semantics.
- At least one cross-skill inconsistency class from this session disappears
  because multiple skills now call the same underlying logic.
- Migration can proceed incrementally without breaking the existing repo-native
  workflow surface.

## Why This Is Still A Proposal

- The work is not yet accepted as a canonical feature.
- It is an architectural option, not just a small bug fix.
- The team may still decide that incremental hardening is sufficient and a full
  shared-engine rewrite is unnecessary.
