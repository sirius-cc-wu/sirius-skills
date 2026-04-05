# Sirius Skills: Planning & Execution Workflow
A Guide for Teams

---

## The Core Concept: Three-Layer Workflow

We separate **Proposal**, **Planning**, and **Implementation**.

1.  **Proposal Layer**: Early exploratory or speculative work that is not yet canonical.
2.  **Planning Layer**: High-level "What" and "How" for accepted feature work.
3.  **Execution Layer**: Low-level "Code" for one implementation slice at a time.

**Goal**: Keep repository history durable, traceable, and generic-first.

---

## 1. The Proposal Layer
*Where speculative ideas are captured before they become real feature work.*

**Key Skills:**
- `propose`: Captures speculative or not-yet-canonical work before it becomes a feature.

---

## 2. Proposal Artifacts
Stored in `docs/proposals/<proposal-slug>/`

- `proposal.md`: Early framing for a candidate capability or change.
- `.proposal-meta.json`: Machine-readable proposal lifecycle tracking.

---

## 3. The Planning Layer
*Where accepted features are designed and decomposed.*

**Key Skills:**
- `guide-planning`: The planning entry point once work is ready for canonical feature handling.
- `evolve-feature`: Creates a change packet when an existing canonical feature needs to evolve.
- `assess`: Records change-scoped impact analysis before change-local design continues.
- `discover`: Defines the problem, outcomes, and constraints.
- `design`: Architecture, interfaces, and PlantUML system diagrams.
- `breakdown`: Splits stories into executable **Slices** and **Increments**.
- `review-planning`: Final planning check before human approval.
- `reconcile-feature`: Feeds approved change-packet results back into canonical feature docs after execution.

---

## 4. Planning Artifacts
Stored in `docs/features/<feature-slug>/`

- `discover.md`: Problem framing.
- `system-design.md`: Technical architecture.
- `slice-planning.md`: Sequencing and increments.
- `slice-traceability.md`: Mapping stories to slices.
- `changes/<change-id>/`: A planning-scoped delta for evolving an existing feature.
- `changes/<change-id>/impact-analysis.md`: Change-scoped impact record for feature evolution.

---

## 5. The Execution Layer
*Where the work gets done, one slice at a time.*

**Key Skills:**
- `slice`: Bootstraps an execution-scoped folder from an approved, committed planned item.
- `guide-execution`: Manages the slice registry and state transitions.
- `brief`: Captures slice-scoped acceptance criteria and requirements.
- `blueprint`: Detailed design, implementation packets, and validation steps.
- `review-execution`: Validates implementation against the brief/blueprint.
- `close-slice`: Records closure metadata for one execution slice.

---

## 6. Execution Artifacts
Stored in `slices/<slice-id>-<slug>/`

- `brief.md`: The "Source of Truth" for this specific slice.
- `blueprint.md`: The execution plan and validation checklist.
- `.slice-meta.json`: Machine-readable lifecycle tracking.

---

## 7. The Handoff Lifecycle

1.  **Propose**: `propose` captures speculative or not-yet-accepted work.
2.  **Hand Off to Planning**: `guide-planning` promotes accepted proposal artifacts into canonical feature planning and then continues the planning workflow.
3.  **Plan a Net-New Feature**: `guide-planning` -> `discover` -> `design` -> `breakdown`.
4.  **Evolve an Existing Feature**: `guide-planning` -> `evolve-feature` -> `assess` -> `design` -> `breakdown`.
5.  **Review**: `review-planning` confirms the plan or change packet is ready.
6.  **Approve**: A human explicitly approves the reviewed planning artifacts.
7.  **Commit Planning**: Commit the approved planning artifacts before execution starts.
8.  **Bootstrap**: `slice` creates the execution folder.
9.  **Execute**: `brief` -> `blueprint` -> (Code) -> `review-execution`.
10. **Close**: `close-slice` marks the slice done and preserves the execution context until feature-level reconciliation is requested.
11. **Reconcile Feature Changes**: `reconcile-feature` folds approved change-packet results back into the canonical feature docs, then removes the temporary slices and completed change packet once all planned slices are closed.

---

## Why This Matters

- **Traceability**: Every line of code maps back to a requirement in a brief.
- **Durability**: Even after a feature is done, the "Why" (Design) and "How" (Blueprint) remain in the repo.
- **Resumability**: Any agent or human can pick up a slice by reading its `brief.md`.
- **Consistency**: Standardized gates ensure quality doesn't drift.

---

## Getting Started

Check the methodology for more details:
`SKILLS_METHODOLOGY.md`

Use `guide-planning` to start your next feature!
