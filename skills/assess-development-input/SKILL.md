---
name: assess-development-input
description: Assesses requirements-shaped inputs from external or mixed workflows and decides whether their content is ready for system recovery, inception, use-case modeling, iterative design, or tested implementation while preserving source meaning, approval state, and unresolved uncertainty. Use when intent statements, specifications, proposals, BDD scenarios, story maps, brainstorm notes, issue descriptions, or similar material exist but their readiness and correct Sirius entry point are unclear.
---

# Assess Development Input

## Overview

Assess an incoming development artifact without assuming that its format proves
its completeness. Recommend the narrowest Sirius skill that owns the next
material decision, or stop with an explicit prerequisite when no Sirius skill
can responsibly proceed.

## When to Use

- Requirements-shaped material was produced by another skill, method, team, or
  repository and its Sirius entry point is unclear.
- Several plausible next skills exist and selecting one requires examining the
  content rather than its label or format.
- A proposal appears implementation-ready but its approval, evidence,
  behavioral detail, or verification oracle may be incomplete.
- Do not use when the user has already selected the correct skill and supplied
  that skill's entry conditions.
- Do not use to conduct discovery, rewrite an artifact, coordinate a full
  lifecycle, or implement the requested behavior.

## Source Discipline

- Treat input names and formats as hints, not readiness evidence. A feature
  file is not necessarily approved behavior; interview notes are not
  necessarily requirements; a proposal is not necessarily feasible.
- Preserve source references, revisions, stated approval, non-goals, and open
  questions. Never upgrade candidate, inferred, or contested statements to
  approved decisions.
- Separate intended behavior from claims about an existing system. Route
  unevidenced current-state claims to recovery before treating them as facts.
- Judge only the completeness needed for the next decision. Do not require
  every input to contain every possible requirements or design artifact.

## Workflow

1. **Identify the input and requested outcome.** Name the material being
   assessed, its known revision or source, the outcome it is meant to support,
   and any explicit non-goals.
2. **Inventory decision-relevant content.** Record what the input actually
   establishes about purpose, actors, system boundary, behavior, examples,
   rules, constraints, quality attributes, approval, current-system evidence,
   and verification. Keep missing content distinct from content that is present
   but contested.
3. **Find the first material gap.** Ask which unresolved decision would force
   the next agent to guess, produce invalid design, or create an unreliable
   oracle. Ignore optional detail that does not block the next useful step.
4. **Select one owner.** Use the routing guide below to choose the narrowest
   Sirius skill that owns that decision. Prefer a specialist over a coordinator
   when the gap is already localized.
5. **Assess readiness.** Mark the input `ready`, `needs prerequisite`, or
   `blocked` for the selected skill. Base the status on visible content,
   evidence, and approval rather than a numeric confidence or completeness
   score.
6. **Produce the routing record.** State established decisions, material
   uncertainty, the recommended skill, the rationale, and any stop condition.
   Do not translate the source into the destination skill's artifact.
7. **Respect the authority boundary.** Recommend the handoff without invoking
   the selected skill, creating its artifacts, or changing production state
   unless the user also authorizes that work.

## Routing Guide

Choose the first row that owns the material decision blocking safe progress.
The source method or file format never determines the route.

| Content condition | Next Sirius skill |
|---|---|
| Claims about current commands, behavior, architecture, or constraints need evidence | `reverse-engineer-software-system` |
| Technical discussions, findings, incidents, or candidate changes need a consequential direction framed for review | `author-software-proposal` |
| Opportunity, vision, business case, feasibility, basic scope, or major risks are unclear | `inception` |
| Actors, user goals, system boundary, main scenarios, or extensions are unclear | `use-case-modeling` |
| Several requirements and design artifacts need a risk-sized iteration and durable ownership | `iterative-up-analysis-design` |
| Business concepts, vocabulary, associations, or attributes are unclear | `domain-modeling` |
| Actor-system events or system operations are unclear | `system-sequence-diagrams` |
| Non-trivial state changes, preconditions, or postconditions are unclear | `operation-contracts` |
| Object responsibility or ownership is unclear | `grasp-responsibility-design` |
| Object collaboration for a selected scenario is unclear | `use-case-realization` |
| Stable software structure needs a class-level summary | `uml-class-diagram-design` |
| Concrete creation, structural, communication, or variation forces justify pattern selection | `design-pattern-application` |
| A language-neutral design needs idiomatic language-specific adaptation | `software-design-language-adaptation` |
| A bounded behavior has an independent oracle such as an approved example, invariant, reference, or defect | `test-driven-implementation` |
| Observable behavior is protected and only internal structure should change | `behavior-preserving-refactoring` |
| Existing technical knowledge is authoritative but difficult to read | `rewrite-technical-artifacts` |

If the blocking decision belongs to a stakeholder, product owner, external
source owner, or another authority outside Sirius, report `blocked` and name
that prerequisite. Do not select a Sirius skill merely to avoid returning
upstream.

## Output

Use this concise conversational form by default:

```markdown
Input:
- [source, artifact, or revision]

Intended outcome:
- [what this material is meant to enable]

Readiness: [ready | needs prerequisite | blocked]

Established:
- [decision, evidence, or approved behavior]

Material uncertainty:
- [gap, conflict, missing approval, or none]

Recommended next skill: `[one Sirius skill, or none while blocked]`

Rationale:
- [why that owner matches the first material gap]

Prerequisite or stop condition:
- [what must be resolved before proceeding, or none]
```

## File Output

Keep the assessment conversational unless it needs a durable cross-session or
cross-team handoff. Before creating a standalone document, apply the
[Artifact Selection Budget](../iterative-up-analysis-design/references/artifact-selection-budget.md).
Prefer an existing issue, proposal, or aggregate feature artifact when it is a
sufficient owner.

When a standalone Markdown assessment is justified, follow
[Markdown Artifact Frontmatter](../iterative-up-analysis-design/references/markdown-artifact-frontmatter.md)
and
[Readable Technical Artifacts](../iterative-up-analysis-design/references/readable-technical-artifacts.md).
Use this frontmatter, giving the record a stable ID only when it will be
cross-referenced, then place the concise output fields in the body without
copying the source material:

```markdown
---
type: "Development Input Assessment"
title: "Assessment: [Input name]"
description: "[Readiness and recommended next owner in one sentence]"
id: "[Stable assessment ID when cross-referenced]"
status: "[active | blocked | completed]"
tags: [intake, routing]
---
```

## Red Flags

- Routing by whether the input is called a specification, story map, feature,
  proposal, interview, or brainstorm.
- Converting raw evidence, candidate requirements, or examples into approved
  decisions during assessment.
- Rewriting the input into a preferred Sirius format before choosing its owner.
- Sending every input to the iterative coordinator when a specialist owns the
  first gap.
- Sending incomplete behavior to implementation because acceptance-language
  syntax is present.
- Producing a roadmap of many downstream skills instead of choosing the next
  responsible owner.
- Automatically continuing into the selected skill without user authority.

## Verification

- [ ] The assessment identifies the actual input, source or revision, intended outcome, and non-goals when known.
- [ ] Readiness is based on content, evidence, approval, and the next decision rather than the originating method or format.
- [ ] Established decisions remain distinct from gaps, conflicts, inference, and missing approval.
- [ ] Exactly one next Sirius skill is recommended, unless an external prerequisite blocks responsible routing.
- [ ] The rationale names the first material decision owned by that skill.
- [ ] No requirement, approval, current-system fact, or verification oracle was invented or silently upgraded.
- [ ] The input was not rewritten into the selected skill's artifact.
- [ ] The selected skill was not executed without separate user authority.
- [ ] Any standalone assessment passes the artifact selection budget and uses readable Markdown with appropriate frontmatter.
