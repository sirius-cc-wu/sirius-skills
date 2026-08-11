# Iterative Analysis and Design

Use this track when a system or feature needs requirements, analysis, and
object design before or alongside incremental implementation.

When requirements-shaped input was produced outside Sirius and the correct
entry point is unclear, first use
[`assess-development-input`](../../skills/assess-development-input/SKILL.md).
Continue with this track only when the assessment identifies a requirements or
design gap owned here; the assessment may instead route to recovery,
implementation, or an external prerequisite.

Use
[`author-software-proposal`](../../skills/author-software-proposal/SKILL.md)
when technical discussions, findings, incidents, or candidate changes need a
direction reviewed before further design or implementation. For one focused,
consequential choice it prefers a proposed decision record or ADR; broader
exploration uses a software proposal. Authoring is optional rather than the
first step of every iteration. It produces or substantively revises a draft;
it does not accept the artifact or execute its handoff.

## Sequence

1. [`iterative-up-analysis-design`](../../skills/iterative-up-analysis-design/SKILL.md)
   coordinates risk-driven iterations and artifact durability.
2. [`inception`](../../skills/inception/SKILL.md) frames vision, scope,
   feasibility, business case, and major risks.
3. [`use-case-modeling`](../../skills/use-case-modeling/SKILL.md) identifies
   actors, goals, scenarios, and related requirements.
4. [`behavior-driven-specification`](../../skills/behavior-driven-specification/SKILL.md)
   turns approved or explicitly candidate behavior into concrete examples and
   observable acceptance scenarios.
5. [`domain-modeling`](../../skills/domain-modeling/SKILL.md) captures
   conceptual classes, associations, and attributes.
6. [`system-sequence-diagrams`](../../skills/system-sequence-diagrams/SKILL.md)
   identifies actor-system events.
7. [`operation-contracts`](../../skills/operation-contracts/SKILL.md) specifies
   non-trivial system-operation effects.
8. [`grasp-responsibility-design`](../../skills/grasp-responsibility-design/SKILL.md)
   assigns object responsibilities.
9. [`use-case-realization`](../../skills/use-case-realization/SKILL.md) designs
   object collaborations for selected scenarios.
10. [`uml-class-diagram-design`](../../skills/uml-class-diagram-design/SKILL.md)
   summarizes the resulting software design.
11. [`design-pattern-application`](../../skills/design-pattern-application/SKILL.md)
    addresses justified creation, structure, communication, or variation
    pressures.

Use
[`software-design-language-adaptation`](../../skills/software-design-language-adaptation/SKILL.md)
alongside responsibility design, realizations, patterns, and implementation
when the implementation language is known.

## Iteration Rule

This is a dependency-oriented sequence, not a requirement to create every
artifact. Apply the
[Artifact Selection Budget](../../skills/iterative-up-analysis-design/references/artifact-selection-budget.md)
before creating a standalone document. Prefer implementation evidence, an
existing canonical artifact, or an aggregate feature section unless a new file
has clear value, distinct ownership, and an independent lifecycle. Refine
durable artifacts as feedback arrives.

Use
[`rewrite-technical-artifacts`](../../skills/rewrite-technical-artifacts/SKILL.md)
when an existing artifact contains the required knowledge but needs
progressive disclosure or a clearer reading path, or as a focused final review
of substantial changed artifacts before commit or review. The pass is optional
for narrow structural artifacts and must preserve normative meaning,
identifiers, lifecycle, and traceability.
