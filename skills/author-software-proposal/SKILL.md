---
name: author-software-proposal
description: Creates or substantively revises a decision-ready software proposal or proposed decision record from technical discussions, findings, incidents, candidate changes, and existing drafts. Use when asked to write, draft, create, or update a software or technical proposal; frame a consequential change before implementation; capture one focused architectural decision as a proposed ADR; separate current evidence from intended behavior; or document scope, alternatives, risks, open decisions, and acceptance evidence without approving or implementing the change.
---

# Author Software Proposal

## Overview

Turn technical input into one decision-seeking artifact that lets its intended
reviewers understand the problem, evaluate a direction, and make the next
decision. Use a proposed decision record (an ADR when the choice is
architectural) for one bounded consequential choice; use a software proposal
when exploration spans several decisions, stakeholders, or a wider scope.
Preserve the difference between what is known now, what is inferred, what is
proposed, and what remains undecided.

## When to Use

- Technical input needs a durable decision-seeking artifact before
  implementation or broader design work.
- One consequential, cross-cutting, or expensive-to-reverse choice needs a
  proposed decision record/ADR; broader exploration or several decisions need a
  software proposal.
- An existing proposal needs substantive changes to its direction, scope,
  alternatives, risks, acceptance evidence, or open decisions.
- Reviewers need current-system evidence and intended behavior separated in one
  decision-oriented artifact.
- Do not use merely to assess whether an existing proposal is ready or choose
  its next Sirius owner; use `assess-development-input`.
- Do not use for a semantic-preserving readability pass; use
  `rewrite-technical-artifacts`.
- Do not replace an incident record, operator guide, accepted decision record,
  verification plan, use case, implementation brief, or issue when that
  artifact already owns the requested outcome.
- Do not create both a proposal and a proposed decision record for the same
  focused choice unless they have different audiences or independently changing
  lifecycles.

## Workflow

1. **Read local authority.** Inspect repository guidance, proposal and decision
   governance, indexes, templates, validators, and neighboring artifacts.
   Preserve local paths, lifecycle states, identifiers, and frontmatter.
2. **Choose the artifact form and confirm ownership.** Apply the
   [Artifact Selection Budget](../iterative-up-analysis-design/references/artifact-selection-budget.md).
   Inspect existing proposals and decision records, and choose one canonical
   owner. Prefer a proposed decision record for one bounded choice; use a
   separate proposal for several decisions, broad exploration, or a distinct
   review lifecycle. Do not create a companion artifact merely to use a
   familiar name.
3. **Identify the decision.** Name reviewers, the requested decision or
   feedback, the important consequence, and any deadline or compatibility
   boundary. Expose gaps instead of inventing authority or urgency.
4. **Inventory sources.** Record discussions, findings, code and test evidence,
   runtime observations, existing documents, approved decisions, assumptions,
   and unresolved questions with revisions, confidence, and approval states.
5. **Separate evidence from intent.** State current behavior only from cited or
   inspectable evidence; label inference and uncertainty; keep proposed
   behavior distinct. If recovery is needed, hand it to
   `reverse-engineer-software-system`.
6. **Draft for the reviewer.** Follow
   [Readable Technical Artifacts](../iterative-up-analysis-design/references/readable-technical-artifacts.md).
   Lead with the problem, direction, and consequence; add a representative
   scenario before exact rules when it materially improves understanding.
7. **Specify material detail only.** Include relevant scope, constraints,
   behavior, compatibility, migration, security, operations, alternatives,
   risks, acceptance evidence, and open decisions. Define each rule once and
   link to its canonical owner.
8. **Make acceptance reviewable.** Describe observable examples, invariants,
   measurements, compatibility checks, or manual evidence without claiming
   that unexecuted checks passed.
9. **Preserve authority.** Keep new artifacts draft/proposed. Recommendations
   may be explicit, but only the responsible authority can accept them. After
   acceptance, preserve a decision record and supersede it rather than
   rewriting it. Do not accept, promote, implement, commit, push, or publish
   without separate authorization.
10. **Validate and review.** Run repository-specific proposal/decision,
    frontmatter, link, and index checks; inspect the diff; verify the artifact
    against its source inventory; and use `rewrite-technical-artifacts` only
    when substantial reader friction remains.

## Proposal Shape

For a broad proposal, use headings that fit the repository and decision. A
useful reading order is:

1. problem, proposed direction, and consequence;
2. one representative scenario when it materially helps;
3. current evidence and constraints;
4. proposed scope, non-goals, behavior, and exact rules;
5. compatibility, operational effects, and rollout when relevant;
6. alternatives and why the recommendation is preferred;
7. risks, acceptance evidence, and open decisions; and
8. the next decision or authorized handoff.

Omit empty sections. Prefer one proposal file; create a directory only when
supporting references have independent value but share its lifecycle.

For a focused proposed decision record, keep the artifact short and centered on
the decision, context, alternatives, rationale, consequences, and status. Link
to supporting proposal, requirements, design, risk, and verification artifacts
instead of copying them. If the repository uses ADRs, preserve its numbering,
location, frontmatter, and supersession convention.

## File Output

Follow repository-defined paths and frontmatter. When no proposal convention
exists, use
[Proposal Placement](../iterative-up-analysis-design/references/artifact-layouts.md#proposal-placement)
to choose a proposal collection or feature/product-area co-location. Follow
[Markdown Artifact Frontmatter](../iterative-up-analysis-design/references/markdown-artifact-frontmatter.md)
with this fallback:

```markdown
---
type: "Software Proposal"
title: "[Human-readable proposal title]"
description: "[Problem and proposed direction in one sentence]"
status: "draft"
tags: ["proposal"]
---
```

Add a stable ID only for cross-references. Update an index only when local
governance requires or maintains one.

For a focused decision, follow the repository's decision-record or ADR
template and lifecycle. Without one, use the same frontmatter rules with
`type: "Decision Record"` and `status: "proposed"`; do not invent acceptance
or architecture rationale.

## Red Flags

- The opening describes document-writing instead of the problem and
  consequence reviewers must evaluate.
- Current behavior, desired behavior, inference, and approval are blended.
- A preferred implementation lacks alternatives or the forces behind it.
- A focused choice receives both a proposal and a proposed decision record with
  duplicated content and no distinct audience or lifecycle.
- A proposed decision record is written as accepted, or an accepted decision is
  silently rewritten instead of superseded.
- Acceptance criteria merely restate the artifact or cannot distinguish
  success from failure.
- Compatibility claims ignore clients, stored data, deployment order, or
  operational recovery.
- A new directory, index, or exhaustive template adds more ceremony than value.
- Drafting silently changes lifecycle or continues into implementation,
  commit, or publication.

## Verification

- [ ] The artifact names reviewers, requested decision, problem, direction, and consequence.
- [ ] The artifact form fits the scope: proposed decision record for one focused choice, proposal for broader exploration.
- [ ] The canonical owner was updated instead of creating a duplicate artifact.
- [ ] Current evidence, inference, proposed behavior, approval, and uncertainty remain distinct.
- [ ] The opening is understandable before exact rules and reference detail.
- [ ] Scope, non-goals, constraints, alternatives, risks, and open decisions are proportionate.
- [ ] Acceptance evidence is observable and is not reported as executed when it was only proposed.
- [ ] Compatibility, migration, operational, security, and recovery effects are addressed when relevant.
- [ ] Repository lifecycle, frontmatter, indexing, and layout conventions are preserved.
- [ ] Proposed decision records remain proposed until the responsible authority accepts them; accepted decisions are not rewritten and later changes supersede them.
- [ ] No acceptance, implementation, commit, push, or publication occurred without separate authority.
- [ ] Repository checks and final-diff inspection pass, or remaining gaps are reported precisely.
