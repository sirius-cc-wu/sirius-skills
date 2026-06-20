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

```markdown
## Design Class Diagram Notes

Classes:
- [Class]
  - Responsibilities: [summary]
  - Operations: [operation(params): return]
  - Attributes: [attribute: type]

Relationships:
- [Class A] -> [Class B]: [reason/navigability/multiplicity]

Interfaces or Abstract Types:
- [Type]: [variation protected]

Package Notes:
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

