---
name: iterative-up-analysis-design
description: Guides iterative Unified Process-style analysis and design. Use when planning requirements-to-design work across inception, elaboration, construction, risks, artifacts, and incremental refinement.
---

# Iterative UP Analysis and Design

## Overview

Use an iterative, risk-driven flow: produce just enough artifacts for the current decision, refine them as learning increases, and drive design from use cases and architectural risk.

## When to Use

- A feature or system needs requirements, analysis, and object design rather than immediate coding.
- Work spans multiple artifacts such as vision, use cases, domain model, SSDs, contracts, and design model.
- Architectural risk or unclear requirements require iterative exploration.
- Do not use for isolated bug fixes or trivial implementation tasks.

## Workflow

1. **Identify phase intent.**
   - Inception: clarify scope, business case, actors, key use cases, major risks.
   - Elaboration: address architectural risk, detail significant use cases, model domain concepts, design core scenarios.
   - Construction: implement and test incrementally from stabilized design decisions.
   - Transition: validate deployment, training, feedback, and release readiness.
2. **Select an iteration objective.** Choose a thin slice driven by risk, learning value, or stakeholder priority.
3. **Choose only necessary artifacts.** Do not create every artifact by default; create what reduces uncertainty for the current iteration.
4. **Sequence analysis before design.** Use cases lead to SSDs, domain model, contracts, GRASP decisions, realizations, and design class diagrams.
5. **Keep artifacts evolving.** Mark artifacts as started or refined; expect corrections as contracts and design reveal gaps.
6. **Tie artifacts together.** Each design decision should trace back to use cases, system events, contracts, or risks.
7. **Timebox detail.** Fully detail architecturally significant use cases; keep low-risk artifacts lightweight.
8. **End with executable next steps.** Convert design outcomes into implementation tasks and verification checks.

## Iteration Plan Template

```markdown
## Iteration: [Name]

Goal:
- [Learning, risk reduction, or stakeholder outcome]

Risks Addressed:
- [Risk]

Artifacts to Start:
- [Artifact]: [why now]

Artifacts to Refine:
- [Artifact]: [trigger for refinement]

Trace:
- [Use case] -> [SSD/contract] -> [design realization/class]

Exit Criteria:
- [Evidence that the iteration answered the question]
```

## Red Flags

- All artifacts are created at full detail before risk is understood.
- Coding starts from a domain model without use cases or system events.
- Artifact updates are treated as failure rather than expected refinement.
- The plan follows phases mechanically instead of risk and learning.

## Verification

- [ ] The current phase intent and iteration objective are explicit.
- [ ] Artifact choices are justified by risk, learning, or implementation need.
- [ ] Use cases drive downstream analysis and design artifacts.
- [ ] Design decisions trace to requirements or contracts.
- [ ] The iteration has concrete exit criteria and implementation handoff points.

