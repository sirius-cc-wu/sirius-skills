---
name: reverse-engineer-software-system
description: Coordinates evidence-driven reverse engineering of existing software. Use when planning a bounded recovery effort across repository reconnaissance, observable behavior, as-built architecture, documentation drift, or modernization preparation.
---

# Reverse Engineer Software System

## Overview

Recover only the system knowledge needed for a concrete decision. Coordinate
reconnaissance, behavior recovery, architecture reconstruction, and
reconciliation while keeping observations, inferences, intent, and history
distinct.

## When to Use

- A codebase must be understood before maintenance, migration, modernization,
  onboarding, audit, or resumed development.
- Requirements or design documents are missing, stale, contradictory, or mixed
  with retired behavior.
- A team needs an evidence-backed as-built model rather than a symbol inventory.
- Do not use for a small isolated change whose relevant behavior and ownership
  are already clear.

## Evidence Discipline

Read [Recovery Evidence and Confidence](references/recovery-evidence.md) before
recording findings. Fix the repository revision under study, attach evidence
to every material claim, and preserve conflicts instead of selecting the most
convenient source.

## Workflow

1. **State the recovery decision.** Name the maintenance, migration, audit,
   onboarding, risk, or documentation question the recovered knowledge must
   answer.
2. **Inspect governance and freeze scope.** Read repository instructions,
   record the revision, identify authorized roots, and separate read-only
   analysis from any probes or changes requiring approval.
3. **Survey the system.** Use
   [Survey Existing System](../survey-existing-system/SKILL.md) to map entry
   points, interfaces, dependencies, verification surfaces, and likely risk
   areas.
4. **Select a representative slice.** Prefer one user-visible scenario,
   external interface, security boundary, data flow, or change hotspot over an
   exhaustive whole-repository model.
5. **Recover observable behavior when needed.** Use
   [Recover System Behavior](../recover-system-behavior/SKILL.md) to establish
   black-box events, outcomes, failures, and externally visible constraints.
6. **Reconstruct architecture when needed.** Use
   [Reconstruct Software Architecture](../reconstruct-software-architecture/SKILL.md)
   for module, component, runtime, state, deployment, and trust-boundary views.
7. **Reconcile competing accounts.** Use
   [Reconcile Recovered Design](../reconcile-recovered-design/SKILL.md) when
   code, tests, runtime evidence, documents, decisions, or history disagree.
8. **Close the recovery iteration.** Answer the original question, link the
   recovered artifacts, expose residual uncertainty, and name the smallest
   next investigation or forward-engineering step.

## Artifact Lifecycle

- Treat recovered artifacts as as-of-revision descriptions, not timeless
  requirements.
- Keep recovered models separate from canonical intended requirements until a
  stakeholder or authoritative decision validates the intent.
- Refine one canonical recovered artifact for the selected scope; keep the
  recovery record as iteration history.
- Hand validated behavior to forward use-case, contract, design, and
  implementation skills without laundering inferences into requirements.

## Recovery Record Template

Before creating a new document, apply
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
Prefer updating an existing recovery record or keeping evidence near its
executable source when either is a sufficient owner.

When persisting a standalone Markdown record, follow
[Markdown Artifact Frontmatter](../plan-up-iterations/references/markdown-artifact-frontmatter.md)
and use STE-style.
The decision and scope normally provide the reader-oriented opening; retain
evidence status and uncertainty when simplifying later sections.

```markdown
---
type: "Reverse Engineering Record"
title: "Recovery: [Question or Slice]"
description: "[Decision this recovery effort supports]"
id: "[Stable recovery ID when cross-referenced]"
status: "[planned | active | completed]"
revision: "[Commit, tag, build, or snapshot]"
tags: [reverse-engineering]
---

# Recovery: [Question or Slice]

## Decision and Scope

- Decision: [why this knowledge is needed]
- In scope: [bounded interfaces, scenarios, components, or paths]
- Out of scope: [explicit exclusions]

## Evidence Plan

- [perspective and sources to inspect or observe]

## Recovered Artifacts

- [survey, behavior model, architecture view, reconciliation]

## Findings

- [claim with evidence status, confidence, and temporal status]

## Contradictions and Unknowns

- [unresolved conflict or uncertainty]

## Outcome and Next Step

- [answer, residual risk, and smallest justified follow-up]
```

## Red Flags

- Attempting to model the entire repository before naming a decision.
- Treating source code as proof of business intent.
- Mixing current, retired, and superseded behavior in one undated model.
- Producing diagrams without claim-level evidence or uncertainty.
- Changing production code merely to make it easier to explain.

## Verification

- [ ] The recovery question, revision, scope, and exclusions are explicit.
- [ ] Every material claim follows the shared evidence vocabulary.
- [ ] Selected views are justified by the decision, risk, or scenario.
- [ ] As-built, as-tested, as-observed, as-documented, intended, and historical
      perspectives remain distinguishable.
- [ ] Contradictions and residual unknowns remain visible.
- [ ] The outcome answers the original question or identifies the precise
      evidence still required.
- [ ] The decision and scope orient readers before the evidence plan and findings.
- [ ] A standalone record exposes identity, revision, summary, and lifecycle
      metadata in one frontmatter block.
