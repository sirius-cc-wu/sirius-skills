---
name: operation-contracts
description: Specifies system operation effects. Use when a system operation has non-trivial state changes, business rules, created objects, associations, or postconditions that use-case text does not capture precisely.
---

# Operation Contracts

## Overview

Operation contracts define what a system operation guarantees, especially changes to domain state. They bridge black-box requirements and object design.

## When to Use

- SSDs reveal system operations with complex effects.
- A use case changes multiple domain objects or associations.
- Designers need exact postconditions before assigning responsibilities.
- Do not write contracts for trivial reads or operations already obvious from the use case.

## Workflow

1. **Select the operation.** Use an operation from a system sequence diagram.
2. **Name the operation and scope.** Include parameters and the owning system boundary.
3. **State preconditions sparingly.** Only include conditions assumed true before the operation starts.
4. **Write postconditions as state changes.** Capture created/deleted instances, changed attributes, formed/broken associations, and recorded events.
5. **Use domain model vocabulary.** Contracts should reference conceptual objects, not implementation classes.
6. **Avoid algorithm steps.** State what must be true after the operation, not how to implement it.
7. **Update the domain model.** If a postcondition needs a missing concept or association, revise the domain model.
8. **Use contracts to drive design.** Feed postconditions into GRASP responsibility assignment.

## Output Template

```markdown
## Contract: [operation(parameters)]

Operation: [name(parameters)]
Cross References: [Use case, SSD step]

Preconditions:
- [Condition that must already be true]

Postconditions:
- [Instance] was created/deleted.
- [Association] was formed/broken.
- [Attribute] became [value or relationship].
- [Event or transaction] was recorded.

Open Issues:
- [Question affecting design]
```

## Red Flags

- Postconditions are written as procedural implementation steps.
- The contract references controllers, services, repositories, or database tables.
- Preconditions repeat ordinary validation instead of true assumptions.
- Contracts are written for every operation by default, including simple queries.

## Verification

- [ ] Each contract corresponds to a system operation from an SSD.
- [ ] Postconditions are declarative and testable.
- [ ] Created/deleted instances, associations, and attribute changes are explicit.
- [ ] Domain model gaps discovered by the contract are recorded.
- [ ] The contract provides enough detail to assign object responsibilities.

