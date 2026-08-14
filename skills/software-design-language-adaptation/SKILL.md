---
name: software-design-language-adaptation
description: Adapts language-neutral behavior, boundaries, state, responsibilities, collaborations, patterns, and diagrams to idiomatic Rust, Python, TypeScript, C#, or C++. Use when implementation-facing design must account for a target language's native data, interface, ownership, error, concurrency, lifecycle, or runtime semantics without forcing object-oriented structure.
---

# Software Design Language Adaptation

## Overview

Preserve approved behavior and design intent while expressing boundaries,
state, collaboration, variation, and lifecycle with the target language's
natural constructs. This is a general implementation-facing adaptation layer,
not a reason to force every concept into a class, type, method, or module.

## When to Use

- Language-neutral behavior, contracts, responsibilities, boundaries, state
  transitions, or collaborations need an implementation-facing shape.
- GRASP assignments or use-case realizations are being translated when an
  object-oriented route was deliberately selected.
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
2. **Preserve design intent.** Keep required behavior, invariants, boundaries,
   state transitions, collaboration, dependency direction, and variation
   forces explicit. Preserve responsibilities when they are part of the input.
3. **Choose the smallest native mechanism.** Consider values, functions, modules, algebraic variants, callables, and language protocols before creating class hierarchies.
4. **Account for runtime semantics.** Make ownership, lifetime, mutation, error, concurrency, cancellation, and resource behavior visible where the language requires it.
5. **Adapt diagrams.** Represent actual language constructs and runtime participants rather than relabeling everything as a class or object.
6. **Reconcile physical boundaries.** Treat logical packages as evidence, then apply repository governance before creating files, modules, projects, crates, or libraries.

## File Output

Before creating a new document, apply
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
Prefer merging implementation-facing guidance into the design artifact it
adapts when that artifact remains the clear owner.

When persisting a standalone Markdown adaptation note, follow
[Markdown Artifact Frontmatter](../iterative-risk-driven-development/references/markdown-artifact-frontmatter.md)
and use STE-style.
Use `type: "Implementation Design Adaptation"`, a `language` field with the
selected target, and identity, summary, lifecycle, and tags as appropriate.
When modifying another design artifact, merge the language metadata into that
file's existing frontmatter only if the file as a whole is language-specific;
otherwise keep the adaptation details in the body. Do not add a second
frontmatter block.

## Boundaries

- Requirements and operation contracts remain language-neutral; adaptation
  links to them rather than rewriting them around target-language constructs.
- Domain concepts do not automatically become implementation types.
- A responsibility or operation may map to a type, method, function, module,
  closure, process, task, data transformation, or other native construct.
- A pattern name records a resolved design force; it does not require the canonical class structure from another language.
- Repository governance remains authoritative for physical source boundaries and verification commands.

## Verification

- [ ] The selected construct has a language-specific justification.
- [ ] Approved behavior, invariants, and boundary semantics remain intact.
- [ ] Ownership, lifecycle, errors, and concurrency are explicit where relevant.
- [ ] Polymorphism matches whether variation is open or closed and static or runtime-selected.
- [ ] Diagrams distinguish compile-time declarations from runtime collaborators.
- [ ] No class, interface, factory, or module exists only to preserve language-neutral diagram symmetry.
- [ ] The adaptation explains the preserved design intent and important runtime consequence before language-specific detail.
- [ ] A standalone Markdown adaptation exposes its artifact type, target language, summary, and lifecycle metadata in one frontmatter block.
