---
name: iterative-risk-driven-analysis-design
description: Coordinates one approved, risk-sized, iterative analysis and design objective across product questions, architecture risks, durable artifacts, and incremental refinement. Use when a team needs scenario-driven analysis, use cases, domain models, system sequence diagrams, contracts, conditional object-design methods, or iterative artifact refinement; use run-development-iteration for implementation and commit execution.
---

# Iterative Risk-Driven Analysis and Design

## Overview

Use an iterative, risk-driven analysis and design flow. Produce only the
artifacts needed for the current decision. Preserve selected durable design
knowledge across iterations. Use scenarios and architectural risk to choose the
needed techniques.

This skill is an optional planning specialization. It is not the default
coordinator for every language or development iteration.

## When to Use

- A feature or system needs explicit work framing and selected requirements,
  analysis, or object-design techniques before coding.
- Work spans several artifacts, such as vision, use cases, domain models, SSDs,
  contracts, and design models.
- Architectural risk or unclear requirements need iterative exploration.
- Selected durable artifacts and historical iteration records need
  lifecycle-aware ownership across multiple iterations.
- Do not use for an isolated bug fix, a trivial implementation task, one
  language-native design question, or one paradigm-neutral iteration.

## Workflow

1. **Frame the work.** State the product question, architectural risk,
   stakeholder need, or delivery constraint that matters before coding.
2. **Choose one iteration objective.** Select a thin slice driven by risk,
   learning value, or stakeholder priority.
3. **Inspect repository conventions.** Read governance, indexes, and neighboring
   artifacts before selecting paths or creating directories.
4. **Classify artifact lifecycles.** Refine design artifacts at canonical paths.
   Create one historical record per iteration. Record durable cross-cutting
   decisions separately when needed.
5. **Budget artifact creation.** Apply
   [Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
   Use `select-technical-artifacts` when several material owners or dispositions
   compete. Create a standalone artifact only when it has durable, reusable, or
   risk-reducing value, no sufficient existing owner, and an independent
   lifecycle.
6. **Choose artifact placement.** Preserve established canonical paths. When no
   convention exists, several homes compete, or migration is material, use
   [Design Repository Artifact Layout](../design-repository-artifact-layout/SKILL.md).
   Do not use work phases as the directory structure.
7. **Apply dependencies selectively.** Let use cases lead to examples, SSDs,
   domain concepts, or contracts when those questions matter. Add GRASP,
   realizations, patterns, or design class diagrams only when object
   responsibility or collaboration is the selected problem. Do not treat the
   dependency graph as a deliverable checklist.
8. **Keep durable artifacts evolving.** Mark canonical artifacts as started or
   refined. Expect corrections when contracts, design, implementation, or
   feedback reveal gaps.
9. **Link artifacts.** Trace each design decision to use cases, system events,
   contracts, risks, or verification evidence.
10. **Timebox detail.** Fully detail architecturally significant use cases. Keep
    low-risk artifacts lightweight.
11. **Close the iteration.** Record results against exit criteria. Do not copy
    canonical artifact bodies into the iteration record.
12. **Define next steps.** Convert design outcomes into implementation tasks and
    verification checks. Use [Test-Driven Implementation](../test-driven-implementation/SKILL.md)
    and [Behavior-Preserving Refactoring](../behavior-preserving-refactoring/SKILL.md)
    during construction. Feed design-relevant discoveries back into canonical
    artifacts.

## File Output

Before creating a new document, apply
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
Prefer code, tests, configuration, an existing canonical artifact, or an
aggregate feature section when one of them is sufficient.

When persisting standalone Markdown, follow
[Markdown Artifact Frontmatter](references/markdown-artifact-frontmatter.md)
and use STE-style for reader-facing artifacts. Put discovery metadata in
frontmatter and substantive analysis or design in the body. When several
artifacts share a flat feature file, describe the aggregate once in file-level
frontmatter. Do not insert nested frontmatter. Treat `index.md` and `log.md` as
reserved structural files.

## Artifact Durability

- Treat selected use cases, domain models, SSDs, contracts, realizations, and
  design class diagrams as durable, evolving sources of truth.
- Give artifacts referenced across iterations or by other artifacts stable
  identifiers and one canonical path. Local supporting notes may use only a
  title and path.
- Treat iteration goals, selected risks, scope, exit criteria, and results as a
  historical iteration record.
- Link iteration records to canonical artifacts. State whether each artifact was
  started, refined, or consulted.
- Treat version control as revision history, not as the only way readers find
  the current artifact or a closed iteration.
- Do not organize durable artifacts by work phase. Artifacts commonly mature
  across several iterations.

## Iteration Plan Template

```markdown
---
type: "Iteration Record"
title: "Iteration: [Name]"
description: "[One-sentence learning, risk-reduction, or stakeholder goal]"
id: "[Stable iteration ID]"
status: "[planned | active | completed]"
tags: [analysis, design, iteration]
---

# Iteration: [Name]

Goal:
- [Learning, risk reduction, or stakeholder outcome]

Risks Addressed:
- [Risk]

Artifact Budget:
- [create / update / embed / keep with implementation / omit]: `[path or subject]` - [consumer, decision, or risk] - [ownership and lifecycle reason]

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

Omit empty `Artifact Budget` dispositions. Do not add ceremony to complete the
template. Keep the planned artifact headings unchanged when closing an
iteration. Use `Artifact Outcomes` to record actual results, including work
deferred or changed after the plan was written.

## Red Flags

- All artifacts are created at full detail before risk is understood.
- A standalone document has no durable decision, named consumer, material risk,
  or independent lifecycle.
- Object design starts from a domain model without behavior or system events.
- Artifact updates are treated as failure instead of expected refinement.
- The plan follows a fixed sequence instead of risk and learning.
- Durable design artifacts are copied into each iteration directory, leaving no
  obvious current source of truth.
- An iteration record becomes the only canonical location for a use case,
  contract, or design model.
- A new documentation taxonomy is imposed without checking repository
  conventions or using the artifact-layout specialist for a material placement
  decision.
- Artifacts are moved between phase directories as they mature.

## Verification

- [ ] Current phase intent and iteration objective are explicit.
- [ ] Material documentation candidates have dispositions, and every new
      standalone artifact passes the value, ownership, and lifecycle gate.
- [ ] Durable artifacts, iteration records, and decision records have distinct
      lifecycles.
- [ ] Every started or refined artifact has one canonical path. Cross-referenced
      artifacts have stable IDs.
- [ ] The selected layout fits existing conventions and expected navigation
      without unnecessary directories.
- [ ] Every selected downstream artifact traces to a scenario, risk, or design
      question. No artifact exists only to complete a sequence.
- [ ] Design decisions trace to requirements or contracts.
- [ ] The iteration has concrete exit criteria and implementation handoff points.
- [ ] A closed iteration records results and links to canonical artifacts
      without duplicating them.
- [ ] Reader-facing artifacts use STE-style language and explain their problem,
      behavior, or decision before exhaustive detail.
- [ ] A representative scenario precedes detailed contracts or state rules when
      it materially improves understanding.
- [ ] Every standalone Markdown artifact has one OKF-aligned frontmatter block;
      aggregate and reserved files follow their special rules.
