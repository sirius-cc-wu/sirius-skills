# Implementation and Evolution

Use this track when requirements or design inputs are sufficiently clear to
implement behavior, or when verified behavior needs structural improvement.

When an external specification, scenario set, or proposal appears ready for
implementation but its approval, uncertainty, or independent oracle is unclear,
use
[`assess-development-input`](../../skills/assess-development-input/SKILL.md)
before entering this track.

`test-driven-implementation` is retired. Existing behavior-slice evidence
remains valid at its recorded revision. With the `all` installation, use
external
[`test-driven-development`](https://github.com/addyosmani/agent-skills/blob/5a1b82d6445d1e2f0abeea1072851419a50c0e5c/skills/test-driven-development/SKILL.md)
for new logic, bug fixes, and behavior changes. Otherwise, follow repository implementation and verification guidance
directly. Use `iterative-risk-driven-development` when analysis, design,
implementation, verification, or commit boundaries require coordination.

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
4. With the `all` installation, use external `test-driven-development`.
   Otherwise, follow repository-native implementation and verification
   guidance. Size one coherent behavior change, establish checks that can
   detect an incorrect result, implement the smallest sufficient change, and
   run proportional regression checks.
5. Feed implementation discoveries back into durable requirements or design
   artifacts when their represented knowledge changes.

Keep verification evidence with code, tests, schemas, or configuration by
default. Use
[`select-technical-artifacts`](../../skills/select-technical-artifacts/SKILL.md)
when several evidence artifacts compete; otherwise apply its
[Artifact Selection Budget](../../skills/select-technical-artifacts/references/artifact-selection-budget.md)
locally before creating a separate behavior-slice or implementation record.

## Review and Improve Existing Structure

1. With the `all` installation, use external `code-review-and-quality` after
   implementation. Otherwise, use repository-native review. A direct,
   independently bounded structural request may skip this review entry point.
2. Route each requested change or review finding to one owner:
   - Use external `code-simplification` for routine naming, extraction,
     duplication, control-flow, or recent-code clarity work.
   - Use
     [`behavior-preserving-refactoring`](../../skills/behavior-preserving-refactoring/SKILL.md)
     for an established responsibility, dependency, variation, or
     configuration-ownership change.
   - Use
     [`iterative-risk-driven-development`](../../skills/iterative-risk-driven-development/SKILL.md)
     when the change creates or moves a material test seam, composition root,
     backend, entrypoint, process-global dependency, runtime owner, readiness
     condition, cleanup boundary, or end-to-end verification boundary.
3. Establish a passing baseline before either behavior-preserving change. Keep
   each transformation independently reviewable and rerun affected checks.
4. Return substantive changes to review. Retain material integration and
   end-to-end oracles, and feed durable responsibility or pattern pressure back
   to its design owner.

Do not use refactoring to conceal intentional behavior changes. Do not let an
implementation process guess unresolved business rules.
