---
name: iterative-risk-driven-development
description: Coordinates one or more approved, risk-sized development iterations across analysis, design, implementation, and verification. Selects only the needed specialists, evolves canonical artifacts, applies Rust ownership design when required, validates each result, and creates at most one authorized commit per iteration. Use when a feature needs risk-driven iterative progress or one commit per iteration until the requested work is complete.
---

# Iterative Risk-Driven Development

## Overview

Advance an approved change through one or more risk-sized iterations. Each
iteration answers one decision, learning, design, or delivery question. Select
methods from the current question and implementation forces. Do not follow a
mandatory artifact sequence, programming paradigm, or phase checklist.

## When to Use

- An approved idea, feature source, prepared analysis/design objective, or
  other authoritative input needs bounded progress.
- The user requests one commit per iteration and expects work to continue until
  the requested outcome is complete.
- Several specialist skills may apply, but they must serve one objective and one
  coherent change.
- A design question may require analysis, object design, implementation, or
  verification in the same risk-sized loop.
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

## Workflow

1. **Fix authority and baseline.** Read repository governance. Identify the
   approved source, revision, lifecycle state, requested outcome, non-goals,
   current branch, and unrelated workspace changes. Do not promote candidate
   intent or absorb unrelated work.
2. **Choose one objective.** State one behavior, decision, risk, or learning
   question and its exit evidence. Keep the objective small enough for one
   coherent commit.
3. **Select the narrowest owners.** Route each material question to an existing
   specialist. Use requirements, recovery, analysis, and design skills for
   product intent. Use `test-driven-implementation` for bounded behavior and
   `behavior-preserving-refactoring` for verified structural improvement.
   Prefer one localized specialist when no coordination remains.
4. **Budget artifacts.** Apply
   [Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
   Prefer code, tests, configuration, an existing canonical artifact, or an
   embedded section. Create a standalone artifact only when its value, owner,
   and independent lifecycle are clear.
5. **Select Rust lifecycle design when needed.** If the target is Rust and
   ownership, capability transfer, startup, rollback, cancellation,
   supervision, or cleanup affects the objective, use
   [Design Rust Lifecycles](../design-rust-lifecycles/SKILL.md). Treat its result
   as part of the current iteration. Do not force Rust lifecycle design when
   those semantics do not affect the objective.
6. **Execute the selected work.** Read and follow every selected specialist
   skill. Keep all work tied to the objective. Stop if missing approval,
   product rules, compatibility decisions, or a verification oracle would
   require invention.
7. **Reconcile durable knowledge.** Feed discoveries back only when they change
   knowledge owned by a canonical requirement, design, decision, test, schema,
   or configuration artifact. Preserve idea and decision history. Do not
   silently rewrite it. Use `record-architecture-decision` only when one
   authoritative, consequential architecture choice needs an independent
   proposed, accepted, or superseding lifecycle.
8. **Validate exit evidence.** Run repository-required and changed-scope
   checks. Distinguish completed evidence from human-owned or unavailable
   validation. Do not close or commit an iteration when its exit evidence
   failed.
9. **Simplify changed code.** If source or test code changed, use
   [Simplify](../simplify/SKILL.md) within the iteration scope. Rerun the
   affected validation.
10. **Commit once per iteration when authorized.** If the user authorized a
    commit, use [Commit](../commit/SKILL.md) with scoped staging. Create at most
    one commit for the current iteration. Do not amend, push, or publish without
    matching authority.
11. **Apply the execution mode.** In single-iteration mode, report the
    objective, canonical changes, validation, commit, and residual risk, then
    stop. In continuous mode, report the current result, choose the next
    objective, and continue until the requested work or an explicit stop
    condition ends the run.

## Rust Ownership and Lifecycle Design

Use `design-rust-lifecycles` only when Rust semantics create material design
pressure. The specialist covers:

- ownership and capability transfer;
- staged startup and readiness;
- rollback and partial initialization;
- asynchronous cancellation and supervision; and
- resource termination and fallible cleanup.

Keep product behavior, requirements, and language-neutral design separate from
these implementation-facing lifecycle decisions.

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
- [Use case] -> [SSD/contract] -> [design realization/class]

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
- Several objectives are combined into one commit.
- A mandatory artifact chain or programming paradigm is imposed.
- All artifacts are created at full detail before risk is understood.
- A standalone document has no durable decision, named consumer, material risk,
  or independent lifecycle.
- Object design starts from a domain model without behavior or system events.
- Rust lifecycle design is added without material ownership or resource
  pressure.
- Durable artifacts are copied into iteration records instead of linked.
- The iteration continues after failed validation or a missing authority.
- Continuous execution starts without a user request or single mode ignores an
  explicit stop boundary.
- Push, publication, or an unrelated change occurs inside the iteration.

## Verification

- [ ] Authority, source revision, lifecycle state, requested outcome, and
      non-goals are fixed.
- [ ] One objective and its exit evidence bound each iteration.
- [ ] Selected specialists match the actual questions or implementation forces.
- [ ] Rust lifecycle design was selected only when Rust semantics created
      material pressure.
- [ ] No language, programming paradigm, phase, or artifact chain was assumed.
- [ ] Every new standalone artifact passes the value, ownership, and lifecycle
      gate.
- [ ] Durable knowledge changed only in its canonical owner.
- [ ] Required validation passed, or human-owned checks remain explicit.
- [ ] Changed source and tests received a scoped simplification pass.
- [ ] Each iteration created at most one authorized, scoped commit.
- [ ] Continuous mode continued only under the user's request. Single mode
      stopped after one commit.
- [ ] No push or publication occurred without authority.
- [ ] The final report states residual risk and the reason execution stopped.
