---
name: define-project-vision
description: Defines or refines an evidence-backed project vision with explicit identity, principles, non-goals, and accept-or-resist criteria. Use when a repository or independently sponsored initiative needs a durable vision, contribution policy, or vision revision; clarify candidate directions with external idea-refine or interview-me, mine repository history only as evidence, and obtain approval from the responsible vision authority.
---

# Define Project Vision

## Overview

Create the smallest durable statement of what a project exists to do, what it
refuses to become, and how a reviewer can judge a proposed change. A vision is
an approval-controlled policy, not a business case, feature roadmap, or
marketing summary.

## When to Use

- A repository or independently sponsored initiative lacks a shared project
  identity, principles, non-goals, or contribution-acceptance policy.
- An existing vision needs a revision after material approved direction or
  evidence has changed.
- Maintainers ask what the project should accept, resist, or deliberately not
  become.
- Do not use when one requester's intent is unclear; use external
  `interview-me`.
- Do not use when a candidate direction needs alternatives, assumptions, or
  MVP scope; use external `idea-refine`.
- Do not use to approve a business case, feasibility commitment, funding, or
  investment decision; use the responsible external product or portfolio
  process.
- Do not use to infer intended architecture or product behavior from an
  undocumented codebase.

## Inputs and Evidence

Use the smallest reliable input set:

- the responsible vision authority, project or initiative boundary, and the
  decision the vision must support;
- a confirmed candidate-direction one-pager from external `idea-refine`, when
  the direction is not already sufficiently clear;
- clarification from external `interview-me`, when one requester's intent is
  unclear;
- approved requirements, decisions, repository guidance, and existing vision
  artifacts; and
- relevant merged pull requests, commit messages, documentation, rejection
  history, and implementation evidence when history can reveal a pattern.

Treat history as evidence, not approval. Code, tests, commits, and prior
releases can support a draft but cannot establish the current vision or
business authority. Stop for the responsible authority when the sources are
sparse, conflicting, obsolete, or insufficient for a claimed principle.

External add-ons require the `all` installation. Otherwise, request the
responsible external clarification or candidate-direction process.

## Workflow

1. **Set the vision boundary.** Identify the project or independent initiative,
   intended users, responsible vision authority, current decision, existing
   vision status, and non-goals. Do not make a release, component, or completed
   milestone a project vision unless it has independent authority and scope.
2. **Check for an existing vision.** Treat an approved `VISION.md` or canonical
   vision artifact as the baseline. Propose a bounded, evidence-backed delta;
   do not create a competing vision document.
3. **Clarify the direction.** Route a vague candidate direction to external
   `idea-refine`. Route unclear individual intent to external `interview-me`.
   Preserve their result as candidate input until the responsible authority
   accepts it.
4. **Mine proportionate evidence.** Inspect approved artifacts and a relevant
   range of repository history. Record source revisions and recurring patterns:
   what the project builds, refuses, fixes at the root, or protects. Keep the
   evidence sheet conversational or otherwise ephemeral unless it has a
   justified independent lifecycle.
5. **Draft the acceptance policy.** State the project identity, intended users,
   durable principles, concrete non-goals, and accept-or-resist criteria. Make
   each claim traceable to approved intent, evidence, or authority-approved
   reasoning. Use short declarative sentences.
6. **Stress-test the draft.** Present a small set of concrete boundary cases:
   tempting off-mission features, principle conflicts, scope expansions, and
   ambiguous contributions. Explain both defensible outcomes. Replace trivial
   cases whose answer is already obvious.
7. **Obtain approval or preserve uncertainty.** Ask the responsible authority
   to approve, reject, or revise the draft. Record the authority and approved
   source revision. Return `needs prerequisite` rather than presenting an
   evidence-mined draft as approved.
8. **Route follow-up decisions.** Route business cases, feasibility commitments,
   and investment decisions to the responsible external product or portfolio
   process. Route actor goals to `use-case-modeling`, quality requirements to
   `specify-quality-constraints`, and architecture questions to
   `design-software-architecture`.

## Output

Before creating a new document, apply the
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
Prefer updating the existing canonical vision. Create `VISION.md` only when it
has a distinct consumer and lifecycle and repository governance permits it. Use
`design-repository-artifact-layout` when a justified vision lacks a canonical
home.

For a standalone Markdown file, follow
[Markdown Artifact Frontmatter](../iterative-risk-driven-development/references/markdown-artifact-frontmatter.md)
and use STE-style. Keep evidence references in the body. Do not commit review
transcripts or a separate answers ledger merely to preserve hypothetical
verdicts.

```markdown
---
type: "Vision"
title: "Vision: [Project or Initiative]"
description: "[One sentence stating the project purpose and acceptance boundary]"
id: "[Stable ID when cross-referenced]"
status: "[draft | proposed | approved | superseded]"
tags: [vision, governance]
---

# Vision: [Project or Initiative]

[Project] exists so that [intended user and outcome].
It owns [bounded responsibility].

## Principles

- [Principle]: [Concrete commitment and refusal]

## Non-Goals

- [Explicit excluded direction]: [Reason]

## Acceptance Policy

- A change aligns when [testable positive criterion].
- A change should be resisted when [testable negative criterion].

## Authority and Evidence

- Authority and status: [role, decision, and revision]
- Evidence: [approved artifact, pull request, commit, or source revision]
- Open questions: [unresolved authority or evidence]
```

## Boundaries

- External `idea-refine` owns candidate-direction exploration. External
  `interview-me` owns clarification of one requester's intent. This skill turns
  sufficiently grounded input into a project-level acceptance policy.
- The responsible external product or portfolio process owns business-case,
  feasibility, funding, and investment approval. A vision does not authorize
  those decisions.
- `use-case-modeling` owns actor goals and black-box behavior.
  `specify-quality-constraints` owns measurable quality requirements and
  binding constraints. `design-software-architecture` owns intended major
  structure.
- Repository history may reveal evidence but does not recover missing approval
  or make an inferred policy authoritative.

## Red Flags

- A vision repeats generic virtues without source evidence or a concrete
  acceptance consequence.
- A draft presents commit history, code, or a candidate idea as approved
  organizational intent.
- A business case, delivery plan, roadmap, or architecture design appears in
  the vision.
- Every hypothetical has an obvious answer or the authority never reviews the
  draft.
- A new `VISION.md` duplicates an approved canonical vision.
- A review transcript or answers ledger becomes a second source of truth.

## Verification

- [ ] The project or independent-initiative boundary and vision authority are
      explicit.
- [ ] Existing approved vision material is refined in place or its delta is
      explicit.
- [ ] Candidate direction, repository evidence, approved intent, and authority
      reasoning remain distinguishable.
- [ ] Each principle and non-goal has an evidence reference or
      authority-approved rationale.
- [ ] The acceptance policy gives concrete positive and negative tests for a
      proposed change.
- [ ] Boundary cases exposed non-trivial scope or principle decisions.
- [ ] Approval status, authority, and source revision are explicit; missing
      approval returns `needs prerequisite`.
- [ ] Business, requirements, and architecture decisions remain with their
      responsible owners.
- [ ] Any standalone vision passes the artifact budget and has one `Vision`
      frontmatter block.
