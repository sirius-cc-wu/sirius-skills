# Playbook 2: Tier 2 Feature Slice (Streamlined TDD)

**Trigger:** New capabilities, syntax additions, or business rules localized within an established crate/component boundary (skip ADR and external contracts).
**Alpha Progression:** *Requirements* → *Acceptable*, *Work* → *Prepared* *(Architecture already selected)*.

## Steps

1. **Intake & Rule Capture**
   - Ingest issue or feature context.
   - Map user steps and variations (`feature-mapping`) and extract thin business rules (`R1`, `R2`...) via `example-mapping` in `docs/requirements/<module-id>.md`.

2. **MANDATORY HUMAN SIGN-OFF**
   - Present the journey flow and business rules to the operator for confirmation before planning or implementation.

3. **Abstraction Mapping & Task Plan (when applicable)**
   - Before execution planning, apply **Abstraction-to-Evidence Mapping** (see `SKILL.md`) when its trigger is met, and record the mapping in the relevant `docs/architecture/` document.
   - Package ordered slices in `docs/execution/<module-id>.md` (`planning-and-task-breakdown`), linking the governing rules and any architecture mapping without duplicating them.
   - Include any applicable mapping in Gate 1 review when Gate 1 is run.

4. **Builder Dispatch (Mode A)**
   - Verify clean pre-dispatch state (`git status --porcelain`).
   - Allocate isolated worktree: `bun scripts/worktree.ts create <branch-name> [base]`.
   - Dispatch builder subagent with the Example Mapping rules and explicit file scope; builder executes Red-Green-Refactor TDD, verifies with the test runner, and commits atomically via explicit paths.

5. **Acceptance Verification & Gate 3**
   - Verify 100% of defined rules pass in the builder's test matrix (and via Gate 2 qualification when configured).
   - Pass the cross-cutting Gate 3 check (see `SKILL.md`) whenever a runtime verification harness exists or before cutting any release tag.
   - Package the completed deliverable or open a PR via `create-pr`.
