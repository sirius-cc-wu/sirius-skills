---
name: reconcile-recovered-design
description: Reconciles recovered software behavior and architecture across current code, executed tests, runtime observations, documentation, decisions, and history. Use when checking as-built against as-designed, classifying documentation drift, exposing implementation or test gaps, or deciding which artifact needs authoritative follow-up.
---

# Reconcile Recovered Design

## Overview

Compare competing accounts of a system without assuming one source is
universally authoritative. Classify agreement, drift, gaps, lifecycle changes,
and unresolved intent so that the next update is deliberate.

## When to Use

- Recovered behavior or architecture must be checked against existing
  requirements, diagrams, ADRs, tests, or runtime evidence.
- Documentation may describe retired or superseded behavior.
- A modernization or maintenance decision depends on whether code or design
  drifted.
- Do not use to silently edit code, tests, or canonical documents.

## Evidence Discipline

Read
[Recovery Evidence and Confidence](../reverse-engineer-software-system/references/recovery-evidence.md).
Judge authority by the question: current code is strong for as-built structure,
executed observations for current behavior, and accepted requirements or
stakeholder confirmation for intent.

## Workflow

1. **Fix the comparison baseline.** Record the implementation revision,
   recovered artifact IDs, document versions, test results, runtime conditions,
   and the decision requiring reconciliation.
2. **Normalize comparable claims.** Compare the same scope, scenario, element,
   relation, state transition, quality constraint, or lifecycle point. Do not
   compare a high-level intent statement to a low-level helper mechanically.
3. **Build a perspective matrix.** For each material claim, record as-built,
   as-tested, as-observed, as-documented, intended, and historical evidence
   where available.
4. **Respect lifecycle and chronology.** Follow active, retired, superseded,
   replacement, and decision links. Use version history to order changes, not
   to invent rationale.
5. **Classify the result.**
   - `consistent`: relevant perspectives agree.
   - `documentation drift`: current implementation changed but the applicable
     document did not.
   - `implementation drift`: authoritative intended behavior or architecture
     is not reflected in the current implementation.
   - `test gap`: a material intended or implemented behavior lacks adequate
     executable evidence.
   - `observation gap`: static evidence cannot establish runtime behavior.
   - `historical only`: the claim belongs to a retired or superseded state.
   - `intent unknown`: no authoritative source establishes what should win.
6. **Assess impact.** Explain affected actors, behavior, change risk,
   security, operability, maintainability, or downstream artifacts without
   overstating certainty.
7. **Recommend the authority and next action.** Identify the stakeholder,
   experiment, test, code change, document refinement, retirement marker, or
   decision record needed. When an authority confirms one consequential
   architecture choice that needs durable history, route it to
   `record-architecture-decision`; do not turn recovered code rationale into an
   ADR. Do not perform the next action unless requested.
8. **Close traceability.** Link each discrepancy to its evidence and affected
   canonical artifact or implementation boundary.

## Reconciliation Template

Before creating a new document, apply
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
Prefer updating the existing reconciliation when it owns the same baseline,
scope, and decision.

When persisting a standalone Markdown reconciliation, follow
[Markdown Artifact Frontmatter](../iterative-up-analysis-design/references/markdown-artifact-frontmatter.md)
and [Readable Technical Artifacts](../iterative-up-analysis-design/references/readable-technical-artifacts.md).
State the consequential agreement, drift, gap, or uncertainty before the full
perspective matrix.

```markdown
---
type: "Design Reconciliation"
title: "Design Reconciliation: [Scope]"
description: "[Recovered and documented perspectives compared]"
id: "[Stable reconciliation ID when cross-referenced]"
status: "[draft | active | resolved]"
revision: "[Implementation commit, tag, build, or snapshot]"
tags: [reverse-engineering, reconciliation]
---

# Design Reconciliation: [Scope]

## At a Glance

[Explain what agrees or differs, why the difference matters, and who or what
must resolve any remaining uncertainty.]

## Baseline

- Implementation: [revision]
- Recovered artifacts: [IDs and revisions]
- Documents and decisions: [IDs and lifecycle]
- Executed evidence: [commands, tests, observations, or not run]

## Perspective Matrix

| Claim | As-built | As-tested/observed | As-documented | Intended/historical | Classification |
|---|---|---|---|---|---|
| [claim] | [evidence] | [evidence] | [evidence] | [evidence] | [result] |

## Discrepancies and Impact

- [classification]: [evidence, confidence, temporal status, and impact]

## Recommended Authority and Action

- [who or what must decide]: [smallest justified next step]

## Residual Unknowns

- [question and evidence needed]
```

## Red Flags

- Declaring code correct merely because it is current.
- Declaring documentation correct without checking lifecycle or implementation
  revision.
- Calling a difference a defect when intent is unknown.
- Treating an unexecuted test as current runtime evidence.
- Erasing historical artifacts instead of marking their lifecycle.

## Verification

- [ ] Compared claims share the same scope and lifecycle point.
- [ ] Implementation revision, artifact versions, and executed evidence are
      explicit.
- [ ] Authority is selected by question rather than a universal source ranking.
- [ ] Every difference has a classification, impact, evidence, and confidence.
- [ ] Retired and superseded behavior remains distinguishable from drift.
- [ ] Recommendations identify the smallest authoritative next action without
      silently mutating code or documents.
- [ ] The opening states the consequential result before the evidence matrix.
- [ ] A standalone reconciliation exposes identity, revision, summary, and
      lifecycle metadata in one frontmatter block.
