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

```markdown
## Use-Case Realization: [Use Case] - [Scenario]

System Operations:
- [operation(parameters)]

Collaborators:
- [Object/Class]: [role]

Interaction Summary:
1. [Controller] receives [system event].
2. [Sender] -> [Receiver]: [message]

Responsibility Notes:
- [Message]: [GRASP rationale]

Design Classes Discovered:
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

