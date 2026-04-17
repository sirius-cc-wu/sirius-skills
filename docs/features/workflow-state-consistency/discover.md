# Discover: Workflow State Consistency

## Problem

`sirius-skills` keeps durable workflow state across planning metadata, feature and
subfeature registries, execution-slice metadata, traceability tables, and
proposal artifacts. That durability is a strength, but the current skillset does
not yet enforce all of the semantic invariants that connect those artifacts.

Recent repo evidence showed the practical failure mode:

- execution slices can be closed while subfeature metadata still says `reviewed`
- `affected_slice_ids` can remain empty even when traceability points to closed
  execution slices
- audit and repair tooling can disagree when they do not share the same parsing
  and reconciliation logic
- installed skill copies can lag behind repo-local fixes and keep stale behavior

The feature needs to harden the existing workflow so drift becomes harder to
create, easier to detect, and safer to repair without abandoning the current
repo-first planning and execution model.

## Goals

- Define and enforce the most important cross-artifact workflow invariants.
- Reuse shared reconciliation logic across artifact-maintenance skills instead
  of letting each skill infer the workflow state independently.
- Add narrow guardrails around state transitions that commonly leave stale
  metadata behind.
- Make it clearer whether a problem is derived-registry drift or semantic
  metadata drift.
- Improve confidence that the active installed skill behavior matches the
  checked-in repo source.

## Non-Goals

- Replace the current repo-native planning and execution methodology.
- Collapse all workflow state into one artifact.
- Rewrite the whole skillset as part of this feature.
- Replace deterministic workflow mutation with agent-only reasoning.

## Primary Actors

- Maintainer evolving the core `sirius-skills` workflow engine and maintenance
  skills.
- Reviewer diagnosing planning-versus-execution drift in durable repo artifacts.
- Project owner relying on installed skills and expecting them to match the
  checked-in repository behavior.
- Skill author extending artifact-maintenance flows without duplicating semantic
  logic.

## Constraints

- The solution must remain generic-first and reusable across repositories.
- Planning and execution must stay separate workflow layers with explicit
  ownership boundaries.
- Derived registries and README tables should remain owned by their registry
  writers instead of being hand-maintained.
- Semantic mutations should remain explicit and traceable; maintenance tooling
  should not silently guess corrections.
- The feature should improve the existing skillset incrementally before forcing
  a deeper architectural rewrite.

## Confirmed Signals in Repo

- `audit-artifacts`, `trace-artifacts`, `report-artifacts`, and
  `repair-artifacts` all reason about overlapping workflow artifacts.
- Traceability parsing recently had to move into shared helpers because multiple
  skills depended on the same table semantics.
- `repair-artifacts` is intentionally conservative and currently focuses on
  derived registry/readme regeneration rather than semantic metadata repair.
- The repository now has a concrete example of subfeature drift:
  `host-safe-validation/subfeatures/vs-backend-abstraction/` was left in a
  reviewed state while its traceability-linked execution slices were closed.
- The installed skill copy can drift from the repo-local source, which can leave
  maintainers invoking stale maintenance behavior.

## Assumptions

- The highest-value near-term improvements are shared reconciliation logic,
  transition guardrails, and better parity checks rather than a full rewrite.
- The current artifact model is worth preserving if its invariants are made more
  explicit and more consistently enforced.
- The deeper `skill-state-engine-rewrite` proposal remains a follow-on option,
  not a prerequisite for this feature.

## Desired Outcomes

- Closing or finalizing workflow artifacts no longer silently leaves obvious
  semantic drift behind.
- Artifact-maintenance skills converge on one interpretation of
  feature/subfeature/slice linkage.
- Repo-local fixes do not remain hidden behind stale installed skill behavior.
- Maintainers can preview semantic follow-up work separately from derived
  registry repair.

## Success Criteria

- The concrete drift class from this session is prevented at transition time or
  surfaced immediately by shared consistency checks.
- The relevant maintenance skills share reconciliation behavior for
  subfeature-to-slice linkage instead of reimplementing it separately.
- The repository has a durable way to detect or warn when installed skills do
  not match the checked-in source.

## Risks and Open Questions

- Incremental hardening may still leave enough duplication behind that the
  rewrite proposal becomes necessary later.
- Transition guardrails can become noisy if they are not scoped tightly to
  high-confidence invariants.
- Repo-local versus installed parity checks need to work across supported agent
  environments without becoming brittle or overly platform-specific.
