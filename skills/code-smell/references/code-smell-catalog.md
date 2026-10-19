# Code Smell Catalog

This catalog details implementation-level code smells, their concrete diagnostic symptoms, and their canonical Fowler and Kerievsky refactoring remedies. It distills the taxonomy established by Martin Fowler and Kent Beck (*Refactoring: Improving the Design of Existing Code*, 2nd ed.) and Joshua Kerievsky (*Refactoring to Patterns*).

Use this reference during **Gate 2 code reviews**, builder refactoring loops, or before executing [`behavior-preserving-refactoring`](../../behavior-preserving-refactoring/SKILL.md) on function- or class-level code.

---

## 1. Bloaters & Parameter Smells

Bloaters are code elements, methods, or parameter lists that have grown so large that they are hard to read, understand, and maintain.

| Smell | Diagnostic Symptoms & Code Patterns | Canonical Refactoring Remedy |
| :--- | :--- | :--- |
| **Long Function / Method** | - A single function exceeds 30–50 lines of logic.<br>- Multiple distinct stages separated by whitespace comments (`// 1. Parse`, `// 2. Validate`, `// 3. Save`).<br>- High cyclomatic complexity with nested loops or branches. | **Extract Function**:<br>Extract cohesive blocks into small, well-named helper functions named after *what* they do, not *how* they do it. |
| **Long Parameter List** | - A function accepts 4 or more positional arguments.<br>- Call sites are difficult to read and error-prone (e.g., passing 3 consecutive strings or booleans).<br>- Parameters change together across multiple functions. | **Introduce Parameter Object / Combine Functions into Class**:<br>Bundle clumped parameters into a typed options struct or object. Replace positional args with named fields. |
| **Primitive Obsession** | - Using primitive types (`string`, `number`, `boolean`, `tuple`) to model domain concepts with specific rules (e.g., currency, phone numbers, email addresses, coordinates, raw status codes).<br>- Repeated validation checks scattered across call sites. | **Replace Primitive with Value Object / Branded Type**:<br>Wrap the primitive in a dedicated type with private constructor or boundary validation parser (e.g., `zod` schema or Rust newtype). |
| **Data Clumps** | - The same 3–4 fields (e.g., `startDate`, `endDate`, `timezone` or `street`, `city`, `zipCode`) appear together across multiple classes, structs, or method signatures. | **Extract Class / Value Object**:<br>Group the clumped data into a standalone class or struct. Move operations that act on that data onto the new object. |

---

## 2. Couplers & Envy

Couplers describe excessive or misdirected coupling between classes or functions, hindering independent modification.

| Smell | Diagnostic Symptoms & Code Patterns | Canonical Refactoring Remedy |
| :--- | :--- | :--- |
| **Feature Envy** | - A function or method accesses the fields or getters of another object more than its own.<br>- Calculation logic lives in a service or caller while the required data lives in a passive data holder. | **Move Function / Move Method**:<br>Move the logic directly onto the object that owns the data it manipulates. |
| **Inappropriate Intimacy** | - Two modules or classes spend too much time delving into each other's private or internal structures.<br>- Subclasses accessing internal fields of superclasses directly. | **Move Function / Hide Delegate / Extract Interface**:<br>Decouple interactions behind explicit public methods or introduce a shared interface. |
| **Message Chains (Law of Demeter Violation)** | - Client code navigates long trains of getters or property accesses: `a.getB().getC().getD().doSomething()`.<br>- Tightly couples the client to the entire navigation structure between objects. | **Hide Delegate / Extract Method on Intermediate**:<br>Ask `a` to perform the operation directly (`a.doSomething()`), delegating internally rather than exposing the intermediary chain. |

---

## 3. Control-Flow & Branching Smells

Smells where control flow is overly complex, nested, or procedural instead of polymorphic or declarative.

| Smell | Diagnostic Symptoms & Code Patterns | Canonical Refactoring Remedy |
| :--- | :--- | :--- |
| **Switch / Conditional Obsession** | - Complex `switch` or cascading `if/else` ladders checking type tags, status codes, or enums.<br>- The same conditional switch repeated across multiple files or methods. | **Replace Conditional with Polymorphism / Discriminated Union**:<br>Move variant behavior into polymorphic implementations or exhaustive pattern matchers. |
| **Deep Nesting (Arrow Anti-Pattern)** | - Code indented 4–6 levels deep with nested `if`, `for`, `try/catch` blocks.<br>- Difficult to scan happy path due to defensive checks wrapping the main logic. | **Replace Nested Conditional with Guard Clauses**:<br>Invert checks and return or throw early. Keep the happy path flat and unindented. |
| **Temporary Field** | - Fields on an object that are only set and used in certain edge-case scenarios or specific methods, remaining `null`/`None`/`undefined` the rest of the time. | **Extract Class / Introduce Null Object / Typestate**:<br>Extract the temporary fields and their dependent operations into a separate specialized object or state. |

---

## 4. Dispensables & Redundancy

Dispensables are pointless code elements whose removal makes the codebase cleaner, smaller, and easier to understand.

| Smell | Diagnostic Symptoms & Code Patterns | Canonical Refactoring Remedy |
| :--- | :--- | :--- |
| **Dead Code / Zombie Code** | - Unused variables, uncalled private methods, commented-out code blocks, or unreachable branches.<br>- Backwards-compatibility shims that no longer have external consumers. | **Delete Unused Code**:<br>Remove the dead code completely. Rely on version control history rather than leaving dead scaffolding in source files. |
| **Speculative Generality** | - Abstract classes, generics, configuration flags, or hooks added for "future requirements" that do not yet exist.<br>- Adds indirection and cognitive load without delivering value today. | **Collapse Hierarchy / Inline Function / Remove Flag**:<br>Delete the unused abstractions and configuration knobs. Implement only what is required now. |
| **Comments as Deodorant** | - Long narrative comments explaining *what* dense, poorly written, or convoluted code is doing.<br>- Comments that duplicate the code or drift out of date. | **Extract Function / Rename Variable**:<br>Refactor the code so it is self-documenting through clear names and small functions. Keep comments only for non-obvious *why* (intent or constraints). |
| **Loose Casting & Type Workarounds** | - Frequent use of `as unknown as T`, `any`, non-null assertions (`!`), or silent fallback defaults to paper over unclear data shapes. | **Type-System Discipline / Parse at Boundary**:<br>Replace unchecked casts with runtime schema parsing or discriminated union guards. |
