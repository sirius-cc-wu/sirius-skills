# Client to Code

This proposed track covers the missing path from stakeholder evidence to a
bounded, traceable coding-agent brief. The discovery skills named below do not
exist yet.

The deployed
[`assess-development-input`](../../skills/assess-development-input/SKILL.md)
provides a smaller, method-independent alternative when requirements-shaped
material already exists. It assesses that material and selects a Sirius entry
point; it does not perform the stakeholder discovery, validation, or briefing
proposed by this track.

## Proposed Sequence

1. `stakeholder-requirements-elicitation` identifies relevant stakeholders and
   collects evidence through interviews, observation, workshops, documents,
   and prototypes.
2. `requirements-synthesis-validation` turns the evidence into candidate goals,
   workflows, rules, constraints, quality attributes, scenarios, assumptions,
   and decisions, then plays them back to stakeholders.
3. [`inception`](../../skills/inception/SKILL.md) frames the validated business
   case, scope, feasibility, and major risks.
4. [`use-case-modeling`](../../skills/use-case-modeling/SKILL.md) expresses
   validated actor goals and black-box behavior.
5. The
   [iterative analysis and design track](iterative-analysis-design.md) supplies
   only the downstream artifacts needed for the selected risk and behavior
   slice.
6. `implementation-slice-briefing` assembles approved decisions, visible
   uncertainty, acceptance examples, non-goals, trace links, and verification
   expectations.
7. The
   [implementation and evolution track](implementation-evolution.md) turns the
   brief into verified production behavior.
8. Delivery evidence and stakeholder feedback refine the canonical
   requirements and design artifacts.

## Handoff Rule

Coding agents receive validated decisions plus visible uncertainty. The
briefing step must not make unresolved requirements appear settled or invent
business rules, architecture, or acceptance criteria.

See the [client-discovery proposal](../../docs/proposals/client-discovery-skills.md)
for candidate skill boundaries and reference material.
