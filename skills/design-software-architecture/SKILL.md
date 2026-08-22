---
name: design-software-architecture
description: Designs the smallest sufficient intended software architecture for approved behavior, constraints, and measurable quality scenarios. Use when major components, services, processes, data owners, interfaces, dependencies, trust or failure boundaries, deployment topology, or architecture trade-offs must be decided before responsibility and detailed design; do not use to infer an undocumented current architecture or generate a complete diagram set.
---

# Design Software Architecture

## Overview

Turn approved system behavior and architecturally significant requirements into
the smallest architecture that addresses the current risk. Define only the
major structure, boundaries, interactions, and deployment consequences needed
for the decision. Keep requirements, current-system evidence, detailed module
design, language realization, and decision history with their proper owners.

An architecture view answers a stakeholder question. It is not a required
document type or diagram level.

## When to Use

- Approved scenarios must be allocated across major components, services,
  processes, modules, data stores, or external systems.
- Data ownership, trust, transaction, failure, integration, or deployment
  boundaries are unclear.
- Availability, latency, security, scalability, modifiability, operability,
  privacy, or cost creates a measurable architecture trade-off.
- A critical runtime interaction or deployment topology must be designed before
  detailed responsibilities or implementation can proceed.
- Several architecture candidates must be compared against explicit drivers.
- Do not use when one established component only needs internal responsibility,
  collaboration, pattern, language, or resource-lifecycle design.

## Inputs

Use only inputs with sufficient authority for the architecture question:

- approved use cases, system events, operation contracts, invariants, and
  boundary examples;
- measurable quality-attribute scenarios and binding constraints;
- evidenced current-system facts, compatibility obligations, and external
  interfaces;
- explicit scope, non-goals, decision authority, and verification oracles.

Stop for `assess-development-input` when readiness or the initial owner is
unclear. Stop for a responsible external recovery process when current behavior,
architecture, deployment, or constraints lack evidence. Do not present an
intended design as an as-built description.

## Workflow

1. **Fix the architecture question.** State the approved outcome, system under
   discussion, decision authority, non-goals, current evidence, and one
   architecture risk or choice to resolve.
2. **Extract significant drivers.** Keep functional scenarios, constraints, and
   quality attributes distinct. Express each material quality attribute as a
   scenario with a stimulus, operating condition, affected part, expected
   response, and measurable response target.
3. **Establish context and boundaries.** Identify relevant users, external
   systems, and the system boundary. Add data, trust, transaction, failure,
   integration, process, and deployment boundaries only when they affect the
   question.
4. **Select the minimum views.** Use the view-selection guide below. Reuse an
   existing canonical architecture owner when it can answer the question. Do
   not create every C4 level, UML view, or deployment diagram.
5. **Develop viable candidates.** Name major components and their cohesive
   responsibilities, owned data, provided and required interfaces, connectors,
   dependency direction, runtime placement, and failure behavior at the detail
   needed to compare alternatives. Do not descend into classes or exact APIs.
6. **Evaluate trade-offs.** Compare candidates against the approved scenarios,
   constraints, quality targets, coupling, failure propagation, consistency,
   trust, operability, reversibility, delivery cost, and known uncertainty.
   Reject unsupported adjectives such as “scalable” or “secure.”
7. **Select or escalate.** Record the chosen candidate only when the responsible
   authority can make that decision. Otherwise, return explicit options,
   consequences, missing evidence, and the required decision owner.
8. **Define verification.** Select proportional evidence such as an interface
   contract, architecture test, prototype, load test, failure exercise, threat
   analysis, deployment probe, or representative end-to-end scenario. State
   which claims remain human-owned or unverified.
9. **Route detailed design.** Hand internal responsibility placement to
   `grasp-responsibility-design`; use `use-case-realization` for detailed
   collaboration when an object-oriented route is appropriate. Hand justified
   local variation to `design-pattern-application`, target-language realization
   to `software-design-language-adaptation`, and material Rust ownership or
   resource semantics to `design-rust-lifecycles`.
10. **Reconcile durable knowledge.** Update the smallest existing architecture
    owner when possible. Use external `documentation-and-adrs` with the `all`
    installation, or repository-native ADR guidance, when one consequential
    choice needs an independent proposed, accepted, or superseding history. Do
    not copy the architecture design into the ADR.

## View Selection

| View | Select when the question concerns | Minimum content |
|---|---|---|
| System context | Scope or external dependencies | System boundary, users, external systems, material relationships |
| Decomposition | Major responsibility, interface, dependency, or data ownership | Components, cohesive responsibilities, interfaces, owned data, dependency direction |
| Runtime interaction | Ordering, concurrency, failure propagation, or one critical scenario | Runtime participants, interactions, state or data movement, failure paths |
| Deployment | Nodes, regions, processes, scaling, availability, networking, or rollout | Material runtime units, placement, communication, redundancy, failure and rollout boundaries |
| Data and trust | Consistency, privacy, security, transaction, or ownership boundaries | Data owners, trust zones, authoritative stores, flows, consistency and access constraints |

Select no separate view when code, configuration, schemas, contracts, or an
existing design already communicate the decision with sufficient clarity.

## Output

Keep architecture evidence with executable boundaries and existing canonical
design by default. Before creating a standalone artifact, apply the
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
When several canonical locations compete, use
`design-repository-artifact-layout`.

For a justified standalone artifact, follow
[Markdown Artifact Frontmatter](../iterative-risk-driven-development/references/markdown-artifact-frontmatter.md)
and use this compact shape:

```markdown
---
type: "Software Architecture Design"
title: "Architecture: [Bounded outcome or decision]"
description: "[Architecture question and intended structural outcome]"
status: "[proposed | accepted | blocked | superseded]"
tags: [architecture, design]
---

# Architecture: [Bounded outcome or decision]

## Architecture Question
- [One risk, boundary, or choice]

## Significant Drivers
- Approved behavior: [scenario or contract]
- Quality scenarios: [stimulus, condition, response, measure]
- Constraints and evidence: [binding facts]

## Context and Boundaries
- [System, external participants, and only material boundaries]

## Selected Views
- [View and the question it answers]

## Candidates and Trade-offs
- [Candidate]: [benefits, costs, risks, and evidence]

## Decision Status
- [Chosen option and authority, or unresolved decision owner]

## Verification
- [Claim, evidence, owner, and result]

## Detailed-Design Handoffs
- [Owner and remaining question]
```

## Boundaries

- Requirements Analysis owns scope, actors, goals, and approved scenarios.
  System Analysis owns domain vocabulary, system events, and state effects.
- This skill designs intended major structure. It does not recover the current
  architecture or treat source layout as proof of intended boundaries.
- `grasp-responsibility-design` owns responsibility placement within established
  architecture boundaries. This skill does not assign every function, class,
  task, or resource handle.
- Detailed Design owns language, API-shape, memory, concurrency, and resource
  lifecycle choices after the architecture constrains them.
- External `documentation-and-adrs` or repository-native ADR guidance owns
  independent decision history. An ADR records a consequential choice; it does
  not replace architecture analysis.
- Use `iterative-risk-driven-development` when architecture, analysis, detailed
  design, implementation, and verification must advance as one risk-sized
  objective.

## Red Flags

- Components are inferred from current directories or deployment units without
  evidence that those boundaries are intended.
- Microservices, events, layers, or a specific architecture style are selected
  before the drivers and trade-offs are explicit.
- Quality attributes appear only as unmeasured adjectives.
- Every C4 level, UML diagram, deployment view, and ADR is required regardless
  of the architecture question.
- A diagram names boxes and arrows but omits responsibilities, owned data,
  interfaces, dependency direction, or failure behavior.
- Detailed classes, exact language APIs, or Rust ownership mechanics obscure
  the architecture decision.
- A proposed architecture is presented as approved or as-built.
- A standalone architecture document duplicates code, configuration, an
  existing design owner, or an independent ADR.

## Verification

- [ ] The architecture question, approved outcome, authority, non-goals, and
      current evidence are explicit.
- [ ] Material quality attributes use measurable scenarios.
- [ ] The system context and only relevant architectural boundaries are clear.
- [ ] Every selected view answers a named question; unnecessary views are
      omitted.
- [ ] Candidate components have cohesive responsibilities, explicit interfaces,
      owned data where material, and deliberate dependency direction.
- [ ] Trade-offs cover the approved drivers, failure behavior, uncertainty, and
      reversibility.
- [ ] The selected option has matching authority, or the responsible decision
      owner and missing evidence remain explicit.
- [ ] Verification evidence is proportional and preserves a representative
      end-to-end scenario when material.
- [ ] Detailed responsibility, collaboration, language, and lifecycle questions
      are handed to their existing specialists.
- [ ] Any standalone artifact passes the artifact budget, uses the required
      frontmatter, and does not duplicate an ADR or existing architecture owner.
