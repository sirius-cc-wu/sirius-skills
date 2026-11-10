# Factors, decisions, and views

## A small architectural factor record

| Field | Purpose |
|---|---|
| Factor and source | Identify the requirement or constraint and where it came from |
| Scenario and measure | State the stimulus, environment, workload, response, and measurable target |
| Variation | Separate present flexibility from probable evolution |
| Impact | Identify affected users, components, and other factors |
| Priority and uncertainty | Explain why this deserves architectural attention |
| Decision and alternatives | State the choice and why plausible alternatives were rejected |
| Consequences and evidence | Record costs, tradeoffs, test results, and unresolved risks |

The factor fields come from chapter 33; the combined decision/evidence layout is an adaptation.

Original illustrative scenario: “When the catalog provider is unreachable, a staff member can complete a checkout for an item already present in the approved local catalog within the agreed response target, and the interface identifies any deferred synchronization.” This is incomplete until the target, freshness rule, allowed offline operations, and workload are known. Do not silently fill them with invented requirements.

If offline updates are required, consider their effect on conflicting reservations and reconciliation. Availability and correctness can conflict; the system needs an explicit business policy and an implementation that can support it.

## N+1 architectural views

Larman presents a variable number of significant views plus a use-case view that ties them to behavior. N is not a command to produce every possible document.

| View | Reader's question |
|---|---|
| Logical | What are the significant responsibilities, packages, interfaces, and collaborations? |
| Process | How are responsibilities allocated to processes/threads, and how do they coordinate? |
| Deployment | Which artifacts and processes run on which nodes and execution environments? |
| Data | What persistent structure and mapping decisions matter? |
| Use case (+1) | Which scenarios exercise and demonstrate the architecture? |
| Additional views where needed | What domain, security, implementation, or development-environment information helps this audience? |

Document enough context for a new developer to understand the essential decisions. Reuse existing artifacts and excerpt significant views rather than copying every model into a second document.

## Cross-view checks

- Name a single scenario and trace its system entry point, logical collaborators, process boundaries, deployment, and persistent effects.
- Confirm the “local” versus “remote” assumptions agree across views.
- Ensure a provided interface has an owner and each required interface has a planned provider or an explicit gap.
- Distinguish static dependencies from physical network connections.
- State what actually happened in an architectural experiment, including load and failure conditions; do not report a proposed mechanism as a measured property.

Source: §§33.4–33.9 and §§39.1–39.5; supplied PDF pp. 740–757 and 871–887. The lending scenario and cross-view checklist are adaptations.
