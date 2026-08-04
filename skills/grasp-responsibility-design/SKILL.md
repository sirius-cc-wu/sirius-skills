---
name: grasp-responsibility-design
description: Assigns object responsibilities with GRASP. Use when deciding which object should create, know, coordinate, vary, mediate, or protect behavior in an object-oriented design.
---

# GRASP Responsibility Design

## Overview

GRASP patterns are decision tools for assigning responsibilities. Use them to keep behavior near the right information while controlling coupling, cohesion, and variation.

## When to Use

- You have use cases, SSDs, contracts, or domain concepts and need software object responsibilities.
- Multiple classes could plausibly perform the same behavior.
- Creation, coordination, variation, or dependency pressure is unclear.
- Do not use as a naming exercise after responsibilities have already been chosen.

## Language Adaptation

When the implementation language is known, also use [Software Design Language Adaptation](../software-design-language-adaptation/SKILL.md) and read only its matching language reference. Preserve the GRASP rationale while allowing a responsibility owner to become a native type, function, module, callable, or other appropriate construct rather than forcing a class.

## Workflow

1. **Start from a responsibility.** Phrase it as "Who should know..." or "Who should do..."
2. **Try Information Expert first.** Assign behavior to the class with the information needed to fulfill it.
3. **Apply Creator for object creation.** Prefer a creator that contains, aggregates, records, closely uses, or has initialization data for the created object.
4. **Choose a Controller for system events.** Use a facade controller for system-wide events or a use-case/session controller for scenario coordination.
5. **Check Low Coupling.** Reject assignments that create unnecessary dependency chains or knowledge of unstable details.
6. **Check High Cohesion.** Reject assignments that overload an object with unrelated work.
7. **Use Polymorphism for type-varying behavior.** Put alternatives behind a common interface rather than branching on type.
8. **Use Pure Fabrication when domain objects would become bloated or coupled.** Create a service-like object only to preserve cohesion and reuse.
9. **Use Indirection to mediate dependencies.** Insert an intermediate object when direct coupling creates design pressure.
10. **Use Protected Variations.** Identify likely variation points and stabilize access through interfaces or adapters.

## Decision Record Template

Before creating a new document, apply
[Artifact Selection Budget](../iterative-up-analysis-design/references/artifact-selection-budget.md).
Prefer recording a local responsibility choice in its realization or design
model when it does not need an independent decision lifecycle.

For a standalone Markdown file, follow
[Markdown Artifact Frontmatter](../iterative-up-analysis-design/references/markdown-artifact-frontmatter.md)
and [Readable Technical Artifacts](../iterative-up-analysis-design/references/readable-technical-artifacts.md),
then use this shape. When embedding the decision in an aggregate file, omit the
frontmatter and adjust heading levels.

```markdown
---
type: "Responsibility Decision"
title: "Responsibility: [Concise responsibility]"
description: "[One sentence naming the chosen owner and design reason]"
id: "[Stable decision ID when cross-referenced]"
responsibility: "[Who should know or do what]"
chosen_owner: "[Class or language-native construct]"
grasp_basis: ["[Expert | Creator | Controller | other GRASP principle]"]
status: "[proposed | accepted | superseded]"
tags: [design, grasp]
---

# Responsibility Decision: [Responsibility]

## Context and Consequence

- Problem: [why an owner must be chosen]
- Consequence: [what this assignment makes possible or protects]

## Candidates

- [Class]: [reason for/against]

## Rationale

- Coupling/cohesion impact: [impact]
- Variation point: [none or protected by interface/polymorphism]
```

## Red Flags

- A controller performs business rules instead of coordinating.
- A domain object knows about UI, persistence, infrastructure, or external APIs.
- Type checks replace polymorphic dispatch for stable variants.
- "Service" or "Manager" is chosen before evaluating Expert, Creator, and Controller.

## Verification

- [ ] Each non-trivial behavior has an explicit owner.
- [ ] Responsibility decisions cite at least one GRASP rationale.
- [ ] Controllers coordinate but do not absorb domain logic.
- [ ] Coupling and cohesion were checked for each major assignment.
- [ ] Variation points are protected by polymorphism, interfaces, adapters, or indirection.
- [ ] The decision explains its problem and consequence before comparing candidates.
- [ ] A standalone Markdown decision exposes identity, responsibility, chosen owner, GRASP basis, and lifecycle metadata in one frontmatter block.
