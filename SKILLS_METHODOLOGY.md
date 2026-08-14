# Skills Methodology

The catalog contains independent skills grouped into installation profiles and
optional workflow tracks. Choose the smallest skill or combination that
addresses the current outcome and risk; installing a profile does not require
following every step in it.

## Select a profile

| Need | Profile |
|---|---|
| Refine, record, and publish repository changes | `workflow` |
| Assess external development inputs, select technical artifacts, record architecture decisions, design artifact layouts, and run question-driven analysis, design, implementation, simplification, and scoped-commit iterations | `iterative-design` |
| Recover current behavior and architecture, find governing ADRs, select durable recovered artifacts, and place them | `reverse-engineering` |
| Make the entire catalog available | `all` |

`applying-uml-and-patterns` remains a compatibility alias for
`iterative-design`.

## Common compositions

### Route an external development input

1. Use `assess-development-input` when a specification, proposal, scenario set,
   story map, brainstorm result, or other requirements-shaped input exists but
   its Sirius entry point is unclear.
2. Preserve the source's revision, approval state, non-goals, and unresolved
   questions; assess readiness from content rather than format or originating
   method.
3. Return to the relevant external authority when a missing decision cannot be
   owned by a Sirius skill.
4. Invoke the one recommended Sirius skill only when the user authorizes the
   downstream work.

The assessment is an intake boundary, not a mandatory first step or a
replacement for discovery and specification methods.

### Clarify intent and refine a candidate direction

1. When one requester's actual outcome, user, success condition, constraint, or
   non-goals are unclear, optionally use Addy Osmani's
   [`interview-me`](https://github.com/addyosmani/agent-skills/blob/5a1b82d6445d1e2f0abeea1072851419a50c0e5c/skills/interview-me/SKILL.md).
2. When a raw idea needs alternatives, assumption testing, MVP scope, and an
   explicit not-doing list, optionally use
   [`idea-refine`](https://github.com/addyosmani/agent-skills/blob/5a1b82d6445d1e2f0abeea1072851419a50c0e5c/skills/idea-refine/SKILL.md).
3. Treat the confirmed idea one-pager as candidate input, not approval. Save
   it in `docs/ideas/` or a feature location defined by local governance. Do not
   create a new proposal artifact. Preserve existing legacy proposals at their
   historical paths.
4. Use `assess-development-input` only when the next Sirius owner is unclear.
   Route evidence, stakeholder authority, scope, acceptance behavior, design,
   and implementation readiness to their narrow specialists.

`author-software-proposal` is retired because its normal output overlapped the
confirmed idea one-pager. Existing legacy proposal artifacts remain valid.
Owning artifact skills write reader-facing material in STE-style from the
outset.

### Record a consequential architecture decision

1. Use `record-architecture-decision` after one bounded architecture choice is
   ready for proposed review, has been explicitly accepted, or must supersede a
   governing ADR.
2. Apply the artifact-selection budget and preserve established ADR paths,
   templates, statuses, opaque identifiers, and indexes.
3. Put the decision, status, authority, and important consequence first; retain
   context and forces, serious alternatives, positive and negative consequences,
   confidence, reconsideration triggers, and material advice.
4. Keep proposed status distinct from acceptance. Do not reconstruct rationale
   from code, rewrite an accepted decision when it changes, or continue into
   implementation, commit, or publication without separate authority.

Use the corresponding design specialist when the choice is unresolved. Keep a
local pattern or responsibility decision in its owning artifact unless the
choice is independently consequential and expensive to reverse.

### Select the smallest durable artifact set

1. Use `select-technical-artifacts` when the material question is whether
   candidate knowledge should be created, updated, embedded, kept with
   implementation, omitted, or deferred.
2. Inspect executable and canonical owners, then require standalone artifacts
   to demonstrate concrete value, insufficient existing ownership, and an
   independent lifecycle.
3. Consolidate candidates that share an owner and lifecycle. Route selected
   content to its specialist and material placement questions to
   `design-repository-artifact-layout`.
4. Keep the recommendation read-only unless the user separately authorizes an
   existing budget or plan update. Creating selected artifacts and executing
   their handoffs remain separate actions. Owning skills may apply the same
   budget locally when selection is straightforward.

### Design durable artifact placement

1. Use `design-repository-artifact-layout` when the primary outcome is a
   canonical home or migration plan for durable technical artifacts.
2. Inspect local governance, indexes, and neighboring files; preserve a coherent
   established structure unless a concrete navigation or ownership problem
   justifies change.
3. Require justified artifacts before assigning new files or directories, and
   separate current knowledge, ideas, decisions, verification evidence, and
   historical iteration records by lifecycle. Preserve legacy proposals at
   their historical paths.
4. Keep a recommendation read-only unless the user explicitly authorizes file
   creation or migration. Return content authoring to the artifact's owning
   specialist.

### Deliver an existing change

1. Implement and verify the requested outcome.
2. Use `simplify` for a focused cleanup pass over the branch or pull-request
   diff while preserving behavior.
3. Use `commit` to review, verify, and intentionally stage the change.
4. Use `create-pr` to publish committed work when the user requests it.

`governance-update` is retired. When repeated evidence reveals a durable policy
gap, directly update the nearest applicable `AGENTS.md` with the narrowest
enforceable rule. Do not turn a one-off defect into policy or duplicate an
existing rule owner.

### Understand before changing

1. Use `reverse-engineer-software-system` to frame the decision and recovery
   scope.
2. Use `survey-existing-system` for first contact.
3. Recover observable behavior or reconstruct architecture only where the
   decision requires it.
4. Use `reconcile-recovered-design` when code, tests, observations,
   documentation, intent, or history may disagree.
5. Hand validated knowledge to iterative design or a bounded implementation.

### Design and implement iteratively

1. Use `iterative-risk-driven-development` to execute approved, risk-sized
   iterations. By default, one commit per iteration continues until the
   requested work is complete. Request one iteration explicitly when the run
   must stop after one commit.
2. Use `stakeholder-requirements-elicitation` when the affected roles, current
   work, authority, or evidence coverage is unclear.
3. Use `requirements-synthesis-validation` to turn an identified evidence set
   into source-linked candidate requirements, concrete examples, and
   authority-aware validation states.
4. Select requirements and analysis skills from the current uncertainty:
   scope, behavior, examples, vocabulary, system events, or state effects.
5. Use `iterative-risk-driven-development` when an approved change needs
   risk-driven progress. Give each objective exit evidence. Select GRASP,
   realizations, class diagrams, patterns, and Rust lifecycle design only when
   their questions or design forces are present. Delegate material repository
   placement to `design-repository-artifact-layout`.
6. Use `software-design-language-adaptation` when implementation-facing design
   must reflect a target language. Use `design-rust-lifecycles` when Rust
   ownership, resource transfer, startup, rollback, cancellation, or fallible
   cleanup is itself a material design problem. Add future language
   specialists by demonstrated design pressure, not by completing a language
   matrix.
7. Use `implementation-slice-briefing` when an unfamiliar implementer needs one
   ready vertical slice assembled from approved requirements, examples, design
   inputs, and revision-fixed repository facts.
8. Use `test-driven-implementation` for behavior changes and
   `behavior-preserving-refactoring` for verified structural improvement.

One iteration may coordinate several specialists only when they serve the same
objective and coherent commit. A separate Markdown iteration record is
optional; create one only when it passes the artifact budget. Commit and push
remain separately authorized effects.

The detailed handoffs and stopping rules live in [`catalog/tracks/`](catalog/tracks/).

## Shared principles

- Follow the nearest `AGENTS.md` and repository-local instructions.
- Keep actions within the authority granted by the user; one skill does not
  implicitly authorize later commits or publication.
- Preserve established layouts and canonical artifact ownership.
- Keep staging, formatting, and validation scoped to the intended change.
- Prefer explicit repository rules in the applicable `AGENTS.md` over company-
  or tracker-specific hardcoding in shared skills.
- Report the checks run, their results, and material residual uncertainty.

## Repository rules

When the applicable `AGENTS.md` defines commit-message, pull-request-title,
branch-identifier, or identifier-validation rules, `commit` and `create-pr`
follow them. Without explicit repository rules, both skills use their
documented generic defaults.
