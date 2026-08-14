---
name: reconstruct-software-architecture
description: Reconstructs evidence-backed as-built software architecture from an existing system. Use when recovering modules, components, dependencies, runtime collaborations, state ownership, deployment, data flow, concurrency, or trust boundaries for maintenance, migration, audit, or documentation.
---

# Reconstruct Software Architecture

## Overview

Transform extracted implementation facts into the smallest architectural views
that answer a concrete question. Represent actual language and runtime
constructs, and distinguish present structure from intended design or
historical rationale.

## When to Use

- Current architectural documentation is missing, stale, or needs conformance
  checking.
- Ownership, dependency direction, runtime collaboration, deployment, or trust
  boundaries must be understood before change.
- A representative behavior needs an as-built realization.
- Do not use to generate exhaustive class or call graphs without a decision.

## Evidence Discipline

Read
[Recovery Evidence and Confidence](../reverse-engineer-software-system/references/recovery-evidence.md).
Fix the revision and trace each abstraction to source, build, configuration,
runtime, or test evidence.

When the implementation language is known, use
[Software Design Language Adaptation](../software-design-language-adaptation/SKILL.md)
and read only its matching reference. Model modules, functions, values, tasks,
channels, processes, or services when they own behavior; do not force every
participant into a class.

## Workflow

1. **Name the architectural question.** Examples include change impact,
   security authority, service decomposition, state ownership, runtime
   ordering, deployment, or replacement boundaries.
2. **Choose necessary views.** Select among context, module/dependency,
   component-and-connector, runtime interaction, data/state, deployment, and
   trust-boundary views. Do not create all views by default.
3. **Extract implementation facts.** Inspect manifests, module declarations,
   imports, public interfaces, call sites, constructors/composition roots,
   configuration, generated wiring, schemas, and deployment definitions.
4. **Abstract cohesive elements.** Group facts by stable responsibility and
   change reason. Preserve meaningful dependencies, ownership, direction, and
   multiplicity; omit incidental local calls.
5. **Recover state and authority.** Identify owners of mutable state,
   synchronization, transactions, caches, filesystem roots, credentials,
   network clients, and process or user authority.
6. **Trace representative runtime scenarios.** Start at an external event and
   follow controllers, collaborators, asynchronous boundaries, side effects,
   error propagation, and responses. Note when static evidence cannot establish
   runtime dispatch.
7. **Recover deployment and external connectors.** Show processes, hosts,
   browser or device boundaries, databases, queues, third parties, protocols,
   and failure dependencies when relevant.
8. **Check against negative evidence.** Look for forbidden routes, absent
   dependencies, rejected inputs, no-fallback rules, and tests proving boundary
   containment.
9. **Record alternatives, not invented rationale.** Mark possible abstractions
   and unclear ownership as inference. Leave design motivation to accepted
   decisions or reconciliation.
10. **Review usefulness.** Confirm that every element and relation helps answer
    the architectural question and is traceable to evidence.

## Architecture Template

Before creating a new document, apply
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
Prefer adding the smallest necessary view to an existing architecture artifact
when it already owns the question and evidence.

When persisting a standalone Markdown reconstruction, follow
[Markdown Artifact Frontmatter](../plan-up-iterations/references/markdown-artifact-frontmatter.md)
and use STE-style.
Use the representative runtime scenario before exhaustive element inventories
when runtime behavior is the architectural question.

```markdown
---
type: "Recovered Architecture"
title: "Recovered Architecture: [System, Area, or Scenario]"
description: "[Architectural question and views represented]"
id: "[Stable reconstruction ID when cross-referenced]"
status: "[draft | active | reconciled]"
revision: "[Commit, tag, build, or snapshot]"
language: "[Language or mixed]"
tags: [reverse-engineering, architecture]
---

# Recovered Architecture: [System, Area, or Scenario]

## At a Glance

[Explain the architectural question, the answer supported by current evidence,
and the important consequence or uncertainty.]

## Question and View Selection

- Question: [decision supported]
- Views: [chosen views and why]

## Context and External Connectors

- [actor, process, system, protocol, or dependency]

## Modules or Components

- [element]: [evidenced responsibility]

## Relationships and Ownership

- [source] -> [target]: [call, data, ownership, synchronization, or authority]

## Representative Runtime Scenario

1. [external event]
2. [collaboration, async boundary, state change, side effect, response]

## State, Deployment, and Trust Boundaries

- [state owner, process allocation, privileged boundary, or failure dependency]

## Evidence and Confidence

- [claim record using the shared vocabulary]

## Unknowns and Alternative Interpretations

- [unresolved dispatch, generated wiring, runtime condition, or abstraction]
```

## Red Flags

- Equating a generated call graph with architecture.
- Inventing pattern names or GRASP rationales not supported by design evidence.
- Omitting ownership, direction, async boundaries, or external effects.
- Drawing runtime order solely from imports.
- Combining current code with historical components in one unlabeled view.

## Verification

- [ ] The architectural question and selected views are explicit.
- [ ] Elements and relations abstract current implementation evidence at a
      useful level.
- [ ] Language, ownership, concurrency, state, deployment, and authority are
      represented where relevant.
- [ ] Representative runtime scenarios trace to recovered behavior or an
      external interface.
- [ ] Every material abstraction has evidence and calibrated confidence.
- [ ] Intent, rationale, and history are not inferred from structure alone.
- [ ] The opening and representative runtime scenario orient readers before exhaustive architecture detail.
- [ ] A standalone reconstruction exposes identity, revision, summary,
      language, and lifecycle metadata in one frontmatter block.
