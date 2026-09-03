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
5. **Orient the reader.** State the actor's problem, intended outcome, and the most important behavioral boundary in plain language.
6. **Write black-box scenarios.** Describe actor intent and system responsibilities without UI widgets or internal classes.
7. **Separate main success from extensions.** Keep the successful representative scenario readable, then add alternate and failure flows.
8. **Attach related requirements.** Link business rules, data requirements, and the canonical quality requirements and constraints to relevant use cases. Do not copy cross-cutting requirements into each scenario; use `specify-quality-constraints` when their definition, measure, or conflict is unclear.
9. **Use diagrams only as an index.** Create a use-case diagram when it helps show actors and use-case names.
10. **Mark detail level by risk.** Fully dress architecturally significant or risky use cases; keep low-risk cases brief or casual.

## Output Template

Before creating a new document, apply
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
Prefer updating an existing use case or embedding the scenario in its
aggregate feature artifact when either is a sufficient owner.

For a standalone Markdown file, follow
[Markdown Artifact Frontmatter](../iterative-risk-driven-development/references/markdown-artifact-frontmatter.md)
and use STE-style,
then use this shape. The main success scenario normally serves as the
representative scenario. When embedding the use case in an aggregate file,
omit the frontmatter and adjust heading levels.

```markdown
---
type: "Use Case"
title: "[Goal Name]"
description: "[One sentence describing the actor's goal and outcome]"
id: "[Stable use-case ID when cross-referenced]"
status: "[draft | active | retired]"
primary_actor: "[Actor]"
scope: "[System under discussion]"
level: "[user goal | summary | subfunction]"
tags: [requirements, use-case]
---

# Use Case: [Goal Name]

## Goal

[Explain the actor's problem, intended outcome, and important behavioral
boundary in plain language.]

## Main Success Scenario

1. [Actor intent]
2. [System responsibility]

## Extensions

1a. [Condition]: [alternate behavior]

## Special Requirements

- [Rule, data requirement, or link to a canonical quality requirement or constraint]

## Open Questions

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
- [ ] The goal orients the reader before detailed scenarios and requirements.
- [ ] Main success scenarios are black-box and actor-goal oriented.
- [ ] Important extensions and failure paths are captured.
- [ ] Business rules and canonical quality requirements or constraints are linked to affected use cases without duplicating cross-cutting definitions.
- [ ] A standalone Markdown use case exposes identity, summary, actor, scope, level, and lifecycle metadata in one frontmatter block.
