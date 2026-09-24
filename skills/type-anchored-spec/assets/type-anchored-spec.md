---
type: "Type-Anchored Spec"
title: "Type-Anchored Spec: [Capability]"
description: "[What business rules this type layer encodes and what drift it prevents]"
id: "[Stable identifier]"
status: "[draft | proposed | accepted | retired]"
language: "rust"
revision: "[Requirements and repository revision this was drawn from]"
tags: [design, rust, type-anchored, spec]
---

# Type-Anchored Spec: [Capability]

## At a Glance

[State the strongest compile-time guarantee this spec layer provides, which
spec violations become compiler errors, and the main residual risk that remains
a runtime or test concern.]

## Spec Inputs

- Representative scenario: [initiating actor, ordered steps, observable outcome]
- Business rules anchored here:
  - Always Do: [rule]
  - Never Do: [rule]
- Verification oracle: [integration or end-to-end evidence retained alongside type checks]
- Approved boundary: [sealed, open, or module-scoped]

## Anchor Map

| Business rule | Anchor mechanism | Rust construct | Spec violation signal |
|---|---|---|---|
| [rule text] | Typestate / Sealed trait / Newtype / Error enum | [type or trait name] | Compile error / Test failure |

## State Machine

### State Tokens

```rust
// Proposed — not as-built.
// SPEC: [capability] must traverse states in this order.
pub struct [StateA];
pub struct [StateB];
pub struct [StateC];
```

### Domain Type

```rust
// Proposed — not as-built.
pub struct [DomainType]<State> {
    pub id: String,
    // [field]: [invariant comment — e.g. "Always: atomic units; Never: float"]
    _state: std::marker::PhantomData<State>,
}
```

### Consuming Transitions

```rust
// Proposed — not as-built.
impl [DomainType]<[StateA]> {
    /// SPEC: [rule that this transition enforces]
    pub fn [transition_name](self) -> [DomainType]<[StateB]> { … }
}

impl [DomainType]<[StateB]> {
    /// SPEC: [rule that this transition enforces]
    pub fn [transition_name](self) -> Result<[DomainType]<[StateC]>, [CapabilityError]> { … }
}
```

## Sealed Boundary

```rust
// Proposed — not as-built.
pub trait [CapabilityTrait]: private::Sealed {
    fn [operation](&self, …) -> Result<[Output], [CapabilityError]>;
}

mod private {
    pub trait Sealed {}
    impl Sealed for super::[ApprovedImpl] {}
    // Add new implementors here only with explicit spec change and human review.
}
```

Approved implementors: [list]

## Opaque Wrappers

```rust
// Proposed — not as-built.
/// SPEC: [invariant — e.g. "Always: cents; Never: float"]
pub struct [ValueType]([PrimitiveType]);

impl [ValueType] {
    pub fn new(value: [PrimitiveType]) -> Self { … }
    pub fn as_[unit](&self) -> [PrimitiveType] { self.0 }
}

/// SPEC: [sensitive value] must not appear in logs or error messages.
pub struct [SecretType](String);
impl std::fmt::Debug for [SecretType] {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str("<redacted>")
    }
}
```

## Domain Error Enum

```rust
// Proposed — not as-built.
// SPEC: All failure modes for [capability] are named here.
// Forbidden: unwrap(), expect() in spec-anchored modules.
#[derive(Debug)]
pub enum [CapabilityError] {
    [FailureVariant] { [context_fields] },
    [AnotherVariant],
}
```

## Agent Workflow Constraints

- Spec types live in `src/specs/[capability].rs`.
- Before modifying application code, map every markdown rule to a type in this file.
- `cargo check` must pass at each iteration; a compile error = spec violation.
- `cargo test` covers the integration oracle listed above.
- `unwrap()` / `expect()` are forbidden in `src/specs/` modules.
- Adding a sealed implementor requires modifying `mod private` — a human-visible diff.

## Verification Obligations

- Compile-error coverage: [list illegal transitions, sealed extensions, and type mismatches]
- Test coverage: [invalid inputs, boundary values, exhaustive error match, integration oracle]
- Human-owned checks: [runtime invariants, infrastructure, security review of sealed changes]

## Traceability

| Type or trait | Anchors | Source rule or scenario step |
|---|---|---|
| [TypeName] | [Always Do / Never Do / Ordered transition] | [Spec section or scenario ref] |

## Deferred Anchors

| Candidate rule | Why deferred | Trigger to promote |
|---|---|---|
| [rule] | [Insufficient evidence; not a compile-time concern] | [Concrete failure or design pressure] |
