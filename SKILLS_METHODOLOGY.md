# Skills Methodology

The catalog contains independent skills grouped into installation profiles and
optional workflow tracks. Choose the smallest skill or combination that
addresses the current outcome and risk; installing a profile does not require
following every step in it.

## Select a profile

| Need | Profile |
|---|---|
| Refine, record, and publish repository changes | `workflow` |
| Assess external development inputs, design artifact layouts, author software proposals, and run question-driven analysis, design, implementation, simplification, and scoped-commit iterations | `iterative-design` |
| Recover current behavior and architecture and place durable recovered knowledge | `reverse-engineering` |
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

### Develop a candidate change into a proposal

1. Use `author-software-proposal` when technical input needs a consequential
   direction reviewed before implementation or broader design work.
2. Preserve the repository's proposal governance, canonical owner, lifecycle,
   and index; prefer one proposal file unless supporting references justify a
   proposal directory.
3. Separate current evidence and inference from proposed behavior, approval,
   and unresolved decisions.
4. Stop with a draft and a clear next decision unless the user separately
   authorizes acceptance, implementation, commit, or publication.

Once a proposal exists, use `assess-development-input` only when its readiness
or next Sirius owner is unclear. Use `rewrite-technical-artifacts` when its
meaning is already sound and only its reading path needs improvement.

### Design durable artifact placement

1. Use `design-repository-artifact-layout` when the primary outcome is a
   canonical home or migration plan for durable technical artifacts.
2. Inspect local governance, indexes, and neighboring files; preserve a coherent
   established structure unless a concrete navigation or ownership problem
   justifies change.
3. Apply the artifact-selection budget before assigning new files or
   directories, and separate current knowledge, proposals, decisions,
   verification evidence, and historical iteration records by lifecycle.
4. Keep a recommendation read-only unless the user explicitly authorizes file
   creation or migration. Return content authoring to the artifact's owning
   specialist.

### Deliver an existing change

1. Implement and verify the requested outcome.
2. Use `simplify` for a focused cleanup pass over the branch or pull-request
   diff while preserving behavior.
3. Use `commit` to review, verify, and intentionally stage the change.
4. Use `create-pr` to publish committed work when the user requests it.

`governance-update` is orthogonal. Use it only when repeated evidence reveals a
durable policy gap.

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

1. Use `run-development-iteration` to execute one approved, risk-sized
   iteration, validate it, create one authorized commit, and stop.
2. Use `stakeholder-requirements-elicitation` when the affected roles, current
   work, authority, or evidence coverage is unclear.
3. Use `requirements-synthesis-validation` to turn an identified evidence set
   into source-linked candidate requirements, concrete examples, and
   authority-aware validation states.
4. Select requirements and analysis skills from the current uncertainty:
   scope, behavior, examples, vocabulary, system events, or state effects.
5. Use `iterative-up-analysis-design` only when a team explicitly wants UP
   phase framing or a multi-iteration use-case and object-design plan. Select
   GRASP, realizations, class diagrams, and patterns only when their questions
   or design forces are present. Delegate a material repository-placement
   question to `design-repository-artifact-layout`.
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
