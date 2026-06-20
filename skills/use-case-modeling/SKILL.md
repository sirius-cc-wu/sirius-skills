---
name: use-case-modeling
description: Guides black-box use-case modeling for requirements discovery. Use when identifying actors, user goals, functional requirements, system scope, or scenario flows before design or implementation.
---

# Use-Case Modeling

## Overview

Use cases capture how actors achieve goals with the system as a black box. They are text-first requirements artifacts; diagrams are summaries, not substitutes.

## When to Use

- Requirements are vague, feature-shaped, or UI-driven.
- You need actors, goals, scope, and functional behavior before object design.
- A feature has alternate flows, failure paths, or business rules that affect behavior.
- Do not use for internal algorithm design, database schema design, or object collaboration details.

## Workflow

1. **Set the system boundary.** Name the system under discussion and what is outside it.
2. **Find primary actors.** List who or what has goals served by the system.
3. **Find actor goals.** Prefer elementary business processes over tiny UI actions.
4. **Name use cases by goals.** Use verb-object names such as `Process Sale`, not button labels.
5. **Write black-box scenarios.** Describe actor intent and system responsibilities without UI widgets or internal classes.
6. **Separate main success from extensions.** Keep the happy path readable, then add alternate and failure flows.
7. **Attach related requirements.** Link non-functional requirements, business rules, data requirements, and constraints to the relevant use cases.
8. **Use diagrams only as an index.** Create a use-case diagram when it helps show actors and use-case names.
9. **Mark detail level by risk.** Fully dress architecturally significant or risky use cases; keep low-risk cases brief or casual.

## Output Template

```markdown
## Use Case: [Goal Name]

Primary Actor: [Actor]
Scope: [System under discussion]
Level: [user goal / summary / subfunction]

Main Success Scenario:
1. [Actor intent]
2. [System responsibility]

Extensions:
1a. [Condition]: [alternate behavior]

Special Requirements:
- [Quality attribute, rule, constraint]

Open Questions:
- [Unresolved issue]
```

## Red Flags

- Use case steps mention screens, buttons, SQL tables, services, or classes.
- Use cases are CRUD-only when user goals are larger.
- Alternate flows are missing for payment failure, validation failure, cancellation, authorization, or unavailable dependencies.
- The diagram exists but the text scenarios do not.

## Verification

- [ ] The system boundary is explicit.
- [ ] Every primary actor has at least one user-goal use case.
- [ ] Main success scenarios are black-box and actor-goal oriented.
- [ ] Important extensions and failure paths are captured.
- [ ] Non-functional requirements and business rules are linked to affected use cases.

