# Client to Code

This track starts after a responsible external process has gathered stakeholder
evidence and validated the decisions needed for development. Sirius does not
currently provide stakeholder elicitation, requirements synthesis and
validation, or implementation-slice briefing skills.

`stakeholder-requirements-elicitation`,
`requirements-synthesis-validation`, and `implementation-slice-briefing` are
retired. Existing evidence records, requirements briefs, and implementation
briefs remain valid at their recorded revisions. Do not recreate or rename
those historical artifact types merely because their skills are retired.

## Sequence

1. Gather stakeholder evidence and validate requirements through the responsible
   external process. Preserve sources, authority, approval state, conflicts,
   confidentiality, and unresolved decisions.
2. Use
   [`assess-development-input`](../../skills/assess-development-input/SKILL.md)
   when the externally produced material's readiness or Sirius entry point is
   unclear. It may return another external prerequisite instead of forcing a
   Sirius owner.
3. Use [`inception`](../../skills/inception/SKILL.md) when vision, business
   case, scope, feasibility, or major risks remain unclear.
4. Use [`use-case-modeling`](../../skills/use-case-modeling/SKILL.md) to express
   approved actor goals and black-box behavior.
5. Use
   [`behavior-driven-specification`](../../skills/behavior-driven-specification/SKILL.md)
   to make bounded behavior concrete through source-linked examples and
   acceptance scenarios.
6. Use the
   [iterative analysis and design track](iterative-analysis-design.md) for only
   the analysis, design, implementation, and verification needed by the current
   risk-sized objective.
7. Use the
   [implementation and evolution track](implementation-evolution.md) directly
   when approved behavior or design provides an independent oracle. Carry
   source revisions, authority, non-goals, exclusions, verification, and stop
   conditions into the implementation request without creating a separate
   briefing artifact by default.
8. Return delivery evidence and new uncertainty to the canonical external
   requirements owner or the responsible decision authority. Do not promote
   implementation discoveries into approved intent.

## Handoff Rule

Coding agents receive approved decisions plus visible uncertainty. Stop when
missing stakeholder evidence, validation, approval, business rules,
architecture, access, or an independent oracle would require invention.

See the
[client-discovery idea](../../docs/ideas/client-discovery-skills.md) for the
retired skill family's rationale and implementation history.
