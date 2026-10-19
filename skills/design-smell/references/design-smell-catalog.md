# Design Smell Catalog

This catalog details the structural design smells, their concrete diagnostic symptoms, and their canonical architectural remedies. It distills the taxonomy established by Girish Suryanarayana, Ganesh Samarthyam, and Tushar Sharma (*Refactoring for Software Design Smells: Managing Technical Debt*).

Use this reference during **Gate 1 design reviews**, architectural triage, or when identifying structural pressures before [`behavior-preserving-refactoring`](../../behavior-preserving-refactoring/SKILL.md).

---

## 1. Abstraction Smells

Abstraction smells arise when an abstraction is missing, poorly named, takes on multiple roles, or duplicates concepts.

| Smell | Diagnostic Symptoms & Code Patterns | Canonical Architectural Remedy |
| :--- | :--- | :--- |
| **Missing Abstraction** | - Primitive obsession: raw strings, numbers, or boolean tuples used for complex domain concepts (e.g., passing `(ip, port, timeout)` instead of `SocketEndpoint`).<br>- Repeated parallel arrays or dictionaries.<br>- Scattered validation logic checking data shapes. | **Extract Value Object / Type-Anchored Spec**:<br>Wrap data in an authoritative domain type or newtype. Parse at the boundary once; rely on compiler type guarantees inside. |
| **Imperfect Abstraction** | - An abstraction exposes operations that don't match its conceptual responsibility.<br>- Calling code must perform manual preconditions or compensating work to use the abstraction.<br>- The name implies one concept, but its public API handles unrelated operations. | **Interface Segregation / Realign Responsibilities**:<br>Extract mismatched methods to a separate collaborator or adapter. Narrow the abstraction so operations directly fulfill its named role. |
| **Multifaceted Abstraction** | - A single component, class, or module has multiple unrelated reasons to change (SRP violation).<br>- High fan-out: imports dozens of disparate packages (persistence, UI, formatting, domain logic).<br>- Mixed levels of abstraction (high-level orchestration mingled with raw bytes parsing). | **Decompose by Architectural Layer / Responsibility**:<br>Separate orchestration from execution. Extract pure domain rules into pure functions; push I/O, persistence, and formatting into dedicated edge adapters. |
| **Duplicate Abstraction** | - Multiple distinct types or modules representing the same domain entity with slightly different names or shapes.<br>- Parallel model hierarchies across modules with repetitive mapping glue. | **Unify Canonical Model / Introduce Shared Kernel**:<br>Establish one authoritative model type in the owning bounded context; deprecate and eliminate duplicate representations. |

---

## 2. Encapsulation Smells

Encapsulation smells occur when an abstraction fails to hide its implementation secrets, internal state, or variation mechanics from client code.

| Smell | Diagnostic Symptoms & Code Patterns | Canonical Architectural Remedy |
| :--- | :--- | :--- |
| **Leaky Encapsulation** | - Returning direct mutable references or internal collection instances that callers modify.<br>- Exposing database record shapes, internal locks, or transport DTOs directly through public module boundaries.<br>- Callers must know internal sequencing or lock acquisition order. | **Encapsulate Boundary & Return Read-Only Projections**:<br>Return immutable snapshots, views, or domain types. Hide locks behind transactional methods or single-writer actor mailboxes. |
| **Missing Encapsulation** | - Data structures with all public fields and zero behavior, manipulated by procedural functions scattered across external packages.<br>- Business rules duplicated across multiple callers because the data holder cannot enforce its own invariants. | **Colocate State with Invariant Enforcement**:<br>Encapsulate state behind constructors and methods that preserve domain invariants. Restrict field visibility to package-private or private. |
| **Unexploited Encapsulation** | - Client code uses `switch` or `if/else` checks on type tags, string names, or enums to decide how to handle an object.<br>- Adding a new variant requires hunting down and updating conditionals across multiple files. | **Polymorphic Dispatch / Discriminated Union Dispatch**:<br>Move behavior into the polymorphic abstraction or centralize variant exhaustion behind a single typed pattern match. |

---

## 3. Modularization Smells

Modularization smells occur when code is broken into packages or modules that have improper cohesion, coupling, or dependency topology.

| Smell | Diagnostic Symptoms & Code Patterns | Canonical Architectural Remedy |
| :--- | :--- | :--- |
| **Broken Modularization** | - Data and the operations that modify it are placed in separate modules.<br>- Changes to one concept require simultaneous edits across multiple unrelated directories (Shotgun Surgery).<br>- Circular imports or bidirectional cross-module references. | **Realign Module Boundaries by Cohesion**:<br>Consolidate tightly coupled files into a single owning module. Group by functional cohesion (feature slice) rather than technical type (all controllers together, all models together). |
| **Cyclic Dependency** | - Module A imports B, and Module B (directly or transitively) imports A.<br>- Cannot test, compile, or reason about one module without loading the other.<br>- Tightly couples lifecycles and build graphs. | **Dependency Inversion (DIP) / Extract Shared Port**:<br>Define an interface/port in the caller's layer; implement it in the callee's adapter. Alternatively, extract the shared concept into an independent leaf module. |
| **Insufficient Modularization (God Module / Blob)** | - A single file or module exceeds 1,000+ lines, has massive fan-in and fan-out, and centralizes all logic.<br>- Acts as the "brain" while other modules are merely passive data holders.<br>- Git conflicts and merge churn are concentrated in this single file. | **Vertical Slice Decomposition**:<br>Break the God module into cohesive sub-components organized around discrete workflows, subdomains, or state transitions. Delegate orchestration to event dispatchers or pipelines. |
| **Hub-like Modularization** | - A single intermediary module is connected to nearly every other module in the system, acting as a tangled clearinghouse.<br>- Any change to any module causes the hub to recompile and ripple changes outward. | **Decouple via Domain Events or Ports & Adapters**:<br>Replace central hub mediator with publish-subscribe domain events, direct point-to-point abstractions, or clean layered boundaries. |

---

## 4. Hierarchy & Coupling Smells

Hierarchy smells appear when inheritance, trait extension, or layered abstraction hierarchies are misapplied, overly deep, or rebellious.

| Smell | Diagnostic Symptoms & Code Patterns | Canonical Architectural Remedy |
| :--- | :--- | :--- |
| **Speculative Hierarchy** | - Complex trait/interface hierarchies or abstract base classes created for hypothetical future extensions, with only a single concrete implementation.<br>- Excessive indirection where a concrete struct/function would be simpler and clearer. | **Collapse Hierarchy (Inline Abstraction)**:<br>Remove the abstract trait or base class. Program directly to the concrete implementation until a second distinct variation actually materializes. |
| **Deep Hierarchy** | - Nesting of wrappers, adapters, or inheritance classes exceeds 3–4 levels.<br>- Tracing a single method call requires jumping through 5 layers of empty pass-through methods (`AdapterA -> AdapterB -> Service -> Manager -> Impl`). | **Flatten Indirection / Minimize Reader Load**:<br>Eliminate pass-through wrapper layers. Direct callers straight to the underlying engine or use lightweight function composition. |
| **Rebellious Hierarchy** | - Subtypes throw `NotImplementedException`, return empty/dummy values, or violate the contract of the parent abstraction.<br>- Violates the Liskov Substitution Principle (LSP). | **Segregate Contracts / Favor Composition**:<br>Extract a narrower contract that only promises what the subtype can actually deliver. Replace inheritance with composition (hold the component as a field). |
| **Multipath Coupling** | - Multiple parallel paths exist between two components (e.g., importing a service directly AND listening to its events AND mutating its shared state via global config).<br>- Indeterminate ordering and race conditions during lifecycle startup/shutdown. | **Enforce Single Canonical Path**:<br>Eliminate redundant interaction channels. Route all communication through one explicit, typed port or message channel. |
