# Iterative Analysis and Design

Use this track when an approved change needs analysis, design, and possibly
implementation in bounded, risk-sized iterations. Select work from the current
question and implementation forces rather than following a mandatory artifact
or object-design sequence.

When requirements-shaped input was produced outside Sirius and the correct
entry point is unclear, first use
[`assess-development-input`](../../skills/assess-development-input/SKILL.md).
Continue only when the input has sufficient authority for the selected work.
The assessment may instead route to recovery, proposal authoring, a localized
specialist, implementation, or an external prerequisite.

Use
[`author-software-proposal`](../../skills/author-software-proposal/SKILL.md)
when technical discussions, findings, incidents, or candidate changes need a
direction reviewed before design or implementation. Proposal authoring stops
before acceptance. Once the responsible authority approves the proposal,
preserve its accepted revision and outcome as the next iteration establishes a
canonical feature, requirement, decision, or design owner.

## Run One Iteration

Use
[`run-development-iteration`](../../skills/run-development-iteration/SKILL.md)
to execute exactly one approved, risk-sized iteration. It fixes the source
revision, selects one objective and exit evidence, coordinates only the needed
specialists, validates the result, creates one commit when authorized, and
stops before the next iteration.

Choose the narrowest specialist for each material question:

| Current question or force | Candidate owner |
|---|---|
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

## Optional UP Planning

Use
[`iterative-up-analysis-design`](../../skills/iterative-up-analysis-design/SKILL.md)
when a team explicitly wants Unified Process phase framing, a multi-iteration
risk plan, or use-case-driven dependencies among selected UP artifacts. It is
an optional planning specialization, not the generic execution coordinator.
Its artifact graph describes dependencies when those techniques are selected;
it is not a checklist for every feature or language.

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

Apply the
[Artifact Selection Budget](../../skills/iterative-up-analysis-design/references/artifact-selection-budget.md)
before creating a standalone document. Prefer executable evidence, an existing
canonical artifact, or an aggregate feature section unless a new file has
clear value, distinct ownership, and an independent lifecycle.

A narrow iteration does not require a Markdown iteration record. Its canonical
changes, validation, and scoped commit can preserve sufficient history. Create
a historical iteration record only when coordination, audit, cross-session
continuity, or durable unresolved risk justifies it. Never copy canonical
artifact bodies into the record.

One commit per iteration is an execution boundary, not permission to commit or
push. Create the commit only when the user authorizes it, keep staging scoped,
and stop after the commit. Push or publication requires separate authority.

Use
[`rewrite-technical-artifacts`](../../skills/rewrite-technical-artifacts/SKILL.md)
when existing knowledge needs progressive disclosure or a clearer reading
path. Use it only as a semantic-preserving pass.
