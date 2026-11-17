# Playbook 6: Investigation & Architectural Spike

**Trigger:** Ambiguous questions, performance profiles, runtime call flows, or historical code intent without production code changes.
**Alpha Progression:** *Requirements* → *Bounded (Exploratory)*.

## Steps

1. **Scope the Inquiry**
   - Define the question, hypothesis, performance bottleneck, or unknown boundary to investigate.
   - **Constraint:** Zero production code modifications.

2. **Select the Diagnostic Practice**
   - **Subsystem Runtime & Architecture Flow:** Use `how` to explore parallel angles via the host's configured exploration/investigation runners and synthesize runtime flows and Mermaid sequence diagrams.
   - **Historical Intent & Design Archaeology:** Use `why` to trace code anchors (`git blame`, PRs, commits), search 7 evidence categories, calibrate claims across 5 epistemic confidence tiers (*Direct*, *Supported*, *Inferred*, *Speculative*, *Unknown*), and deliver a *Preserve / Change / Avoid / Risk* constraint set.
   - **Interactive Code Tour:** Use `walkthrough-me` for a paced, section-by-section diff walkthrough.

3. **Deliverable**
   - Provide cited, evidence-backed findings and recommendations.
   - If an architectural decision or invariant boundary change emerges, recommend transitioning to **Playbook 1 (Architectural)**.
