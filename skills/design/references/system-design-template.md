# System Design Template

Use this reference to structure `<feature_path>/system-design.md`.

Prefer these sections unless a section is genuinely irrelevant to the feature:

1. `# System design: <feature name>`
2. `## Design summary`
3. `## Related stories`
4. `## Goals and non-goals`
5. `## Architecture`
6. `## Interfaces and dependencies`
7. `## Configuration surfaces and ownership`
8. `## Data flow, state, and lifecycle`
9. `## Failure handling and operational constraints`
10. `## Alternatives considered`
11. `## Risks, assumptions, and open questions`
12. `## Validation strategy`
13. `## Summary`

## Required content

Always include:

- what problem the design solves
- which feature stories the design directly serves
- the major architectural decision
- the boundaries between components or modules
- the interfaces, inputs, outputs, or contracts that matter
- which configuration and state surfaces own each externally supplied value
- constraints that affect execution, rollout, or safety
- how the design will be validated

## Framing mode

Default to a forward-looking design for work that will later feed `breakdown`.

The design may start from any of these sources:

- a prior `discover.md`
- a direct user prompt or backlog item without discovery artifacts
- existing implementation that needs a reviewable current-state design

If the task is to capture existing implemented behavior instead:

- state that clearly in the title or opening summary
- describe the current behavior as implemented, not as aspiration
- add an explicit delta section when the implementation differs from intended or previously documented design

## Quality bar

A strong `system-design.md` should let a reviewer answer these questions quickly:

1. What is being built or documented?
2. Why is this approach chosen over the obvious alternatives?
3. Which interfaces or dependencies constrain the work?
4. Why is each configuration surface necessary, and where does raw external input stop and typed internal state begin?
5. What state, lifecycle, or operational rules must remain true?
6. How will later planning and implementation verify the design?

## Diagram guidance

Choose diagrams that clarify real design risk:

- component or package diagrams for structure and ownership
- sequence diagrams for request flow, integration flow, or failure handling
- state diagrams for lifecycle-heavy features
- deployment diagrams for topology or network placement

Do not add diagrams that merely restate section prose without improving precision.

When `.skills/planning.json` uses `design_diagram_mode: "linked_svg"`, keep the
generated figures visually stable across themes:

- set `skinparam backgroundColor white` in each PlantUML source
- ensure each generated or hand-authored SVG starts with an explicit white
  canvas rect such as `<rect fill="#FFFFFF" height="100%" width="100%" x="0"
  y="0"/>`
