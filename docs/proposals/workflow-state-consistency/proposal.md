# Proposal: Workflow State Consistency

## Problem

`sirius-skills` keeps workflow state across multiple durable artifacts:

- planning metadata and registries
- subfeature metadata and registries
- proposal metadata and registries
- execution slice registries and per-slice metadata
- traceability tables that link planning stories to execution slices

That split is useful for durable repo-native workflows, but it currently allows
semantic drift when the deterministic ownership boundaries are incomplete.

Recent repo evidence exposed several failure modes:

- execution slices can close while subfeature metadata still says `reviewed`
- `affected_slice_ids` can lag behind closed execution slices recorded in
  traceability
- audit, trace, and repair skills can disagree when they do not share the same
  parsing or reconciliation logic
- installed skill copies can drift from the repo-local source and continue using
  stale behavior
- repair tooling intentionally fixes derived registries/readmes, but lacks a
  safe path for semantic metadata reconciliation

The main need is to harden the existing skillset so drift becomes harder to
create, easier to detect, and easier to repair without replacing the current
repo-first workflow.

## Goals

- Detect planning, subfeature, traceability, and execution drift earlier.
- Reuse one shared reconciliation model across audit, trace, report, and repair
  workflows.
- Add safer guardrails around state transitions that commonly leave stale
  metadata behind.
- Preserve the current skill layout and durable artifact model while making the
  deterministic parts more complete.
- Improve repo-local versus installed-skill parity checks so maintainers can
  trust the active behavior they are invoking.

## Non-Goals

- Replace the current repo-native planning and execution methodology.
- Collapse all workflow artifacts into one file.
- Promote speculative fixes directly into canonical feature planning from this
  proposal.
- Require a large rewrite before incremental consistency improvements can land.

## Candidate Capability Areas

- **Shared reconciliation helpers**
  - Move cross-artifact linkage and traceability parsing into common code used
    by multiple maintenance skills.
  - Define shared helpers for feature, subfeature, and slice linkage instead of
    letting each skill infer state independently.

- **Transition guardrails**
  - Add narrow post-transition checks after state-changing operations such as
    closing slices or finalizing subfeatures.
  - Warn or block when a command would leave obvious semantic drift behind.

- **Semantic repair previews**
  - Extend maintenance tooling so it can preview semantic follow-ups, not just
    derived registry regeneration.
  - Keep apply mode conservative unless the repo explicitly chooses a safe
    mutation path.

- **Version and parity checks**
  - Detect when installed skill copies lag behind the checked-in repo source.
  - Make stale packaged behavior visible before maintainers rely on it.

- **Consistency validation in CI**
  - Run audit and targeted reconciliation checks in automation so drift is
    caught before it becomes durable.

## Constraints

- The skills should remain generic-first and reusable outside one project.
- Derived artifacts should still be owned by the relevant registry writers.
- Semantic state mutations should stay explicit and traceable rather than
  silently inferred.
- Planning and execution should remain separate workflow layers with clear
  ownership boundaries.

## Desired Outcomes

- Closing execution slices no longer silently leaves stale subfeature metadata
  behind.
- Artifact-maintenance skills agree on the same cross-artifact facts.
- Maintainers can tell whether a problem is derived-registry drift or semantic
  metadata drift.
- Repo-local fixes are not masked by stale installed skill copies.

## Success Criteria

- The main drift class from this session is either prevented at transition time
  or surfaced immediately by shared consistency checks.
- `audit-artifacts`, `trace-artifacts`, and `repair-artifacts` reuse the same
  reconciliation rules for subfeature-to-slice linkage.
- The repository has an explicit path to detect or warn on installed-vs-local
  skill version drift.

## Why This Is Still A Proposal

- The work is not yet accepted as a canonical feature.
- The solution may span multiple maintenance skills, shared helpers, CI checks,
  and transition semantics.
- Keep speculative notes here until the team decides whether to pursue
  incremental hardening, a deeper rewrite, or both.
