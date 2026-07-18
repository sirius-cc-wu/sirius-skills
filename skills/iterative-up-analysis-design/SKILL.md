---
name: iterative-up-analysis-design
description: Guides iterative Unified Process-style analysis and design. Use when planning requirements-to-design work across inception, elaboration, construction, risks, durable artifacts, repository layouts, and incremental refinement.
---

# Iterative UP Analysis and Design

## Overview

Use an iterative, risk-driven flow: produce just enough artifacts for the current decision, preserve durable design knowledge across iterations, and drive design from use cases and architectural risk.

## When to Use

- A feature or system needs requirements, analysis, and object design rather than immediate coding.
- Work spans multiple artifacts such as vision, use cases, domain model, SSDs, contracts, and design model.
- Architectural risk or unclear requirements require iterative exploration.
- Design artifacts and iteration records need durable, navigable repository locations.
- Do not use for isolated bug fixes or trivial implementation tasks.

## Workflow

1. **Identify phase intent.**
   - Inception: clarify scope, business case, actors, key use cases, major risks.
   - Elaboration: address architectural risk, detail significant use cases, model domain concepts, design core scenarios.
   - Construction: implement and test incrementally from stabilized design decisions.
   - Transition: validate deployment, training, feedback, and release readiness.
2. **Select an iteration objective.** Choose a thin slice driven by risk, learning value, or stakeholder priority.
3. **Inspect repository conventions.** Read governance, indexes, and neighboring artifacts before selecting paths or creating directories.
4. **Classify artifact lifecycles.** Refine design artifacts at canonical paths, create one historical record per iteration, and record durable cross-cutting decisions separately when needed.
5. **Choose only necessary artifacts.** Do not create every artifact by default; create what reduces uncertainty for the current iteration.
6. **Choose artifact placement.** Preserve an established layout. When none exists, use the smallest suitable option from [Artifact Durability and Repository Layouts](references/artifact-layouts.md); default to the feature-iteration hybrid with flat feature files, promoting a feature to a package only when its artifacts change independently.
7. **Sequence analysis before design.** Use cases lead to SSDs, domain model, contracts, GRASP decisions, realizations, and design class diagrams.
8. **Keep durable artifacts evolving.** Mark canonical artifacts as started or refined; expect corrections as contracts, design, implementation, and feedback reveal gaps.
9. **Tie artifacts together.** Each design decision should trace back to use cases, system events, contracts, risks, or verification evidence.
10. **Timebox detail.** Fully detail architecturally significant use cases; keep low-risk artifacts lightweight.
11. **Close the iteration.** Record results against exit criteria without copying canonical artifact bodies into the iteration record.
12. **End with executable next steps.** Convert design outcomes into implementation tasks and verification checks. Use [Test-Driven Implementation](../test-driven-implementation/SKILL.md) and [Behavior-Preserving Refactoring](../behavior-preserving-refactoring/SKILL.md) during construction, and feed design-relevant discoveries back into canonical artifacts.

## Artifact Durability

- Treat use cases, domain models, SSDs, contracts, realizations, and design class diagrams as durable, evolving sources of truth.
- Give artifacts referenced across iterations or by other artifacts stable identifiers and one canonical path; local supporting notes may use only a title and path.
- Treat iteration goals, selected risks, scope, exit criteria, and results as a historical iteration record.
- Link iteration records to canonical artifacts and state whether each artifact was started, refined, or consulted.
- Treat version control as revision history, not as the only way readers can find the current artifact or a closed iteration.
- Do not organize durable artifacts by UP phase; artifacts commonly mature across several phases.

## Iteration Plan Template

```markdown
## Iteration: [Name]

Status: [planned / active / completed]

Goal:
- [Learning, risk reduction, or stakeholder outcome]

Risks Addressed:
- [Risk]

Artifacts to Start:
- [Stable ID when cross-referenced, artifact]: `[canonical path]` - [why now]

Artifacts to Refine:
- [Stable ID when cross-referenced, artifact]: `[canonical path]` - [trigger for refinement]

Artifacts Consulted:
- [Stable ID when cross-referenced, artifact]: `[canonical path]`

Decisions to Record:
- [Decision]: `[canonical path or pending location]`

Trace:
- [Use case] -> [SSD/contract] -> [design realization/class]

Exit Criteria:
- [Evidence that the iteration answered the question]

Results:
- [Completed when the iteration closes: evidence, residual risk, or follow-up]

Artifact Outcomes:
- [started / refined / consulted / deferred]: [stable ID when cross-referenced, title, and canonical path] - [actual result]
```

Keep the planned artifact headings unchanged when closing an iteration. Use
`Artifact Outcomes` to record what actually happened, including work that was
deferred or changed after the plan was written.

## Red Flags

- All artifacts are created at full detail before risk is understood.
- Coding starts from a domain model without use cases or system events.
- Artifact updates are treated as failure rather than expected refinement.
- The plan follows phases mechanically instead of risk and learning.
- Durable design artifacts are copied into each iteration directory, leaving no obvious current source of truth.
- An iteration record becomes the only canonical location for a use case, contract, or design model.
- A new documentation taxonomy is imposed without checking existing repository conventions.
- Artifacts are moved between phase directories as they mature.

## Verification

- [ ] The current phase intent and iteration objective are explicit.
- [ ] Artifact choices are justified by risk, learning, or implementation need.
- [ ] Durable artifacts, iteration records, and decision records have distinct lifecycles.
- [ ] Every started or refined artifact has one canonical path; artifacts cross-referenced across iterations or other artifacts have stable IDs.
- [ ] The selected layout fits existing conventions and expected navigation without unnecessary directories.
- [ ] Use cases drive downstream analysis and design artifacts.
- [ ] Design decisions trace to requirements or contracts.
- [ ] The iteration has concrete exit criteria and implementation handoff points.
- [ ] A closed iteration records results and links to canonical artifacts without duplicating them.
