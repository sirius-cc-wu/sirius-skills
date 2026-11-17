# Playbook 9: Behavior-Preserving Refactoring & Technical Debt Remediation

**Trigger:** Behavior-preserving technical debt reduction in Mode A (tactical Fowler code-smell) or Mode B (structural Suryanarayana design-smell).
**Alpha Progression:** *Software System*: *Degraded* → *Re-aligned & Invariants Preserved*, *Work*: *Diagnosed* → *Concluded*.

## Steps

1. **Stage 1: Diagnosis & Census Audit (Zero Code Changes)**
   - **Mode A (Tactical / Code Smell):** Use `code-smell` to diagnose function-level smells (primitive obsession, data clumps, long methods, feature envy). Produce `code_smell_census_<target>.md`.
   - **Mode B (Structural / Design Smell):** Use `design-smell` to audit macro-architectural smells across 4 pillars (*Abstraction*, *Encapsulation*, *Modularization*, *Hierarchy & Coupling*). Produce `design_smell_diagnostic_<target>.md`.
   - Deliver concrete evidence citations (file paths, line numbers, caller patterns) and canonical remedies.

2. **Stage 2: Phase 0 Characterization Safety Net Gate**
   - Before any structural modifications, provision an isolated worktree and dispatch Builder to author characterization tests:
     - Exact output snapshots (byte-identical token streams, structured outputs).
     - Pinned error messages, warning texts, and source spans across all resolution paths.
     - Pinned diagnostic precedence and edge cases.
   - Run Gate 2 dual-lane qualification, verify 100% pass, and merge the Phase 0 PR targeting `main`.

3. **Stage 3: Ordered Invariant Slices ($S_1 \to S_2 \dots \to S_n$)**
   - For each phase in the approved roadmap:
     - Provision isolated worktree via `bun scripts/worktree.ts create <branch> [base]`.
     - Dispatch Builder Mode B with explicit file staging instructions (never `git add .` or sweeping wildcards).
     - **Strict Invariance Mandate:** Emitted outputs and characterization tests must remain 100% identical; zero behavior drift.
     - Subject every slice to Gate 2 dual-lane qualification via the host's configured reviewer lanes with a binary `VERIFIED` requirement.
     - Bottom-up squash merge into `main`, prune worktree, and advance to the next slice.

4. **Sequencing Doctrine: The Two-Gear Refactoring Engine**
   - **Post-Milestone Consolidation (Feature Recently Landed):** Execute **Mode A → Mode B (Bottom-Up)**. Clear local clutter first to reveal true architectural seams safely.
   - **Pre-Milestone Preparation (Enabling a New Capability):** Execute **Mode B → Mode A (Top-Down)**. Carve Ports & Adapters, break cycles, and decompose God modules before polishing internals.
   - **Localized Debt:** Single-mode execution (`Mode A` for routine-internal; `Mode B` for cross-module coupling).
