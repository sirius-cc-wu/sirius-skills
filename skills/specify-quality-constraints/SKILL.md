---
name: specify-quality-constraints
description: Specifies measurable quality requirements, binding constraints, and acceptance evidence without designing the architecture. Use when performance, availability, security, privacy, accessibility, regulatory, operational, compatibility, data, platform, or other cross-cutting requirements are unclear or unmeasured; do not use for actor-goal flows, business-investment decisions, or architecture design.
---

# Specify Quality Constraints

## Overview

Establish the quality requirements and binding constraints that govern a
bounded system or feature. Keep stakeholder intent, evidence, approval, and
unknowns visible. Produce criteria that architecture, implementation, and
verification can use without choosing the design.

## When to Use

- A quality attribute has only an adjective, such as “fast,” “secure,” or
  “reliable,” rather than a measurable requirement.
- Operational, legal, privacy, accessibility, compatibility, data, platform,
  interface, or technology constraints affect the outcome.
- Several use cases share a cross-cutting requirement.
- A use case needs a special requirement that architecture or tests must
  interpret consistently.
- Do not use to discover actors or main success scenarios; use
  `use-case-modeling`.
- Do not use to select components, interfaces, deployment, or an architecture
  candidate; use `design-software-architecture` after requirements are
  approved.
- Do not use to establish a product vision, business case, or investment
  decision; use the responsible external product or portfolio process. External
  `idea-refine` may prepare a candidate direction.

## Workflow

1. **Fix the requirement boundary.** Name the system or feature, relevant
   actors and use cases, decision authority, non-goals, and the question the
   requirement must answer. Stop for missing stakeholder evidence or authority.
2. **Separate qualities from constraints.** Record qualities as observable
   behavior to optimize or protect. Record constraints as binding limits,
   obligations, mandated interfaces, environments, standards, technologies, or
   policies. Do not disguise a design preference as a requirement.
3. **Make qualities measurable.** For each material quality, state the stimulus,
   operating condition, affected scope, required response, and measure or
   acceptance threshold. State any human-owned assessment when no automated
   measure is possible.
4. **Preserve source and status.** Link every requirement to its source,
   evidence revision, authority, and status. Keep candidate, approved,
   contested, inferred, and unknown material distinct. Do not treat code,
   tests, or a prototype as stakeholder approval.
5. **Relate requirements to behavior.** Link each requirement to the affected
   use cases, system boundary, data, or external interface. Keep a shared
   requirement canonical here; use cases should link to it rather than copy it.
6. **Resolve conflicts and priorities.** Identify incompatible targets,
   trade-offs, dependencies, and the authority that must decide them. State
   priority only when its source is explicit.
7. **Choose verification evidence.** Name the test, inspection, exercise,
   analysis, accessibility review, operational probe, or human assessment that
   could establish each approved claim. Do not invent a passing result.
8. **Route the next question.** Route architecturally significant approved
   requirements to `design-software-architecture`; retain local links from
   `use-case-modeling`; route a missing authority to the responsible external
   owner.

## Output

Before creating a new document, apply the
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
Prefer a section in the canonical feature or requirements artifact when it has
the same owner and lifecycle. Create a standalone supplementary specification
only when shared or cross-cutting requirements need independent discovery.

For a standalone Markdown file, follow
[Markdown Artifact Frontmatter](../iterative-risk-driven-development/references/markdown-artifact-frontmatter.md)
and use STE-style. When embedding this content, omit the frontmatter and adjust
heading levels.

```markdown
---
type: "Supplementary Specification"
title: "Supplementary Requirements: [System or Feature]"
description: "[Quality requirements and binding constraints for the bounded outcome]"
id: "[Stable ID when cross-referenced]"
status: "[draft | active | retired]"
tags: [requirements, quality, constraints]
---

# Supplementary Requirements: [System or Feature]

## Purpose and Boundary

- Outcome and scope: [bounded outcome]
- Decision authority: [role or source]
- Non-goals: [excluded behavior]

## Quality Requirements

- [ID, quality]: Given [stimulus and condition], [affected scope] shall
  [response] within [measure or threshold].
  - Source and status: [source, revision, and status]
  - Affected behavior: [use case, boundary, or interface]
  - Verification: [test, analysis, review, or human-owned assessment]

## Binding Constraints

- [ID, constraint]: [obligation or limit].
  - Source and status: [source, revision, and status]
  - Affected behavior: [use case, boundary, or interface]
  - Verification: [evidence]

## Conflicts, Assumptions, and Open Questions

- [Issue]: [impact, decision owner, and stop condition]
```

## Boundaries

- This skill owns requirements, constraints, traceability, and acceptance
  evidence. It does not choose an architecture or an implementation.
- `use-case-modeling` owns actor goals and black-box scenario flow. It links
  applicable quality requirements and constraints.
- `design-software-architecture` owns responses to approved architecturally
  significant requirements. It does not turn an unapproved target into a
  requirement.
- A responsible external product or portfolio owner owns business cases,
  feasibility commitments, and investment decisions. External `idea-refine`
  can prepare a candidate direction, not approve it.

## Red Flags

- A quality requirement is an unmeasured adjective.
- A chosen technology, component, or architecture style appears as an invented
  constraint.
- A cross-cutting requirement is copied into several use cases with no
  canonical owner.
- A test result, prototype, or current implementation is presented as approved
  intent.
- A conflict between qualities is silently resolved by architecture or code.
- A business case or investment decision is inferred from a candidate idea.

## Verification

- [ ] The system or feature boundary, decision authority, and non-goals are
      explicit.
- [ ] Material qualities have a stimulus, condition, scope, response, and
      measure or explicit human-owned assessment.
- [ ] Binding constraints are distinguishable from design preferences.
- [ ] Every material claim retains source, revision, authority, and status.
- [ ] Affected use cases, boundaries, data, or external interfaces link to the
      canonical requirement.
- [ ] Conflicts, assumptions, and missing authority remain explicit.
- [ ] Approved requirements have proportional verification evidence.
- [ ] Architecture and implementation decisions remain with their owning
      skills.
- [ ] Any standalone artifact passes the artifact budget and has one
      frontmatter block with the `Supplementary Specification` type.
