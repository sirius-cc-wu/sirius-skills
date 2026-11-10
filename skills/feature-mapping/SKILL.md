---
name: feature-mapping
description: Discover and clarify multi-step user workflows and journey scenarios through Feature Mapping and Three Amigos role dynamics. Use for flow-based BDD discovery, mapping sequential steps and variations, and extracting business rules before formal Gherkin formulation or implementation.
---

# Feature Mapping

## Discovery Workflow

Feature Mapping explores the chronological flow of a feature or user story through collaborative discovery, surfacing variations, business rules, and edge cases along the user journey.

### 1. Three Amigos Role Dynamics

Discovery thrives on creative tension across three fluid roles rather than rigid job titles:

* **One to Request (Problem Owner):** Introduces a problem to solve, not an order or finalized contract. Invites the team to explore solutions and asks the team to demonstrate shared understanding.
* **One to Suggest (Solution Explorer):** Diverges to explore options ("What if we do X?"), sketching workflows, wireframes, and alternative user paths before converging under constraints.
* **One to Protest (The Cross-Examiner / Edge Hunter):** Challenges assumptions, hunts for inconsistencies, and introduces negative conditions ("What if this step fails?", "What other outcome could occur?").

*The Gherkin Constraint:* Never write Given-When-Then syntax during the discovery workshop. Focus on plain-language concepts, flow steps, and concrete values; defer Gherkin formulation to a focused post-workshop session.

---

### 2. The Spatial Feature Map

A Feature Map arranges requirements across two dimensions:

```
[Goal / Story: User Outcome]
     │
     ├── Step 1 ──────────────► Step 2 ──────────────► Step 3 (Horizontal Flow)
     │     │                         │                         │
     │   (Example 1.1: Normal)     (Example 2.1: Valid)      (Example 3.1: Success)
     │   (Example 1.2: Variation)  (Example 2.2: Invalid)    (Example 3.2: Failure)
     │                               ▼                         ▼
     │                          [Rule 1: Limit]           [Rule 2: Retry]
     │
     └── [Red Cards: Unanswered Questions & Assumptions]
```

1. **Horizontal Axis (The Flow / Backbone):** The chronological sequence of user actions or system interactions required to achieve the goal (equivalent to a Use Case Main Success Scenario).
2. **Vertical Axis (Variations & Examples):** Placed directly beneath each step to illustrate concrete happy paths, alternate paths, validation failures, and edge conditions (equivalent to Use Case Extensions).
3. **Extracted Rules:** As variations accumulate, identify the underlying business rules and system invariants governing those outcomes.
4. **Questions & Assumptions:** Any unknown outcome, unconfirmed constraint, or missing business policy is recorded as an open question card without halting the session.

---

### 3. Sizing & Selection Filter

| Technique | Primary Dimension | Best Suited For |
|---|---|---|
| **`feature-mapping`** | **Flow / Temporal Progression** (Steps $\times$ Variations) | Multi-step workflows, onboarding, checkout funnels, conversational flows, and stateful journeys. |
| **`example-mapping`** | **Rules & Constraints** (Rules $\times$ Concrete Data) | Complex policies, calculation logic, tabular limits, pricing engines, and state-machine transitions without long temporal sequences. |

When a step within a Feature Map reveals a dense cluster of calculation rules, branch that step into a focused Example Mapping session.

---

## Agent Adaptation

These conventions adapt the Feature Mapping practice to an AI assistant:

* **Start from the Goal:** Anchor the map to a concrete user outcome or system capability. If ambiguous, ask the operator for the primary goal before mapping.
* **Adopt the Three Perspectives:** In autonomous or paired analysis, explicitly apply:
  * The *Request* lens: Verify that the workflow directly addresses the business problem without gold-plating.
  * The *Suggest* lens: Propose minimal, viable step sequences and wireframe/flow ideas.
  * The *Protest* lens: Proactively challenge with edge cases, missing preconditions, timeout/failure paths, and concurrency collisions.
* **Structured Markdown Output:** Represent the map using a clean table or nested structure:
  1. *Goal & Context*
  2. *Workflow Steps (Horizontal Sequence)*
  3. *Step Variations & Concrete Examples* (Happy path vs. Edge cases)
  4. *Extracted Business Rules*
  5. *Open Questions & Deferred Slices*
* **Downstream Handoff:**
  * For executable BDD tests $\to$ pass the mapped examples to `gherkin-formulation`.
  * For system architecture $\to$ steps map 1:1 to system events in `system-behavior` (SSDs).
  * For execution task boards $\to$ slice vertical paths via `use-case-slicing`.

---

## Source

Distilled from John Ferguson Smart, *BDD in Action* (2nd Edition, Manning Publications) and [*One to request, one to suggest and one to protest – the anatomy of a Three Amigos Requirements Discovery workshop*](https://johnfergusonsmart.com/three-amigos-requirements-discovery/), November 12, 2017. The agent conventions above are adaptations, not direct claims from the author.
