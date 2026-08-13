---
name: use-case-realization
description: Designs object collaborations for use-case scenarios. Use when translating SSD operations and contracts into sequence or communication diagrams with controllers, domain objects, and services.
---

# Use-Case Realization

## Overview

Use-case realization shows how software objects collaborate to satisfy a use-case scenario. It is where GRASP decisions become interaction diagrams and design classes.

## When to Use

- You have a use-case scenario, SSD, and important operation contracts.
- You need to discover design classes, methods, and collaborations.
- A system operation requires coordinated domain behavior.
- Do not use before black-box requirements and system events are understood.

## Language Adaptation

When the implementation language is known, also use [Software Design Language Adaptation](../software-design-language-adaptation/SKILL.md) and read only its matching language reference. Model actual runtime participants such as functions, modules, callables, values, or channels when they own meaningful behavior; do not invent object lifelines for diagram symmetry.

## Workflow

1. **Select one scenario and operation sequence.** Use the SSD as the external event source.
2. **Add the controller entry point.** Route each system event to a chosen controller.
3. **Assign work with GRASP.** For every message, decide the receiver by Expert, Creator, Controller, and coupling/cohesion checks.
4. **Show object messages in time order.** Use sequence diagrams when order matters; communication diagrams when link structure matters.
5. **Create objects at the responsible point.** Show creation messages where Creator justifies them.
6. **Keep persistence and UI secondary.** Include infrastructure only when architecturally relevant to the collaboration.
7. **Reflect contract postconditions.** Ensure the interaction creates, links, and modifies objects required by contracts.
8. **Promote discovered classes.** Add stable design classes, methods, and associations to the design class diagram.
9. **Repeat for extensions.** Realize alternate flows that introduce different collaborations or responsibilities.

## Output Template

Before creating a new document, apply
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
Prefer updating or embedding the realization in its owning feature artifact
when it does not change independently.

For a standalone Markdown file, follow
[Markdown Artifact Frontmatter](../iterative-up-analysis-design/references/markdown-artifact-frontmatter.md)
and [Readable Technical Artifacts](../iterative-up-analysis-design/references/readable-technical-artifacts.md),
then use this shape. The realized use-case scenario supplies the representative
scenario; summarize its outcome instead of repeating the black-box steps. When
embedding the realization in an aggregate file, omit the frontmatter and adjust
heading levels.

```markdown
---
type: "Use-Case Realization"
title: "[Use Case] - [Scenario] Realization"
description: "[One sentence summarizing the collaboration and outcome]"
id: "[Stable realization ID when cross-referenced]"
use_case: "[Use-case ID or title]"
scenario: "[Scenario name]"
status: "[draft | active | retired]"
tags: [design, use-case-realization]
---

# Use-Case Realization: [Use Case] - [Scenario]

## Scenario and Outcome

[Explain the initiating event, meaningful result, and design pressure in plain
language.]

## System Operations

- [operation(parameters)]

## Collaborators

- [Object/Class]: [role]

## Interaction Summary

1. [Controller] receives [system event].
2. [Sender] -> [Receiver]: [message]

## Responsibility Notes

- [Message]: [GRASP rationale]

## Design Classes Discovered

- [Class.operation()]
```

## Red Flags

- The controller does all the work.
- The diagram repeats SSD black-box messages without internal collaboration.
- Messages are invented without reference to contracts or use-case steps.
- Object creation has no Creator rationale.

## Verification

- [ ] Every system event is handled by an explicit controller operation.
- [ ] Contract postconditions are satisfied by the collaboration.
- [ ] Message receivers have GRASP-based responsibility rationale.
- [ ] New design classes and methods are recorded for the class diagram.
- [ ] Important alternate flows are realized or intentionally deferred.
- [ ] The scenario outcome orients readers before the internal collaboration.
- [ ] A standalone Markdown realization exposes identity, use-case trace, scenario, summary, and lifecycle metadata in one frontmatter block.
