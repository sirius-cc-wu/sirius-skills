---
name: software-design-language-adaptation
description: Adapts GRASP responsibilities, use-case realizations, design patterns, and UML to idiomatic Rust, Python, TypeScript, C#, or C++. Use when implementation-facing design must be mapped to one of these languages.
---

# Software Design Language Adaptation

## Overview

Preserve responsibility, collaboration, and variation decisions while expressing them with the target language's natural constructs. This is a translation layer between object design and implementation, not a reason to force every conceptual class or message into a software type or method.

## When to Use

- GRASP assignments or use-case realizations are being translated into implementation-facing designs.
- Design patterns need to be evaluated against native language mechanisms.
- UML classes, interfaces, packages, or messages need language-specific notation.
- Do not use during black-box requirements or conceptual domain modeling.

## Workflow

1. **Select one target reference.** Read only the reference for the implementation language:
   - [Rust](references/rust.md)
   - [Python](references/python.md)
   - [TypeScript](references/typescript.md)
   - [C#](references/csharp.md)
   - [C++](references/cpp.md)
2. **Preserve design intent.** Keep the responsibility, required collaboration, dependency direction, and variation force explicit.
3. **Choose the smallest native mechanism.** Consider values, functions, modules, algebraic variants, callables, and language protocols before creating class hierarchies.
4. **Account for runtime semantics.** Make ownership, lifetime, mutation, error, concurrency, cancellation, and resource behavior visible where the language requires it.
5. **Adapt diagrams.** Represent actual language constructs and runtime participants rather than relabeling everything as a class or object.
6. **Reconcile physical boundaries.** Treat logical packages as evidence, then apply repository governance before creating files, modules, projects, crates, or libraries.

## Boundaries

- Requirements and operation contracts remain language-neutral.
- Domain concepts do not automatically become implementation types.
- A GRASP responsibility may map to a type, method, function, module, closure, or other native construct.
- A pattern name records a resolved design force; it does not require the canonical class structure from another language.
- Repository governance remains authoritative for physical source boundaries and verification commands.

## Verification

- [ ] The selected construct has a language-specific justification.
- [ ] Ownership, lifecycle, errors, and concurrency are explicit where relevant.
- [ ] Polymorphism matches whether variation is open or closed and static or runtime-selected.
- [ ] Diagrams distinguish compile-time declarations from runtime collaborators.
- [ ] No class, interface, factory, or module exists only to preserve language-neutral diagram symmetry.
