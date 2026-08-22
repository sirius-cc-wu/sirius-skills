---
name: design-rust-lifecycles
description: Designs ownership-safe Rust lifecycles for resources, state transitions, staged startup, readiness, rollback, cancellation, concurrency, and fallible cleanup. Use when approved system behavior and native responsibilities must become explicit capability ownership, task supervision, consuming transitions, RAII, or shutdown design without losing the system or verification boundary.
---

# Design Rust Lifecycles

## Overview

Turn approved behavior and responsibility decisions into the smallest idiomatic
Rust lifecycle that makes ownership, transitions, failure, and cleanup
explicit. Treat resource and cancellation semantics as design inputs rather
than implementation details.

## When to Use

- A Rust component owns files, sockets, locks, tasks, processes, credentials,
  reservations, transactions, or other fallible resources.
- Startup has preparation, readiness, partial success, rollback, or ordered
  cleanup requirements.
- Consuming methods, a private state enum, typestate, RAII, or explicit
  shutdown must be selected deliberately.
- Multiple async or threaded participants need one cancellation and supervision
  policy.
- A boundary-sensitive Rust refactoring has an established system scenario and
  native responsibility assignment but still needs implementation-facing
  ownership design.
- Do not use to discover product behavior, choose the system boundary, assign
  language-neutral responsibilities, or implement the design.

## Workflow

1. **Fix the input authority and design context.** Identify the approved or
   recovered representative scenario, system boundary, externally visible
   readiness or effects, native responsibility decisions, compatibility
   obligations, repository facts, verification oracle, and unresolved intent.
   For a boundary-sensitive objective, return to the owning analysis or
   responsibility specialist when that context is absent or stale. Stop rather
   than invent a missing business or protocol rule.
2. **Inventory resources and capabilities.** Read
   [Ownership and Transitions](references/ownership-and-transitions.md). Record
   creation, prepared ownership, transfer, running ownership, release, and
   emergency `Drop` behavior for every material resource. Map each lifecycle
   owner to the native software responsibility it realizes.
3. **Model lifecycle states.** Select the smallest representation that prevents
   consequential invalid transitions: consuming methods first, then a private
   enum, and typestate only when compile-time separation repays its API cost.
4. **Separate preparation from effects.** Define what must be validated,
   acquired, and reserved before the first externally visible action. Keep
   reservations alive until ownership transfers to the consumer.
5. **Design failure and cancellation.** Read
   [Failure, Cancellation, and Cleanup](references/failure-cancellation-cleanup.md).
   Define rollback for every partial-start boundary, cancellation at every
   relevant `.await`, reverse-order cleanup, primary-error preservation, and
   cleanup-error reporting.
6. **Choose concurrency and variation mechanisms.** Read
   [Concurrency and Variation](references/concurrency-and-variation.md) when
   tasks, threads, heterogeneous participants, or alternative providers are
   present. Prefer concrete types, enums, generics, functions, and modules
   before runtime traits.
7. **Sketch the Rust API.** Show owned fields, borrowed views, consuming
   transitions, transferred handles, `Result` types, and `Send`/`Sync`
   boundaries. Mark sketches as proposed rather than existing code.
8. **Define verification obligations.** Cover invalid inputs, ownership
   uniqueness, transition invariants, partial startup, cancellation, repeated
   and concurrent use, cleanup failure, compatibility, and secret-safe errors.
   Retain the representative integration or end-to-end oracle alongside
   focused lifecycle checks and identify human-owned validation.
9. **Close traceability and feedback.** Link each design choice to the system
   behavior, native responsibility, risk, repository fact, or demonstrated
   variation that requires it. If ownership evidence changes a responsibility,
   system boundary, or verification obligation, return that change to its
   canonical owner. Record a concrete trigger for every deferred abstraction.

## Artifact Output

Before creating a file, apply
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
Prefer refining an existing implementation-facing design when it owns the same
lifecycle. Otherwise, copy and tailor
[Rust Lifecycle Design Template](assets/rust-lifecycle-design.md).

For a standalone artifact, follow
[Markdown Artifact Frontmatter](../iterative-risk-driven-development/references/markdown-artifact-frontmatter.md)
and
use STE-style.
Use this artifact type:

```yaml
type: "Rust Lifecycle Design"
language: "rust"
```

Keep ownership, state, startup, rollback, cancellation, cleanup, API shape,
and verification in one artifact unless one cross-cutting, expensive-to-reverse
choice has a genuinely independent lifecycle. In that case, use external
`documentation-and-adrs` with the `all` installation or follow
repository-native ADR guidance. Do not copy the lifecycle design into the ADR.

## Boundaries

- Do not use a Rust lifecycle design as a substitute for a missing system
  boundary, representative scenario, native responsibility map, or
  verification boundary.
- Preserve GRASP responsibilities without creating a struct or trait for every
  conceptual collaborator. A module, function, task, enum, adapter, resource
  handle, or composition root may remain the responsibility owner.
- Do not use typestate merely to mirror a state diagram; use it when callers
  materially benefit from compile-time transition enforcement.
- Do not claim RAII completes fallible or asynchronous cleanup. Use explicit
  terminal operations when ordering, error reporting, termination, or reaping
  matters, and define `Drop` as an emergency fallback.
- Do not introduce a trait until substitution, heterogeneous storage,
  dependency inversion, or an unstable integration boundary is evidenced.
- Keep requirements and domain models language-neutral. This skill owns the
  implementation-facing lifecycle, not product intent.
- Completing a lifecycle handle or resource seam may finish the current design
  objective. It does not prove a broader parent outcome without the retained
  representative vertical oracle.

## Verification

- [ ] The system boundary, representative scenario, native responsibilities,
      compatibility obligations, and verification oracle are current enough to
      constrain the lifecycle.
- [ ] Every lifecycle owner maps to an explicit software responsibility.
- [ ] Every material resource has one owner at each lifecycle point.
- [ ] Every transfer and consuming transition is explicit.
- [ ] Validation and reservation precede the first externally visible effect.
- [ ] Partial startup has a complete rollback path.
- [ ] Cancellation behavior is defined at relevant `.await` and task boundaries.
- [ ] Explicit cleanup attempts all required actions in the intended order.
- [ ] The primary outcome survives cleanup failures.
- [ ] `Drop` behavior is safe, bounded, non-blocking, and not overstated.
- [ ] Concurrency uses the narrowest justified sharing and synchronization.
- [ ] Traits and typestate correspond to demonstrated design forces.
- [ ] Verification obligations cover failure, repetition, concurrency, the
      representative vertical flow, and human-owned checks.
- [ ] Ownership discoveries that change responsibilities, boundaries, or
      verification have been returned to their canonical owners.
- [ ] Proposed API sketches remain distinguishable from as-built symbols.
