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

- Gathered stakeholder evidence needs synthesis, concrete examples, fit
  criteria, conflict handling, or authority-aware validation.
- Requirements need correction, approval, contest, or supersession without
  losing source history.
- Do not use to collect missing evidence, define project feasibility, write
  detailed use cases, choose architecture, or create implementation tasks.

## Evidence and Decision Discipline

Read the input evidence and
[Stakeholder Requirements Elicitation](../stakeholder-requirements-elicitation/SKILL.md).
Reuse source IDs; do not rewrite raw notes, erase contradictions, or convert
agent confidence into stakeholder approval.

Use these requirement states consistently:

- `candidate`: synthesized but not validated by an appropriate stakeholder;
- `validated`: confirmed accurate by a relevant stakeholder, but not binding;
- `approved`: accepted for this revision by the authorized role;
- `contested`: relevant sources or authorities disagree;
- `superseded`: replaced by a traceable later requirement or decision.

Validation and approval are revision-specific. Record rejection and abstention
without inventing a status that hides the outcome.

Every material candidate retains the fields `Source evidence IDs:`,
`Validation and approval:`, and
`Status: [candidate | validated | approved | contested | superseded]`, whether
embedded in an existing owner or written to a standalone brief.

## Workflow

1. **Bound the synthesis.** Name the decision or problem, exact evidence set and
   revisions, coverage gaps, and non-goals.
2. **Check readiness.** Confirm source IDs, roles, authority, sensitivity,
   conflicts, and limits. Route missing evidence or access to
   `stakeholder-requirements-elicitation`; do not simulate it.
3. **Synthesize with provenance.** Derive candidate goals, workflows, rules,
   constraints, qualities, scenarios, assumptions, and decisions. Link each to
   supporting and contradicting sources; separate requested solutions from
   underlying outcomes.
4. **Shape inspectable candidates.** Record an opaque ID, precise statement,
   kind, status, context, sources, needed authority, limits, and open questions.
   Preserve manual IDs and repository validation rules.
5. **Make behavior concrete.** Add examples, counterexamples, or measurable fit
   criteria. Label unconfirmed values instead of inventing thresholds.
6. **Expose conflicts and assumptions.** Record the disagreement, applicable
   authority, consequence, and next evidence or decision. Availability or
   seniority does not settle authority.
7. **Play back by authority.** Present the smallest coherent set to validating
   and approving roles. Record revision, role, authority, outcome, corrections,
   abstentions, and known date. Apply status changes without rewriting history.
8. **Route accepted knowledge.** Update existing canonical owners: vision,
   scope, feasibility, and risk to `inception`; actor goals and scenarios to
   `use-case-modeling`; domain terms and rules to `domain-modeling`; and
   cross-cutting qualities to the established supplementary owner.
9. **Close or stop visibly.** Produce requirements, examples, decision and
   conflict history, open questions, and handoffs. Stop before design. Leave
   unsupported or unauthorized decisions candidate or contested.

Without live playback, prepare questions, retain `candidate` or `contested`
states, and record the access gap. Never manufacture validation, approval,
quotes, or dates.

## Confidentiality

Carry sensitivity, access, retention, and publication constraints forward.
Prefer sanitized claims and protected links. Confirm source permission before
publishing or sending material to an external service.

## File Output

Apply
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
Prefer existing requirements owners. Create a standalone brief only when its
synthesis, validation history, and conflict log change independently.

For standalone Markdown, follow
[Markdown Artifact Frontmatter](../plan-up-iterations/references/markdown-artifact-frontmatter.md)
and [Readable Technical Artifacts](../plan-up-iterations/references/readable-technical-artifacts.md).
When a standalone brief is justified, read and adapt the
[Requirements Discovery Brief Template](references/requirements-discovery-brief-template.md).

## Red Flags

- Requirements lack source IDs or evidence limits.
- A requested solution is treated as the underlying outcome.
- Validation is treated as approval, or approval comes from the wrong role.
- Rank, availability, or majority vote substitutes for decision authority.
- Thresholds, examples, rules, quotes, or dates are invented.
- Sensitive raw evidence is copied into a broadly visible brief.
- The synthesis chooses interfaces, schemas, architecture, or implementation.

## Verification

- [ ] Evidence revisions, coverage gaps, and synthesis boundaries are explicit.
- [ ] Each candidate has an opaque ID, precise statement, status, sources, context, and limits.
- [ ] Requested solutions remain distinguishable from goals and evidence.
- [ ] Examples, counterexamples, and fit criteria are traceable and contain no invented values.
- [ ] Validation, rejection, approval, abstention, conflict, and supersession preserve role, authority, revision, and history.
- [ ] Confidentiality and publication constraints survive synthesis.
- [ ] Missing evidence returns to elicitation; accepted knowledge reaches its smallest canonical owner.
- [ ] The result stops before software design and implementation planning.
- [ ] Standalone Markdown has one frontmatter block and a reader-oriented opening.
