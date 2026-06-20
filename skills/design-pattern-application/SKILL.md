---
name: design-pattern-application
description: Applies object design patterns judiciously. Use when creation, adaptation, algorithm variation, part-whole structure, event notification, or family-of-products variation creates design pressure.
---

# Design Pattern Application

## Overview

Design patterns are named solutions to recurring design forces. Apply them after identifying the force; do not paste patterns into a design because they are familiar.

## When to Use

- GRASP reveals coupling, cohesion, creation, or variation pressure.
- The design must adapt external APIs, select algorithms, compose recursive structures, notify dependents, or create related object families.
- You need a concise rationale for a pattern choice.
- Do not use to make a simple design look sophisticated.

## Workflow

1. **State the force.** Identify the concrete design problem: variation, creation, notification, adaptation, composition, or dependency direction.
2. **Try the simplest GRASP-consistent design.** Patterns should solve a pressure that the simple design cannot handle well.
3. **Choose a narrow pattern.**
   - Adapter: external or incompatible interface must look like a stable domain-facing interface.
   - Factory: creation is complex, variable, or would couple clients to concrete classes.
   - Strategy: interchangeable algorithms or policies vary independently from clients.
   - Composite: clients should treat individual and grouped objects uniformly.
   - Observer: dependents need notification without tight coupling to the subject.
   - Abstract Factory: families of related products must vary together.
4. **Define participants in project terms.** Name actual classes/interfaces, not generic pattern roles only.
5. **Check consequences.** Record benefits and costs: indirection, extra types, testability, runtime flexibility, and cognitive load.
6. **Integrate with UML.** Update interactions and class diagrams to show participants and dependencies.
7. **Stop when the force is resolved.** Avoid chaining patterns unless each one has a separate pressure.

## Decision Template

```markdown
## Pattern Decision: [Pattern]

Force:
- [Problem creating design pressure]

Participants:
- [Project type] as [pattern role]

Alternatives Considered:
- [Simpler option]: [why insufficient or acceptable]

Consequences:
- Benefits: [coupling/cohesion/variation impact]
- Costs: [indirection/complexity impact]
```

## Red Flags

- The pattern is selected before a force is stated.
- A factory only wraps a constructor with no creation complexity or variation.
- Strategy is used for behavior that will not vary.
- Observer hides important ordering, delivery, or error-handling requirements.
- Pattern names appear in class names where domain names would communicate better.

## Verification

- [ ] The pattern solves a named design force.
- [ ] Project-specific participants are identified.
- [ ] Simpler alternatives were considered.
- [ ] UML interactions/classes reflect the pattern accurately.
- [ ] Added indirection has a justified benefit.

