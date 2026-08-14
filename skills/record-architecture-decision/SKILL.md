---
name: record-architecture-decision
description: Records or supersedes one consequential architecture decision as a short Architecture Decision Record (ADR) with explicit status, authority, context, forces, serious alternatives, consequences, uncertainty, and reconsideration triggers. Use when asked to write, create, capture, update, supersede, or list the governing ADR for a database, API, integration, deployment, security, runtime, dependency, or other cross-cutting technical choice; use the relevant design skill to make an unresolved design choice and reverse engineering to recover undocumented rationale.
---

# Record Architecture Decision

## Overview

Make one consequential architecture decision easy to find and understand later.
An Architecture Decision Record (ADR) is a short historical record of the
choice, why it was made, the serious alternatives, and its ramifications. The
writing can clarify a proposed choice, but this skill never supplies missing
decision authority or turns inferred rationale into fact.

This workflow distills Martin Fowler's
[Architecture Decision Record](https://martinfowler.com/bliki/ArchitectureDecisionRecord.html)
guidance while preserving Sirius rules for artifact budgeting, opaque
identifiers, repository-local conventions, evidence, and authorization.

## When to Use

- A consequential, cross-cutting, or expensive-to-reverse architecture choice
  needs a durable record.
- Reviewers need one short proposed ADR to discuss a bounded architecture
  choice with its forces and alternatives.
- An accepted ADR must be superseded because context or requirements changed.
- A repository needs the governing ADR for a choice to be discoverable by
  future maintainers and agents.
- A maintainer asks which recorded architecture decisions currently govern a
  product, subsystem, or cross-cutting concern.
- Do not create an ADR for every local implementation choice, pattern use, or
  responsibility assignment. Keep those in the owning design artifact unless
  they independently pass the artifact-selection budget.
- Do not use an ADR to choose an unresolved pattern, responsibility, lifecycle,
  or language design; use the corresponding specialist first.
- Do not reconstruct an undocumented decision or rationale from code alone;
  use reverse engineering and reconciliation, then obtain authoritative
  confirmation before recording intended architecture.

## Workflow

1. **Read local authority and history.** Inspect the nearest `AGENTS.md`,
   existing ADRs and indexes, decision governance, templates, validators,
   identifier rules, and relevant accepted or superseded records. Preserve the
   established location, format, filename scheme, headings, and statuses.
2. **Apply the creation gate.** Use the
   [Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
   Update an existing proposed ADR when it already owns the choice. Create one
   standalone ADR only when the decision is durable, has no sufficient owner,
   and needs an independent lifecycle.
3. **Bound one decision.** State the product or ecosystem scope and express one
   architecture choice in a sentence. Split unrelated choices; link supporting
   requirements, designs, experiments, benchmarks, and discussions rather than
   copying them.
4. **Establish status and authority.** Use repository-defined statuses. Without
   them, use `proposed`, `accepted`, or `superseded`. Mark `accepted` only from
   explicit evidence that the responsible authority accepted this exact
   decision revision. If authority is absent, keep it `proposed` or stop.
5. **Establish the evidence baseline.** Identify the problem, relevant
   requirements, constraints, forces, advice, observations, and source
   revisions. Separate verified current-system facts, stakeholder intent,
   inference, and uncertainty. Route unsupported current-state claims to
   `reverse-engineer-software-system`.
6. **Record serious alternatives.** Include only credible alternatives that
   materially affected the choice, with their important benefits, costs, and
   reason they were not selected. Do not invent rejected options after the
   fact to make the decision look rigorous.
7. **Record ramifications.** State positive and negative consequences,
   compatibility and migration effects, operational or security obligations,
   and follow-up work when material. Consequences are not implementation
   authorization.
8. **Record uncertainty and reconsideration triggers.** Calibrate confidence
   from the available evidence and name contextual changes, measurements, or
   failed assumptions that should cause the decision to be reevaluated. Do not
   convert confidence into approval.
9. **Draft for fast retrieval.** Put the decision, status, and important
   consequence first; then context and forces, alternatives, consequences,
   confidence, advice, and references. Keep the ADR to roughly one or two pages
   when possible and link detailed evidence.
10. **Place and identify it safely.** Follow
    [Design Repository Artifact Layout](../design-repository-artifact-layout/SKILL.md)
    when no decision convention exists or several homes compete. Treat IDs as
    opaque: continue an explicit repository scheme, but do not infer dates or
    sequence numbers or invent a monotonic numbering policy. Use one file per
    ADR unless established governance says otherwise.
11. **Preserve history.** A proposed ADR may be revised during review. Do not
    substantively rewrite an accepted ADR when the decision changes. Create a
    new ADR, link it as the successor, and make only the lifecycle/link update
    to the old record that repository governance requires. Never reuse an old
    ADR identifier for a different choice.
12. **Validate and stop.** Run ADR, frontmatter, identifier, link, index, and
    repository checks; inspect the diff; and report status, authority evidence,
    residual uncertainty, and any follow-up. Do not implement, commit, or
    publish without separate authorization.

## ADR Shape

Preserve an established template. Without one, follow
[Markdown Artifact Frontmatter](../iterative-risk-driven-analysis-design/references/markdown-artifact-frontmatter.md)
and
use STE-style,
then use this proportionate shape. Remove optional fields and empty sections.

```markdown
---
type: "Architecture Decision"
title: "[Decision in a short human-readable phrase]"
description: "[Chosen direction and important consequence]"
id: "[Opaque stable ID only when repository rules or cross-references require it]"
status: "[proposed | accepted | superseded]"
supersedes: "[Prior ADR ID or path, only when applicable]"
tags: ["architecture", "decision"]
---

# [Decision title]

## Decision

[One bounded choice, its status, scope, and important consequence.]

- Decision authority: [role or governing source]
- Authority evidence: [approval record and revision; omit while merely proposed]

## Context and Forces

- [Problem, requirement, constraint, trade-off, and source link]

## Alternatives Considered

- **[Alternative]:** [material advantages, disadvantages, and why not selected]

## Consequences

- [Positive consequence]
- [Cost, risk, obligation, migration effect, or follow-up]

## Confidence and Reconsideration

- Confidence: [calibrated statement and evidence limit]
- Reconsider when: [context change, measurement, or failed assumption]

## Advice and References

- [Consulted expertise, material disagreement, supporting evidence, or link]
```

The `Advice and References` section is conditional. Summarize advice that
materially shaped the decision, especially when using an advice process; keep
full discussion elsewhere. Advice is not acceptance unless the consulted role
also has documented decision authority.

## Decision Discovery Mode

When asked which architecture decisions have been made, use a read-only mode:

1. Locate established ADR directories, indexes, templates, and status rules.
2. Read the records relevant to the requested product, subsystem, or concern.
3. Follow supersession links and distinguish `proposed`, governing `accepted`,
   and historical `superseded` decisions.
4. Return a concise table of decision ID or path, title, status, scope, governing
   successor when any, and canonical link.
5. Report gaps or conflicting records. Do not infer an undocumented decision or
   rationale from code, and do not silently create ADRs to complete the list.

## Discovery and Indexing

Before adding an ADR, search existing proposed, accepted, and superseded
records so the new file does not duplicate or silently contradict a governing
decision. Give the filename a readable decision phrase. Update an existing ADR
index when repository governance maintains one; do not create a ceremonial
index for a small collection. A current-decision view must preserve links to
superseded history rather than hiding it.

## Red Flags

- The ADR records several loosely related decisions.
- A choice is marked accepted because the requester agreed with an idea, the
  code already behaves that way, or the agent is confident.
- Current behavior is presented as decision rationale without evidence.
- Alternatives are decorative, implausible, or invented after the decision.
- Consequences list only benefits and omit migration, operations, security, or
  follow-up obligations that materially matter.
- A numeric ID, date-like ID, directory, or index is invented despite absent or
  conflicting repository rules.
- A local implementation detail receives a standalone ADR without an
  independent consumer and lifecycle.
- An accepted ADR is rewritten to make a later decision appear original.
- The ADR becomes a design specification, evidence archive, meeting transcript,
  implementation plan, or changelog.
- Recording the decision silently proceeds into implementation, commit, or
  publication.

## Verification

- [ ] The ADR captures exactly one consequential architecture decision, or read-only discovery reports only evidenced ADRs in the requested scope.
- [ ] A standalone ADR passes the value, ownership, and lifecycle gate.
- [ ] Repository location, format, identifier, status, template, and index conventions are preserved.
- [ ] Status and authority evidence are explicit; no inference or confidence was promoted to acceptance.
- [ ] The decision and important consequence appear before supporting detail.
- [ ] Context and forces are source-linked and distinguish fact, intent, inference, and uncertainty.
- [ ] Serious alternatives include material trade-offs and were not invented retrospectively.
- [ ] Positive and negative consequences, obligations, and follow-up are proportionate.
- [ ] Confidence and concrete reconsideration triggers are recorded.
- [ ] Advice is summarized only when material and is not confused with approval.
- [ ] An accepted decision remains historically stable and any replacement is a linked superseding ADR.
- [ ] The ADR stays brief and links detailed supporting material instead of copying it.
- [ ] No implementation, commit, or publication occurred without separate authority.
- [ ] Repository checks and final-diff inspection pass, or remaining gaps are reported precisely.
