---
name: stakeholder-requirements-elicitation
description: Plans stakeholder research and records traceable client evidence through participant interviews, contextual observation, workshops, document review, and prototype feedback. Use when selecting affected stakeholder roles, clarifying decision authority, or discovering unmet needs before requirements synthesis, inception, or use-case modeling.
---

# Stakeholder Requirements Elicitation

## Overview

Learn how affected people actually work and what constrains them while keeping
source evidence distinct from requirements, solution requests, and agent
hypotheses. Finish with an evidence set and explicit coverage gaps, not a
software specification.

## When to Use

- A requester may not represent affected roles, or a proposed solution obscures
  the underlying problem and current work.
- Interviews, observation, workshops, documents, or prototypes are needed to
  resolve evidence, coverage, or authority gaps before synthesis.
- Do not use to approve requirements, choose architecture, write use cases, or
  create implementation tasks.

## Evidence Discipline

Read
[Recovery Evidence and Confidence](../reverse-engineer-software-system/references/recovery-evidence.md)
and reuse its claim-status and confidence vocabulary where the meanings fit.
Keep stakeholder statements, observed work, repository facts, and agent
hypotheses distinct.

Treat every source as limited evidence. A requested solution is evidence about
a perspective, not automatically a requirement. Agent confidence never becomes
stakeholder approval.

## Workflow

1. **Frame discovery.** State the problem, decision informed, known boundary,
   and non-goals.
2. **Map coverage and authority.** Identify applicable sponsors,
   decision-makers, operators, users, support, compliance, and external roles.
   Record representation, access gaps, and decision authority; do not infer
   authority from seniority or payment.
3. **Choose proportionate methods.** Use interviews for goals, observation for
   actual work, workshops for shared understanding and conflict, documents for
   durable rules, and prototypes for reactions to alternatives. Address only
   the current uncertainty or risk.
4. **Plan responsible capture.** Establish consent, intended use, recording,
   sensitivity, access, retention, deletion, and publication limits. Prefer
   roles over names unless identity is material.
5. **Acquire evidence neutrally.** Ask open questions about recent events,
   current work, exceptions, consequences, and workarounds. Label hypotheses;
   record observed events before interpreting them.
6. **Record sources independently.** Give each material source an opaque ID and
   record method, role, authority, conditions or revision, content, claim
   status, confidence, sensitivity, and limits. Preserve disagreement.
7. **Assess sufficiency.** Check role coverage, evidence diversity,
   contradictions, open questions, and observed-versus-reported behavior.
   Independent corroboration raises confidence; repetition from one source does
   not.
8. **Close or stop visibly.** Produce coverage, plan, evidence records,
   conflicts, and open questions. Stop and state limitations when a material
   role, consent, or conflict investigation is unavailable.

Without live access, prepare the map and plan, record the gap, and request
coordination. Do not simulate stakeholder answers.

## Evidence Record Shape

Use the smallest existing artifact that can own the evidence. Every material
record retains `Opaque source ID`, acquisition method, source role,
`Authority:`, conditions or revision, content,
`Claim status and confidence:`, `Sensitivity and handling:`, and
`Limits and conflicts:` with related source IDs.

Keep raw notes private when appropriate. Link sanitized records to protected
sources without copying confidential material.

## File Output

Apply
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
Prefer an existing discovery record or aggregate feature artifact.

For a standalone Markdown record, follow
[Markdown Artifact Frontmatter](../iterative-risk-driven-analysis-design/references/markdown-artifact-frontmatter.md)
and use STE-style.
When a standalone record is justified, read and adapt the
[Stakeholder Evidence Record Template](references/stakeholder-evidence-record-template.md).

## Red Flags

- Questions embed a preferred solution or expected answer.
- Treating one available requester as every stakeholder class.
- Recording interpretations as observations or removing contradictory details.
- Publishing raw personal, contractual, or commercially sensitive evidence.
- Measuring completeness by interview count rather than material coverage.
- Producing requirements, acceptance criteria, architecture, or implementation
  plans from evidence collection.

## Verification

- [ ] The discovery decision, non-goals, roles, authority, representation, and access gaps are explicit.
- [ ] Methods are proportionate to the current uncertainty or risk.
- [ ] Consent, sensitivity, retention, access, and publication handling are explicit.
- [ ] Statements, observations, repository facts, and hypotheses remain distinct.
- [ ] Every material claim has a source ID, status, confidence, and limits.
- [ ] Conflicts and missing coverage remain visible.
- [ ] The result stops at evidence without synthesizing requirements or designing software.
- [ ] Standalone Markdown has one frontmatter block and a reader-oriented opening.
