---
name: architecture
description: Analyze architectural factors and design or review logical layers, package dependencies, and scenario-based architecture views using Larman's approach. Use for consequential system structure decisions, quality tradeoffs, or concise architecture documentation.
---

# Make architecture decisions traceable to requirements

Start with significant scenarios, quality requirements, constraints, and the current implementation. Architecture is shaped by reliability, performance, variability, skills, and cost as well as functional behavior. Work within the existing architecture unless the task calls for broader change.

## Identify and resolve the factors

For each influential factor, record its source, measurable response, conditions, variation, impact, priority, and uncertainty. Distinguish variation already required from a plausible future evolution point. Do not protect every imaginable change.

Convert vague goals into testable questions. For example, “fast checkout” needs a workload, measurement boundary, and response target. If a target is unavailable, propose one as an assumption for review rather than attributing it to stakeholders.

Compare candidate solutions against the factors. Record the decision, alternatives, rationale, consequences, and an experiment or observation that could falsify it. Respect fixed constraints first, then business goals, then other preferences. Architectural work during elaboration includes executable tests of risky decisions.

## Structure the logical design

- Group responsibilities into cohesive layers or packages appropriate to the system. Typical concerns include presentation, application coordination, domain behavior, technical services, and general foundations; this is not a required folder hierarchy.
- Keep business rules out of UI objects and concrete UI dependencies out of domain objects.
- Define allowed dependency directions. Use a cohesive facade for a subsystem when useful; a package that merely groups related types does not automatically need one.
- For upward notification, use an abstraction such as an observer contract. Distinguish runtime message direction from static source dependency.
- Identify package cycles. Consider regrouping strongly related types or extracting a genuinely stable interface to break a harmful cycle.
- Group types that collaborate or change together. Place reusable abstractions where their dependents do not inherit unrelated volatile dependencies.
- Avoid introducing remote calls, independently deployed services, or a new persistence framework merely to implement a logical layer.

Read [architecture views and factors](references/views-and-factors.md) for documentation structure and quality scenarios.

## Deliver and validate

Provide a focused factor/decision record, a logical dependency view, and the important cross-boundary scenario. Add process, deployment, data, security, or other views only where they answer real questions.

Trace each architectural mechanism back to its motivating requirement and its evidence. Check the implementation's actual dependency graph where available. Distinguish demonstrated properties from proposed designs: a diagram of redundancy does not prove recoverability, and a cache does not prove acceptable response time or freshness.

Preserve the distinction between a logical layer, an operating-system process, a physical node, and a deployable artifact. One process can contain many logical layers, and one logical service can have multiple deployments.

## Source

Distilled and paraphrased from Larman, *Applying UML and Patterns*, third edition, chapters 13, 33–34, 36–37, and 39; supplied PDF pp. 313–335, 734–780, 819–832, and 869–888. Page positions are 1-based. Decision-record and implementation-validation wording is a practical adaptation of technical memos and executable architectural investigation.
