---
name: run-development-iteration
description: Runs exactly one risk-sized, language-neutral development iteration from an approved proposal or other authoritative input, selecting specialist analysis, design, implementation, and repository skills, controlling artifact creation, validating the result, and creating one authorized commit before stopping. Use when asked to promote an approved proposal, advance a feature by one iteration, perform iterative analysis and design without prescribing object-oriented artifacts, or work one commit per iteration.
---

# Run Development Iteration

## Overview

Advance one approved change by one decision, learning, design, or delivery
objective. Select methods from the current question and implementation forces,
not from a mandatory artifact sequence or programming paradigm.

## When to Use

- An approved proposal or feature source should advance through one bounded
  analysis, design, or construction iteration.
- The user requests one commit per iteration and expects work to stop at that
  boundary.
- Several specialist skills may apply, but they must serve one shared
  objective and one coherent change.
- Do not use merely to assess readiness, plan a multi-iteration roadmap,
  perform one already-localized specialist task, commit an existing diff, or
  publish completed work.

## Workflow

1. **Fix authority and baseline.** Read repository governance and identify the
   approved source, its revision and lifecycle state, the requested outcome,
   non-goals, current branch, and unrelated workspace changes. Do not promote
   candidate intent or absorb unrelated work.
2. **Choose one iteration objective.** State one behavior, decision, risk, or
   learning question plus concrete exit evidence. Keep the objective small
   enough for one coherent commit. Treat phase names as context, not as an
   artifact checklist.
3. **Select the narrowest owners.** Route each material uncertainty to an
   existing specialist. Use language-neutral requirements and analysis skills
   for product intent; use implementation-facing language adaptation or a
   language specialist only when runtime semantics matter. Prefer one
   localized specialist over this coordinator when no coordination remains.
4. **Budget artifacts.** Apply
   [Artifact Selection Budget](../iterative-up-analysis-design/references/artifact-selection-budget.md).
   Prefer code, tests, configuration, an existing canonical artifact, or an
   embedded section. A Git commit can preserve narrow iteration history; do
   not require a separate iteration record unless coordination, audit, or
   durable unresolved risk gives it an independent lifecycle.
5. **Execute only the selected iteration.** Read and follow every selected
   specialist skill. Keep all work tied to the shared objective and stop if a
   missing approval, product rule, compatibility decision, or verification
   oracle would require invention.
6. **Reconcile durable knowledge.** Feed discoveries back only when they
   change knowledge owned by a canonical requirement, design, decision, test,
   schema, or configuration artifact. Preserve proposal and decision history
   rather than silently rewriting it.
7. **Validate exit evidence.** Run repository-required and changed-scope
   checks. Distinguish completed evidence from human-owned or unavailable
   validation. Do not close or commit an iteration whose stated exit evidence
   failed.
8. **Simplify changed code.** When source or test code changed, use
   [Simplify](../simplify/SKILL.md) within the iteration scope and rerun the
   affected validation.
9. **Commit once when authorized.** If the user authorized a commit for this
   iteration, use [Commit](../commit/SKILL.md) with scoped staging. Create
   exactly one commit containing the coherent iteration outcome. Do not amend,
   push, publish, or start another iteration without matching authority.
10. **Stop at the boundary.** Report the objective, canonical changes,
    validation, commit when created, residual risk, and one candidate next
    iteration. Do not execute that candidate.

## Proposal Promotion Mode

When the iteration promotes a proposal:

1. Require explicit acceptance or promotion authority and preserve the exact
   accepted revision.
2. Record the proposal outcome according to repository governance.
3. Create or update the smallest canonical feature, requirement, decision, or
   design owner without copying the whole proposal.
4. Preserve approved meaning, open questions, non-goals, and traceability.
5. Treat promotion as the full iteration unless the user explicitly scoped a
   different single objective that remains coherent in the same commit.

## Language Extension Boundary

- Keep the coordinator independent of classes, traits, modules, functions,
  ownership models, garbage collection, exceptions, or async runtimes.
- Route general implementation mapping to
  [Software Design Language Adaptation](../software-design-language-adaptation/SKILL.md).
- Route demonstrated language-specific forces to a specialist such as
  [Design Rust Lifecycles](../design-rust-lifecycles/SKILL.md).
- Add another language specialist only when repeated design pressure exceeds
  the general adapter and has a distinct output and routing boundary.
- Do not manufacture one skill or document template per language.

## File Output

Follow established repository paths. If a justified artifact lacks a clear
canonical home, several paths compete, or migration is material, use
[Design Repository Artifact Layout](../design-repository-artifact-layout/SKILL.md)
for that placement decision. When a standalone Markdown artifact is justified,
follow
[Markdown Artifact Frontmatter](../iterative-up-analysis-design/references/markdown-artifact-frontmatter.md)
and
[Readable Technical Artifacts](../iterative-up-analysis-design/references/readable-technical-artifacts.md).
Refine canonical artifacts in place. If a durable iteration record is
justified, use the iteration-record structure owned by
[`iterative-up-analysis-design`](../iterative-up-analysis-design/SKILL.md)
without copying canonical artifact bodies into it.

## Verification

- [ ] The input authority, revision, lifecycle state, and non-goals are fixed.
- [ ] One objective and its exit evidence bound the iteration.
- [ ] Selected specialists match actual questions or implementation forces.
- [ ] No language, programming paradigm, phase, or artifact chain was assumed.
- [ ] Every new standalone artifact passes the value, ownership, and lifecycle gate.
- [ ] Durable knowledge changed only in its canonical owner.
- [ ] Required validation passed or human-owned checks remain explicit.
- [ ] Changed source and tests received a scoped simplification pass.
- [ ] At most one authorized, scoped commit was created.
- [ ] No push, publication, or next iteration occurred without authority.
- [ ] The final report states residual risk and stops at the iteration boundary.
