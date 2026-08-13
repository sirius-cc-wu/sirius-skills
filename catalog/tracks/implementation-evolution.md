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
   invariant, defect report, or other independent oracle.
2. If the approved behavior lacks shared examples or has important boundary
   cases, use
   [`behavior-driven-specification`](../../skills/behavior-driven-specification/SKILL.md)
   before implementation.
3. Use
   [`software-design-language-adaptation`](../../skills/software-design-language-adaptation/SKILL.md)
   when language-specific ownership, errors, concurrency, or interface
   conventions affect the design.
4. Use
   [`design-rust-lifecycles`](../../skills/design-rust-lifecycles/SKILL.md)
   before implementation when Rust resource ownership, startup, rollback,
   cancellation, supervision, or fallible cleanup requires an explicit
   implementation-facing lifecycle.
5. Use
   [`test-driven-implementation`](../../skills/test-driven-implementation/SKILL.md)
   to size the behavior slice, demonstrate discriminatory verification, and
   implement the smallest coherent change.
6. Feed implementation discoveries back into durable requirements or design
   artifacts when their represented knowledge changes.

Keep verification evidence with code, tests, schemas, or configuration by
default. Use
[`select-technical-artifacts`](../../skills/select-technical-artifacts/SKILL.md)
when several evidence artifacts compete; otherwise apply its
[Artifact Selection Budget](../../skills/select-technical-artifacts/references/artifact-selection-budget.md)
locally before creating a separate behavior-slice or implementation record.

## Improve Existing Structure

1. Establish a passing baseline that protects the behavior to preserve.
2. Use
   [`behavior-preserving-refactoring`](../../skills/behavior-preserving-refactoring/SKILL.md)
   for independently reviewable structural transformations.
3. Return to responsibility design or pattern selection only when the
   refactoring exposes a durable design pressure.

Do not use refactoring to conceal intentional behavior changes, and do not ask
the implementation skill to guess unresolved business rules.
