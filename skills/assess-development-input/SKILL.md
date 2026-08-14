---
name: assess-development-input
description: Assesses requirements-shaped input from external or mixed workflows and decides whether its content is ready for system recovery, inception, use-case modeling, architecture-decision recording, iterative design, or tested implementation while preserving source meaning, approval state, and unresolved uncertainty. Use when intent statements, specifications, proposals, BDD scenarios, story maps, brainstorm notes, issue descriptions, or similar material exist but their readiness and correct Sirius entry point are unclear.
---

# Assess Development Input

## Overview

Assess an incoming development artifact. Do not treat its format as proof of
completeness. Recommend the narrowest Sirius skill that owns the next material
decision. Stop with an explicit prerequisite when no Sirius skill can
responsibly proceed.

## When to Use

- Requirements-shaped material came from another skill, method, team, or
  repository, and its Sirius entry point is unclear.
- Several next skills appear plausible, and the content must determine the
  route.
- A proposal appears ready for implementation, but its approval, evidence,
  behavior, or verification oracle may be incomplete.
- Do not use when the user selected the correct skill and supplied its entry
  conditions.
- Do not use to conduct discovery, rewrite an artifact, coordinate a full
  lifecycle, or implement behavior.

## Source Discipline

- Treat input names and formats as hints, not readiness evidence. A feature file
  is not necessarily approved behavior. Interview notes are not necessarily
  requirements. A proposal is not necessarily feasible.
- Preserve source references, revisions, stated approval, non-goals, and open
  questions. Never upgrade candidate, inferred, or contested statements to
  approved decisions.
- Do not treat unsupported claims about the current system as facts. Verify
  them with the reverse-engineering skills before using them as requirements or
  design inputs.
- Judge only the completeness needed for the next decision. Do not require
  every input to contain every possible requirements or design artifact.

## Workflow

1. **Identify the input and outcome.** Name the material, its known revision or
   source, the outcome it should support, and its explicit non-goals.
2. **Inventory decision-relevant content.** Record what the input establishes
   about purpose, actors, system boundary, behavior, examples, rules,
   constraints, quality attributes, approval, current-system evidence, and
   verification. Keep missing content separate from contested content.
3. **Find the first material gap.** Identify the unresolved decision that could
   make the next agent guess, produce invalid design, or create an unreliable
   oracle. Ignore optional detail that does not block the next useful step.
4. **Select one owner.** Use the routing guide below to choose the narrowest
   Sirius skill that owns the decision. Prefer a specialist over a coordinator
   when the gap is localized. If requester intent or the candidate direction is
   unconfirmed, name external clarification or idea refinement as the
   prerequisite. Do not force a Sirius owner.
5. **Assess readiness.** Mark the input `ready`, `needs prerequisite`, or
   `blocked` for the selected skill. Base the status on visible content,
   evidence, and approval. Do not use a numeric confidence or completeness
   score.
6. **Produce the routing record.** State established decisions, material
   uncertainty, the recommended skill, the rationale, and any stop condition.
   Do not rewrite the input as a requirements, design, decision, or
   implementation artifact. Preserve the source for the next skill.
7. **Respect authority.** Recommend the handoff without invoking the selected
   skill, creating its artifacts, or changing production state unless the user
   also authorizes that work.

## Routing Guide

Choose the first row that owns the decision blocking safe progress. The source
method or file format never determines the route.

| Content condition | Next Sirius skill |
|---|---|
| Current commands, behavior, architecture, or constraints need evidence | `reverse-engineer-software-system` |
| Candidate knowledge needs a disposition: create, update, embed, keep-with-implementation, omit, or defer | `select-technical-artifacts` |
| A justified durable artifact needs a canonical home, lifecycle separation, or migration | `design-repository-artifact-layout` |
| One bounded architecture choice has proposed or accepted status and needs a durable ADR | `record-architecture-decision` |
| Opportunity, vision, business case, feasibility, scope, or major risks are unclear | `inception` |
| Actors, user goals, system boundary, main scenarios, or extensions are unclear | `use-case-modeling` |
| An approved change needs risk-driven iterative analysis, design, implementation, or verification | `iterative-risk-driven-development` |
| Business concepts, vocabulary, associations, or attributes are unclear | `domain-modeling` |
| Actor-system events or system operations are unclear | `system-sequence-diagrams` |
| Non-trivial state changes, preconditions, or postconditions are unclear | `operation-contracts` |
| Object responsibility or ownership is unclear | `grasp-responsibility-design` |
| Object collaboration for a selected scenario is unclear | `use-case-realization` |
| Stable software structure needs a class-level summary | `uml-class-diagram-design` |
| Creation, structural, communication, or variation forces justify pattern selection | `design-pattern-application` |
| A language-neutral design needs idiomatic language-specific adaptation | `software-design-language-adaptation` |
| Approved Rust behavior has material ownership, startup, rollback, cancellation, or cleanup risk | `design-rust-lifecycles` |
| A bounded behavior has an independent oracle, such as an approved example, invariant, reference, or defect | `test-driven-implementation` |
| Observable behavior is protected and only internal structure should change | `behavior-preserving-refactoring` |

Use external `interview-me` when one requester's intent is unclear. Use
external `idea-refine` when a candidate direction needs alternatives,
assumption testing, or MVP scoping. Neither requester confirmation nor a
polished idea document establishes organizational approval.

If the blocking decision belongs to a stakeholder, product owner, external
source owner, or another authority outside Sirius, report `blocked` and name
the prerequisite. Do not select a Sirius skill merely to avoid returning
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
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
Prefer an existing issue, idea, or aggregate feature artifact when it is a
sufficient owner.

When a standalone Markdown assessment is justified, follow
[Markdown Artifact Frontmatter](../iterative-risk-driven-development/references/markdown-artifact-frontmatter.md)
and use STE-style. Use this frontmatter. Give the record a stable ID only when
it will be cross-referenced. Put the concise output fields in the body. Do not
copy the source material.

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
- Treating confirmed requester intent or a refined idea as organizational
  approval.
- Sending incomplete behavior to implementation because acceptance-language
  syntax is present.
- Producing a roadmap of many downstream skills instead of choosing the next
  responsible owner.
- Automatically continuing into the selected skill without user authority.

## Verification

- [ ] The assessment identifies the input, source or revision, intended outcome,
      and known non-goals.
- [ ] Readiness is based on content, evidence, approval, and the next decision,
      not on the originating method or format.
- [ ] Established decisions remain distinct from gaps, conflicts, inference,
      and missing approval.
- [ ] Exactly one next Sirius skill is recommended, unless an external
      prerequisite blocks responsible routing.
- [ ] The rationale names the first material decision owned by that skill.
- [ ] No requirement, approval, current-system fact, or verification oracle was
      invented or silently upgraded.
- [ ] The input was not rewritten into the selected skill's artifact.
- [ ] The selected skill was not executed without separate user authority.
- [ ] Any standalone assessment passes the artifact selection budget and uses
      STE-style Markdown with appropriate frontmatter.
