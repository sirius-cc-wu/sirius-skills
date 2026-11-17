# Playbook 1: Tier 1 Architectural Change (Full Golden Path)

**Trigger:** Cross-crate/subsystem boundaries, wire/network protocols, storage schemas, security models, or new components.
**Alpha Progression:** *Software System* → *Architecture Selected*, *Requirements* → *Acceptable*, *Work* → *Prepared*.

## Steps

1. **Intake & Intent Discovery**
   - Ingest context via issue tracker or user brief.
   - If intent is ambiguous, interview the operator with `interview-me` (one question at a time) and check `VISION.md` alignment with `vision` when present.

2. **Requirements Mapping**
   - Map user journey steps and variations using `feature-mapping`.
   - Surface concrete business rules (`R1`, `R2`, `R3`...) using `example-mapping` in `docs/requirements/<module-id>.md` (or `recover-specification` when documenting already-implemented behavior).
   - **MANDATORY HUMAN SIGN-OFF:** Present the journey flow and rules table to the operator. Obtain explicit approval before advancing.

3. **System & Domain Analysis**
   - If the capability alters an external system boundary (what external actors/testers experience): derive black-box System Sequence Diagrams (SSDs) and operation contracts in `docs/contracts/<module-id>.md` using `system-behavior`.
   - If the task is an internal refactoring or seam extraction with zero external behavior change: skip `docs/contracts/` and specify internal port seams directly in `docs/architecture/`.
   - Model aggregates and Ubiquitous Language with `model-discovery`, and bounded contexts with `context-mapping` when crossing domain boundaries.

4. **Architecture, Invariants & Upfront ADR**
   - Before execution planning, apply **Abstraction-to-Evidence Mapping** (see `SKILL.md`) when its trigger is met, recording the table in `docs/architecture/<subsystem>.md`.
   - Analyze layering, seams, and structural dependencies with `architecture` and `api-and-interface-design`.
   - Author the binding upfront ADR in `docs/decisions/adr-XXX-<slug>.md` with `architecture-decision-records` as pure declarative text (zero Mermaid diagrams).
   - Author the living architecture blueprint in `docs/architecture/<subsystem>.md` (visual topologies, composition roots, internal port seams, native rules `A1..An`, zero ADR back-references; embed `design-rust-lifecycles` / `type-anchored-spec` findings directly rather than creating standalone detailed-design files).
   - Package ordered vertical slices in `docs/execution/<module-id>.md` using `planning-and-task-breakdown`, linking governing rules and architecture mappings rather than duplicating them.

5. **Gate 1: Adversarial Doubt Review**
   - Execute fresh-context adversarial review using `doubt-driven-development` to audit unstated assumptions, edge cases, backward compatibility, and any applicable abstraction mapping.
   - Reconcile all findings directly in `docs/` before Builder dispatch.

6. **Builder Dispatch (Mode A)**
   - Verify clean pre-dispatch state (`git status --porcelain`).
   - Allocate isolated worktree: `bun scripts/worktree.ts create <branch-name> [base]`.
   - Dispatch builder subagent with governing spec, ADR, execution plan, and Mode A TDD instructions.

7. **Gate 2: Code Qualification**
   - Inspect the Builder Execution Report and diff via `spec-qualification` and `code-review-and-quality` ("Audit, Don't Execute").
   - Issue binary verdict (`VERIFIED` or `UNVERIFIED`) in `docs/verification/qualification-<module-id>.md`.

8. **Gate 3: Runtime Surface & Pre-Release Qualification**
   - Pass the cross-cutting Gate 3 check (see `SKILL.md`) whenever a runtime verification harness exists or before cutting any release tag.
