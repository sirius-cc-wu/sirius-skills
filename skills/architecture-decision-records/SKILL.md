---
name: architecture-decision-records
description: Author and maintain concise Architecture Decision Records (ADRs) capturing accepted architectural choices, consequences, and system invariants. Use when establishing significant technical decisions, interface boundaries, protocols, or irreversible system designs.
---

# Architecture Decision Records (ADR) Authoring

## Overview

An **Architecture Decision Record (ADR)** is an authoritative, binding contract that captures a significant technical decision, the context that necessitated it, its consequences, and the system invariants it establishes.

In `thinker`, ADRs are **decision-making instruments authored upfront** by the `spec-validate` loop's `design` profile *before* the `execution` loop's `build` profile begins. They serve as the architectural specification and implementation boundary.

---

## The Prime Directive: Final Decision Only

> [!IMPORTANT]
> **An ADR records solely the accepted final decision and its direct rationale.**
> It does **NOT** contain debate journals, meeting minutes, pros/cons comparison tables, rejected alternatives matrices, or visual diagrams.

### Pure Text Policy: Zero Mermaid or Visual Topologies
An ADR is an immutable legal statute, not a visual blueprint:
* **ADRs are pure declarative text**: State the context, decisions (`D1..Dn`), consequences, and binding invariants (`I1..In`).
* **Zero Mermaid or wiring diagrams**: Visual component topologies, box-and-wire flowcharts, and composition matrices belong exclusively in the living architecture document (`docs/architecture/<subsystem>.md`), never in the ADR.

### One-Way Dependency Invariant (ADR ──► Architecture)
The relationship between ADRs and Architecture documents is strictly one-way:
* The ADR references the living architecture blueprint that realizes the decision (`Blueprint: docs/architecture/<subsystem>.md`).
* **The Architecture document must NEVER back-reference ADR numbers or decision IDs.** Architecture documents are living, mutable system models; forcing them to reference historical ADR numbers couples the current system state to an append-only decision ledger and causes architectural rot when ADRs are superseded.

### Where Do Alternatives and Debates Belong?
* **Technical Design Specifications (`*-technical-design.md`)**: Explore competing options, trade-off matrices, and deep implementation mechanics.
* **Doubt Cycle Records (`doubt-driven-development`)**: Subject assumptions, security boundaries, and failure modes to adversarial challenge.
* **The ADR (`adr-*.md`)**: Records strictly the **final consensus and accepted policy**. Once a decision is made, downstream engineers and maintainers need an unambiguous statement of the law, not a chronicle of the legislative debate.

---

## When to Use

Author an ADR whenever a technical choice meets any of these criteria:
* Introduces, alters, or deprecates a core system boundary, communication protocol, or IPC interface.
* Selects a primary persistence model, data format, serialization strategy, or cryptographic foundation.
* Defines concurrency, process lifecycle, signal handling, or resource disposal models.
* Imposes non-negotiable security, isolation, or permission constraints.
* Represents an architectural decision that would be expensive or breaking to reverse later.

**When NOT to write an ADR:**
* Routine code refactoring within existing architectural boundaries.
* Cosmetic UI/styling adjustments or minor copy changes.
* Internal implementation details of a single private function.

---

## Workflow

```text
Discovery ──► Architecture & ADR ──► Detailed Design ──► Work Preparation ──► Qualification
```

1. **Identify the decision boundary:** Confirm that the technical choice introduces a durable system constraint, interface boundary, persistence model, or irreversible trade-off.
2. **Consult artifact budget and layout:** Before creating a standalone ADR, apply
   [Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
   Store the record in the target project's canonical decision directory (e.g. `docs/decisions/`). Follow
   [Markdown Artifact Frontmatter](../design-repository-artifact-layout/references/markdown-artifact-frontmatter.md).
3. **Verify sequence and numbering:** Check existing ADR numbers to avoid collisions (`adr-XXX-short-slug.md`).
4. **Draft the authoritative record:** Author the decision upfront using the standard template. Record strictly the final accepted decision, direct context, and binding consequences. Omit debate transcripts, chronological journals, and rejected alternatives matrices.
5. **Establish traceability:** Link the ADR bidirectionally to affected requirements, use cases, or detailed designs.
6. **Submit for approval:** Confirm acceptance with the governing architecture authority before downstream implementation begins.

---

## Artifact Structure & Numbering

Before creating an ADR, inspect the target project's conventions:
* **Location**: Store in the target repository's canonical decision directory (e.g. `docs/decisions/`).
* **Naming**: `adr-XXX-short-kebab-slug.md` using continuous zero-padded three-digit numbers (e.g. `adr-024-background-service-stop-command.md`).
* **Sequence Integrity**: Always verify the latest ADR number in the target repository to prevent collisions with concurrent branches.

---

## Standard ADR Template

Every ADR must follow this clean, four-part structure:

```markdown
---
type: "Architecture Decision"
title: "ADR-XXX: Direct Title of the Decision"
description: "Concise summary of the accepted architectural choice and its core rationale."
id: "ADR-XXX"
status: "accepted" # proposed | accepted | superseded | deprecated
date: "YYYY-MM-DD"
tags: [architecture, decision, subsystem-name]
generated: { by: "human:sirius", at: "YYYY-MM-DDTHH:MM:SSZ" }
verified: { by: "human:sirius", at: "YYYY-MM-DDTHH:MM:SSZ" }
supersedes: "" # optional, e.g. "ADR-001"
superseded_by: "" # optional, set when superseded
---

# ADR-XXX: Direct Title of the Decision

Status: accepted

Date: YYYY-MM-DD

## Context

Describe the technical problem, user requirement, or system constraint that necessitated this decision. State the facts, requirements, and system boundaries plainly without narrative fluff or chronological journal entries.

## Decision

State the accepted architectural choice clearly using direct, active declarative statements:
1. What components, protocols, data models, or interfaces are introduced or changed.
2. How state transitions, lifecycles, or concurrency boundaries are governed.
3. What security, permission, or isolation rules are enforced.

## Consequences

Detail the concrete results of this decision:
- What capabilities and guarantees are established.
- What trade-offs or constraints are explicitly accepted.
- What invariants must be preserved by subsequent implementations.

## Trace

- Blueprint: [`docs/architecture/<subsystem>.md`](../architecture/subsystem.md)
- Use case: [`UC-XX`](../features/path/use-cases.md)
- Requirements: [`FEAT-XX-REQ`](../features/path/feature-requirements.md)
- Technical design: [`docs/features/path/feature-technical-design.md`](../features/path/feature-technical-design.md)
```

---

## Anti-Patterns & Prohibitions

| Anti-Pattern | Why It Dilutes the Contract | Correct Discipline |
| :--- | :--- | :--- |
| **Visual Diagrams & Topologies** | Embedding Mermaid flowcharts, box-and-wire topologies, or composition roots in the ADR. | Keep the ADR purely declarative text. Put structural blueprints and diagrams in `docs/architecture/<subsystem>.md`. |
| **Bidirectional Coupling** | Expecting the living architecture document to cite ADR numbers. | The ADR links outward to the architecture blueprint (ADR $\to$ Architecture). The living architecture document must never back-reference ADR numbers. |
| **Alternatives Matrices** | Including full pros/cons tables of rejected tools (e.g., MongoDB vs PostgreSQL). | Keep the ADR focused purely on the selected architecture. Move comparisons to the Technical Design. |
| **Chronological Journaling** | "On Monday we thought X, then the team lead suggested Y, so on Tuesday we agreed on Z." | Delete the journal. State only the current authoritative decision. Provenance belongs in git commit logs. |
| **Zombie Comparisons** | Contrasting every single sentence against legacy behavior. | Describe the target state directly as positive invariant behavior. |
| **Post-hoc Paperwork** | Writing the ADR after the feature is implemented just to tick a "Ship" checkbox. | Author the ADR upfront as the architectural guide for implementation. |
| **Vague Ambiguity** | Using non-committal words like "we should consider", "might explore". | Use binding declarative voice: "The service initiates...", "The controller rejects...". |

---

## Verification

Before committing any ADR, verify against this checklist:
- [ ] **Solely Final Decision**: Does the ADR omit debate history, pros/cons tables, and rejected options?
- [ ] **Pure Text Policy**: Does the ADR omit Mermaid diagrams, visual topologies, and composition tables?
- [ ] **One-Way Reference**: Does the ADR point to the architecture blueprint without requiring the architecture document to back-reference ADR IDs?
- [ ] **Upfront Timing**: Is the ADR being authored *before* implementation code is written?
- [ ] **OKF v0.2 Frontmatter**: Does the ADR include required frontmatter (`type`, `title`, `description`, `status`, `generated`, `verified`)?
- [ ] **Active Voice**: Are decisions expressed as direct, positive system behaviors?
- [ ] **Numbering**: Is the sequential ID correct and non-colliding?
- [ ] **Traceability**: Are links to Architecture Blueprint, Use Cases, Requirements, and Technical Design included?
