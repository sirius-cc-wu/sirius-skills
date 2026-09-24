---
name: type-anchored-spec
description: Translates approved business rules, "Always Do / Never Do" boundaries, and agent workflow constraints into Rust's compile-time type system — using phantom types, typestate, sealed traits, and opaque wrappers — so the compiler enforces spec fidelity rather than relying on runtime checks or markdown alone. Use after a domain model, system boundary, and responsibility assignment exist but before implementation begins.
---

# Type-Anchored Spec

## Overview

Embed approved business rules and spec boundaries directly into Rust types so
that `cargo check` acts as an automated boundary guard. A correctly anchored
spec makes it structurally impossible — at compile time — for an implementation
agent to skip a required step, widen a sealed boundary, or leak an opaque
domain invariant.

This skill produces **Rust type-layer artifacts**: phantom-type state machines,
sealed trait boundaries, opaque wrappers, and domain error enums. It does not
produce product logic, application behaviour discovery, or lifecycle resource
management (see `design-rust-lifecycles` for the latter).

## When to Use

- An approved domain model, representative scenario, and native responsibility
  assignment exist and must be hardened against agentic or human drift.
- A business rule has an "Always Do / Never Do" character strong enough to
  warrant compiler enforcement rather than a test or code-review convention.
- A state machine must be traversed in a fixed order and skipping a step would
  constitute a spec violation (e.g. validate → reserve → process).
- A module boundary must be sealed so that new implementations require
  explicit human sign-off rather than silent agent extension.
- A sensitive value (secret, PII, currency amount) must not cross a module
  boundary in an unchecked form.
- An agent loop needs a type-system feedback signal — in addition to tests —
  to self-correct during `cargo check` iterations.

Do **not** use this skill to:
- Discover product behaviour or choose system boundaries (→ spec-validate/discovery).
- Assign language-neutral responsibilities (→ spec-validate/design, GRASP skill).
- Design resource ownership, RAII, or async cancellation (→ design-rust-lifecycles).
- Implement production code (→ execution/build).

## Workflow

1. **Anchor to approved inputs.** Collect the representative scenario, domain
   model, "Always Do / Never Do" rules, sealed boundary decisions, and
   verification oracle. If any of these are absent or stale, return to the
   owning analysis skill rather than inventing a missing rule.

2. **Identify anchor candidates.** For every business rule, classify it:

   | Rule class | Preferred anchor |
   |---|---|
   | Ordered state transition | Phantom type / typestate |
   | Exclusive implementation set | Sealed trait |
   | Sensitive or opaque value | Newtype wrapper |
   | Forbidden representation (e.g. float currency) | Domain type with private constructor |
   | Domain failure modes | Closed `Error` enum |

3. **Design phantom-type state machines.** Read
   [Phantom Types and Typestate](references/phantom-types-and-typestate.md).
   Assign one zero-size struct per meaningful state. Use consuming methods to
   enforce legal transitions; use typestate only when the compile-time API
   benefit exceeds the added type-parameter complexity.

4. **Seal boundaries.** Read
   [Sealed Traits and Extension Control](references/sealed-traits-and-extension-control.md).
   Place the `private::Sealed` super-trait in a `mod private` block. Enumerate
   approved implementors explicitly. Any new implementor requires a deliberate
   change to the sealed module — a human-visible diff.

5. **Wrap opaque values.** Use newtype wrappers and private fields to prevent
   raw sensitive types from crossing module boundaries. Apply `zeroize` or
   redaction traits where secret data must not appear in logs or errors.

6. **Define the domain error enum.** All failure modes reachable from
   spec-constrained operations must map to named variants in a closed `Error`
   enum defined alongside the spec types. Forbid `unwrap()` and `expect()` in
   spec-anchored modules.

7. **Sketch the spec-layer API.** Show only the types, traits, and module
   boundaries. Mark sketches as **proposed** — not as-built symbols. Do not
   include application logic.

8. **Define verification obligations.** Cover: illegal transition attempts,
   sealed boundary extension attempts, opaque value leakage, error enum
   exhaustiveness, and the retained integration oracle.

9. **Link to agent workflow constraints.** Record the `cargo check` and
   `cargo test` feedback loop that the implementation agent must honour.
   State which spec violations will appear as compile errors vs. test failures.

10. **Close traceability.** Link each anchor type to the business rule,
    scenario step, or "Never Do" constraint it encodes. If anchoring reveals a
    missing or contradictory rule, return that finding to its canonical owner.

## Artifact Output

Before creating a file, apply
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
Follow
[Markdown Artifact Frontmatter](../design-repository-artifact-layout/references/markdown-artifact-frontmatter.md)
and use STE-style.

Copy and tailor
[Type-Anchored Spec Template](assets/type-anchored-spec.md) for the capability
under design.

Use this artifact type in frontmatter:

```yaml
type: "Type-Anchored Spec"
language: "rust"
```

Keep state machines, sealed boundaries, opaque wrappers, error enums, and
agent workflow constraints in one artifact per capability unless a type crosses
multiple bounded contexts — in that case, split by context and cross-reference.

## Boundaries

- This skill owns the **type layer** only. It does not own application logic,
  service orchestration, or test implementations.
- Do not introduce typestate merely because a state diagram exists. Use it only
  when callers benefit materially from compile-time transition enforcement.
- Do not seal a trait whose implementor set is legitimately open to extension.
  Sealing is a deliberate architectural commitment, not a default.
- Opaque wrappers must preserve the domain invariant they encode; do not wrap
  values arbitrarily.
- The `Error` enum must remain closed to the boundary it governs. Do not leak
  internal variants across module boundaries.
- Completing a type-anchored spec does not substitute for a system scenario,
  representative integration test, or native responsibility map.

## Agent Workflow Integration

When an implementation agent operates against a type-anchored spec:

1. Every capability's business rules are anchored in `src/specs/<capability>.rs`.
2. The agent maps markdown spec requirements to the type-layer file before
   modifying any application code.
3. `cargo check` and `cargo test` are the primary feedback loops. A compile
   error signals a spec violation, not merely a syntax error.
4. `unwrap()` and `expect()` are forbidden in spec-anchored modules; all failure
   modes map to the domain `Error` enum.
5. Adding a new sealed implementor requires a deliberate change to the
   `mod private` block — triggering human review.

## Verification

- [ ] Every "Always Do / Never Do" rule has a named type-layer anchor.
- [ ] Every state transition is enforced by a consuming method or typestate; no
      public constructor bypasses the intended entry point.
- [ ] Every sealed trait lists exactly the approved implementors and no others.
- [ ] Every sensitive value crosses boundaries only through its opaque wrapper.
- [ ] Every reachable failure mode maps to a named variant in the domain
      `Error` enum.
- [ ] No spec-anchored module calls `unwrap()` or `expect()`.
- [ ] Illegal transitions, sealed extensions, and value leaks are covered by
      compile-error or test-failure evidence.
- [ ] The representative integration oracle is retained alongside type-layer
      checks.
- [ ] All anchor types trace to an approved business rule or "Never Do"
      constraint.
- [ ] Proposed API sketches remain distinguishable from as-built symbols.
