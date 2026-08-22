# Iterative Analysis and Design

Use this track when an approved change needs analysis, design, and possibly
implementation in bounded, risk-sized iterations. It also applies when a
complex refactoring moves a system, test, responsibility, runtime, or resource
boundary. Select work from the current question and implementation forces
rather than following a mandatory artifact or object-design sequence.

When the initial owner is unclear, several routes appear plausible, or an input
may lack sufficient authority, first use
[`assess-development-input`](../../skills/assess-development-input/SKILL.md).
The assessment may route directly to a localized specialist, implementation,
review, repository workflow, or an external prerequisite. Enter this track only
when the selected objective requires coordinated analysis, design,
implementation, verification, or iteration boundaries.

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

At each baseline, identify the canonical owner, revision, lifecycle status,
and authority for every material behavior, rule, constraint, quality, and
decision. Treat code, tests, observations, and historical iteration records as
evidence rather than approved intent. Return unclear readiness to
`assess-development-input`. When a bounded evidence set has unresolved
implications, conflicts, or decision status, stop for the responsible external
stakeholder-validation prerequisite. Reapply artifact selection when enabling
behavior gains reuse, a new consumer, or an independent lifecycle.

Within an active iteration, choose the narrowest specialist for each material
question. `assess-development-input` owns initial routing, and the coordinator's
**In-Iteration Routing** tree owns specialist selection after entry. This table
summarizes those handoffs:

| Group | Current question or force | Candidate owner |
|---|---|---|
| Cross-cutting Support | Whether candidate knowledge should be created, updated, embedded, kept with implementation, omitted, or deferred | [`select-technical-artifacts`](../../skills/select-technical-artifacts/SKILL.md) |
| Cross-cutting Support | Canonical repository homes, lifecycle separation, or artifact migration | [`design-repository-artifact-layout`](../../skills/design-repository-artifact-layout/SKILL.md) |
| Cross-cutting Support | One consequential architecture choice needs proposed review, accepted history, or supersession | External `documentation-and-adrs` with the `all` installation; otherwise repository-native ADR guidance |
| Requirements Analysis | Vision, feasibility, project scope, or major business risk | [`inception`](../../skills/inception/SKILL.md) |
| Requirements Analysis | Actors, goals, system boundary, or scenario flow | [`use-case-modeling`](../../skills/use-case-modeling/SKILL.md) |
| System Analysis | Business concepts and shared vocabulary | [`domain-modeling`](../../skills/domain-modeling/SKILL.md) |
| System Analysis | Actor-system events and operation names | [`system-sequence-diagrams`](../../skills/system-sequence-diagrams/SKILL.md) |
| System Analysis | Non-trivial state effects and invariants | [`operation-contracts`](../../skills/operation-contracts/SKILL.md) |
| Software/System Design | Major components, services, processes, data owners, architectural boundaries, deployment topology, or measurable quality trade-offs | [`design-software-architecture`](../../skills/design-software-architecture/SKILL.md) |
| Software/System Design | Native software responsibility, cohesion, coupling, coordination, or dependency direction | [`grasp-responsibility-design`](../../skills/grasp-responsibility-design/SKILL.md) |
| Software/System Design | Detailed internal collaboration for one selected scenario | [`use-case-realization`](../../skills/use-case-realization/SKILL.md) |
| Software/System Design | Stable object-oriented structure that needs a summary | [`uml-class-diagram-design`](../../skills/uml-class-diagram-design/SKILL.md) |
| Software/System Design | Demonstrated creation, structural, communication, or variation pressure | [`design-pattern-application`](../../skills/design-pattern-application/SKILL.md) |
| Detailed Design | General mapping into a target language and runtime | [`software-design-language-adaptation`](../../skills/software-design-language-adaptation/SKILL.md) |
| Detailed Design | Rust ownership, transfer, startup, rollback, cancellation, or cleanup | [`design-rust-lifecycles`](../../skills/design-rust-lifecycles/SKILL.md) |
| Implementation and Evolution | A bounded approved behavior with an independent verification oracle and no remaining coordination need | External `test-driven-development` with the `all` installation; otherwise repository-native implementation and verification |
| Implementation and Evolution | A non-trivial in-flight decision or claim needs fresh-context adversarial review | External `doubt-driven-development` with the `all` installation |

Several specialists may contribute to one iteration only when they answer the
same objective. Do not create one artifact merely because another artifact can
feed it.

After entry routing selects coordinated work, the coordinator chooses the
narrowest in-iteration specialists for each material question. It can coordinate
requirements analysis, system analysis, software/system design, detailed
design, implementation, and verification in one risk-sized loop. These groups
classify responsibility; they do not require a complete design chain.

## Support-Envelope Gate

Apply the coordinator's support-envelope gate when an approved coordinated
change selects or derives behavior by identity, type, model, version, platform,
provider, capability, operating mode, or another material variation axis. The
gate distinguishes one exact variant, one family, a closed catalog, a
pattern-matched set, and a dynamically extensible population. It does not turn
every conditional into coordinated work.

Before implementation, establish only the material parts of:

- the approved support claim, population, exclusions, and compatibility
  authority;
- named siblings, aliases, revisions, registrations, pattern matches, generic
  or dynamic fallbacks, and unknown paths;
- the capability source in normal, startup, degraded, offline, persisted,
  cached, or replayed modes, including whether available identity and
  configuration are sufficient without live evidence;
- the canonical requirement, catalog, schema, registry, configuration, or
  component that owns the rule and any consumers that duplicate it;
- representative reported, included, boundary, fallback, unknown, and
  cross-mode verification; and
- whether the iteration proves the approved population or only one bounded
  slice of the parent outcome.

Keep a narrow change narrow when broader intent lacks approval. Stop for the
responsible authority when the supported population or compatibility policy is
unclear. Stop for a responsible external recovery process when current sibling,
fallback, or mode behavior lacks evidence. Route non-trivial expected state
effects to `operation-contracts` and material cross-component capability-source
ownership to `design-software-architecture`. Do not guess unavailable facts,
recover the whole system, or require a standalone support matrix.

## Boundary-Sensitive Refactoring

Do not assume that a refactoring is local merely because observable behavior
should remain unchanged. Apply the coordinator's design-sufficiency gate when
work creates or moves a material test seam, composition root, backend,
entrypoint, process-global dependency, runtime task, resource owner, readiness
condition, or cleanup boundary.

Before implementation, retain the smallest sufficient account of:

- the system boundary and representative vertical behavior to preserve;
- responsibilities assigned to native modules, functions, tasks, adapters,
  handles, types, or composition roots;
- material resource ownership, transfer, supervision, cancellation, joining,
  and cleanup;
- focused, integration, end-to-end, and human-owned verification; and
- whether the iteration closes the approved parent outcome or completes an
  enabling boundary for later integration.

Stop for a responsible external recovery process when current behavior or
architecture is unclear. Use `design-software-architecture` when intended major
components, data ownership, trust or failure boundaries, deployment, or quality
trade-offs are unresolved. Use `grasp-responsibility-design` for responsibility
placement within those boundaries and `design-rust-lifecycles` for exact Rust
ownership realization. Let ownership
pressure feed back into responsibility design. Do not require a standalone
artifact for these answers or report a local seam as the parent outcome without
a representative end-to-end flow.

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
home, several paths compete, or no usable placement guide exists, use
[`design-repository-artifact-layout`](../../skills/design-repository-artifact-layout/SKILL.md)
to preserve local conventions or select the smallest lifecycle-aware addition.
Do not create a layout document or speculative directory tree solely because
the repository lacks explicit guidance.
When one independently consequential architecture choice needs durable proposed,
accepted, or superseding history, use external `documentation-and-adrs` with the
`all` installation or follow repository-native ADR guidance. Do not copy the
whole design artifact into an ADR.

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
