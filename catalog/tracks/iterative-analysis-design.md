# Iterative Analysis and Design

Use this track when an approved change needs analysis, design, and possibly
implementation in bounded, risk-sized iterations. Select work from the current
question and implementation forces rather than following a mandatory artifact
or object-design sequence.

When requirements-shaped input was produced outside Sirius and the correct
entry point is unclear, first use
[`assess-development-input`](../../skills/assess-development-input/SKILL.md).
Continue only when the input has sufficient authority for the selected work.
The assessment may instead route to recovery, a localized specialist,
implementation, or an external prerequisite.

When the upstream request or direction is still vague, optionally use the
external
[`interview-me`](https://github.com/addyosmani/agent-skills/blob/5a1b82d6445d1e2f0abeea1072851419a50c0e5c/skills/interview-me/SKILL.md)
and
[`idea-refine`](https://github.com/addyosmani/agent-skills/blob/5a1b82d6445d1e2f0abeea1072851419a50c0e5c/skills/idea-refine/SKILL.md)
before entering this track. Their confirmed idea one-pager remains candidate
input until the responsible authority approves it. Save the confirmed idea in an
ideas path or a feature path defined by local governance. Do not create a new
proposal artifact. Preserve existing legacy proposals at their historical
paths. Once approved,
preserve the accepted revision and outcome as the next iteration establishes a
canonical feature, requirement, decision, or design owner.

## Iterative Risk-Driven Development

Use
[`iterative-risk-driven-development`](../../skills/iterative-risk-driven-development/SKILL.md)
to execute one or more approved, risk-sized iterations. It selects one
objective and exit evidence per iteration, coordinates only the needed
specialists, validates the result, and creates at most one authorized commit.
By default, one commit per iteration continues until the requested work is
complete. Use single-iteration mode when the user explicitly asks for one
iteration.

Choose the narrowest specialist for each material question:

| Current question or force | Candidate owner |
|---|---|
| Whether candidate knowledge should be created, updated, embedded, kept with implementation, omitted, or deferred | [`select-technical-artifacts`](../../skills/select-technical-artifacts/SKILL.md) |
| Canonical repository homes, lifecycle separation, or artifact migration | [`design-repository-artifact-layout`](../../skills/design-repository-artifact-layout/SKILL.md) |
| One consequential architecture choice needs proposed review, accepted history, or supersession | [`record-architecture-decision`](../../skills/record-architecture-decision/SKILL.md) |
| Vision, feasibility, project scope, or major business risk | [`inception`](../../skills/inception/SKILL.md) |
| Actors, goals, system boundary, or scenario flow | [`use-case-modeling`](../../skills/use-case-modeling/SKILL.md) |
| Observable examples and boundary cases | [`behavior-driven-specification`](../../skills/behavior-driven-specification/SKILL.md) |
| Business concepts and shared vocabulary | [`domain-modeling`](../../skills/domain-modeling/SKILL.md) |
| Actor-system events and operation names | [`system-sequence-diagrams`](../../skills/system-sequence-diagrams/SKILL.md) |
| Non-trivial state effects and invariants | [`operation-contracts`](../../skills/operation-contracts/SKILL.md) |
| Object responsibility or collaboration, when deliberately selected | [`grasp-responsibility-design`](../../skills/grasp-responsibility-design/SKILL.md) and [`use-case-realization`](../../skills/use-case-realization/SKILL.md) |
| Stable object-oriented structure that needs a summary | [`uml-class-diagram-design`](../../skills/uml-class-diagram-design/SKILL.md) |
| Demonstrated creation, structural, communication, or variation pressure | [`design-pattern-application`](../../skills/design-pattern-application/SKILL.md) |
| General mapping into a target language and runtime | [`software-design-language-adaptation`](../../skills/software-design-language-adaptation/SKILL.md) |
| Rust ownership, transfer, startup, rollback, cancellation, or cleanup | [`design-rust-lifecycles`](../../skills/design-rust-lifecycles/SKILL.md) |
| A bounded behavior with an independent verification oracle | [`test-driven-implementation`](../../skills/test-driven-implementation/SKILL.md) |

Several specialists may contribute to one iteration only when they answer the
same objective. Do not create one artifact merely because another artifact can
feed it.

The coordinator selects the narrowest specialists for each material question.
It can coordinate requirements, analysis, object design, implementation,
verification, and Rust lifecycle design in one risk-sized loop. It does not
require a complete object-design chain.

## Language Extension Rule

Keep requirements and analysis independent of implementation language. Use the
general language adapter for ordinary implementation mapping. Add or select a
language specialist only when repeated, material runtime semantics require a
distinct workflow and output. Rust lifecycle design is the first such
specialist; it does not make Rust the coordinator's default.

Future specialists should be driven by concrete forces such as memory and
ownership, ABI compatibility, runtime validation, cancellation, resource
disposal, process boundaries, or concurrency. Do not create a parallel skill
or document template for every language merely to complete a matrix.

## Artifact and Commit Rule

Apply
[`select-technical-artifacts`](../../skills/select-technical-artifacts/SKILL.md)
when artifact selection is a material question. Its
[Artifact Selection Budget](../../skills/select-technical-artifacts/references/artifact-selection-budget.md)
remains the local creation gate for every owning skill: prefer executable
evidence, an existing canonical artifact, or an aggregate feature section
unless a new file has clear value, distinct ownership, and an independent
lifecycle.

When a standalone artifact passes that budget but lacks a clear canonical
home, use
[`design-repository-artifact-layout`](../../skills/design-repository-artifact-layout/SKILL.md)
to preserve local conventions or select the smallest lifecycle-aware addition.
When one independently consequential architecture choice needs durable proposed,
accepted, or superseding history, use
[`record-architecture-decision`](../../skills/record-architecture-decision/SKILL.md)
instead of copying the whole design artifact into an ADR.

A narrow iteration does not require a Markdown iteration record. Its canonical
changes, validation, and scoped commit can preserve sufficient history. Create
a historical iteration record only when coordination, audit, cross-session
continuity, or durable unresolved risk justifies it. Never copy canonical
artifact bodies into the record.

Write reader-facing artifacts in STE-style from the owning skill. Keep the
artifact's meaning, lifecycle, evidence, identifiers, and traceability intact.

One commit per iteration is a commit boundary, not permission to commit or
push. Create the commit only when the user authorizes it and keep staging scoped.
In continuous mode, recheck the baseline before the next iteration. Push or
publication requires separate authority.
