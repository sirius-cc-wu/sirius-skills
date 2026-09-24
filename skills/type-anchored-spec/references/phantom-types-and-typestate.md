# Phantom Types and Typestate

## Core Idea

A **phantom type** is a type parameter that appears only in `PhantomData` — it
carries no runtime data but changes the type's identity from the compiler's
perspective. A **typestate** pattern uses distinct types (often zero-size
structs) as state tokens so that invalid transitions become compile errors.

## Anatomy of a Typestate

```rust
// State tokens — zero-size, carry no runtime data.
pub struct Initiated;
pub struct Validated;
pub struct Processed;

// The domain value parameterised by its state.
pub struct Payment<State> {
    pub id: String,
    pub amount_in_cents: u64,   // Never: f64 or f32 for currency.
    _state: std::marker::PhantomData<State>,
}
```

### Consuming Transitions

Transitions take `self` by value, consuming the current state token and
returning the next. The compiler guarantees no code can use the old state.

```rust
impl Payment<Initiated> {
    pub fn validate(self) -> Payment<Validated> {
        Payment {
            id: self.id,
            amount_in_cents: self.amount_in_cents,
            _state: std::marker::PhantomData,
        }
    }
}

impl Payment<Validated> {
    pub fn process(self) -> Payment<Processed> {
        Payment {
            id: self.id,
            amount_in_cents: self.amount_in_cents,
            _state: std::marker::PhantomData,
        }
    }
}
```

An agent (or developer) cannot call `process()` on a `Payment<Initiated>` —
the method simply does not exist on that type.

## Decision Criteria

| Use typestate when… | Use a private enum instead when… |
|---|---|
| Callers benefit from different method sets per state | All state-sensitive logic lives inside one module |
| Cross-module APIs must enforce ordering | The state space is large or dynamic |
| Compile-time proof of transition is worth added type params | Runtime state inspection is needed |
| States are few, stable, and distinguishable by capability | Storing heterogeneous states in a collection |

## Common Patterns

### Builder Typestate

Use separate `Builder<Incomplete>` and `Builder<Complete>` types to guarantee
a required field is set before `build()` is callable.

### Restricted Entry Points

Use a private constructor (`fn new_internal(…) -> Payment<Initiated>`) and
expose only a factory function that enforces entry-point invariants.

### Erased State for Storage

When heterogeneous states must be stored (e.g. in a `Vec`), define a sealed
trait `AnyPayment: private::Sealed` and implement it for each state type.
The collection holds `Box<dyn AnyPayment>` without exposing state tokens
externally.

## What Phantom Types Do Not Enforce

- **Runtime invariants** — the compiler checks types, not values. A
  `Payment<Validated>` may still hold an out-of-range `amount_in_cents`
  unless the constructor enforces it.
- **Async cancellation safety** — use `design-rust-lifecycles` for `.await`
  boundaries and `Drop` semantics.
- **Thread safety** — `PhantomData<State>` affects `Send`/`Sync` inference;
  verify bounds explicitly.
