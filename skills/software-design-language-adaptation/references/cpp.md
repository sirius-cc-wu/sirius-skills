# C++ Design Adaptation

Adapt responsibilities to modern C++ without assuming every behavior requires a heap object or virtual interface. Prefer values, direct composition, deterministic lifetime, and compile-time constraints before indirection.

## Responsibility Mapping

| Design intent | Idiomatic C++ mapping |
| --- | --- |
| Information Expert | A member when behavior needs private state or preserves an invariant; otherwise a non-member function. |
| Creator | Direct construction in the owning aggregate; a named factory for validation, variable types, or resource acquisition. |
| Controller | A thin application object, command handler, or free function that coordinates collaborators. |
| Polymorphism | Templates, concepts, callables, `std::variant`, or virtual dispatch according to openness and binding time. |
| Pure Fabrication | A free function, namespace algorithm, repository, adapter, or application service that preserves cohesion. |
| Protected Variations | Concepts or templates for compile-time variation; a narrow interface or type erasure for runtime-open variation. |

- Assign behavior to the smallest cohesive value, class, free function, callable, or algorithm with the required information.
- Prefer free functions for symmetric multi-object operations, conversions, and behavior needing no privileged access.
- Avoid utility classes containing only static methods; use cohesive namespaces and functions.

## Choosing Constructs

| Construct | Use when |
| --- | --- |
| Value type | A quantity, identifier, validated concept, or entity benefits from value semantics. |
| `struct` | A transparent record or policy bundle has no hidden invariant requiring controlled construction. |
| `class` | Invariants, encapsulation, identity, or resource ownership require a controlled API. |
| `enum class` | A closed set of labels needs type-safe identity. |
| `std::variant` | Closed alternatives carry distinct state and exhaustive handling is valuable. |
| Template or concept | Reusable behavior varies at compile time and recompilation is acceptable. |
| Callable | One strategy or deferred operation varies without requiring an object hierarchy. |
| Virtual interface | Runtime-open substitution, ABI boundaries, plugins, or heterogeneous collections justify it. |

- Keep virtual interfaces narrow and behavior-oriented, with a virtual destructor when deletion through the base is possible.
- Do not create an interface for every class or use inheritance only for implementation reuse.
- Use namespaces for cohesive vocabulary and APIs.

## Ownership and Lifecycle

- Store by value when the containing object owns a collaborator and value semantics fit.
- Use `T&` for required non-owning collaborators and `T*` for nullable non-owning collaborators; document lifetimes.
- Use `std::span`, `std::string_view`, iterators, or ranges for borrowed views whose source outlives the use.
- Use `std::unique_ptr<T>` for exclusive heap ownership and transfer it by value.
- Use `std::shared_ptr<T>` only for genuine shared lifetime and `std::weak_ptr<T>` to break ownership cycles.
- Prefer the Rule of Zero and RAII wrappers for memory, files, locks, sockets, threads, and other resources.
- Do not expose naked owning pointers, manual `new` and `delete`, or throwing destructors.

## Construction, Errors, and Concurrency

- Let constructors establish invariants; use aggregates when all representable states are valid.
- Use named factories returning a value, `std::optional`, or a typed result when construction is descriptive, validated, or fallible.
- Add builders or abstract factories only for staged construction or variable product families.
- Establish a boundary-aware error policy: exceptions for exceptional propagation and typed results for expected failure.
- Use `std::expected<T, E>` when available and callers must inspect anticipated failure; avoid sentinel values and ignored status codes.
- Acquire resources before mutating state and state the required exception guarantee for important operations.
- Prefer scoped threads and cooperative cancellation; place synchronization with the state it protects.
- Specify callback and task lifetime, thread affinity, ordering, cancellation, backpressure, and failure behavior.

## Pattern Adaptations

| Pattern | Prefer in C++ |
| --- | --- |
| Adapter | A concrete wrapper, conversion function, or constrained overload; add a virtual boundary only for runtime-open adaptation. |
| Factory | Direct or named construction first; a function when selection, validation, caching, or resource acquisition creates pressure. |
| Strategy | A template policy, callable, lambda, or type-erased function; virtual strategy only for justified runtime substitution. |
| Composite | Value containment for stable trees; exclusive pointers plus a virtual node only for open heterogeneous behavior. |
| Observer | An explicit subscription token with defined disconnect, lifetime, ordering, threading, reentrancy, and error semantics. |
| Abstract Factory | A policy bundle of creators or a narrow runtime factory only when product families genuinely vary together. |

## UML and Boundaries

- Use stereotypes such as `<<value>>`, `<<enum>>`, `<<concept>>`, `<<template>>`, `<<free function>>`, and `<<module>>`.
- Show associations for stored collaborators and dependencies for temporary parameters or function calls.
- Use composition only for ownership by value or exclusive ownership; label links as owned, borrowed, nullable, shared, or view where relevant.
- Represent concepts as constraints and template bindings rather than inheritance hierarchies.
- Include namespace functions and value objects as sequence participants; show moves and ownership transfer when significant.
- Keep public headers self-contained and limited to intentional API; place non-template implementation and unstable dependencies in source files.
- Define templates where instantiation can see them and export only deliberate C++ module surfaces.
- Use Pimpl only for ABI stability or meaningful compile-time isolation, not as automatic encapsulation.
- Prevent cyclic includes and package dependencies instead of masking them with service locators or indiscriminate forward declarations.

## Red Flags

- Most domain objects are heap allocated and connected through raw or shared pointers.
- Every dependency is a virtual interface despite a closed, compile-time-known implementation set.
- Data is exposed through getters while business behavior accumulates in managers or services.
- Runtime type checks replace open polymorphism, or virtual dispatch obscures a simple closed `std::variant`.
- Inheritance provides code reuse where composition or an algorithm would be clearer.
- Public headers expose unstable implementation details, broad transitive includes, global mutable state, or implicit ownership.
