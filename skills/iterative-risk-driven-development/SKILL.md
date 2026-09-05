---
name: iterative-risk-driven-development
description: Coordinates an already selected, approved development objective through risk-sized iterations across system analysis, software architecture, native responsibility and Rust lifecycle design, implementation, and verification. Rechecks canonical knowledge ownership; applies support-envelope and boundary-sensitive refactoring gates; preserves system, resource-ownership, end-to-end verification, and parent-completion boundaries; validates each result; and creates at most one authorized commit per iteration. Use after initial routing when a feature, support-sensitive change, or boundary-sensitive refactoring needs coordinated progress or one commit per iteration until the requested work is complete; do not use for session-start discovery or one isolated specialist task.
---

# Iterative Risk-Driven Development

## Overview

Advance an approved change through one or more risk-sized iterations after the
initial route is known. Each iteration answers one decision, learning, design,
or delivery question. Select in-iteration methods from the current question
and implementation forces. Entry routing belongs to
`assess-development-input`; this coordinator does not own session-start skill
discovery.

## When to Use

- An approved idea, feature source, prepared analysis/design objective, or
  other authoritative input needs bounded progress.
- The user requests one commit per iteration and expects work to continue until
  the requested outcome is complete.
- Several specialist skills may apply, but they must serve one objective and one
  coherent change.
- A design question may require analysis, native responsibility design, object
  design, implementation, or verification in the same risk-sized loop.
- A complex refactoring creates or moves a test seam, backend, composition
  root, entrypoint, runtime owner, readiness condition, or cleanup boundary.
- An approved coordinated change specializes behavior by identity, type, model,
  version, platform, provider, capability, or operating mode, and its supported
  population or fallback behavior is material.
- Do not use to assess readiness, perform one isolated specialist task, commit
  an existing diff, or publish completed work.

## Execution Modes

- **Continuous mode (default):** Treat “one commit per iteration” as a commit
  cadence. After each authorized commit, recheck the current baseline, choose
  the next objective, and continue until the requested work is complete.
- **Single-iteration mode:** Use this mode when the user explicitly asks for
  one iteration or asks to stop after the commit.
- Stop in either mode for failed validation, missing authority, an unresolved
  product or compatibility decision, an unavailable verification oracle, or a
  user instruction to stop. Do not push or publish without separate authority.

## In-Iteration Routing

Use this tree after entry routing has selected coordinated work. It is a
conditional routing index, not a lifecycle or required sequence.

```text
Approved coordinated objective begins
├─ Initial owner, readiness, or authority is unclear
│  └─ return to assess-development-input
├─ Current behavior, architecture, deployment, or constraints lack evidence
│  └─ stop for a responsible external recovery process
├─ Requirements Analysis question
│  ├─ durable project vision, non-goals, or contribution-acceptance policy → define-project-vision
│  ├─ actors, goals, boundary, or scenarios → use-case-modeling
│  ├─ quality requirements, binding constraints, or acceptance evidence → specify-quality-constraints
│  └─ business case, feasibility commitment, or investment decision → responsible external product or portfolio process; external idea-refine may prepare candidate input
├─ System Analysis question
│  ├─ domain concepts or vocabulary → domain-modeling
│  ├─ actor-system events or operations → system-sequence-diagrams
│  └─ preconditions, postconditions, or state effects → operation-contracts
├─ Software/System Design question
│  ├─ components, boundaries, deployment, or quality trade-offs → design-software-architecture
│  ├─ responsibility, cohesion, coupling, or dependency → grasp-responsibility-design
│  ├─ collaboration for one scenario → use-case-realization
│  ├─ stable object structure summary → uml-class-diagram-design
│  └─ demonstrated variation or structural force → design-pattern-application
├─ Detailed Design question
│  ├─ target-language realization → software-design-language-adaptation
│  └─ Rust ownership or resource lifecycle → design-rust-lifecycles
├─ Approved behavior needs implementation and verification
│  └─ external test-driven-development or repository-native implementation and verification
├─ Browser behavior needs real runtime evidence
│  └─ external browser-testing-with-devtools or repository-native verification
├─ Tests, builds, or behavior fail unexpectedly
│  └─ external debugging-and-error-recovery or repository-native debugging
├─ A non-trivial in-flight claim needs adversarial review before it stands
│  └─ external doubt-driven-development
├─ A bounded artifact needs one explicitly authorized Antigravity CLI opinion
│  └─ agy-second-opinion (all installation only)
├─ Existing structure needs behavior-preserving improvement
│  ├─ routine clarity → external code-simplification or native cleanup
│  ├─ established structural ownership → behavior-preserving-refactoring
│  └─ material boundary change → remain under iterative coordination
├─ Durable knowledge needs disposition or placement
│  ├─ create, update, embed, keep, omit, or defer → select-technical-artifacts
│  └─ justified artifact lacks a canonical home → design-repository-artifact-layout
├─ A consequential architecture decision needs durable history
│  └─ external documentation-and-adrs or repository-native ADR guidance
├─ Several questions serve the same objective
│  └─ select the smallest necessary specialist set
└─ No coordination remains
   └─ return a direct handoff and stop coordinating
```

External Addy routes and `agy-second-opinion` require the `all` installation.
Otherwise, use the named repository-native workflow or return the responsible
prerequisite.

## Workflow

1. **Fix authority and baseline.** Read repository governance. Identify the
   approved source, revision, lifecycle state, requested outcome, non-goals,
   current branch, and unrelated workspace changes. Do not promote candidate
   intent or absorb unrelated work.
2. **Confirm canonical knowledge ownership.** For every material behavior,
   rule, constraint, quality, or decision needed by the iteration, identify its
   current canonical owner, revision, lifecycle status, and approving
   authority. Treat code, tests, runtime observations, and historical iteration
   records as evidence, not approved intent. If material input exists only in
   those sources, a candidate direction or enabling proof is being used beyond
   its approved boundary, or readiness and the correct owner are unclear, stop and use
   `assess-development-input`. When evidence implications, conflicts, or
   decision status still need stakeholder validation, stop and name that
   external prerequisite instead of inventing approval.
3. **Choose one objective.** State one behavior, decision, risk, or learning
   question and its exit evidence. Name the approved parent outcome and state
   whether this iteration can close it or only enable later work. Keep the
   objective small enough for one coherent commit.
4. **Select in-iteration owners.** Start from the approved objective and initial
   route. Use the in-iteration routing tree and the owner boundaries in
   [Assess Development Input](../assess-development-input/SKILL.md) without
   treating either as a phase sequence. Assign each material question to the
   narrowest requirements analysis, system analysis, software/system design,
   detailed design, implementation, or verification owner. Select
   several specialists only when they serve the same objective and coherent
   change. Stop for a responsible external recovery or
   authority prerequisite when evidence or approval is missing. If the work no
   longer requires coordination, return a direct handoff instead of using this
   skill as a general router. Return to `assess-development-input` when the
   initial owner or readiness must be reconsidered.
5. **Apply the support-envelope gate.** When behavior is selected or derived by
   identity, type, model, version, platform, provider, capability, operating
   mode, or another variation axis, determine whether the approved claim covers
   one exact variant, one family, a closed catalog, a pattern-matched set, or a
   dynamically extensible population. Inspect sibling, fallback, unknown, and
   cross-mode behavior only as far as the selected capability requires. Confirm
   the authoritative support boundary, capability source, explicit exclusions,
   and representative verification before implementation. Keep a narrow fix
   narrow when broader intent lacks approval. Do not report one observed variant
   as proof of a broader parent outcome.
6. **Apply the boundary-sensitive refactoring gate.** When the change creates
   or moves a material test seam, composition root, backend, entrypoint,
   process-global dependency, runtime task, resource owner, readiness
   condition, or cleanup boundary, establish the system boundary,
   representative vertical scenario, native responsibilities, ownership
   consequences, verification ownership, and completion boundary before
   implementation. Stop for a responsible external recovery process when
   current behavior or architecture is unclear. Do not treat the `refactoring`
   label as evidence that this design context is unnecessary.
7. **Budget artifacts and locate justified owners.** Apply
   [Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
   Prefer code, tests, configuration, an existing canonical artifact, or an
   embedded section. Create a standalone artifact only when its value, owner,
   and independent lifecycle are clear. Inspect repository governance and
   actual artifact homes before assigning a path. When a justified standalone
   artifact has no clear canonical home, several paths compete, or the
   repository has no usable placement convention, use
   `design-repository-artifact-layout`. Do not create a layout document or
   speculative directory tree merely because no guide exists.
8. **Select Rust lifecycle design when needed.** If the target is Rust and
   ownership, capability transfer, startup, rollback, cancellation,
   supervision, or cleanup affects the objective, use
   [Design Rust Lifecycles](../design-rust-lifecycles/SKILL.md). Treat its result
   as part of the current iteration. Do not use it as a substitute for missing
   system-boundary, responsibility, or verification decisions.
9. **Execute the selected work.** Read and follow every selected specialist
   skill and the repository's implementation and verification guidance. Keep
   all work tied to the objective. Stop if missing approval, support-population
   authority, product rules, compatibility decisions, capability-source
   evidence, design context required by either gate, or a verification oracle
   would require invention.
10. **Reconcile durable knowledge and promotion pressure.** Feed discoveries
   back only when they change
   knowledge owned by a canonical requirement, design, decision, test, schema,
   or configuration artifact. Preserve idea and decision history. Do not
   silently rewrite it. Reapply artifact selection and the appropriate owning
   specialist when a later iteration reuses an enabling behavior, a second
   consumer appears, durable user-visible rules accumulate in code, tests, or
   iteration history, or an approved source is stretched beyond its non-goals.
   Promote evidence into current intended knowledge only with matching
   authority and validation. When one authoritative, consequential architecture
   choice needs an independent proposed, accepted, or superseding lifecycle,
   use external `documentation-and-adrs` with the `all` installation or follow
   repository-native ADR guidance.
11. **Validate exit evidence.** Run repository-required and changed-scope
   checks. For a material support envelope, verify the reported variant plus
   representative included, boundary, fallback, unknown, and cross-mode cases
   justified by the claim. Retain the representative end-to-end oracle when a
   local seam or component check is the current result. Distinguish completed
   evidence from human-owned or unavailable validation. Do not close the parent
   outcome or commit an iteration when its stated exit evidence failed.
12. **Commit once per iteration when authorized.** If the user authorized a
    commit, review repository state and diffs, follow local message conventions,
    and stage only the current iteration's intended paths. Create at most one
    commit for the iteration. Do not amend, push, or publish without matching
    authority.
13. **Apply the execution mode.** In single-iteration mode, report the
    objective, canonical changes, validation, commit, and residual risk, then
    stop. In continuous mode, report the current result, choose the next
    objective, and continue until the requested work or an explicit stop
    condition ends the run.

## Support-Envelope Gate

Apply this gate when a change makes behavior depend on a variation axis and the
approved claim may extend beyond the reported example. Do not apply it merely
because code contains a conditional. Answer only the questions material to the
selected capability:

- **Claim and population:** Does the approved outcome cover one exact variant,
  one family, a closed catalog, a pattern-matched set, or a dynamically
  extensible population? Which authority defines inclusion, exclusion, and
  compatibility?
- **Variation and negative space:** Which named siblings, aliases, revisions,
  pattern matches, registrations, generic fallbacks, dynamic extensions, and
  unknown paths share or bypass the changed behavior?
- **Source sufficiency across modes:** Which source determines the capability in
  normal, startup, degraded, offline, persisted, cached, or replayed modes? Can
  the available identity and configuration determine it without live evidence?
  Do not guess or silently treat one mode's source as authoritative in another.
- **Ownership and consistency:** Which requirement, product catalog, schema,
  registry, configuration, or component owns the support rule? Which consumers
  duplicate or derive it? Route a material cross-component source or boundary
  choice to `design-software-architecture`.
- **Verification coverage:** Which reported, representative included, boundary,
  fallback, unknown, and cross-mode cases are needed to support the claim? A
  single customer, fixture, platform, model, or revision proves only its bounded
  case unless approved evidence establishes more.
- **Completion boundary:** Does the iteration prove the approved support claim,
  or only one bounded slice? Keep excluded or unevidenced variants and the
  broader parent outcome explicit.

Route intended scope or compatibility authority to the responsible requirements
or external owner. Route non-trivial expected state effects to
`operation-contracts`. Stop for a responsible external recovery process when
current variant, fallback, or mode behavior lacks evidence. The gate is a
bounded change-impact check. It does not recover the whole system, require a
standalone support matrix, or authorize broadening a narrowly approved change.

## Boundary-Sensitive Refactoring Gate

Apply this gate by material effect, not by an arbitrary count of changed files
or modules. Answer only the questions that the change makes material:

- **System boundary and preservation oracle:** What system is under discussion?
  Which representative actor-to-outcome flow and observable behavior must
  remain protected?
- **Native responsibilities:** Which crate, module, type, function, task,
  adapter, resource handle, or composition root should know, create,
  coordinate, vary, supervise, or clean up? What dependency direction follows?
- **Ownership and lifecycle:** Which resources and capabilities are owned,
  borrowed, transferred, cancelled, joined, released, or reported on failure?
- **Verification ownership:** Which focused, integration, end-to-end, and
  human-owned checks protect each claim? Do not replace the representative
  vertical oracle with component checks.
- **Completion boundary:** Does the iteration prove the approved parent
  outcome, or does it complete an enabling abstraction boundary for later
  integration?

Use an existing canonical design, executable evidence, an embedded section, or
an iteration report when durable context is justified. The gate does not
require a new document, use case, contract, diagram, or object-design chain.

## Rust Ownership and Lifecycle Design

Use `design-rust-lifecycles` only when Rust semantics create material design
pressure. The specialist covers:

- ownership and capability transfer;
- staged startup and readiness;
- rollback and partial initialization;
- asynchronous cancellation and supervision; and
- resource termination and fallible cleanup.

Keep product behavior, requirements, and language-neutral design separate from
these implementation-facing lifecycle decisions. Map lifecycle owners to the
selected native responsibilities. If Rust ownership pressure changes a
responsibility, system boundary, or verification obligation, return that
feedback to its owning design instead of silently changing it in the API.

## File Output

Follow established repository paths. If a justified artifact lacks a clear
canonical home, several paths compete, or migration is material, use
[Design Repository Artifact Layout](../design-repository-artifact-layout/SKILL.md)
for that placement decision. When a standalone Markdown artifact is justified,
follow
[Markdown Artifact Frontmatter](references/markdown-artifact-frontmatter.md)
and use STE-style.

Refine canonical artifacts in place. If a durable iteration record is justified,
use the template below. Record actual results and artifact outcomes. Do not copy
canonical artifact bodies into the record.

## Iteration Record Template

```markdown
---
type: "Iteration Record"
title: "Iteration: [Name]"
description: "[One-sentence learning, risk-reduction, or delivery goal]"
id: "[Stable iteration ID]"
status: "[planned | active | completed]"
tags: [iteration]
---

# Iteration: [Name]

Goal:
- [Learning, risk reduction, decision, or delivery outcome]

Parent Outcome:
- [Approved broader outcome and whether this iteration closes or enables it]

Risks Addressed:
- [Risk]

Artifact Budget:
- [create / update / embed / keep with implementation / omit]: `[path or subject]` - [consumer, decision, or risk] - [ownership and lifecycle reason]

Artifacts to Start:
- [Stable ID when cross-referenced, artifact]: `[canonical path]` - [why now]

Artifacts to Refine:
- [Stable ID when cross-referenced, artifact]: `[canonical path]` - [trigger for refinement]

Artifacts Consulted:
- [Stable ID when cross-referenced, artifact]: `[canonical path]`

Decisions to Record:
- [Decision]: `[canonical path or pending location]`

Trace:
- [Representative scenario/oracle] -> [system boundary or operation] -> [native responsibility owner] -> [language/lifecycle design] -> [checks]

Completion Boundary:
- [parent outcome closed / enabling result / deferred]: [evidence and remaining vertical gap]

Exit Criteria:
- [Evidence that the iteration answered the question]

Results:
- [Evidence, residual risk, or follow-up]

Artifact Outcomes:
- [started / refined / consulted / deferred]: [stable ID when cross-referenced, title, and canonical path] - [actual result]
```

Omit empty `Artifact Budget` dispositions. Do not add ceremony to complete the
template. Use `Artifact Outcomes` to record actual results, including work
deferred or changed after the objective was defined.

## Red Flags

- The iteration starts without approved authority or a fixed source baseline.
- Material intent has no current canonical owner, revision, lifecycle status,
  or approving authority.
- Code, tests, observations, or historical iteration records silently become
  approved product intent.
- A candidate direction or enabling proof is reused beyond its approved boundary
  without reassessing ownership and promotion pressure.
- The coordinator is used for session-start discovery or one isolated
  specialist task.
- Several objectives are combined into one commit.
- A mandatory artifact chain or programming paradigm is imposed.
- All artifacts are created at full detail before risk is understood.
- A standalone document has no durable decision, named consumer, material risk,
  or independent lifecycle.
- A new artifact path or directory is invented without inspecting local
  conventions or routing a material placement gap to artifact-layout design.
- A missing layout guide triggers a generic taxonomy, empty directory tree, or
  standalone layout document without a justified artifact and consumer.
- Object design starts from a domain model without behavior or system events.
- A change generalizes from one observed variant without an approved support
  population, sibling and fallback review, cross-mode source check, or coverage
  argument.
- A runtime-derived, cached, or observed capability is guessed in a mode where
  its authoritative source is unavailable.
- A boundary-sensitive refactoring proceeds without a preserved system
  scenario, native responsibility assignment, or verification boundary.
- Rust lifecycle design is added without material ownership or resource
  pressure, or substitutes for missing system analysis and responsibility
  decisions.
- A local backend, constructor, settings seam, or lifecycle handle is reported
  as the parent outcome without a representative end-to-end flow.
- Durable artifacts are copied into iteration records instead of linked.
- The iteration continues after failed validation or a missing authority.
- Continuous execution starts without a user request or single mode ignores an
  explicit stop boundary.
- Push, publication, or an unrelated change occurs inside the iteration.

## Verification

- [ ] Authority, source revision, lifecycle state, requested outcome, and
      non-goals are fixed.
- [ ] Every material behavior, rule, constraint, quality, and decision has a
      current canonical owner, revision, lifecycle status, and authority, or
      the iteration stopped at the correct readiness or validation handoff.
- [ ] One objective and its exit evidence bound each iteration.
- [ ] The approved parent outcome and current completion boundary are explicit.
- [ ] Initial routing was already known, and selected in-iteration specialists
      match the objective's actual questions or implementation forces.
- [ ] A material support envelope names the approved claim and population,
      variation and fallback paths, cross-mode capability sources, explicit
      exclusions, representative coverage, and completion boundary.
- [ ] A bounded variant fix is not reported as broader support, and no missing
      capability or compatibility rule was guessed.
- [ ] Boundary-sensitive refactoring retains its system boundary,
      representative vertical oracle, native responsibilities, ownership
      consequences, and verification ownership.
- [ ] Rust lifecycle design was selected only when Rust semantics created
      material pressure and did not substitute for missing design context.
- [ ] No language, programming paradigm, phase, or artifact chain was assumed.
- [ ] Every new standalone artifact passes the value, ownership, and lifecycle
      gate.
- [ ] Justified artifact paths follow repository governance and established
      homes, or a material placement gap was routed to artifact-layout design.
- [ ] Durable knowledge changed only in its canonical owner.
- [ ] Reuse, new consumers, accumulated durable rules, and stretched non-goals
      triggered a fresh promotion check where material.
- [ ] Required validation passed, or human-owned checks remain explicit.
- [ ] Focused checks did not displace a material integration or end-to-end
      oracle, and enabling results were not reported as the parent outcome.
- [ ] Each iteration created at most one authorized, scoped commit.
- [ ] Continuous mode continued only under the user's request. Single mode
      stopped after one commit.
- [ ] No push or publication occurred without authority.
- [ ] The final report states residual risk and the reason execution stopped.
