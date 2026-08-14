---
name: run-development-iteration
description: Runs one risk-sized, language-neutral development iteration at a time from an approved idea, selected analysis/design candidate, or other authoritative input. Selects specialist analysis, design, implementation, and repository skills; controls artifact creation; validates the result; and creates at most one authorized commit per iteration. Use when asked to promote an approved idea, execute one approved development iteration, advance a feature continuously, perform iterative analysis and design without prescribing object-oriented artifacts, or work one commit per iteration until the requested work is complete.
---

# Run Development Iteration

## Overview

Advance one approved change through one decision, learning, design, or delivery
objective. Select methods from the current question and implementation forces.
Do not follow a mandatory artifact sequence or programming paradigm.

## When to Use

- An approved idea, feature source, or selected UP roadmap candidate needs one
  bounded analysis, design, or construction iteration.
- The user requests one commit per iteration. Use continuous mode by default
  and continue until the requested work is complete. Use single-iteration mode
  only when the user explicitly asks for one iteration or asks you to stop after
  the commit.
- Several specialist skills may apply, but they must serve one objective and
  one coherent change.
- Do not use this skill to assess readiness, coordinate iterative analysis and
  design, perform one localized specialist task, commit an existing diff, or
  publish completed work. Use `iterative-risk-driven-analysis-design` for
  risk-driven analysis and design coordination.

## Execution Modes

- **Continuous mode (default):** Treat “one commit per iteration” as a commit
  cadence. After each authorized commit, recheck the current baseline and begin
  the next iteration. Continue until the requested work is complete.
- **Single-iteration mode:** Use this mode when the user explicitly asks for
  one iteration or says to stop after the commit.
- In either mode, stop for failed validation, missing authority, an unresolved
  product or compatibility decision, an unavailable verification oracle, or a
  user instruction to stop. Do not push or publish without separate authority.

## Workflow

1. **Fix authority and baseline.** Read repository governance. Identify the
   approved source, revision, lifecycle state, requested outcome, non-goals,
   current branch, and unrelated workspace changes. Do not promote candidate
   intent or absorb unrelated work.
2. **Choose one objective.** State one behavior, decision, risk, or learning
   question and its exit evidence. If a UP roadmap supplied the candidate,
   preserve its traceability. Recheck its assumptions, readiness, and artifact
   dispositions against the current baseline. Keep the objective small enough
   for one coherent commit. Treat phase names as context, not as an artifact
   checklist.
3. **Select the narrowest owners.** Route each material uncertainty to an
   existing specialist. Use language-neutral requirements and analysis skills
   for product intent. Use language adaptation or a language specialist only
   when runtime semantics matter. Prefer one localized specialist when no
   coordination remains.
4. **Budget artifacts.** Apply
   [Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
   Prefer code, tests, configuration, an existing canonical artifact, or an
   embedded section. Use `select-technical-artifacts` when the iteration
   exposes a material choice among artifact owners or dispositions. A Git
   commit can preserve narrow iteration history. Do not require a separate
   iteration record unless coordination, audit, or durable unresolved risk
   gives it an independent lifecycle.
5. **Execute only the selected iteration.** Read and follow every selected
   specialist skill. Keep all work tied to the objective. Stop if missing
   approval, product rules, compatibility decisions, or a verification oracle
   would require invention.
6. **Reconcile durable knowledge.** Feed discoveries back only when they change
   knowledge owned by a canonical requirement, design, decision, test, schema,
   or configuration artifact. Preserve idea and decision history. Do not
   silently rewrite it. Use `record-architecture-decision` only when one
   authoritative, consequential architecture choice needs an independent
   proposed, accepted, or superseding lifecycle.
7. **Validate exit evidence.** Run repository-required and changed-scope
   checks. Distinguish completed evidence from human-owned or unavailable
   validation. Do not close or commit an iteration when its exit evidence
   failed.
8. **Simplify changed code.** If source or test code changed, use
   [Simplify](../simplify/SKILL.md) within the iteration scope. Rerun the
   affected validation.
9. **Commit once per iteration when authorized.** If the user authorized a
   commit, use [Commit](../commit/SKILL.md) with scoped staging. Create at most
   one commit for the current iteration. In continuous mode, recheck the
   current baseline before the next iteration. Do not amend, push, or publish
   without matching authority.
10. **Apply the execution mode.** In single-iteration mode, report the
    objective, canonical changes, validation, commit, and residual risk, then
    stop. In continuous mode, report the current result, select the next
    objective, and continue until the requested work or an explicit stop
    condition ends the run.

## Prepared Analysis Candidate Mode

When executing a candidate prepared by
`iterative-risk-driven-analysis-design`:

1. Treat the candidate as planning input, not execution authority by itself.
2. Require explicit authority for the candidate. Fix its current source
   revisions, non-goals, dependencies, and exit evidence.
3. Re-evaluate the selected specialists and artifact budget from current
   evidence. Preserve traceability while correcting stale assumptions.
4. Execute only this candidate. Record actual results in justified canonical or
   historical owners. Make at most one authorized commit for this candidate.
5. Apply the selected execution mode. Continue only when the user requested
   continuous execution. Report whether more risk-driven objectives remain or
   need replanning.

## Idea Promotion Mode

When the iteration promotes an approved idea:

1. Require explicit acceptance or promotion authority. Preserve the exact
   accepted revision.
2. Record the idea outcome according to repository governance.
3. Create or update the smallest canonical feature, requirement, decision, or
   design owner. Do not copy the whole idea.
4. Preserve approved meaning, open questions, non-goals, and traceability.
5. Treat promotion as the full iteration unless the user explicitly scoped a
   different single objective that remains coherent in the same commit.

## Language Extension Boundary

- Keep the coordinator independent of classes, traits, modules, functions,
  ownership models, garbage collection, exceptions, and async runtimes.
- Route general implementation mapping to
  [Software Design Language Adaptation](../software-design-language-adaptation/SKILL.md).
- Route demonstrated language-specific forces to a specialist such as
  [Design Rust Lifecycles](../design-rust-lifecycles/SKILL.md).
- Add another language specialist only when repeated design pressure exceeds
  the general adapter and has a distinct output and routing boundary.
- Do not create one skill or document template per language without a distinct
  need.

## File Output

Follow established repository paths. If a justified artifact lacks a clear
canonical home, several paths compete, or migration is material, use
[Design Repository Artifact Layout](../design-repository-artifact-layout/SKILL.md)
for that placement decision. When a standalone Markdown artifact is justified,
follow
[Markdown Artifact Frontmatter](../iterative-risk-driven-analysis-design/references/markdown-artifact-frontmatter.md)
and use STE-style.

Refine canonical artifacts in place. If a durable execution record is justified,
adapt the selected-objective structure from
[`iterative-risk-driven-analysis-design`](../iterative-risk-driven-analysis-design/SKILL.md). Record actual results and
artifact outcomes. Do not copy canonical artifact bodies into the record.

## Verification

- [ ] The input authority, revision, lifecycle state, and non-goals are fixed.
- [ ] A UP roadmap, when present, was treated as planning input rather than
      blanket execution authority.
- [ ] One objective and its exit evidence bound the iteration.
- [ ] Selected specialists match the actual questions or implementation forces.
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
