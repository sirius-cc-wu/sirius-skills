# Sirius Skills: Planning & Execution Workflow
A Guide for Teams

---

## The Core Concept: Four Workflow Surfaces

We separate **Proposal**, **Planning**, **Execution**, and **Maintenance**.

1.  **Proposal Layer**: Early exploratory or speculative work that is not yet canonical.
2.  **Planning Layer**: High-level "What" and "How" for accepted feature work.
3.  **Execution Layer**: Low-level "Code" for one implementation slice at a time, with an optional backlog orchestrator for batch progress.
4.  **Maintenance Layer**: Reporting, audit, repair, and archival after planning or execution work is complete.

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
- `add-subfeature`: Creates a subfeature when an existing canonical feature needs to evolve.
- `assess`: Records change-scoped impact analysis before subfeature-local design continues.
- `discover`: Defines the problem, outcomes, and constraints.
- `design`: Architecture, interfaces, and PlantUML system diagrams.
- `breakdown`: Splits stories into executable **Slices** and **Increments**.
- `review-planning`: Final planning check before human approval.

---

## 4. Planning Artifacts
Stored in `docs/features/<feature-slug>/`

- `discover.md`: Problem framing.
- `system-design.md`: Technical architecture.
- `slice-planning.md`: Sequencing and increments.
- `slice-traceability.md`: Mapping stories to slices.

Default planned slice IDs should use a scope-prefixed format such as
`atf-read-file` or `shp-store` rather than bare `slice-*` placeholders.
- `subfeatures/<change-id>/`: The default delivery planning unit under a feature-owned story catalog.
- `subfeatures/<change-id>/impact-analysis.md`: Change-scoped impact record for feature evolution.

---

## 5. The Execution Layer
*Where the work gets done, one slice at a time.*

**Key Skills:**
- `slice`: Bootstraps an execution-scoped folder from an approved, committed planned item and syncs the relevant planning handoff state.
- `guide-execution`: Manages the slice registry and state transitions.
- `ship`: Resolves one reviewed and committed feature or subfeature backlog, then resumes or bootstraps one mapped slice at a time.
- `brief`: Captures slice-scoped acceptance criteria and requirements.
- `blueprint`: Detailed design, implementation packets, and validation steps.
- `review-execution`: Validates implementation against the brief/blueprint.
- `close-slice`: Records closure metadata for one execution slice.

---

## 6. The Maintenance Layer
*Where durable history is reported, repaired, and archived.*

**Key Skills:**
- `governance-update`: Tightens repo-level workflow rules when repeated drift exposes a policy gap.
- `report-artifacts`: Summarizes proposals, features, subfeatures, and slices.
- `audit-artifacts`: Finds drift, missing files, and broken links.
- `repair-artifacts`: Repairs registries from valid durable state.
- `archive-artifacts`: Archives closed slices directly, or summarizes and archives all closed planned slices for one feature or subfeature.

---

## 7. Execution Artifacts
Stored in `slices/<slice-id>-<slug>/`

- `brief.md`: The "Source of Truth" for this specific slice.
- `blueprint.md`: The execution plan and validation checklist.
- `.slice-meta.json`: Machine-readable lifecycle tracking.

---

## 8. The Handoff Lifecycle

1.  **Propose**: `propose` captures speculative or not-yet-accepted work.
2.  **Hand Off to Planning**: `guide-planning` promotes accepted proposal artifacts into canonical feature planning and then continues the planning workflow.
3.  **Plan a Net-New Feature**: `guide-planning` -> `discover` creates feature context and stories, then `add-subfeature` creates delivery units for `design` and `breakdown`.
4.  **Evolve an Existing Feature**: `guide-planning` -> `add-subfeature` -> `assess` -> `design` -> `breakdown`.
5.  **Review**: `review-planning` confirms the plan or subfeature is ready.
6.  **Approve**: A human explicitly approves the reviewed planning artifacts.
7.  **Commit Planning**: Commit the approved planning artifacts before execution starts.
8.  **Bootstrap**: `slice` creates the next execution folder. For canonical features it syncs planning metadata to `slice_ready`; for reviewed subfeatures it requires explicit approval already recorded in `.subfeature-meta.json` and then records the chosen ready slice ID there so the derived planning view becomes `slice_ready`.
9.  **Optional Batch Orchestration**: `ship` can keep working a reviewed and committed backlog one mapped slice at a time, but it stops at blockers and per-slice commit checkpoints.
10. **Execute**: `brief` -> `blueprint` -> (Code) -> `review-execution`.
11. **Close**: `close-slice` marks the slice done and preserves the execution context.
12. **Reconcile Feature Closeout**: `reconcile-execution` aligns the canonical `system-design.md` with completed slice execution before feature-level archive.
13. **Maintain Durable History**: `ship --finalize` can require that reconciliation and then route `archive-artifacts` to summarize closed slices into `system-design.md` and move them into the archive area.

When the same closeout drift shows up across features, use `governance-update`
to tighten the repo rule. `bootstrap` is not the owner for that policy; it only
sets up the initial repo control surfaces.

---

## 9. The Two-Step Accelerator Fast Path

When accelerator config is enabled, the default operator flow can collapse to
two high-level steps:

1. `autoplan --execute-owner-chain` drives planning until the explicit approval boundary.
2. After approval, `ship --approve` records the gate and `ship --resume` drives execution until the next manual boundary.

`guide-scope`, `guide-planning`, and `guide-execution` still matter, but they
become the recovery and fine-grained control path rather than the default happy
path.

---

## 10. Why This Matters

- **Traceability**: Every line of code maps back to a requirement in a brief.
- **Durability**: Even after a feature is done, the "Why" (Design) and "How" (Blueprint) remain in the repo.
- **Resumability**: Any agent or human can pick up a slice by reading its `brief.md`.
- **Consistency**: Standardized gates ensure quality doesn't drift.
- **Retention Without Clutter**: Closed slices can leave the active slice area without losing their design context.

---

## 11. Getting Started

Check the methodology for more details:
`SKILLS_METHODOLOGY.md`

Use `autoplan` for the default accelerator path when it is enabled, `guide-scope`
when you want the workflow to pick the right manual surface, or `guide-planning`
when you already know the work belongs in planning.
