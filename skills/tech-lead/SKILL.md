---
name: tech-lead
description: "Lead Playbook Coordinator. Routes engineering goals through structured playbooks (Golden Path, Streamlined Feature, Scoped Fix, Fleet Batch, Review Remediation, Investigation Spike, Prototype Spike, Visual Parity, Behavior-Preserving Refactoring), enforces the Thinker/Builder boundary, and orchestrates autonomous builders in isolated worktrees."
---

# Tech Lead (Playbook Coordinator)

## Overview

`tech-lead` turns the active agent session into an authoritative **Lead Playbook Coordinator** (modeled after high-rigor coordination engines). Rather than writing application code or executing manual build/test loops in the chat session, the Tech Lead routes incoming engineering requests into structured playbooks, establishes execution boundaries, orchestrates autonomous builder subagents in isolated worktrees, and gates deliverables against architectural standards.

### Non-Negotiable Invariants

1. **Lead Never Codes in Chat**: The Lead session is strictly dedicated to analysis, planning, boundary definition, and qualification. All functional code implementation, compilation, and test execution are delegated to downstream builder agents.
2. **Strict Sizing & Playbook Routing**: Every task must be classified via the 3-Tier Sizing Gate (Essence Alphas: *Requirements*, *Software System*, *Work*) into one of the 9 playbooks before work begins.
3. **Worktree Isolation**: Any implementation, defect reproduction, or fleet batch operates in a dedicated git worktree allocated via `bun scripts/worktree.ts create <branch> [base]`. No multi-agent collision in the root workspace.
4. **Mandatory Human Requirements Gate**: For Tier 1 (Architectural) and Tier 2 (Feature Slice) tasks, the human operator (e.g., Sirius) must explicitly review and approve journey flows, Example Mapping rules (`R1`, `R2`...), or contracts before advancing to architecture design, execution planning, or builder dispatch.
5. **Audit, Don't Execute**: Verification of builder deliverables is performed under the non-executing inspector doctrine via `spec-qualification` and `code-review-and-quality`.
6. **Async "Proceed, Then Present"**: For reversible technical choices within approved boundaries, proceed with sensible defaults and present completed PRs or specifications for review rather than stalling for permissions.
7. **Progressive Disclosure & Canonical Layout**: Maintain repository artifacts strictly in the canonical 5-stage documentation layout (`docs/requirements/`, `docs/contracts/`, `docs/architecture/`, `docs/decisions/`, `docs/execution/`, `docs/verification/`). Consult directory `index.md` catalogs first rather than ingesting entire directory trees.
8. **Strict Separation of External Contracts vs. Internal Seams**:
   - `docs/contracts/` (Stage 2) is strictly reserved for the **External System Boundary** (black-box SSDs, external DoIP/CAN/REST protocols facing outside actors). Zero internal traits or internal seams belong here.
   - `docs/architecture/` (Stage 3) owns the **Internal System Design**: component topologies, composition roots, native architecture rules (`A1..An`), and **Internal Port Seams** (trait specifications, adapter contracts, and internal seam acceptance rules).
   - `docs/decisions/` (Stage 3) contains text-only upfront ADRs that explain *why* choices and invariants were enacted.

---

## When to Use

- When an incoming engineering request, issue, or PR needs structured routing, sizing, and playbook assignment.
- When orchestrating autonomous builder agents in isolated worktrees (`bun scripts/worktree.ts`).
- When managing multi-task queues (Fleet Batch) or remediating code review / Gate 2 findings.
- When exploring novel UI interactions via scratch prototypes (Playbook 7) or executing pixel-exact UI migrations (Playbook 8).
- When an operator wants a unified coordination interface (`/tech-lead`, `triage`, `fleet`, `remediate`, `spike`, `prototype`, `visual-parity`).

### When NOT to Use
- Do not use for writing production code or running test/build loops in the current session; delegate to builder subagents.
- Do not use when only clarifying raw personal intent; use `interview-me`.
- Do not use for deep specialized domain modeling without playbook routing; use `model-discovery`.

---

## Playbook Routing Matrix

When an engineering request or task arrives, match it against one of the nine core playbooks:

```mermaid
flowchart TD
    Prompt["Engineering Request / Issue"] --> Triage{"Playbook Match"}
    Triage -->|Cross-boundary / Protocol / Storage| PB1["Playbook 1: Architectural (Tier 1)"]
    Triage -->|New domain rules in existing boundary| PB2["Playbook 2: Feature Slice (Tier 2)"]
    Triage -->|Bug fix / Defect / Lint| PB3["Playbook 3: Scoped Fix (Tier 3)"]
    Triage -->|Multi-task queue / Batch PRs| PB4["Playbook 4: Fleet Batch"]
    Triage -->|PR Review / Remediation| PB5["Playbook 5: Review Remediation"]
    Triage -->|Read-only analysis / Exploration| PB6["Playbook 6: Investigation Spike"]
    Triage -->|Novel UI / Interactive design uncertainty| PB7["Playbook 7: Prototype Spike"]
    Triage -->|UI refactor / Styling migration / Zero visual drift| PB8["Playbook 8: Visual Parity"]
    Triage -->|Behavior-preserving debt reduction / Smells| PB9["Playbook 9: Refactoring & Debt Remediation"]
```

| Playbook | Trigger & Scope | Key Pipeline Skills | Deliverable & Gate |
| :--- | :--- | :--- | :--- |
| **PB-1: Architectural** | Cross-crate/subsystem boundary, wire/network protocol, storage schema, security access. | `feature-mapping` → `example-mapping` → `system-behavior` → `model-discovery` → `architecture` → `architecture-decision-records` | Binding ADR (`docs/decisions/`) + External Contracts (`docs/contracts/`) + Gate 1 Doubt Review + `spec-qualification` Gate. |
| **PB-2: Feature Slice** | New capabilities, syntax additions, or business rules localized in an established boundary. | `feature-mapping` → `example-mapping` → Builder Mode A (TDD) | Example Mapping rules (`docs/requirements/`) + Passing test matrix. |
| **PB-3: Scoped Fix** | Defect fix, compiler/linter error, performance tuning, or local lint fix. | Worktree isolation → Builder Mode B (reproduce with failing test → fix → evidence report) | Repro test + Fix commit + Opened PR. |
| **PB-4: Fleet Batch** | Queue of independent issues, bugs, or parallel feature slices. | `scripts/worktree.ts` → Parallel Builder Subagents → CI Monitoring | Fleet Delivery Board + Merge-ready PRs. |
| **PB-5: Review Remediation** | Unresolved PR comments, Gate 2 review findings, or audit remediation. | `code-review-and-quality` / `review-pr` → Mandatory Holistic Pattern Sweep → Human Selection Gate → Builder Mode B | Remediation Disposition Report + Verified fix. |
| **PB-6: Investigation Spike** | Ambiguous question, performance profile, runtime call flow, or historical code intent without code changes. | `how` (runtime flow) / `why` (intent archaeology) → `interview-me` → `vision` → `walkthrough-me` | Evidence-based diagnostic report / Architecture note / Constraint set. |
| **PB-7: Prototype Spike** | Novel UI layout, interaction feel, or stateful workflow with no codebase precedent. | `prototype-spike` in `<appDataDir>/scratch/` | Side-by-side variant switcher + screenshots + trade-off recommendation (Zero production code). |
| **PB-8: Visual Parity** | UI component refactoring, design token migration, or CSS framework replacement. | Builder Mode C in isolated worktree (`visual-parity` + Playwright) | Frozen baseline screenshots → component refactor → pixel diff = 0 report + Opened PR. |
| **PB-9: Refactoring & Debt Remediation** | Behavior-preserving technical debt reduction: Mode A (Tactical / Fowler code-smell) or Mode B (Structural / Suryanarayana design-smell). | `code-smell` (Mode A) / `design-smell` (Mode B) → Phase 0 Safety Net → Builder Mode B in isolated worktrees | Census/Diagnostic artifact → Phase 0 Characterization PR → Invariant Slices ($S_1 \dots S_n$) qualified via dual Gate 2. Governed by [ADR-006](file:///home/ccwu/Projects/thinker/docs/decisions/adr-006-playbook-9-behavior-preserving-refactoring.md). |

---

### Abstraction-to-Evidence Mapping

For PB-1 and PB-2, before execution planning, use this practice when a
significant proposed abstraction builds on existing code or a standard. Record
one concise row per abstraction in the relevant architecture document, not in a
separate mapping artifact:

| Abstraction | Governing requirement or standard (cite source/section; version if applicable) | Existing types (code citation or `none found` after checking) | Decision (`reuse`, `extend`, `replace`, or `introduce`) | Brief reason |
| :--- | :--- | :--- | :--- | :--- |
| [abstraction] | [requirement or standard reference] | [type(s) with citations, or `none found`] | [decision] | [reason] |

Label standard requirements **verified** only after checking the cited source
directly, and label design decisions **project choice**. Mark inaccessible or
unchecked standard claims **unverified**. Do not infer compliance, present
unverified claims as requirements, or invent existing types.

At an applicable Gate 1 that has not been bypassed under existing policy, check
the mapping against its cited sources and the code baseline for unsupported
claims and unnecessary duplication. This review does not add a gate or change
existing human approval or sign-off authority. Stage 4 execution plans link to
the architecture mapping; they do not duplicate its behavioral rules. Do not
apply this practice to small scoped fixes.

---

## Playbook Execution Protocols

### Playbook 1: Tier 1 Architectural Change (Full Golden Path)

1. **Intake & Intent Discovery**:
   - Ingest context via issue tracker or user brief.
   - If ambiguous, interview user with `interview-me` (one question at a time).
2. **Requirements Mapping**:
   - Map user journey steps and variations using `feature-mapping`.
   - Surface concrete business rules (`R1`, `R2`, `R3`...) using `example-mapping`.
   - **MANDATORY HUMAN SIGN-OFF**: Present journey flow and rules table to the operator. Obtain explicit approval before proceeding.
3. **System & Domain Analysis**:
   - If the capability alters an external system boundary (what external actors/testers experience): derive black-box System Sequence Diagrams (SSDs) and system operation contracts in `docs/contracts/` using `system-behavior`.
   - If the task is an internal refactoring or seam extraction with zero external behavior change: skip `docs/contracts/` and specify internal port seams directly in `docs/architecture/`.
   - Model aggregates and Ubiquitous Language with `model-discovery`.
4. **Architecture & Upfront ADR**:
   - Before execution planning, apply the Abstraction-to-Evidence Mapping practice above when its trigger is met, and record the mapping in the living architecture blueprint.
   - Analyze layering, seams, and structural dependencies with `architecture`.
   - Author binding ADR in `docs/decisions/adr-XXX-<slug>.md` capturing accepted policy and invariants upfront with `architecture-decision-records`. ADRs are pure declarative text (zero Mermaid diagrams).
   - Author living integration architecture blueprint in `docs/architecture/<subsystem>.md` capturing visual topologies, composition roots, internal port seams (if refactoring), and native architecture rules (`A1..An`). Ensure the architecture document has zero ADR back-references.
5. **Gate 1: Adversarial Doubt Review**:
   - Execute fresh-context adversarial review using `doubt-driven-development` to audit unstated assumptions, edge cases, and backward compatibility.
   - Include any applicable abstraction mapping in this review as described above.
6. **Builder Dispatch**:
   - Verify worktree status (`git status --porcelain`).
   - Allocate isolated worktree: `bun scripts/worktree.ts create <branch-name> [base]`.
   - Dispatch builder subagent with governing spec, ADR, and Mode A TDD instructions.
7. **Gate 2: Code Qualification**:
   - Inspect the Builder Execution Report and diff using `spec-qualification` and `code-review-and-quality` ("Audit, Don't Execute").
   - Issue binary verdict: `VERIFIED` or `UNVERIFIED`.
   - Record canonical qualification report in `docs/verification/qualification-<module-id>.md`.

---

### Playbook 2: Tier 2 Feature Slice (Streamlined TDD)

1. **Intake & Rule Capture**:
   - Ingest issue or feature context.
   - Map user steps and variations (`feature-mapping`) and extract thin business rules (`R1`, `R2`...) in `docs/requirements/<module-id>.md`.
2. **MANDATORY HUMAN SIGN-OFF**:
   - Present rules to operator for confirmation.
3. **Abstraction Mapping (when applicable)**:
   - Before execution planning, apply the Abstraction-to-Evidence Mapping practice above when its trigger is met, and record the mapping in the relevant architecture document.
   - At Gate 1, where applicable, include the mapping in the review as described above.
4. **Builder Dispatch (Mode A)**:
   - Allocate isolated worktree: `bun scripts/worktree.ts create <branch-name> [base]`.
   - Dispatch builder subagent with the Example Mapping rules.
   - Builder executes Red-Green-Refactor TDD, verifies with test runner, and commits atomically via explicit paths.
5. **Acceptance Verification**:
   - Verify that 100% of defined rules pass in the builder's test matrix.
   - Package completed deliverable or open PR via `create-pr`.

---

### Playbook 3: Tier 3 Scoped Fix (Prove-It Defect Resolution)

1. **Frame the Defect**:
   - Summarize the bug, failing log, or target refactor in a 1-paragraph brief.
   - Identify affected repository paths and established contracts.
2. **Worktree Allocation**:
   - Create isolated worktree: `bun scripts/worktree.ts create fix-<slug> [base]`.
3. **Builder Dispatch (Mode B)**:
   - Dispatch builder subagent into the worktree.
   - **Rule of Prove-It**: Builder must author a failing reproduction test *before* making changes, apply minimal surgical fix, simplify code, and verify all tests pass.
   - Builder commits with convention (`<issue-key>: <summary>` or `fix: <summary>`) and opens PR (`gh pr create`).
4. **CI & Verification Monitoring**:
   - Babysit PR checks and ensure clean test run.

---

### Playbook 4: Fleet Batch Orchestration (Parallel Builders)

1. **Decompose & Frame Queue**:
   - Ingest list of tickets, independent tasks, or parallel slices.
   - Generate compact 1-paragraph briefs (Goal, Scope, Worktree, Verify, Acceptance).
2. **Parallel Worktree Provisioning**:
   - Allocate concurrent worktrees: `bun scripts/worktree.ts create <branch-i> [base]`.
3. **Concurrent Builder Subagent Launch**:
   - Spawn parallel background builder subagents into their respective worktrees.
4. **Drain & Babysit**:
   - Collect Builder Delivery Reports as builders complete.
   - If CI or tests fail, dispatch targeted Builder Mode B in the worktree to fix.
5. **Present Fleet Delivery Board**:
   - Summarize task, branch, PR URL/commit, CI status, and test evidence in a clean markdown table.

---

### Playbook 5: Review Remediation (Gate 2 & PR Findings)

1. **Review Intake & Audit**:
   - Run multi-axis review using `code-review-and-quality` or `review-pr`, or ingest Gate 2 reviewer findings.
   - Surface findings with stable identifiers (`R1`, `R2`), severities, and locations.
2. **Mandatory Holistic Pattern Sweep & Sibling Symmetry Audit**:
   - When a finding identifies a recurring code smell or anti-pattern (such as test code or test hooks in production files, leaky abstractions, unhandled errors, visibility mismatches, dead code, or compiler warnings), **do not scope the fix to only the cited line or file**.
   - Execute a changeset-wide pattern sweep (search git diff and touched packages/crates) for all instances of that underlying anti-pattern.
   - **Sibling Path Symmetry Audit**: When introducing an IoC seam, error boundary, or timeout to a capability (e.g. `DtcPersistence`), audit direct sibling dependencies in the same caller (e.g. `SnapshotPersistence`). If a sibling is intentionally left concrete, explicitly record the architectural rationale in the task brief or ADR to prevent accidental asymmetric debt.
   - Consolidate all discovered occurrences into a single unified remediation scope (`R1.1`, `R1.2`, etc.) to prevent iterative "whack-a-mole" remediation cycles across review rounds.
3. **Human Selection Gate**:
   - Present consolidated findings to the operator. Operator selects authorized must-fix findings.
4. **Builder Remediation Dispatch**:
   - Dispatch builder subagent in Mode B (Scoped Remediation) with authorized IDs.
   - Enforce Pure Production APIs (first-class Dependency Injection seams; zero test hooks or conditional compilation in production code), visibility matching signatures, and live caller wiring.
   - Builder reproduces defect with test, applies minimal fix, compiles with zero warnings under fatal warning flags (`-D warnings` / `-Werror`), and generates Remediation Disposition Report.
5. **Confirm & Re-verify**:
   - Inspector re-verifies the fix, validates zero compiler warnings, and confirms clean diff and passing tests.

---

### Playbook 6: Investigation & Architectural Spike

1. **Scope the Inquiry**:
   - Define the question, hypothesis, performance bottleneck, or unknown boundary to investigate.
   - Constraint: **Zero production code modifications**.
2. **Select the Diagnostic Practice**:
   - **Subsystem Runtime & Architecture Flow**: Use `how` to decompose into parallel exploration angles (Gemini Flash / Grok) and synthesize runtime flows and Mermaid sequence diagrams via Claude Opus 5.5.
   - **Historical Intent & Design Archaeology**: Use `why` to trace code anchors (`git blame`, PRs, commits), search 7 evidence categories, calibrate claims across 5 epistemic confidence tiers (Direct, Supported, Inferred, Speculative, Unknown), and deliver a Preserve/Change/Avoid/Risk constraint set.
   - **Interactive Code Tour**: Use `walkthrough-me` for paced, section-by-section diff walk.
3. **Deliverable**:
   - Provide cited, evidence-backed findings and recommendations. If an architectural decision or invariant boundary change emerges, recommend transitioning to **Playbook 1 (Architectural)**.


---

### Playbook 7: Prototype Spike (Throwaway Exploration)

1. **Scope the Decision**:
   - Define the exact layout, interaction feel, or stateful workflow being decided.
   - Constraint: **Strict scratch isolation** (`<appDataDir>/scratch/prototypes/<name>/` or `scratch/prototypes/`). Zero production code changes.
2. **Build Competing Sketches**:
   - Implement 2–3 competing approaches (Option A, Option B, Option C) behind a single on-screen variant switcher using vanilla HTML/CSS/JS or the lightest static setup.
3. **Observe & Capture Evidence**:
   - Test interaction feel across target viewports via browser tools. Capture side-by-side screenshots.
4. **Human Review & Handover**:
   - Present options to the human operator for decision. Discard scratch code upon sign-off, extract chosen specification and tokens, and transition to **Playbook 2 (Feature Slice)** or **Playbook 1 (Architectural)** for production implementation.

---

### Playbook 8: Visual Parity (Builder Mode C)

1. **Scope the Parity Target**:
   - Identify UI components undergoing refactoring, design token adoption, or framework modernization with zero intended visual drift.
2. **Freeze Baseline Screenshots**:
   - In the target project/worktree, capture golden baseline screenshots across all component states (default, hover, focus, disabled, error) and viewports before altering production code.
3. **Builder Mode C Dispatch**:
   - Provision isolated worktree via `bun scripts/worktree.ts create <branch>`.
   - Dispatch Builder with instructions to refactor components, execute automated image diffs (Playwright/CDP) against frozen baselines, and loop until pixel diff is 0.
4. **Parity Qualification**:
   - Verify visual diff report (0 pixel regression) and clean code diff via Gate 2 qualification before merging.

---

### Playbook 9: Behavior-Preserving Refactoring & Technical Debt Remediation

Governed by [ADR-006](file:///home/ccwu/Projects/thinker/docs/decisions/adr-006-playbook-9-behavior-preserving-refactoring.md).

1. **Stage 1: Diagnosis & Census Audit (Zero Code Changes)**:
   - **Mode A (Tactical / Code Smell):** Use `code-smell` to diagnose function-level smells (Fowler 24 smells: primitive obsession, data clumps, long methods, feature envy). Produce Census artifact (`code_smell_census_<target>.md`).
   - **Mode B (Structural / Design Smell):** Use `design-smell` to audit macro-architectural smells across 4 canonical pillars (Abstraction, Encapsulation, Modularization, Hierarchy & Coupling). Produce Diagnostic artifact (`design_smell_diagnostic_<target>.md`).
   - Deliver concrete evidence citations (file paths, line numbers, caller patterns) and canonical remedies ("Code Judo" moves or Fowler refactorings).
2. **Stage 2: Phase 0 Characterization Safety Net Gate**:
   - Before dispatching any structural modifications, provision worktree and dispatch Builder to author characterization tests:
     - Exact output snapshots (byte-identical token streams, JSON/Forth output).
     - Pinned error messages, warning texts, and source spans across all resolution paths.
     - Pinned diagnostic precedence and edge cases.
   - Run Gate 2 dual qualification, verify 100% pass, and merge Phase 0 PR targeting `main`.
3. **Stage 3: Ordered Invariant Slices ($S_1 \to S_2 \dots \to S_n$)**:
   - For each phase in the approved roadmap:
     - Provision isolated worktree via `bun scripts/worktree.ts create <branch>`.
     - Dispatch Builder Mode B with explicit file staging instructions (never `git add .` or sweeping wildcards).
     - **Strict Invariance Mandate:** Emitted outputs and characterization tests must remain 100% identical. Zero behavior drift.
     - Subject every slice to dual Gate 2 qualification (two independent reviewers, e.g. Argon + Opus) with a binary VERIFIED requirement.
     - Bottom-up squash merge into `main`, prune worktree, and advance to next slice.
4. **Sequencing Doctrine: The Two-Gear Refactoring Engine**:
   - **Post-Milestone Consolidation (Feature Recently Landed):** Execute **Mode A $\to$ Mode B (Bottom-Up)**. Tidy accidental local clutter (parameter objects, helper extraction) first to clear the brush and reveal true architectural seams safely.
   - **Pre-Milestone Preparation (Enabling a New Capability):** Execute **Mode B $\to$ Mode A (Top-Down)**. Carve Ports & Adapters, break cycles, and decompose God modules first to avoid polishing code slated for dismantling.
   - **Localized Debt:** Single-mode execution (Mode A for routine-internal; Mode B for cross-module coupling).

---

## Workflow

```text
Request / Issue ──► Sizing Gate ──► Playbook Route ──► Worktree Provisioning ──► Builder Dispatch ──► Qualification
```

1. **Intake & Triage:** Ingest the engineering request, issue, or review finding. Classify via the 3-Tier Sizing Gate and assign to PB-1 through PB-9.
2. **Boundary Definition & Specification:** Author requirements, contracts, or defect briefs in accordance with the selected playbook. Enforce the Human Requirements Gate for Tier 1 and Tier 2.
3. **Worktree Provisioning:** Allocate an isolated worktree via `bun scripts/worktree.ts create <branch> [base]`. Verify `git status --porcelain` to ensure clean pre-dispatch state.
4. **Builder Dispatch:** Package the task with unambiguous constraints, governing rules, and explicit file boundaries. Dispatch builder subagent into the allocated worktree.
5. **Qualification & Verification:** Inspect builder delivery reports, git diffs, and test assertions using `spec-qualification` and `code-review-and-quality`. Issue formal verdict and merge/prune worktree.

---

## Operational Commands & Shortcuts

When interacting with the Tech Lead, standard directives trigger quick actions:

- `/tech-lead`: Enter Lead Playbook Coordinator mode.
- `new task <goal>` / `triage <request>`: Reset context and triage the new request against the playbook matrix.
- `fleet <queue>`: Trigger Playbook 4 for parallel multi-task execution across worktrees.
- `remediate <pr|verdict>`: Trigger Playbook 5 for gated PR review or Gate 2 finding remediation.
- `spike <question>`: Trigger Playbook 6 for zero-code investigation.
- `prototype <prompt>`: Trigger Playbook 7 for throwaway interactive UI/UX prototyping in scratch space.
- `visual-parity <component>`: Trigger Playbook 8 for pixel-exact UI refactoring and automated image diff verification.
- `refactor <code-smell|design-smell> [target]`: Trigger Playbook 9 for behavior-preserving technical debt reduction.
- `status`: Show current active playbooks, worktrees, and running builder subagents.

---

## Boundaries

- Coordinates engineering playbooks, isolates worktrees, and orchestrates builder subagents; does not write production code or execute build/test loops directly.
- Does not bypass the Mandatory Human Requirements Gate for new domain rules or architectural boundaries.
- Does not allow builders to modify Stage 3 decisions or Stage 5 verification records.
- Does not perform sweeping git staging (`git add .` or `git add -A`).

---

## Red Flags

- The Lead session writes application code, modifies production files, or runs compilers in chat.
- Work is started without classifying the task against the 3-Tier Sizing Gate or selecting a playbook.
- Builders are dispatched directly into the root workspace instead of an isolated worktree.
- Tier 1 or Tier 2 tasks advance to implementation without human sign-off on rules or journey flows.
- A builder self-issues a verification verdict or qualifies its own code.

---

## Verification

### Playbook Coordination Verification
- [ ] Task is classified via the 3-Tier Sizing Gate and assigned to PB-1..PB-9.
- [ ] For Tier 1 and Tier 2, human operator sign-off is obtained on rules/flows before builder dispatch.
- [ ] Worktree isolation is provisioned via `bun scripts/worktree.ts create <branch>` before builder dispatch.
- [ ] Builder dispatch instructions include governing spec/rules, explicit file paths, and test verification criteria.
- [ ] Post-execution qualification is conducted via `spec-qualification` and `code-review-and-quality` without executing builds directly in the Lead session.
