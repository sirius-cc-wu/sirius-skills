# TypeScript Design Adaptation

Preserve responsibility decisions while choosing TypeScript's smallest suitable runtime construct. Types and interfaces can document boundaries, but many disappear at runtime and cannot perform validation or collaboration.

## Responsibility Mapping

| Design intent | Idiomatic TypeScript mapping |
| --- | --- |
| Information Expert | A class or object method beside its state, or a pure function over an explicit value. |
| Creator | A constructor for simple invariants; a factory function for validation, variant selection, or dependency acquisition. |
| Controller | A thin route handler, command handler, or application function that coordinates collaborators. |
| Polymorphism | A discriminated union for closed variants; a structural interface or function type for open extension. |
| Pure Fabrication | A cohesive module or capability-named service for persistence, transport, clocks, IDs, or external APIs. |
| Protected Variations | A narrow consumer-owned type plus runtime validation at unstable external boundaries. |

- A responsibility owner may be a function, closure, plain object, class, or module.
- Use explicit parameters for local collaborators, fields for shared lifecycle, and closures for small scoped policies.
- Treat direct imports as dependencies; do not use mutable module singletons as hidden injection.

## Choosing Constructs

| Construct | Use when |
| --- | --- |
| `interface` | Consumers need an open structural capability contract. |
| Class | Identity, encapsulated mutable state, invariants, or lifecycle spans several operations. |
| Discriminated union | Variants are closed and behavior benefits from exhaustive checking. |
| Plain object | Data and a small behavior surface need no prototype identity or hidden lifecycle. |
| Function or closure | One operation owns the responsibility and state is explicit or locally captured. |
| Module | Related types and operations form a cohesive capability with an intentional export surface. |
| Abstract class | Implementations genuinely share stateful mechanics, not merely signatures. |

- Structural compatibility is implicit; do not create an interface solely to mirror each class.
- Brand or validate identifiers and values when accidental structural compatibility would violate domain meaning.
- Prefer literal unions over enums unless a runtime enum object is required.

## Static and Runtime Boundaries

- Interfaces, type aliases, generic parameters, overload signatures, and `import type` disappear after compilation.
- Classes, functions, objects, symbols, and ordinary enums are runtime values.
- Accept untrusted input as `unknown`, validate it at HTTP, storage, message, plugin, and environment boundaries, then return domain-safe values.
- Do not treat a type assertion, `private`, or `readonly` as runtime validation or deep immutability.
- Use `instanceof` only when prototype identity is controlled; otherwise dispatch on validated discriminants.

## Construction, Async, and Resources

- Keep constructors synchronous and unsurprising; use factory functions for async creation, parsing, caching, or multi-step assembly.
- Prefer an options object over a builder unless construction is genuinely staged or order-sensitive.
- Model asynchronous collaborators with `Promise<T>` and pass `AbortSignal` through cancellable operations.
- Use discriminated results for expected domain alternatives; use thrown errors for failures that should unwind the operation.
- Choose one error convention per boundary and translate infrastructure errors there.
- Make resource ownership explicit with `try/finally`, `using` or `await using` when supported, or a clearly owned `dispose` or `close` operation.
- Define callback and event ordering, awaiting, cancellation, backpressure, listener cleanup, and failure propagation.

## Pattern Adaptations

| Pattern | Prefer in TypeScript |
| --- | --- |
| Adapter | A wrapper function or object; use a class when identity or lifecycle matters. |
| Factory | A named function; retain a factory object only when configuration or a family of creations must be stored. |
| Strategy | A function value; use an interface or object for several related operations or stateful policy. |
| Composite | A recursive discriminated union plus functions; use classes for a uniform mutable protocol. |
| Observer | Typed callbacks, an explicit listener set, `EventTarget`, or an async iterable selected by delivery semantics. |
| Abstract Factory | An object of related constructors or functions conforming to one structural interface. |

## UML and Boundaries

- Mark runtime classes normally and use `<<interface>>`, `<<type>>`, `<<union>>`, and `<<module>>` for other forms.
- Mark erased declarations as compile-time when ambiguity matters; they cannot be runtime sequence participants.
- Show implicit conformance as structural rather than implying an `implements` declaration.
- Represent discriminated unions with their variants and discriminant; attach behavior to the owning function or module.
- Distinguish type-only dependencies from runtime imports, retained references, construction, and calls.
- Label asynchronous messages and show cancellation, retries, parallel work, and failure paths when behavior depends on them.
- Group modules by domain capability, keep helpers unexported, and use barrel files only as intentional public APIs.
- Treat import cycles as a responsibility or boundary problem rather than a tooling inconvenience.

## Red Flags

- Classes are DTOs with getters and setters, or functions are wrapped in classes only to resemble UML.
- Every class has a paired interface despite no substitution boundary.
- Erased types are treated as runtime validators after JSON parsing or message receipt.
- `as`, `any`, or non-null assertions bypass boundary validation or invariant construction.
- A dependency-injection container, mutable singleton, or closure conceals lifecycle and collaborators.
- Observer APIs omit ordering, cancellation, cleanup, backpressure, or error semantics.
