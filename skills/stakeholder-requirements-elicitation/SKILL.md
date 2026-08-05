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

- The requester may not represent operators, end users, support, compliance,
  sponsors, or other affected roles.
- A feature request states a solution but not the underlying problem or current
  workflow.
- Interviews, contextual observation, workshops, documents, or prototypes are
  needed before requirements can be synthesized.
- Stakeholders disagree, decision authority is unclear, or evidence is mostly
  hypothetical.
- Do not use to approve requirements, choose architecture, write use cases, or
  create implementation tasks.

## Evidence Discipline

Read
[Recovery Evidence and Confidence](../reverse-engineer-software-system/references/recovery-evidence.md)
before recording claims. Reuse its claim-status and confidence vocabulary where
the meanings fit, but keep intended stakeholder statements distinct from
observed work and repository facts.

Treat each interview statement, observed action, document, prototype response,
and repository discovery as evidence with limits. A participant's requested
solution is evidence about their perspective; it is not automatically a
requirement. Never turn agent confidence into stakeholder approval.

## Workflow

1. **Frame the discovery decision.** State the problem area, the decision this
   evidence will inform, the system boundary if known, and what this activity
   will not decide.
2. **Map stakeholder coverage.** Identify sponsors, decision-makers, operators,
   end users, support, compliance, and affected external roles as applicable.
   Record who is represented, who is missing, and who has authority over which
   decisions. Do not assume seniority or payment establishes authority for
   every rule.
3. **Choose proportionate methods.** Select interviews for goals and meanings,
   observation for actual work, workshops for shared understanding and
   conflict exposure, document review for durable rules, and prototypes for
   reactions to concrete alternatives. Use only the methods needed for the
   current risk.
4. **Plan responsible capture.** Establish consent, intended use, recording
   method, sensitivity, access, retention, deletion, and publication limits.
   Prefer stakeholder roles over personal names unless identity is material.
5. **Acquire evidence neutrally.** Ask open questions about recent concrete
   events, current work, exceptions, consequences, and workarounds. Keep agent
   hypotheses in a labeled section rather than embedding guesses in every
   question. During observation, record what happened before interpreting why.
6. **Record sources independently.** Give every material source an opaque ID and
   capture its method, source role, authority, conditions or revision, content,
   claim status, confidence, sensitivity, and limits. Preserve disagreement
   instead of merging accounts into a smoother narrative.
7. **Assess sufficiency.** Check participant coverage, evidence diversity,
   contradictions, unanswered questions, and whether observed behavior differs
   from reported behavior. Corroboration raises confidence; repeated claims
   derived from one source do not.
8. **Close or stop visibly.** Produce the stakeholder coverage, elicitation
   plan, evidence records, conflicts, and open questions. If a material role is
   unavailable, consent is missing, or a conflict cannot be investigated,
   state the limitation and stop rather than claiming completeness.

When live stakeholder access is unavailable, prepare the map and elicitation
plan from the available context, record the access gap, and request the needed
coordination. Do not simulate stakeholder answers.

## Evidence Record Shape

Use the smallest existing artifact that can own the evidence. Each material
record should include:

- Opaque source ID
- Acquisition method
- Source or stakeholder role
- Relevant decision authority
- Capture date, document revision, or observation conditions
- Statement, quote, observation, prototype response, or repository fact
- Claim status and confidence
- Sensitivity, retention, access, and publication constraints
- Conflicts, limits, and related source IDs

Keep raw notes private when appropriate. A sanitized artifact may link to a
protected source without copying confidential material into the repository.

## File Output

Before creating a document, apply
[Artifact Selection Budget](../iterative-up-analysis-design/references/artifact-selection-budget.md).
Prefer an existing discovery record or aggregate feature artifact when it is a
sufficient owner.

For a standalone Markdown record, follow
[Markdown Artifact Frontmatter](../iterative-up-analysis-design/references/markdown-artifact-frontmatter.md)
and [Readable Technical Artifacts](../iterative-up-analysis-design/references/readable-technical-artifacts.md).
Use this proportionate shape, omitting empty sections:

```markdown
---
type: "Stakeholder Evidence Record"
title: "Stakeholder Evidence: [Problem or Decision]"
description: "[Discovery scope and decision this evidence informs]"
id: "[Stable opaque ID when cross-referenced]"
status: "[active | completed | completed-with-gaps | blocked | superseded]"
tags: ["requirements", "elicitation"]
---

# Stakeholder Evidence: [Problem or Decision]

## Discovery Purpose

- Decision informed: [decision]
- Boundary: [what this activity does and does not decide]

## Stakeholder Coverage

| Role | Relationship to work | Decision authority | Access or gap |
|---|---|---|---|

## Elicitation Plan

- [Method, participant or source, risk addressed, consent and capture plan]

## Evidence

### [Opaque source ID]

- Method: [interview | observation | workshop | document | prototype | repository]
- Source role: [role]
- Authority: [relevant decisions or none]
- Conditions or revision: [date, version, environment]
- Claim status and confidence: [status, confidence]
- Sensitivity and handling: [access, retention, publication]
- Content: [statement, observed action, or fact]
- Limits and conflicts: [limitations and related source IDs]

## Coverage Gaps and Conflicts

- [missing role, contradiction, or evidence needed]

## Open Questions

- [question and who can answer it]
```

## Red Flags

- Asking leading questions that embed the preferred solution or expected
  answer.
- Treating one available requester as every stakeholder class.
- Recording interpretations as observations or removing contradictory details.
- Publishing raw personal, contractual, or commercially sensitive evidence.
- Measuring completeness by interview count rather than material coverage.
- Producing candidate requirements, acceptance criteria, architecture, or an
  implementation plan from this skill.

## Verification

- [ ] The discovery decision and non-goals are explicit.
- [ ] Relevant stakeholder roles, authority, representation, and access gaps
      are recorded.
- [ ] Methods are proportionate to the current uncertainty or risk.
- [ ] Consent, sensitivity, retention, access, and publication handling are
      explicit where applicable.
- [ ] Statements, observations, repository facts, and agent hypotheses remain
      distinguishable.
- [ ] Every material claim has a source ID, status, confidence, and limits.
- [ ] Conflicts and missing coverage remain visible.
- [ ] The result stops at evidence and does not synthesize or approve
      requirements or design software.
- [ ] A standalone record has one frontmatter block and a reader-oriented
      opening.
