# Implementation and Evolution

Use this track when requirements or design inputs are sufficiently clear to
implement behavior, or when verified behavior needs structural improvement.

When an external specification, scenario set, or proposal appears ready for
implementation but its approval, uncertainty, or independent oracle is unclear,
use
[`assess-development-input`](../../skills/assess-development-input/SKILL.md)
before entering this track.

## Add or Change Behavior

1. Start with an approved use case, operation contract, acceptance example,
   invariant, defect report, or other independent oracle. Preserve source-linked
   success, failure, and boundary examples. Stop for the responsible owner when
   material examples or decisions are missing instead of inventing them.
2. Use
   [`software-design-language-adaptation`](../../skills/software-design-language-adaptation/SKILL.md)
   when language-specific ownership, errors, concurrency, or interface
   conventions affect the design.
3. Use
   [`design-rust-lifecycles`](../../skills/design-rust-lifecycles/SKILL.md)
   before implementation when Rust resource ownership, startup, rollback,
   cancellation, supervision, or fallible cleanup requires an explicit
   implementation-facing lifecycle. Establish the system boundary,
   representative scenario, native responsibilities, and verification oracle
   first when the change is boundary-sensitive.
4. Use
   [`test-driven-implementation`](../../skills/test-driven-implementation/SKILL.md)
   to size the behavior slice, demonstrate discriminatory verification, and
   implement the smallest coherent change.
5. Feed implementation discoveries back into durable requirements or design
   artifacts when their represented knowledge changes.

Keep verification evidence with code, tests, schemas, or configuration by
default. Use
[`select-technical-artifacts`](../../skills/select-technical-artifacts/SKILL.md)
when several evidence artifacts compete; otherwise apply its
[Artifact Selection Budget](../../skills/select-technical-artifacts/references/artifact-selection-budget.md)
locally before creating a separate behavior-slice or implementation record.

## Improve Existing Structure

1. Establish a passing baseline that protects the behavior to preserve.
2. Classify boundary impact. If the refactoring creates or moves a material
   test seam, composition root, backend, entrypoint, process-global dependency,
   runtime owner, readiness condition, cleanup boundary, or end-to-end
   verification boundary, use
   [`iterative-risk-driven-development`](../../skills/iterative-risk-driven-development/SKILL.md)
   before treating it as a local transformation.
3. Use
   [`behavior-preserving-refactoring`](../../skills/behavior-preserving-refactoring/SKILL.md)
   for independently reviewable local structural transformations.
4. Return to responsibility design or pattern selection when the refactoring
   exposes a durable design pressure. Assign responsibilities to native
   modules, functions, tasks, adapters, handles, types, or composition roots as
   appropriate.
5. Retain material integration and end-to-end oracles. Report a new seam as an
   enabling result until a representative vertical flow proves the parent
   outcome.

Do not use refactoring to conceal intentional behavior changes, and do not ask
the implementation skill to guess unresolved business rules.
