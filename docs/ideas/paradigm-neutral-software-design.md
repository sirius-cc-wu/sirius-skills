---
type: "Capability Proposal"
title: "Visual, Paradigm-Neutral Software Design"
description: "Proposes question-driven PlantUML views that make AI-generated software understandable while retaining optional OO techniques."
status: "proposed"
tags: [design, skills, plantuml, object-orientation, workflow]
---

# Visual, Paradigm-Neutral Software Design

## At a Glance

AI can generate working code faster than a person can build an accurate mental
model of it. Sirius should help close that comprehension gap with small,
question-driven PlantUML views that make important behavior and structure
quickly reviewable by humans.

Craig Larman's *Applying UML and Patterns* is a strong foundation for this
goal. It connects external behavior, domain vocabulary, system operations,
responsibility assignment, runtime collaborations, and static design instead
of treating a class diagram as an isolated inventory. Those connections help a
human understand why software has its current shape.

The source should inform a visual reasoning toolbox, not require its complete
object-oriented artifact sequence for every task. Select the smallest diagram
that answers the reader's question, represent the code's actual constructs,
and keep durable views reconciled with implementation evidence.

## Representative Scenario

An agent changes an order-processing feature spanning an API handler, domain
rules, storage, and an external payment service. The code and tests pass, but a
reviewer needs to understand the change without reading every modified file.

The agent should identify the reviewer's questions and produce or update only
the views that answer them. A component view can show module and dependency
boundaries; a sequence view can show payment authorization, persistence, and
failure behavior. If the change introduces meaningful domain types or
responsibility changes, a focused class view may also be useful.

The agent should not automatically produce a use-case model, domain model,
system sequence diagram, operation contract, GRASP record, realization, and
design class diagram. More diagrams would increase review and maintenance cost
without necessarily improving understanding.

## Why the Larman Source Fits

*Applying UML and Patterns* contributes more than object-oriented notation:

- use cases and system sequence diagrams connect a design to externally
  observable behavior;
- domain models establish a shared vocabulary without automatically defining
  software classes;
- operation contracts make significant state changes precise;
- GRASP makes responsibility, coupling, cohesion, and variation discussable;
- interaction diagrams explain runtime collaboration; and
- design class diagrams summarize stable implementation-facing structure.

These remain valuable ways to inspect and explain AI-generated code. PlantUML
makes the views textual, version-controlled, diffable, reproducible, and easy
for an agent to maintain beside other technical artifacts.

Sirius should supplement this prospective design path with its existing
evidence-driven [architecture-recovery sources](../../catalog/sources.md).
*Documenting Software Architectures: Views and Beyond* and the architecture
reconstruction guidance already support module, component-and-connector,
runtime, data/state, deployment, and trust-boundary views. Together, the
sources cover both as-designed intent and as-built reality.

## Select Diagrams by Human Question

| Human question | Candidate PlantUML view | Typical evidence |
|---|---|---|
| What is inside the system boundary? | Context, use-case, or system sequence view | Requirements, interfaces, observed interactions |
| What are the major modules and dependencies? | Package or component view | Manifests, modules, imports, composition roots |
| What happens during this operation? | Sequence view | Scenario, contract, calls, traces, and tests |
| Where is state held and how does it change? | State-machine or focused activity view | State definitions, transitions, invariants, persistence behavior |
| How does data move through the system? | Activity or data-flow-oriented view | Schemas, transformations, queues, pipelines, and calls |
| What runs where? | Deployment view | Build, container, infrastructure, process, and network configuration |
| Which types and relationships define this area? | Focused class view | Responsibilities, public types, interfaces, and code |

Diagram selection begins with the question, not with a commitment to complete
the table. A component view plus one runtime sequence will often explain an
AI-generated change better than a comprehensive class diagram.

## Why Sirius Feels More Complicated

Sirius does not have an unusually large skill catalog. Addy Osmani's catalog
contains 24 skills, while the recorded gstack revision contains roughly 55
generated skill templates. The distinctive difference is the axis along which
each repository divides the work:

| Repository | Primary decomposition | Resulting user model |
|---|---|---|
| Addy Osmani's `agent-skills` | User outcomes and delivery phases such as refining, specifying, planning, building, testing, reviewing, and shipping | Select the next delivery outcome, then add a specialization when needed |
| Garry Tan's `gstack` | Roles, reviews, delivery stages, and tool-backed workflows such as product review, engineering review, QA, deployment, and browser work | Follow a delivery spine or invoke a specialist workflow |
| Sirius | Analysis and design techniques such as use cases, domain models, SSDs, contracts, GRASP, realizations, and class diagrams | Select among the internal stages and artifacts of a design method |

Addy Osmani's collection and gstack therefore also divide development into
many skills. Their
primary concepts, however, are closer to user-visible outcomes. Sirius exposes
more of the visual method's internal reasoning structure. That fine-grained
toolbox is valuable, but presenting it as a single sequence increases routing
and coordination cost for both the user and the coding agent.

## Original Tension and Implemented Foundation

Sirius already contains strong limiting rules:

- The [methodology](../../SKILLS_METHODOLOGY.md) says to choose the smallest
  skill or combination that addresses the current outcome and risk.
- The [skill relationship guide](../../catalog/skill-relationships.md) says its
  arrows are handoffs rather than a mandatory waterfall.
- The [artifact selection budget](../../skills/select-technical-artifacts/references/artifact-selection-budget.md)
  prefers code, tests, configuration, or an existing canonical artifact over a
  new document.
- [`test-driven-implementation`](../../skills/test-driven-implementation/SKILL.md)
  permits a bounded implementation to begin from a bug report, approved
  example, invariant, or other independent oracle.

The former coordinator nevertheless instructed the agent to sequence use
cases, SSDs, domain models, contracts, GRASP decisions, realizations, and design
class diagrams. The methodology similarly described the profile as moving
through requirements, analysis, object design, implementation, and
refactoring.

Sirius now addresses that workflow-level bias with
[`iterative-risk-driven-development`](../../skills/iterative-risk-driven-development/SKILL.md).
The coordinator executes one risk-sized objective at a time, selects specialists
from the current question and implementation forces, applies the artifact
budget, validates the result, and creates at most one authorized commit per
iteration. The language-adaptation skill now accepts language-neutral behavior,
boundaries, state, and collaborations without requiring GRASP or class-design
input.

The remaining proposal is narrower: make rapid human comprehension an explicit
design outcome and provide question-driven visual routing where existing
design and architecture-recovery specialists do not already own the view.

## Is Object-Oriented Design Outdated?

No. Responsibility assignment, encapsulation, cohesion, coupling, stable
interfaces, and polymorphism remain useful for rich business domains and
long-lived stateful systems. GRASP can still help when several components could
plausibly own the same behavior.

Sirius also avoids equating every design concept with a class. Its
[`software-design-language-adaptation`](../../skills/software-design-language-adaptation/SKILL.md)
skill permits responsibilities to become functions, modules, values, closures,
algebraic variants, protocols, or other language-native constructs.

What is dated is treating the complete object-oriented analysis artifact chain
as a generally applicable default. A class-centered view alone is often a poor
fit for:

- small changes and ordinary bug fixes;
- functional or data-oriented systems;
- data pipelines and transformations;
- integration and distributed-system work;
- UI component composition;
- infrastructure and configuration; and
- concurrency-, protocol-, or state-machine-driven designs.

These systems still benefit from diagrams, but their central questions may
concern data flow, boundaries, failure modes, ownership, concurrency,
consistency, deployment, or change isolation rather than object collaborations
and class structure.

## Recommended Direction

1. **Keep *Applying UML and Patterns* as a foundational source.** Preserve the
   behavioral traceability and responsibility reasoning it contributes.
2. **Keep the fine-grained modeling skills.** They provide precise,
   independently loadable help when a task has the corresponding question or
   design pressure.
3. **Make human comprehension an explicit outcome.** A diagram should identify
   its intended reader, question, scope, and important omission.
4. **Stop presenting the UP/OO sequence as the normal end-to-end route.** Keep
   it as one valuable specialization within a broader visual design toolbox.
5. **Introduce question-driven diagram routing.** Consider context, behavior,
   module, component, runtime, state, data-flow, deployment, trust-boundary,
   and type views before selecting the smallest useful representation.
6. **Represent native constructs.** Show functions, modules, values, tasks,
   channels, services, processes, schemas, or classes according to the actual
   code rather than forcing every participant into an object.
7. **Connect design and recovery.** Use intended requirements and decisions for
   as-designed views; use source, configuration, tests, and runtime evidence
   for as-built views; reconcile material disagreements explicitly.
8. **Keep implementation close.** Move to code and executable verification as
   soon as the important uncertainty has an adequate oracle. Feed back only
   discoveries that change durable knowledge.
9. **Evaluate routing rather than relying on disclaimers.** Fail scenarios that
   omit a materially useful view as well as scenarios that create an
   unjustified diagram set.

The top-level routing foundation is now implemented and covered by focused
routing cases. Skill consolidation should still follow only if evaluation or
actual use shows that adjacent skills cannot be selected reliably or provide
too little independent value.

## Proposed Capability Shape

A future visual-design coordinator would ask:

1. Who needs to understand the software, and for what decision?
2. Is the required view as-designed, as-built, or a reconciliation of both?
3. What behavior, structure, state, dependency, or deployment fact is currently
   difficult to see?
4. Which single view or small complementary set best exposes it?
5. What code, test, configuration, runtime, requirement, or decision evidence
   supports every material element and relationship?
6. Does the result fit an existing canonical diagram, or does it justify an
   independently maintained artifact?
7. What evidence is sufficient to begin or continue implementation?
8. Did implementation change knowledge that the durable view owns?

The existing `iterative-risk-driven-development` capability now remains the
risk-driven coordinator for work that benefits from its full vocabulary and
traceability model. It selects and executes one ready objective at a time.
`reconstruct-software-architecture` remains the specialist for recovering
as-built views from existing code. A future visual coordinator
should select between them rather than duplicate their detailed procedures.

## Diagram Trust and Lifecycle

A diagram that is quick to read but stale is actively misleading. Durable
PlantUML views should therefore:

- state the question and scope they answer;
- distinguish as-designed intent from as-built evidence;
- identify the code revision or other evidence snapshot for recovered views;
- omit detail that does not help the named reader or decision;
- live with an existing canonical owner when possible;
- be updated only when implementation changes knowledge they own; and
- be reconciled or marked stale when code and diagram disagree materially.

Generated call graphs and exhaustive type inventories are not automatically
architecture. The agent must abstract evidence into a view whose elements and
relationships help answer the stated question.

## Evaluation Implications

The [skill evaluation program](skill-evaluation-program.md) should include at
least these composition cases:

- a small bug fix that proceeds directly to code and tests;
- a focused cross-module change where one component and runtime view materially
  shortens human review;
- a functional data transformation that uses a data-flow-oriented view rather
  than classes or GRASP decisions;
- a distributed workflow whose main design concerns are messages, retries,
  idempotency, consistency, and deployment boundaries;
- a stateful domain problem where responsibility design and a domain model are
  justified; and
- an architecturally significant scenario where a use case, contract, and
  selected interaction view materially reduce risk.

The evals should detect both under-modeling and over-modeling. The desired
result is not to suppress OO techniques or diagrams. It is to distinguish the
cases where a PlantUML view earns its maintenance cost, choose the view that
answers the human question, and avoid producing the rest mechanically.

The initial executable fixtures now cover the first three contrasting outcomes:
a local bug fix whose mutation boundary excludes documentation, a cross-module
order flow requiring component and runtime PlantUML views, and a stateful order
design requiring a focused class view. Mechanical assertions verify mutation
scope and diagram-kind markers; semantic diagram quality remains explicitly
ungraded.

## Remaining Decision

The general paradigm-neutral iteration route is implemented. The remaining
decision is whether visual comprehension needs a small cross-cutting
diagram-selection skill that routes to current prospective-design and
architecture-recovery capabilities, or whether improved relationship guidance
and evaluations are sufficient.

That choice should be informed by routing and behavioral evals rather than by
catalog aesthetics alone.
