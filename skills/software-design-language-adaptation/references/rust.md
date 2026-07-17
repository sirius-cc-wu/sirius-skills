# Rust Design Adaptation

Preserve responsibilities and collaborations without translating classes literally. In Rust, a responsibility may belong to a struct, enum, trait, module, closure, associated function, or free function.

## Responsibility Mapping

| Design intent | Idiomatic Rust mapping |
| --- | --- |
| Information Expert | An `impl` method on the value owning the required state, or a free function when no value is the natural expert. |
| Creator | An associated function, validated conversion, builder, or composition-root factory with the initialization data. |
| Controller | A thin function or stateful struct that accepts a system event and delegates domain work. |
| Polymorphism | An enum for closed alternatives; a generic bound or trait object for open alternatives. |
| Pure Fabrication | A cohesive module, adapter type, or stateless function, not automatically a `Service` or `Manager`. |
| Protected Variations | A narrow trait, wrapper, channel, or module API at a demonstrated source of change. |

- Let receiver choice communicate responsibility: `&self` observes, `&mut self` mutates exclusively, and `self` consumes or transitions.
- Express collaborators as parameters, owned fields, generic bounds, or trait-object fields rather than hidden global access.
- Keep transport controllers thin; orchestration alone does not require a class-shaped struct.

## Choosing Constructs

| Construct | Use when |
| --- | --- |
| `struct` | State and invariants form one cohesive value or resource handle. |
| `enum` | Alternatives are closed, variants carry different data, or exhaustive matching is valuable. |
| Newtype | A primitive or external type needs domain meaning, validation, or a distinct capability. |
| `trait` | Multiple types must satisfy a behavioral contract at a real variation or dependency boundary. |
| Module | Related types and functions need cohesion, privacy, and an intentional public surface. |
| Free function | Behavior is stateless, symmetric across inputs, or has no natural receiver. |
| Closure or `Fn*` bound | One operation varies locally and a named strategy hierarchy would add noise. |

- Prefer concrete types and static dispatch first.
- Prefer an enum when runtime variation is closed and controlled by the current crate.
- Use `dyn Trait` for runtime-selected, heterogeneous, plugin-like, or configuration-selected implementations.
- Choose `&dyn Trait`, `Box<dyn Trait>`, or `Arc<dyn Trait + Send + Sync>` according to borrowing, ownership, and thread-sharing needs.

## Ownership and Lifecycle

- Store owned values for composition and stable aggregate state; borrow with `&T` or `&mut T` for temporary collaboration.
- Consume `self` when transferring a resource or encoding an irreversible state transition.
- Use `Box<T>` for unique heap ownership, `Rc<T>` for genuine single-thread sharing, and `Arc<T>` for cross-thread sharing.
- Add lifetimes only when a value must store a borrow; prefer owned boundary data when lifetimes would spread through unrelated APIs.
- Avoid bidirectional strong ownership and self-referential designs; prefer stable identifiers or redesigned navigation.
- Introduce locks and atomics only for truly shared state. Keep lock scopes short and do not hold blocking locks across I/O or `.await`.

## Construction, Errors, and Resources

- Use `new` for straightforward invariant-preserving creation and `TryFrom` or a `Result`-returning constructor for validation.
- Add a builder only for many optional inputs, staged configuration, or a meaningful terminal operation.
- Select concrete adapters at the composition root and inject only the capability required downstream.
- Model expected failures as `Result<T, E>` with meaningful error variants; use `Option<T>` only for absence.
- Translate infrastructure failures at boundaries and propagate with `?` without erasing useful context.
- Let RAII release resources. Add explicit `close`, `shutdown`, or `finish` when cleanup can fail or ordering matters.
- Prefer channels and owned message enums for coordination; make `Send` and `Sync` requirements explicit at thread boundaries.

## Pattern Adaptations

| Pattern | Prefer in Rust |
| --- | --- |
| Adapter | A wrapper or newtype implementing a domain-facing trait; a conversion function when adaptation is trivial. |
| Factory | A constructor, `TryFrom`, builder terminal method, or composition-root `match`. |
| Strategy | A generic bound, closure, enum, or trait object selected according to openness and runtime needs. |
| Composite | A recursive enum with owned child collections and `Box` only where recursion requires it. |
| Observer | Typed channels, event enums, or callbacks with explicit ordering, backpressure, delivery, and error policy. |
| Abstract Factory | A trait with associated product types or a configuration enum constructing a coherent family. |

## UML and Boundaries

- Use stereotypes such as `<<struct>>`, `<<enum>>`, `<<trait>>`, `<<module>>`, and `<<newtype>>`.
- Distinguish generic bounds from stored trait objects and show ownership-bearing field types when relevant.
- Use composition only for owned fields; show parameter-only use as a dependency and label `Rc` or `Arc` sharing.
- Include modules and free functions as sequence participants when they coordinate meaningful behavior.
- Annotate messages with ownership effects such as `&self`, `&mut self`, or consuming `self`, plus `Result` outcomes.
- Map packages to cohesive crates and modules, using private-by-default items and intentional re-exports.
- Keep tightly coupled types, helpers, and tests together; avoid one-module-per-type layouts and generic `utils` modules.

## Red Flags

- A conceptual class becomes a struct despite having no state, invariant, identity, or resource responsibility.
- Every collaborator becomes a trait or every alternative becomes `Box<dyn Trait>`.
- `Arc<Mutex<_>>`, `Rc<RefCell<_>>`, or repeated cloning hides unclear ownership or mutation responsibility.
- Stored borrows spread lifetime parameters through the architecture without a demonstrated need.
- Getter/setter APIs recreate mutable objects while controllers or managers absorb domain rules.
- UML promises inheritance, omits free functions or modules, or shows associations without ownership meaning.
