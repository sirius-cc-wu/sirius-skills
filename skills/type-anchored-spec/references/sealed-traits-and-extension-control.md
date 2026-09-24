# Sealed Traits and Extension Control

## Core Idea

A **sealed trait** is a public trait that can only be implemented for types
listed in a private `mod private` block inside the defining crate. External
crates — and agents writing new code — cannot add implementations without
modifying the sealed module, producing a deliberate, human-visible diff.

## Anatomy of a Sealed Trait

```rust
// Public trait visible to callers.
pub trait PaymentProcessor: private::Sealed {
    fn process(&self, payment: &Payment<Validated>) -> Result<Receipt, ProcessError>;
}

// Private module holds the sealing super-trait.
mod private {
    pub trait Sealed {}

    // Approved implementors must be listed here explicitly.
    impl Sealed for super::StripeProcessor {}
    // Adding `impl Sealed for CryptoProcessor {}` requires touching this file
    // — a change that triggers human code review.
}

pub struct StripeProcessor;

impl private::Sealed for StripeProcessor {}

impl PaymentProcessor for StripeProcessor {
    fn process(&self, payment: &Payment<Validated>) -> Result<Receipt, ProcessError> {
        // …
    }
}
```

## Why This Guards Agent Boundaries

An implementation agent that tries to add a new `CryptoProcessor` without
also updating `mod private` will receive a compile error:

```
error[E0277]: the trait bound `CryptoProcessor: private::Sealed` is not satisfied
```

The compiler prevents the extension. The agent is forced to modify the sealed
module — a change that must be reviewed by a human before it lands.

## Sealed Trait vs. Enum Dispatch

| Sealed trait | Closed enum |
|---|---|
| Allows separate struct types per implementor | All variants in one type |
| Extension requires `mod private` change | Extension requires adding an enum variant |
| Supports dynamic dispatch (`dyn Trait`) | Monomorphic; no `dyn` overhead |
| Preferred when implementors carry different data | Preferred when variants are value-like |

Use a closed enum when the set of variants is small, value-like, and you want
exhaustive match enforcement. Use a sealed trait when each implementor is a
distinct struct with its own fields and construction path.

## Opaque Wrappers

For sensitive values — secrets, PII, currency — use newtypes with private
fields and controlled constructors:

```rust
/// SPEC: Currency amounts must always be stored in atomic units (cents).
/// NEVER use f32 or f64 for monetary values.
pub struct CentsAmount(u64);

impl CentsAmount {
    pub fn from_cents(value: u64) -> Self {
        CentsAmount(value)
    }
    pub fn as_cents(&self) -> u64 {
        self.0
    }
}

/// SPEC: API secrets must never appear in logs or error messages.
#[derive(zeroize::ZeroizeOnDrop)]
pub struct ApiSecret(String);

impl ApiSecret {
    pub fn new(raw: String) -> Self {
        ApiSecret(raw)
    }
}

impl std::fmt::Debug for ApiSecret {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str("<redacted>")
    }
}
```

The private inner field prevents direct access. Any attempt to extract the raw
value must go through a controlled method — observable in code review.

## Domain Error Enums

All failure modes within a spec-anchored boundary must be explicit variants:

```rust
#[derive(Debug)]
pub enum ProcessError {
    InsufficientFunds { available: CentsAmount, required: CentsAmount },
    ProviderUnavailable { provider: &'static str },
    InvalidPaymentState,
    // No `unwrap()` / `expect()` in spec modules; every failure is named.
}
```

A closed enum forces exhaustive match expressions — the compiler flags any
unhandled failure mode.

## Checklist

- [ ] Every approved implementor is listed in `mod private`.
- [ ] No `mod private` `impl Sealed for` is added without a linked spec change.
- [ ] Sensitive values use private-field newtypes with redacted `Debug` impls.
- [ ] `CentsAmount` (or equivalent) never wraps a float.
- [ ] Domain `Error` enum has one variant per named failure mode.
- [ ] `unwrap()` and `expect()` are absent from spec-anchored modules.
