# Sirius Skills: Planning & Execution Workflow
A Guide for Teams

---

## The Core Concept: Two-Layer Workflow

We separate **Intent** from **Implementation**.

1.  **Planning Layer**: High-level "What" and "How" (Architecture, Stories, Slices).
2.  **Execution Layer**: Low-level "Code" (Briefs, Blueprints, implementation).

**Goal**: Keep repository history durable, traceable, and generic-first.

---

## 1. The Planning Layer
*Where features are born and decomposed.*

**Key Skills:**
- `guide-planning`: The entry point. Validates readiness and routes to other skills.
- `discover`: Defines the problem, outcomes, and constraints.
- `design`: Architecture, interfaces, and PlantUML system diagrams.
- `breakdown`: Splits stories into executable **Slices** and **Increments**.
- `review-planning`: Final check before moving to code.
- `slice`: The handoff. Bootstraps an execution-scoped folder from a planned item.

---

## 2. Planning Artifacts
Stored in `docs/features/<feature-slug>/`

- `discover.md`: Problem framing.
- `system-design.md`: Technical architecture.
- `slice-planning.md`: Sequencing and increments.
- `slice-traceability.md`: Mapping stories to slices.

---

## 3. The Execution Layer
*Where the work gets done, one slice at a time.*

**Key Skills:**
- `guide-execution`: Manages the slice registry and state transitions.
- `brief`: Captures slice-scoped acceptance criteria and requirements.
- `blueprint`: Detailed design, implementation packets, and validation steps.
- `review-execution`: Validates implementation against the brief/blueprint.
- `close-slice`: Records closure metadata and (optionally) publishes history.

---

## 4. Execution Artifacts
Stored in `slices/<slice-id>-<slug>/`

- `brief.md`: The "Source of Truth" for this specific slice.
- `blueprint.md`: The execution plan and validation checklist.
- `.slice-meta.json`: Machine-readable lifecycle tracking.

---

## 5. The Handoff Lifecycle

1.  **Plan**: `guide-planning` -> `discover` -> `design` -> `breakdown`.
2.  **Review**: `review-planning` confirms the plan is ready.
3.  **Bootstrap**: `slice` creates the execution folder.
4.  **Execute**: `brief` -> `blueprint` -> (Code) -> `review-execution`.
5.  **Close**: `close-slice` marks it done and preserves the context.

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
