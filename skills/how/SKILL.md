---
name: how
description: "Explores the codebase to explain subsystem architecture, runtime flow, component boundaries, and onboarding mental models. Answers how does X work, where should this live, and which package owns this."
---

# How (Subsystem Runtime & Architecture Exploration)

## Overview

Explore the codebase to answer "how does X work?" questions. Produce architectural explanations at the level of a senior engineer onboarding onto a subsystem—enough to build a working mental model without drowning in annotated source code dumps.

Companion to the `why` skill:
- **`how`** answers *what* the system does, where boundaries live, and *how* data flows through runtime components.
- **`why`** answers *what forces* (historical decisions, constraints, incidents, trade-offs) led to its shape.

---

## When to Use

- When onboarding onto an unfamiliar subsystem or crate.
- When answering structural questions: *"Where should this feature live?"*, *"Which crate owns this responsibility?"*, *"Is this the right layer?"*.
- Before proposing an architectural change, new contracts, or refactoring in Playbook 6 (`PB-6: Investigation Spike`).
- When a teammate or operator asks for a high-level runtime walkthrough with Mermaid diagrams.

### When NOT to Use

- When asking for historical motivation, commit archaeology, or why an edge case was handled; use `why`.
- When stepping interactively through a bounded git commit, branch diff, or pull request; use `walkthrough-me`.
- When formally deriving black-box system sequence diagrams for business use-cases; use `system-behavior`.

---

## Model Architecture & Roles

This skill leverages a dual-role pattern balancing high-speed parallel exploration with deep architectural synthesis:

- **Explorers (Parallel Gathering)**:
  - Fast, read-only subagents with large context windows.
  - Runtime: Antigravity native subagent (`invoke_subagent` with `Role: "Subsystem Explorer"`, `Model: "flash"` or `inherit`) or Pi Copilot (`grok-4.7`).
- **Explainer / Synthesizer (Synthesis & Diagramming)**:
  - High-rigor frontier model specialized in architectural synthesis.
  - Runtime: Read from `roles.investigation` in `~/.config/thinker/config.yaml` (default: **Claude Opus 5.5** via Claude Code CLI runner: `claude -p --model opus` or native Antigravity `Model: "pro"`).

---

## Workflow

```mermaid
flowchart TD
    Q["1. Assess Complexity (Simple vs Complex)"] -->|Simple (Single module / function)| Direct["Step 2b. Direct Explain Pass (Opus 5.5)"]
    Q -->|Complex (Subsystem / Cross-crate flow)| Parallel["Step 2a. Parallel Decompose (2–4 Angles)"]
    Parallel --> Exp["Spawn Parallel Explorers (Flash / Grok)"]
    Exp --> Synth["Step 3. Synthesize & Diagram (Mermaid via Opus 5.5)"]
    Direct --> Present["Step 4. Present / Record Architecture Note"]
    Synth --> Present
```

### Step 1. Assess Complexity

Evaluate the scope of the question:
- **Simple** (a single module, a small utility, or a narrow function): Skip explorer decomposition. Run a direct explainer pass via Step 2b.
- **Complex** (a subsystem spanning multiple files, services, cross-crate interactions, or full architectural overview): Decompose into parallel exploration angles via Step 2a.

When in doubt, start with the simple direct pass.

### Step 2a. Explore (Complex Questions)

Decompose the question into 2 to 4 exploration angles, each covering a distinct slice of the subsystem (e.g., Entry/Trigger Points, Core Data Transformation, External Boundaries/Storage, Error/Cleanup Lifecycles).

Spawn parallel read-only explorers in a single batch:
- Each explorer receives the prompt template from `references/explorer-prompt.md` filled with its specific angle and the user's question.
- Explorers trace call paths, map abstractions, record files read, and identify non-obvious surprises.

### Step 2b. Direct Explain (Simple Questions)

Run a single exploration and explanation pass using the synthesizer runner:
- Build the prompt from `references/explainer-prompt.md` omitting the explorer findings section.
- Proceed to Step 4.

### Step 3. Synthesize (Complex Questions)

Once all explorer subagents return, invoke the synthesizer (Claude Opus 5.5 via Claude Code CLI runner `claude -p --model opus` or Antigravity `pro`):
- Inject all explorer findings into `references/explainer-prompt.md`.
- Reconcile overlapping areas, verify key files directly, and generate structured Mermaid flow/sequence diagrams.

### Step 4. Present & Record

Present the synthesized walkthrough to the operator:
- **Overview**: 1–2 paragraphs summarizing purpose and behavior.
- **Key Concepts**: Core domain abstractions, structs, and traits.
- **How It Works**: Step-by-step runtime flow, transformation stages, and Mermaid sequence/flowchart diagrams.
- **Where Things Live**: Clear directory/file map.
- **Gotchas**: Non-obvious behaviors, edge cases, and historical traps.

If executed as part of an architecture spike (PB-6), optionally record the artifact in `docs/architecture/investigations/<topic>.md`.

---

## Reference Files

- `references/explorer-prompt.md`: Base prompt template for parallel explorer agents.
- `references/explainer-prompt.md`: Prompt template for architectural synthesis and Mermaid generation.
