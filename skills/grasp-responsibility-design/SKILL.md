---
name: grasp-responsibility-design
description: Assigns software responsibilities with GRASP to classes or language-native modules, functions, tasks, values, adapters, and resource handles. Use when deciding which unit should know, create, coordinate, vary, mediate, supervise, or protect behavior while controlling coupling and cohesion.
---

# GRASP Responsibility Design

## Overview

GRASP patterns are decision tools for assigning software responsibilities. Use
them to keep behavior near the required information and capabilities while
controlling coupling, cohesion, coordination, and variation. A responsibility
owner may be a class, module, function, task, value, adapter, resource handle,
or composition root.

## When to Use

- You have scenarios, system events, contracts, recovered collaborations, or
  domain concepts and need software responsibility decisions.
- Multiple classes or language-native units could plausibly own the same
  behavior.
- A boundary-sensitive refactoring moves coordination, supervision, cleanup,
  dependency direction, or another durable responsibility.
- Creation, coordination, variation, or dependency pressure is unclear.
- Do not use as an as-built module inventory, a naming exercise after
  responsibilities are chosen, or an exact resource-ownership design.

## Language Adaptation

GRASP supplies language-neutral assignment reasoning; it does not require a
class-shaped result. When the implementation language is known, also use
[Software Design Language Adaptation](../software-design-language-adaptation/SKILL.md)
and read only its matching language reference. Preserve the rationale while
selecting a native type, function, module, task, callable, adapter, resource
handle, composition root, or other appropriate construct.

## Workflow

1. **Start from behavior.** Use an approved or recovered scenario, system event,
   contract effect, collaboration, or invariant. Phrase each responsibility as
   “Who should know...?”, “Who should do...?”, or “Who should coordinate...?”
2. **List native candidates.** Consider the domain object and the actual
   language-native units at the boundary: module, type, function, task,
   adapter, resource handle, and composition root. Do not select an owner from
   names alone.
3. **Try Information Expert first.** Prefer the unit with the information or
   capability needed to fulfill the responsibility. Logical information
   responsibility does not by itself decide exact Rust memory or resource
   ownership.
4. **Apply Creator for construction.** Prefer the unit that contains,
   aggregates, records, closely uses, or has the initialization knowledge for
   the created value, task, or resource owner.
5. **Choose a Controller for system events.** Use a facade, use-case/session
   controller, composition function, or composition root to receive and
   coordinate the scenario. Keep domain and service work in its selected
   experts.
6. **Check Low Coupling.** Reject assignments that create unnecessary
   dependency chains, unstable knowledge, process-global access, or hidden
   control flow.
7. **Check High Cohesion.** Reject assignments that combine unrelated
   preparation, business behavior, transport, supervision, and cleanup.
8. **Use Polymorphism only for demonstrated variation.** Let language
   adaptation choose an enum, callable, generic, trait, object, or other native
   mechanism according to whether alternatives are open or closed.
9. **Use Pure Fabrication when existing owners would become bloated or
   coupled.** Prefer a cohesive module, adapter, function, or service-like type
   that has one clear reason to change.
10. **Use Indirection to mediate dependencies.** Insert the smallest native
    mechanism when direct coupling creates demonstrated pressure.
11. **Use Protected Variations.** Identify a real source of change and
    stabilize access through a suitable boundary without predicting arbitrary
    future variation.
12. **Record ownership feedback.** Name the selected responsibility owner and
    dependency direction. If Rust resource ownership, task supervision, or
    fallible cleanup is material, hand the assignment to
    `design-rust-lifecycles`. Revise the responsibility when lifecycle evidence
    shows that the assignment is unsafe or incohesive.

## Decision Record Template

Before creating a new document, apply
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
Prefer recording a local responsibility choice in its realization or design
model. When the choice is cross-cutting, expensive to reverse, and needs an
independent architecture-decision lifecycle, use
[Record Architecture Decision](../record-architecture-decision/SKILL.md)
instead of creating a duplicate responsibility record.

For a standalone Markdown file, follow
[Markdown Artifact Frontmatter](../iterative-risk-driven-development/references/markdown-artifact-frontmatter.md)
and use STE-style,
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

- [Class or language-native unit]: [reason for/against]

## Rationale

- Coupling/cohesion impact: [impact]
- Variation point: [none or protected by interface/polymorphism]
```

## Boundaries

- Use `reconstruct-software-architecture` when the question is which modules or
  runtime participants exist today. This skill decides who should own behavior.
- Use `design-rust-lifecycles` for exact ownership transfer, borrowing,
  cancellation, joining, rollback, `Drop`, and fallible cleanup after the
  native responsibilities are explicit.
- Use `use-case-realization` when one scenario needs a detailed internal
  collaboration. A responsibility decision does not require a complete
  realization or class diagram.
- Keep requirements and domain models free of implementation-unit choices.

## Red Flags

- A controller or composition root performs business or service rules instead
  of coordinating.
- A domain object knows about UI, persistence, infrastructure, or external APIs.
- A module named `service`, `manager`, or `runtime` accumulates preparation,
  protocol behavior, task supervision, and cleanup without one cohesive reason.
- Every responsibility becomes a struct or trait even when a module, function,
  enum, task, or handle is the natural owner.
- Ad hoc type checks replace polymorphic dispatch for open or extensible
  variants. Do not confuse exhaustive matching over a language-native closed
  sum type with this smell.
- A current module inventory is reported as an intended responsibility design.

## Verification

- [ ] Each non-trivial behavior has an explicit class or language-native owner.
- [ ] Responsibility decisions cite at least one applicable GRASP rationale.
- [ ] Controllers and composition roots coordinate but do not absorb domain or
      service logic.
- [ ] Coupling, cohesion, and dependency direction were checked for each major
      assignment.
- [ ] Variation points use the smallest justified native protection mechanism.
- [ ] Responsibility ownership remains distinct from exact memory, task, or
      resource ownership, with a Rust lifecycle handoff when material.
- [ ] The decision explains its problem and consequence before comparing candidates.
- [ ] A standalone Markdown decision exposes identity, responsibility, chosen owner, GRASP basis, and lifecycle metadata in one frontmatter block.
