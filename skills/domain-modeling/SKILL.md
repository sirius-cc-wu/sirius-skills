---
name: domain-modeling
description: Builds conceptual domain models from requirements. Use when discovering business concepts, associations, attributes, vocabulary, and domain rules before software class or database design.
---

# Domain Modeling

## Overview

A domain model visualizes real-world conceptual classes in the problem domain. It is not a software class diagram, persistence model, or implementation plan.

## When to Use

- Use cases mention business entities, events, transactions, roles, places, or policies.
- The team needs shared vocabulary before design.
- Requirements contain noun phrases and rules that need clarification.
- Do not use to decide controllers, services, methods, packages, or database tables.

## Workflow

1. **Mine candidate concepts.** Review use cases, glossary terms, business rules, and event descriptions.
2. **Classify concepts.** Look for transactions, line items, roles, catalogs, descriptions/specifications, places, containers, policies, and external systems.
3. **Keep concepts conceptual.** Include `Sale`, `Payment`, or `ProductSpecification`; exclude `SaleRepository`, `PaymentService`, and UI classes.
4. **Add essential associations.** Include relationships needed to understand requirements, especially whole-part, recording, role, and transaction relationships.
5. **Name associations with meaning.** Prefer domain language over vague verbs like "has" when the relationship matters.
6. **Add attributes only when simple.** Attributes should be primitive or value-like facts; promote complex things to concepts.
7. **Apply description classes.** When an item has stable descriptive data shared by many instances, separate the item from its specification or description.
8. **Update from contracts and design discoveries.** Revise the domain model when later artifacts reveal missing concepts.

## Output Template

Before creating a new document, apply
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
Prefer refining an existing domain model or aggregate feature artifact when it
already owns the vocabulary.

For a standalone Markdown file, follow
[Markdown Artifact Frontmatter](../plan-up-iterations/references/markdown-artifact-frontmatter.md)
and [Readable Technical Artifacts](../plan-up-iterations/references/readable-technical-artifacts.md),
then use this shape. When embedding the model in an aggregate file, omit the
frontmatter and adjust heading levels.

```markdown
---
type: "Domain Model"
title: "[Domain or feature] Domain Model"
description: "[One sentence naming the concepts and scope represented]"
id: "[Stable model ID when cross-referenced]"
status: "[draft | active | retired]"
tags: [analysis, domain-model]
---

# Domain Model: [Domain or Feature]

## Model Purpose

[Explain the real-world scope, the questions this vocabulary resolves, and
what the model intentionally does not represent.]

## Conceptual Classes

- [Concept]: [responsibility in the domain vocabulary]

## Associations

- [Concept A] [relationship] [Concept B] ([multiplicity if known])

## Attributes

- [Concept].[attribute]: [meaning]

## Rules and Questions

- [Domain invariant or unresolved vocabulary issue]
```

## Red Flags

- Classes are named after software layers, tables, pages, commands, or DTOs.
- Attributes hide important domain concepts, such as treating `customerAddress` as a string when addresses have rules.
- Multiplicity is guessed with false precision.
- The model includes methods or implementation visibility.

## Verification

- [ ] Concepts are problem-domain objects, not software artifacts.
- [ ] Associations explain requirements-relevant relationships.
- [ ] Attributes are simple facts and not disguised concepts.
- [ ] Names match stakeholder vocabulary.
- [ ] The model covers the nouns and rules in the important use cases.
- [ ] The model purpose orients readers before the concept inventory.
- [ ] A standalone Markdown domain model exposes identity, summary, and lifecycle metadata in one frontmatter block.
