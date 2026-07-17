# Python Design Adaptation

Assign responsibilities using the lightest Python construct that makes ownership and collaboration clear. A responsibility owner may be an object, function, callable, closure, or cohesive module; it need not be a class.

## Responsibility Mapping

| Design intent | Idiomatic Python mapping |
| --- | --- |
| Information Expert | A method beside the state it needs, or a module function when no object is the natural expert. |
| Creator | Direct construction, a named class method, or a factory function where initialization data and lifecycle already reside. |
| Controller | A thin endpoint, command handler, CLI function, or use-case object that translates input and coordinates collaborators. |
| Polymorphism | Compatible behavior through duck typing, documented with a `Protocol` when static checking adds value. |
| Pure Fabrication | A module, application service, repository adapter, mapper, or gateway that protects domain cohesion. |
| Protected Variations | A consumer-owned protocol, callable, adapter, or module boundary at a real source of change. |

- Prefer plain data and direct control flow until identity, mutable state, lifecycle, substitution, or collaboration justifies an object.
- Pass collaborators explicitly; avoid ambient globals, service locators, and framework objects in domain code.
- Add type annotations at important boundaries, recognizing that they document design rather than enforce runtime architecture.

## Choosing Constructs

| Construct | Use when |
| --- | --- |
| Class | Identity, invariants, encapsulated mutable state, lifecycle, or several cohesive operations matter. |
| `@dataclass` | A state-centric value or entity benefits from generated initialization and equality behavior. |
| `Enum` | A closed symbolic set needs identity and named members. |
| `Protocol` | A consumer-facing structural contract benefits from static checking across implementations. |
| ABC | Runtime nominal membership, shared implementation, or controlled subclassing is required. |
| Module | Stateless responsibilities form a cohesive component, namespace, or facade. |
| Function or callable | One operation owns the behavior and required state is explicit or locally captured. |
| `TypedDict` or `NamedTuple` | Boundary-shaped data has no independent behavior or lifecycle. |

- Define protocols near consumers; implementations normally need not inherit from them.
- Use an ABC only when nominal runtime behavior or shared mechanics are intentional.
- Avoid one protocol or ABC per implementation and do not wrap a simple function in a strategy class.

## Collaboration and Lifecycle

- Inject collaborators through parameters or constructors. Use defaults only for stable, side-effect-free policies.
- Call constructors directly when creation is simple; use a named `@classmethod` for alternate invariant-preserving construction.
- Use a factory function for parsing, implementation selection, caching, or multi-step construction.
- Use a factory object only when creation needs injected state, interchangeable policy, or a coherent product family.
- Keep wiring in a composition root such as `main()` or an application factory.
- Own resources with `with` or `async with`; use context managers for composed lifecycles and transactions.

## Errors and Concurrency

- Use specific exceptions for failures that prevent an operation; use `None` or an explicit domain value for ordinary absence.
- Translate infrastructure exceptions at adapter or application boundaries and preserve causes with `raise ... from error`.
- Prefer EAFP around the operation that may fail; avoid broad pre-checks that duplicate work or introduce races.
- Do not introduce `Result` wrappers everywhere unless that is an intentional repository convention.
- Make code async because collaboration performs asynchronous I/O, not because domain objects need async methods.
- Prefer structured concurrency for related tasks, make cancellation cleanup explicit, and give background tasks an owner and shutdown path.
- Minimize shared mutation and make lock, transaction, and task ownership visible.

## Pattern Adaptations

| Pattern | Prefer in Python |
| --- | --- |
| Adapter | A translating function first; a wrapper object when state, lifecycle, or several operations must be adapted. |
| Factory | A constructor, named constructor, or factory function before a factory class. |
| Strategy | An injected callable; promote to a protocol-backed object when policy has state or several operations. |
| Composite | A shared protocol plus ordinary collections; add a container class when group invariants require it. |
| Observer | Callbacks for local synchronous notification; queues or event buses only for real fan-out or boundary decoupling. |
| Abstract Factory | Related creator callables or a stateful object only when product choices must vary together. |

## UML and Boundaries

- Show classes only when identity, state, lifecycle, or received messages makes them design-significant.
- Use stereotypes such as `<<dataclass>>`, `<<enum>>`, `<<protocol>>`, `<<ABC>>`, and `<<module>>`.
- Show structural protocol conformance without implying implementation inheritance.
- Use associations for retained references, dependencies for parameters or calls, and composition only for owned lifetime.
- Treat `_internal` as a convention rather than claiming Java-like protected or enforced private access.
- Include functions and modules as sequence participants; label awaited calls and meaningful exception or cancellation paths.
- Organize packages by domain capability, expose intentional names through `__init__.py`, and keep import-time work side-effect-free.
- Resolve import cycles by moving responsibilities to their natural owner rather than relying on scattered late imports.

## Red Flags

- `Manager`, `Processor`, or `Service` owns rules that belong with an Information Expert.
- Dataclasses are passive bags while a parallel service layer manipulates all behavior.
- Every implementation has a matching `Protocol` or ABC despite no substitution boundary.
- Getter/setter pairs, builders, DTO duplication, and nominal interfaces reproduce Java ceremony.
- Mutable module globals, singleton instances, or import-time registries hide collaborators and test state.
- Broad exception handling suppresses programming errors, partial failures, or cancellation.
