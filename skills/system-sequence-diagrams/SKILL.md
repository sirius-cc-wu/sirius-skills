---
name: system-sequence-diagrams
description: Creates system sequence diagrams from use-case scenarios. Use when identifying system events, system operations, actor-system boundaries, or operation names before object design.
---

# System Sequence Diagrams

## Overview

A system sequence diagram shows external actors sending events to the system treated as one black-box lifeline. It discovers system operations before internal object collaboration is designed.

## When to Use

- A use-case scenario needs precise actor-system event ordering.
- You need system operation names for contracts or controller design.
- Scope boundaries are unclear between UI, external systems, and the application.
- Do not use to show messages among software objects; use `use-case-realization` for that.

## Workflow

1. **Choose one scenario.** Start with a main success scenario or a significant extension.
2. **Draw the system as one lifeline.** Do not decompose into controllers, services, databases, or UI widgets.
3. **Identify external actors.** Include people and external systems that directly send or receive events.
4. **Convert steps to system events.** Each actor intent that crosses the boundary becomes a message to `:System`.
5. **Name operations by intent.** Use operation names such as `enterItem(id, quantity)` or `makePayment(amount)`.
6. **Add parameters from actor-provided data.** Include data crossing the boundary, not internal lookup results.
7. **Show system responses only when meaningful.** Include returned information that affects the next actor decision.
8. **Repeat for important extensions.** Model alternate scenarios when they introduce different events or ordering.

## Output Template

```markdown
## SSD: [Use Case] - [Scenario]

Actors:
- [Actor]

System Events:
1. [actor] -> System: [operation(parameters)]
2. System -> [actor]: [response, if relevant]

Discovered System Operations:
- [operation(parameters)]: [intent]
```

## Red Flags

- The diagram contains `Controller`, `Repository`, `Database`, domain objects, or UI components.
- Message names are physical UI gestures such as `clickSubmit`.
- Internal data appears as a parameter even though the actor did not provide it.
- A complex use case has no SSD before contracts or design.

## Verification

- [ ] The system is represented as a black box.
- [ ] Every message crossing the boundary maps to a use-case step.
- [ ] System operation names are stable enough for contracts and controllers.
- [ ] Parameters are actor-provided or external-system-provided data.
- [ ] Significant alternate flows have SSD coverage when their events differ.

