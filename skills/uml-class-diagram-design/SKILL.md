---
name: uml-class-diagram-design
description: Produces UML design class diagrams from object design work. Use when summarizing software classes, methods, attributes, associations, visibility, packages, and navigability after use-case realization.
---

# UML Class Diagram Design

## Overview

A design class diagram summarizes software classes discovered during object design. It is an implementation-facing model, unlike the conceptual domain model.

## When to Use

- Use-case realizations have discovered classes, methods, and relationships.
- You need a concise design model for implementation or review.
- Package boundaries, visibility, navigability, or interfaces must be clarified.
- Do not use as the first requirements artifact or as a database ERD substitute.

## Language Adaptation

When the implementation language is known, also use [Software Design Language Adaptation](../software-design-language-adaptation/SKILL.md) and read only its matching language reference. Represent the target language's actual types, functions, modules, variation mechanisms, visibility, and ownership semantics instead of mapping every design element to a class or interface.

## Workflow

1. **Start from realized collaborations.** Add classes and operations that appeared in interaction diagrams.
2. **Separate domain and software concerns.** Domain-inspired names are fine; implementation responsibilities must be explicit.
3. **Add operations from messages.** If an object receives a message, the class likely needs a corresponding operation.
4. **Add attributes cautiously.** Include attributes needed for responsibilities, not every data field imaginable.
5. **Show associations required for navigation.** Add links when one object must know or send messages to another.
6. **Set multiplicity where known.** Avoid false precision when requirements do not establish cardinality.
7. **Use visibility deliberately.** Public operations form the collaboration surface; keep internals private or protected.
8. **Represent interfaces and abstract classes at variation points.** Align them with Protected Variations and Polymorphism.
9. **Organize packages.** Group by cohesive responsibility and dependency direction, not arbitrary technical layers alone.
10. **Reconcile with code constraints.** Adapt notation to the implementation language while preserving design intent.

## Output Template

Before creating a new document, apply
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
Prefer updating the canonical design model or embedding a local class view in
its owning feature artifact when either is sufficient.

For a standalone Markdown file, follow
[Markdown Artifact Frontmatter](../iterative-up-analysis-design/references/markdown-artifact-frontmatter.md)
and [Readable Technical Artifacts](../iterative-up-analysis-design/references/readable-technical-artifacts.md),
then use this shape. When embedding the design model in an aggregate file, omit
the frontmatter and adjust heading levels.

```markdown
---
type: "Design Class Diagram"
title: "[System, area, or feature] Design Class Diagram"
description: "[One sentence summarizing the software design scope]"
id: "[Stable design-model ID when cross-referenced]"
status: "[draft | active | retired]"
tags: [design, class-diagram]
---

# Design Class Diagram: [System, Area, or Feature]

## Design Scope

[Explain the behavior or decisions summarized, the implementation boundary,
and what the diagram intentionally omits.]

## Classes

- [Class]
  - Responsibilities: [summary]
  - Operations: [operation(params): return]
  - Attributes: [attribute: type]

## Relationships

- [Class A] -> [Class B]: [reason/navigability/multiplicity]

## Interfaces or Abstract Types

- [Type]: [variation protected]

## Package Notes

- [Package]: [cohesive purpose]
```

## Red Flags

- The diagram is copied from the domain model with methods bolted on.
- Classes exist without responsibilities or received messages.
- Every association is bidirectional by default.
- Infrastructure dependencies point into domain objects unnecessarily.

## Verification

- [ ] Classes trace back to responsibilities or interactions.
- [ ] Operations correspond to required messages or public responsibilities.
- [ ] Associations show required knowledge/navigation.
- [ ] Interfaces or abstract types protect real variation points.
- [ ] The diagram distinguishes conceptual domain classes from software design classes.
- [ ] The design scope explains the diagram's purpose before the type inventory.
- [ ] A standalone Markdown design class diagram exposes identity, scope summary, and lifecycle metadata in one frontmatter block.
