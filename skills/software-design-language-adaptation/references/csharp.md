# C# Design Adaptation

Use modern C# constructs to preserve responsibility, cohesion, dependency direction, and variation without creating an interface, service, or project for every design element.

## Responsibility Mapping

| Design intent | Idiomatic C# mapping |
| --- | --- |
| Information Expert | An instance method on the entity, value object, or aggregate holding the required facts and invariants. |
| Creator | A constructor, named static factory, aggregate method, or composition-root expression with initialization data. |
| Controller | An endpoint, application service, or use-case handler that translates input and coordinates collaborators. |
| Polymorphism | An interface or abstract base for open variants; a closed hierarchy or enum plus pattern matching for closed variants. |
| Pure Fabrication | A capability-named application or infrastructure service for work that would pollute domain objects. |
| Protected Variations | A narrow interface or delegate at an unstable process, persistence, network, clock, or vendor boundary. |

- Retain collaborators in private `readonly` fields and pass temporary collaborators as parameters.
- Prefer composition and sealed concrete implementations unless subtype extension is an explicit variation point.
- Name collaborators by domain capability rather than generic roles such as `Manager` or `Helper`.

## Choosing Constructs

| Construct | Use when |
| --- | --- |
| Class | An entity, aggregate, stateful collaborator, or resource owner requires reference identity. |
| `sealed class` | A concrete collaborator does not intentionally support inheritance. |
| `record class` | An immutable message, snapshot, or value-like reference needs member-wise equality. |
| `readonly record struct` | A small immutable domain value has appropriate copying, default, and equality semantics. |
| Interface | A real capability, port, or open variation is shared by multiple implementations. |
| Delegate or `Func<...>` | A local one-operation strategy, callback, or factory has a complete function-shaped contract. |
| Abstract class | Related types genuinely share state, invariants, or protected implementation mechanics. |
| Namespace | Cohesive naming and collision avoidance, not deployment or access control. |

- Enable nullable reference types and represent ordinary absence explicitly as `T?`.
- Use `required` and `init` for DTO or configuration assembly, not as substitutes for invariant validation.
- Remember that records and `with` use shallow copying; mutable members remain shared and mutable.

## Construction and Dependency Injection

- Declare mandatory collaborators in constructors; avoid property injection, ambient state, and service location.
- Compose small applications directly in `Program` or another composition root.
- Use the built-in container when hosting, scopes, disposal, or framework integration justifies it.
- Keep `IServiceProvider`, registrations, and scopes at the composition boundary.
- Inject stable concrete collaborators directly; introduce an interface only for actual variation or dependency inversion.
- Use a delegate, local function, or named factory for variable creation; do not wrap a trivial constructor.
- Since constructors cannot be async, expose `CreateAsync` or an explicit initialization operation when needed.
- The creator owns disposal; consumers do not dispose injected dependencies, and containers dispose what they create.

## Async, Errors, and Resources

- Return `Task` or `Task<T>` by default, suffix public asynchronous operations with `Async`, and propagate `CancellationToken`.
- Use `async void` only for required event-handler signatures; avoid `.Result`, `.Wait()`, and unowned fire-and-forget work.
- Use `IAsyncEnumerable<T>` for pull-based streams and `Channel<T>` when buffering or backpressure is required.
- Represent expected rejection with result records, `Try...` APIs, or explicit alternatives; use exceptions for exceptional execution failures.
- Catch only to recover, compensate, add context, or translate at a boundary; preserve cancellation and stack traces.
- Scope `IDisposable` and `IAsyncDisposable` ownership with `using` and `await using`.
- Preserve postconditions under failure through atomic changes, transactions, or explicit compensation.

## Pattern Adaptations

| Pattern | Prefer in C# |
| --- | --- |
| Adapter | An extension method for pure conversion; a wrapper class for state, lifecycle, caching, or dependency inversion. |
| Factory | A constructor or named static factory first; a factory object for variable creation, lifetime ownership, or substantial setup. |
| Strategy | A delegate for one stateless operation; an interface for stateful policy, several members, or open implementations. |
| Composite | A common capability with recursive immutable children and controlled traversal behavior. |
| Observer | An `event` for synchronous local notification; an async stream, channel, or broker for other delivery semantics. |
| Abstract Factory | One cohesive family factory only when related product choices genuinely vary together. |

## UML and Boundaries

- Use stereotypes such as `<<record>>`, `<<record struct>>`, `<<readonly struct>>`, `<<interface>>`, and `<<delegate>>`.
- Show nullable types, generic constraints, significant `required` or `init` semantics, and C# visibility including `internal`.
- Draw associations only for retained navigation and composition only when the whole controls lifetime or disposal.
- Label asynchronous messages with `Async`, `await`, and cancellation; show creation and disposal when ownership matters.
- Map logical packages to cohesive namespaces and components to projects or assemblies; a namespace is not an assembly boundary.
- Keep project references acyclic and policy-directed. Let the executable host compose application policy with selected adapters.
- Make types `internal` by default and expose the smallest intentional public API.
- Split projects for cohesive capability, enforceable dependency direction, or independent deployment, versioning, or reuse, not per namespace.

## Red Flags

- Controllers contain business rules or constructors have unrelated dependency clusters.
- Every class has an interface, factories only wrap `new`, or domain code resolves from `IServiceProvider`.
- Records model mutable identity or mutable structs are used without value-semantics analysis.
- `.Result`, routine `async void`, swallowed cancellation, undisposed ownership, or event leaks obscure lifecycle.
- Namespaces are treated as assemblies or package boxes imply boundaries the project graph does not enforce.
