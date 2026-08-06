# Skills Methodology

The catalog contains independent skills grouped into installation profiles and
optional workflow tracks. Choose the smallest skill or combination that
addresses the current outcome and risk; installing a profile does not require
following every step in it.

## Select a profile

| Need | Profile |
|---|---|
| Refine, record, and publish repository changes | `workflow` |
| Assess external development inputs, author software proposals, discover requirements, and move through analysis, object design, implementation, and refactoring | `iterative-design` |
| Recover current behavior and architecture from an existing system | `reverse-engineering` |
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

1. Use `iterative-up-analysis-design` to coordinate risk-sized iterations and
   durable artifacts.
2. Use `stakeholder-requirements-elicitation` when the affected roles, current
   work, authority, or evidence coverage is unclear.
3. Use `requirements-synthesis-validation` to turn an identified evidence set
   into source-linked candidate requirements, concrete examples, and
   authority-aware validation states.
4. Select requirements and analysis skills according to the uncertainty:
   inception, use cases, domain modeling, system sequence diagrams, and
   operation contracts.
5. Assign responsibilities and collaborations with GRASP and use-case
   realization; summarize stable structure with design class diagrams.
6. Apply patterns and language adaptation only when concrete design forces
   justify them.
7. Use `implementation-slice-briefing` when an unfamiliar implementer needs one
   ready vertical slice assembled from approved requirements, examples, design
   inputs, and revision-fixed repository facts.
8. Use `test-driven-implementation` for behavior changes and
   `behavior-preserving-refactoring` for verified structural improvement.

The detailed handoffs and stopping rules live in [`catalog/tracks/`](catalog/tracks/).

## Shared principles

- Follow the nearest `AGENTS.md` and repository-local instructions.
- Keep actions within the authority granted by the user; one skill does not
  implicitly authorize later commits or publication.
- Preserve established layouts and canonical artifact ownership.
- Keep staging, formatting, and validation scoped to the intended change.
- Prefer project configuration over company- or tracker-specific hardcoding.
- Report the checks run, their results, and material residual uncertainty.

## Configuration

When `.skills/conventions.json` exists, `commit` and `create-pr` may use
`commit_format`, `pr_title_format`, `branch_extract_pattern`, and `id_pattern`.
Without repository-specific configuration, both skills use their documented
generic defaults.
