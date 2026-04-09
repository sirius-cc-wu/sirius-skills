# System Design Template

Use this reference to structure `<feature_path>/system-design.md`.

Prefer these sections unless a section is genuinely irrelevant to the feature:

1. `# System design: <feature name>`
2. `## Design summary`
3. `## Goals and non-goals`
4. `## Architecture`
5. `## Interfaces and dependencies`
6. `## Data flow, state, and lifecycle`
7. `## Failure handling and operational constraints`
8. `## Risks, assumptions, and open questions`
9. `## Validation strategy`
10. `## Summary`

## Required content

Always include:

- what problem the design solves
- the major architectural decision
- the boundaries between components or modules
- the interfaces, inputs, outputs, or contracts that matter
- constraints that affect execution, rollout, or safety
- how the design will be validated

## Framing mode

Default to a forward-looking design for work that will later feed `breakdown`.

If the task is to capture existing implemented behavior instead:

- state that clearly in the title or opening summary
- describe the current behavior as implemented, not as aspiration
- add an explicit delta section when the implementation differs from intended or previously documented design

## Quality bar

A strong `system-design.md` should let a reviewer answer these questions quickly:

1. What is being built or documented?
2. Why is this approach chosen over the obvious alternatives?
3. Which interfaces or dependencies constrain the work?
4. What state, lifecycle, or operational rules must remain true?
5. How will later planning and implementation verify the design?

## Diagram guidance

Choose diagrams that clarify real design risk:

- component or package diagrams for structure and ownership
- sequence diagrams for request flow, integration flow, or failure handling
- state diagrams for lifecycle-heavy features
- deployment diagrams for topology or network placement

Do not add diagrams that merely restate section prose without improving precision.
