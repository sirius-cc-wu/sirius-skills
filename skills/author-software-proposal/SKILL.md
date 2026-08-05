---
name: author-software-proposal
description: Creates or substantively revises decision-ready software proposals from technical discussions, findings, incidents, candidate changes, and existing drafts. Use when asked to write, draft, create, or update a software or technical proposal; frame a consequential change before implementation; separate current evidence from intended behavior; or document scope, alternatives, risks, open decisions, and acceptance evidence without approving or implementing the change.
---

# Author Software Proposal

## Overview

Turn technical input into a proposal that lets its intended reviewers understand
the problem, evaluate a direction, and make the next decision. Preserve the
difference between what is known now, what is inferred, what is proposed, and
what remains undecided.

## When to Use

- A discussion, investigation, incident, review finding, or candidate change
  needs a durable proposal before implementation or broader design work.
- An existing proposal needs substantive changes to its direction, scope,
  alternatives, risks, acceptance evidence, or open decisions.
- Reviewers need current-system evidence and intended behavior in one
  decision-oriented artifact without confusing the two.
- Do not use merely to assess whether an existing proposal is ready or choose
  its next Sirius owner; use `assess-development-input`.
- Do not use for a semantic-preserving readability pass; use
  `rewrite-technical-artifacts`.
- Do not replace an incident record, operator guide, accepted decision record,
  verification plan, use case, implementation brief, or issue when that
  artifact already owns the requested outcome.

## Workflow

1. **Read local authority.** Inspect the nearest repository guidance, proposal
   governance, indexes, templates, validators, and neighboring proposals.
   Preserve repository-defined paths, lifecycle states, identifiers, and
   frontmatter instead of imposing a Sirius-specific format.
2. **Confirm proposal ownership.** Apply the
   [Artifact Selection Budget](../iterative-up-analysis-design/references/artifact-selection-budget.md).
   Update an existing canonical proposal when it already owns the change. Use
   a proposal when a consequential direction still needs review or agreement;
   use an issue or implementation brief for already-approved work, and a
   decision record for a choice that has already been made.
3. **Identify the decision.** Name the primary reviewers, the decision or
   feedback requested from them, the important consequence, and any deadline
   or compatibility boundary. If these cannot be established, expose the gap
   instead of inventing urgency or authority.
4. **Inventory the source material.** Record relevant discussions, findings,
   code and test evidence, runtime observations, existing documents, approved
   decisions, assumptions, and unresolved questions. Preserve their revisions,
   confidence, and approval states when known.
5. **Separate evidence from intent.** State current behavior only to the level
   supported by cited or inspectable evidence. Label inference and uncertainty.
   Put proposed behavior in a distinct section and never turn current code,
   historical behavior, or an author's recommendation into approved intent.
   If current-state claims require substantial recovery, hand that question to
   `reverse-engineer-software-system` rather than filling the gap with prose.
6. **Draft for the reviewer.** Follow
   [Readable Technical Artifacts](../iterative-up-analysis-design/references/readable-technical-artifacts.md).
   Open with the problem, proposed direction, and important consequence. For
   stateful, concurrent, operational, or otherwise unfamiliar behavior, show
   one representative scenario before exact rules and edge cases.
7. **Specify only the material detail.** Include the relevant subset of:
   scope and non-goals; constraints; proposed behavior or design direction;
   compatibility, migration, security, and operational effects; alternatives;
   risks and mitigations; acceptance evidence; and open decisions. Define each
   rule once and link to its canonical owner rather than repeating it.
8. **Make acceptance reviewable.** Describe observable examples, invariants,
   measurements, compatibility checks, or manual evidence that could show the
   proposal was implemented successfully. Distinguish required acceptance
   constraints from suggested verification methods and avoid claiming that
   unexecuted checks passed.
9. **Preserve the authority boundary.** Keep a new proposal in the repository's
   draft or proposed state. Recommendations may be explicit, but undecided
   alternatives remain undecided until the responsible authority chooses.
   Do not accept, promote, implement, commit, push, or publish the proposal
   unless the user separately authorizes that action.
10. **Validate and review.** Run repository-specific proposal, frontmatter,
    link, and index checks; inspect the final diff; and verify the proposal
    against the source inventory. Use `rewrite-technical-artifacts` as an
    optional final pass only when substantial reader friction remains.

## Proposal Shape

Choose headings that fit the repository and decision. A useful default reading
order is:

1. problem, proposed direction, and consequence;
2. one representative scenario when it materially helps;
3. current evidence and constraints;
4. proposed scope, non-goals, behavior, and exact rules;
5. compatibility, operational effects, and rollout when relevant;
6. alternatives and why the recommendation is preferred;
7. risks, acceptance evidence, and open decisions; and
8. the next decision or authorized handoff.

Omit empty or irrelevant sections. Prefer one proposal file. Create a proposal
directory only when supporting references have independent value but belong to
the same proposal lifecycle.

## File Output

Follow repository-defined proposal frontmatter when it exists. Otherwise,
follow
[Markdown Artifact Frontmatter](../iterative-up-analysis-design/references/markdown-artifact-frontmatter.md)
with this minimal fallback:

```markdown
---
type: "Software Proposal"
title: "[Human-readable proposal title]"
description: "[Problem and proposed direction in one sentence]"
status: "draft"
tags: ["proposal"]
---
```

Add a stable ID only when the proposal will be cross-referenced. Update a
proposal index only when local governance requires or already maintains one.

## Red Flags

- The opening describes the document-writing task instead of the problem and
  consequence reviewers must evaluate.
- Current behavior, desired behavior, inference, and approval are blended
  together.
- A preferred implementation is presented without alternatives or forces that
  justify narrowing the choice.
- Acceptance criteria merely restate the proposal or prescribe tests that
  cannot distinguish success from failure.
- Compatibility claims ignore known external clients, stored data, deployment
  order, or operational recovery.
- A new directory, index, terminology table, or exhaustive template adds more
  ceremony than decision value.
- Drafting silently changes lifecycle status or continues into implementation,
  commit, or publication.

## Verification

- [ ] The proposal names its reviewers, requested decision, problem, direction, and important consequence.
- [ ] The canonical owner was updated instead of creating a duplicate artifact.
- [ ] Current evidence, inference, proposed behavior, approval, and uncertainty remain distinct.
- [ ] The opening is understandable before exact rules and reference detail.
- [ ] Scope, non-goals, constraints, alternatives, risks, and open decisions are proportionate to the decision.
- [ ] Acceptance evidence is observable and is not reported as executed when it was only proposed.
- [ ] Compatibility, migration, operational, security, and recovery effects are addressed when relevant.
- [ ] Repository lifecycle, frontmatter, indexing, and layout conventions are preserved.
- [ ] No acceptance, implementation, commit, push, or publication occurred without separate authority.
- [ ] Repository checks and final-diff inspection pass, or remaining gaps are reported precisely.
