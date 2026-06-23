# Expert Evaluation: Specification & Development Workflows

This evaluation analyzes the practical trade-offs, strengths, and weaknesses of the specification and implementation methodologies across the six skill repositories. 

---

## 1. Comparative Evaluation Matrix

| Criterion | addyosmani (Spec-First) | sirius-skills (Two-Layer UML) | superpowers (Subagent-Driven) | applying-uml-and-patterns | mattpocock (Anti-Vibe TDD) | gstack (Browser & GBrain) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Velocity (Speed to Code)**| 🟡 **Medium** (Gating steps add manual check pauses) | 🟢 **High** (`autoplan`/`ship` automate pipeline steps) | 🟢 **High** (Runs task checklists autonomously) | 🔴 **Low** (Heavy upfront analytical modeling) | 🟡 **Medium** (TDD and grilling take initial time) | 🟢 **High** (Boil the Ocean completes code quickly; `/autoplan` and `/ship` automate workflow gates) |
| **Robustness (Bug Prevention)**| 🟢 **High** (Early requirement checks & boundaries) | 🟢 **High** (Traceability checking & UML verification) | 🔵 **Highest** (Automated dual review gates per task) | 🟢 **High** (Rigorous pre/post-conditions) | 🟢 **High** (TDD and glossary prevent naming drift) | 🔵 **Highest** (Continuous browser-based QA testing, console/network monitoring, and unified diff checks) |
| **Reviewability (Human Context)**| 🟡 **Medium** (Markdown text-based reviews) | 🔵 **Highest** (Visual UML diagrams lower cognitive load) | 🟡 **Medium** (Reviewing PR after completion) | 🟢 **High** (Highly detailed diagrams) | 🟢 **High** (Glossary & ADRs clarify decisions) | 🔵 **Highest** (Annotated browser screenshots and visual UI diffs reduce cognitive load for visual review) |
| **Context Management** | 🔴 **Poor** (Single session context accumulates quickly) | 🟢 **Good** (Uses `.skills/runtime/` & subfeatures) | 🔵 **Highest** (Fresh subagent per task eliminates pollution) | 🟡 **Medium** (Requires structured domain boundaries) | 🟢 **Good** (Domain vocabulary reduces token count) | 🔵 **Highest** (GBrain semantic search & cross-session memory bypasses token limits) |
| **Setup Overhead** | 🟢 **Minimal** (Simple Markdown templates) | 🔴 **High** (Config files, PlantUML rendering server) | 🟡 **Medium** (Subagent setup & plan requirements) | 🟡 **Medium** (UML modeling syntax & rules) | 🟢 **Low** (Simple triage/docs setup) | 🟡 **Medium** (Quick setup command, but requires Chromium/Playwright daemon and embedding provider keys) |

---

## 2. In-Depth Workflow Evaluations

### A. addyosmani-agent-skills: The Pragmatic Standard
* **Pros**: Simple, highly readable, and easily understood by both humans and LLMs. The boundary definitions (Always/Ask/Never) are particularly effective at keeping AI agents within guardrails.
* **Cons**: The gated phase transitions (`SPECIFY -> PLAN -> TASKS -> IMPLEMENT`) require manual prompting or approval. In a single-agent environment, the context window can fill up with discussion and spec text during large tasks.
* **Best-Fit**: Small-to-medium features, greenfield project scaffolding, and developers who want high quality without complex scripting or infrastructure.

### B. sirius-skills: The Enterprise Visual Pipeline
* **Pros**: Best-in-class for visual code review. Using PlantUML diagrams (`system-design.md` and `blueprint.md`) ensures that human engineers can audit the agent's logic at a glance rather than reading massive walls of text. Differentiating features from subfeatures enables clean, incremental modifications without corrupting baseline requirements. Highly automated via `autoplan` and `ship` scripts.
* **Cons**: High setup overhead (requires a local PlantUML server) and a steeper learning curve for developers to understand the planning-to-execution state transitions.
* **Best-Fit**: Large, complex codebases, teams with strict code review requirements, and projects requiring clear systems engineering architecture.

### C. superpowers: The Automated Factory
* **Pros**: Solves the LLM context pollution problem completely. By dispatching a fresh, stateless subagent to execute each task and filtering their output through automated Spec and Quality reviewers, code drift is virtually eliminated. It operates like an autonomous software factory.
* **Cons**: Token-heavy and potentially expensive due to spawning multiple subagents (Implementer, Spec Compliance, Code Quality) per task. It relies entirely on having an exceptionally well-written plan up front.
* **Best-Fit**: Rapid, heads-down implementation of large, independent task lists where requirements are already crystal clear.

### D. applying-uml-and-patterns-skills: The Structural Academic
* **Pros**: Unmatched theoretical rigor. Creating black-box System Sequence Diagrams (SSDs) and formal Operation Contracts maps out system states and associations logically before any execution logic is defined.
* **Cons**: High analytical overhead. For modern web services and simple CRUD tasks, writing formal contracts and GRASP responsibility assessments can feel like excessive over-engineering.
* **Best-Fit**: Mission-critical enterprise logic, core business domains, and payment/state engines.

### E. mattpocock-skills: The Developer-Agent Alignment Engine
* **Pros**: The "/grill-me" and "/grill-with-docs" loops are incredibly effective at surfacing implicit requirements. The explicit domain glossary (`CONTEXT.md`) enforces a "ubiquitous language," leading to highly consistent variable and file naming.
* **Cons**: It does not offer automated workflow pipelines or subagent dispatch scripts; implementation is driven task-by-task.
* **Best-Fit**: Individual developers building deep-module applications who want to build a shared language with their agent to minimize vibe-coding bugs.

### F. gstack: The Continuous QA & Semantic Brain
* **Pros**: Solves context limits via GBrain's cross-session semantic memory and per-repo trust policies. Headless browser automation (snapshots, interactive diffs, console/network scans, responsive layout tests) makes verification fast, precise, and visual (via annotated screenshots). Enforces complete, high-quality code and test coverage under the "Boil the Ocean" principle.
* **Cons**: High browser daemon setup overhead (Playwright/Chromium build) and requires configuring embedding keys (Voyage/OpenAI) for semantic features.
* **Best-Fit**: Frontend-heavy apps requiring robust end-to-end visual testing, complex user flow verification, and multi-session projects needing cross-machine shared memory.

---

## 3. Recommendation Checklist

1. **If you want to start immediately with zero friction**: Use the **addyosmani** gated Markdown spec. It provides immediate alignment with minimal tool setup.
2. **If your project has complex backend/frontend integration**: Use **sirius-skills** and set up a local PlantUML server. The visual system diagrams and slice boundaries will prevent the agent from getting lost in translation.
3. **If you have a multi-hour implementation backlog**: Use **superpowers'** Subagent-Driven Development to process the backlog tasks autonomously while you step away.
4. **If your agent's code names feel random or messy**: Adopt the domain dictionary glossary (`CONTEXT.md`) and ADR patterns from **mattpocock-skills**.
5. **If you need cross-session memory or interactive visual verification**: Use **gstack** to run headless browser dogfooding and leverage **GBrain** to preserve architectural decisions across sessions.
