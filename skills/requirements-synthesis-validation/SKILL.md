---
name: requirements-synthesis-validation
description: Synthesizes source-linked stakeholder evidence into candidate goals, workflows, rules, constraints, quality attributes, scenarios, and concrete examples, then records validation and approval by the relevant authorities. Use when an identified evidence set exists but its implications, conflicts, or decision status must be made explicit before inception, use-case modeling, or implementation briefing.
---

# Requirements Synthesis Validation

## Overview

Turn a bounded evidence set into requirements that people can inspect, correct,
and approve. Preserve how every candidate was derived, who is authorized to
decide it, and which conflicts remain open. Finish with traceable requirements
knowledge, not software design or an implementation plan.

## When to Use

- Stakeholder statements, observations, policies, documents, or prototype
  responses have been gathered but remain difficult to act on together.
- Evidence conflicts, requested solutions obscure the underlying need, or the
  relevant decision authority is unclear.
- Important behavior needs concrete examples or measurable fit criteria before
  it can be confirmed.
- A requirement must be played back, corrected, validated, approved, contested,
  or superseded without losing its source history.
- Do not use to collect missing evidence, define project feasibility, write
  detailed use cases, choose architecture, or create implementation tasks.

## Evidence and Decision Discipline

Read the input evidence and the evidence-record guidance in
[Stakeholder Requirements Elicitation](../stakeholder-requirements-elicitation/SKILL.md).
Reuse source IDs exactly as supplied. Do not rewrite raw notes, collapse
contradictory accounts, or infer stakeholder approval from agent confidence.

Use these requirement states consistently:

- `candidate`: synthesized but not yet validated by an appropriate stakeholder;
- `validated`: confirmed as an accurate statement or example by a relevant
  stakeholder, but not necessarily authorized as a binding decision;
- `approved`: accepted for the stated revision by the role authorized to make
  that decision;
- `contested`: relevant sources or authorities still disagree; and
- `superseded`: replaced by a traceable later requirement or decision.

Validation and approval are revision-specific. Record rejection and abstention
in the decision log without inventing a requirement status that hides what
happened.

## Workflow

1. **Bound the synthesis.** Identify the decision or problem being clarified,
   the exact evidence set and revisions in scope, known coverage gaps, and what
   this activity will not decide.
2. **Check readiness.** Confirm that material source IDs, source roles,
   authority, sensitivity, conflicts, and evidence limits are visible. Route
   missing evidence or stakeholder access to
   `stakeholder-requirements-elicitation`; do not simulate it.
3. **Synthesize without erasing provenance.** Derive candidate goals, current
   workflows, rules, constraints, quality attributes, scenarios, assumptions,
   and decisions. Link each statement to its supporting and contradicting
   source IDs. Keep a requested solution distinct from the outcome or problem
   it may represent.
4. **Shape inspectable candidates.** Give each material candidate an opaque ID,
   precise statement, kind, status, applicable actor or scenario, source links,
   authority needed, limits, and unresolved questions. Preserve manual IDs and
   validate them only against repository conventions.
5. **Make behavior concrete.** Add representative examples and counterexamples,
   or measurable fit criteria for quality attributes. Label values that still
   need stakeholder confirmation instead of choosing convenient thresholds.
6. **Expose conflicts and assumptions.** State which claims disagree, whose
   authority applies to each decision, the consequence of leaving it open, and
   the next evidence or decision needed. Availability or seniority alone does
   not settle a conflict.
7. **Play back by authority.** Present the smallest coherent set to the roles
   who can validate its accuracy and approve its decisions. Record the artifact
   revision, participant role, authority, outcome, corrections, abstentions,
   and date when known. Apply resulting status changes without rewriting the
   earlier history.
8. **Route accepted knowledge.** Update an existing canonical owner where one
   exists. Route vision, scope, feasibility, and business risks to `inception`;
   black-box actor goals and scenarios to `use-case-modeling`; domain terms and
   rules to `domain-modeling`; and cross-cutting quality attributes to a
   supplementary specification or established equivalent.
9. **Close or stop visibly.** Produce the discovery brief, requirement records,
   examples, decision and conflict log, open questions, and handoffs. Stop
   before software design. If a material decision lacks evidence or an
   authorized decision-maker, leave it candidate or contested rather than
   declaring the synthesis ready for implementation.

When live playback is unavailable, prepare the candidates and playback
questions, retain their `candidate` or `contested` states, and record the access
gap. Never manufacture validation, approval, participant quotes, or dates.

## Confidentiality

Carry forward sensitivity, access, retention, and publication constraints.
Prefer sanitized claims and protected-source links over copying raw personal,
contractual, or commercially sensitive evidence. Before publishing a discovery
brief or sending it to an external service, confirm that every included source
permits that use.

## File Output

Before creating a document, apply
[Artifact Selection Budget](../iterative-up-analysis-design/references/artifact-selection-budget.md).
Prefer updating existing requirements owners. A standalone discovery brief is
justified when the synthesis, validation history, and conflict log are reused
together and change independently from raw evidence.

For standalone Markdown, follow
[Markdown Artifact Frontmatter](../iterative-up-analysis-design/references/markdown-artifact-frontmatter.md)
and [Readable Technical Artifacts](../iterative-up-analysis-design/references/readable-technical-artifacts.md).
Use this proportionate shape, omitting empty sections:

```markdown
---
type: "Requirements Discovery Brief"
title: "Requirements Discovery: [Problem or Decision]"
description: "[Synthesis scope and important unresolved consequence]"
id: "[Stable opaque ID when cross-referenced]"
status: "[active | completed | completed-with-gaps | blocked | superseded]"
tags: ["requirements", "validation"]
---

# Requirements Discovery: [Problem or Decision]

## Purpose and Boundary

- Decision informed: [decision]
- Evidence set: [source IDs and revisions]
- Coverage limits: [known gaps]
- Non-goals: [what this synthesis does not decide]

## Synthesized Understanding

- Goal or outcome: [source-linked synthesis]
- Current workflow: [source-linked synthesis]
- Material constraints and quality attributes: [source-linked synthesis]

## Candidate Requirements

### [Opaque requirement ID]: [Short name]

- Kind: [goal | workflow | rule | constraint | quality attribute | scenario | decision]
- Statement: [precise, solution-neutral where possible]
- Status: [candidate | validated | approved | contested | superseded]
- Source evidence IDs: [supporting and contradicting IDs]
- Applies to: [actors, scenarios, data, or boundary]
- Example or fit criterion: [concrete behavior or measurable result]
- Validation and approval: [role, authority, revision, outcome, date if known]
- Limits and open questions: [uncertainty and responsible resolver]

## Validation and Decision Log

| Requirement | Revision | Participant role | Authority | Outcome | Correction or rationale |
|---|---|---|---|---|---|

## Conflicts and Open Questions

- [conflict, consequence, responsible role, and next evidence or decision]

## Handoffs

- [accepted knowledge, canonical owner, and status]
```

## Red Flags

- Producing polished requirements with no source IDs or evidence limitations.
- Treating a sponsor's solution request as the underlying outcome.
- Marking a requirement approved after playback to someone without authority.
- Resolving disagreement by majority vote, availability, or organizational rank
  when a different role owns the decision.
- Inventing thresholds, examples, business rules, quotes, or approval dates.
- Copying sensitive raw evidence into a broadly visible brief.
- Choosing interfaces, data schemas, components, architecture, or implementation
  tasks.

## Verification

- [ ] The evidence set, revisions, coverage gaps, and synthesis boundary are
      explicit.
- [ ] Every material candidate has an opaque ID, precise statement, status,
      source links, applicable context, and unresolved limits.
- [ ] Requested solutions remain distinguishable from goals and evidence.
- [ ] Concrete examples, counterexamples, or fit criteria are traceable and do
      not contain invented values.
- [ ] Validation, rejection, approval, abstention, conflict, and supersession
      preserve role, authority, revision, and history.
- [ ] Confidentiality and publication constraints survive synthesis.
- [ ] Missing evidence routes back to elicitation; accepted knowledge routes to
      the smallest canonical requirements owner.
- [ ] The result stops before software design and implementation planning.
- [ ] A standalone record has one frontmatter block and a reader-oriented
      opening.
