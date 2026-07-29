---
name: recover-system-behavior
description: Recovers black-box system behavior with traceable evidence. Use when requirements are missing or stale and current commands, APIs, events, user interactions, failures, or externally visible constraints must be inferred from interfaces, tests, safe runtime observations, and implementation before design or change.
---

# Recover System Behavior

## Overview

Describe what actors can currently cause and observe without confusing
implementation details with intended requirements. Recover successful,
alternate, failure, and security-sensitive behavior one bounded scenario at a
time.

## When to Use

- Existing behavior must be understood before maintenance or migration.
- Tests and interfaces exist but requirements are absent, stale, or uncertain.
- A black-box contract, use-case hypothesis, or system-event sequence is
  needed before architecture or change work.
- Do not use to assign internal responsibilities or approve product intent.

## Evidence Discipline

Read
[Recovery Evidence and Confidence](../reverse-engineer-software-system/references/recovery-evidence.md).
Label behavior as current observation, tested assertion, documented claim,
intended requirement, or inference. A bug that exists is not automatically a
requirement that should persist.

## Workflow

1. **Select one external goal or interface.** Bound the recovery to a command,
   API operation, message, scheduled event, file exchange, or user interaction.
2. **Name the system boundary and actors.** Include people and external
   systems that exchange events; exclude internal modules and classes.
3. **Inventory inputs, outputs, and effects.** Trace arguments, requests,
   events, environment, persisted changes, responses, errors, emitted
   messages, and externally visible timing.
4. **Mine executable evidence.** Read tests by behavior level, fixtures, and
   assertions. When authorized and safe, run the smallest relevant checks or
   observations and record their exact conditions and results.
5. **Trace implementation support.** Follow entry points only far enough to
   explain the observed outcome, boundary rule, or unresolved branch. Keep
   internal calls out of the black-box scenario.
6. **Recover the main scenario.** Express actor intent, system responsibility,
   and meaningful result in external terms.
7. **Recover extensions and negative behavior.** Include invalid input,
   authorization failure, unavailable dependencies, partial effects,
   cancellation, retry, timeout, concurrency, and recovery where evidenced.
8. **Recover externally visible qualities.** Record enforced limits, ordering,
   confidentiality, integrity, availability, accessibility, portability, and
   performance constraints without inventing guarantees from constants alone.
9. **Separate intent and anomalies.** Mark surprising behavior, inconsistent
   tests, unreachable branches, and documentation conflicts for reconciliation.
10. **Hand off carefully.** Use recovered events to inform system sequence
    diagrams or contracts only after their evidence and intended status are
    explicit.

## Behavior Model Template

When persisting a standalone Markdown model, follow
[Markdown Artifact Frontmatter](../iterative-up-analysis-design/references/markdown-artifact-frontmatter.md)
and [Readable Technical Artifacts](../iterative-up-analysis-design/references/readable-technical-artifacts.md).
The main observed scenario provides the representative scenario; keep its
evidence status distinct from intended behavior.

```markdown
---
type: "Recovered Behavior Model"
title: "Recovered Behavior: [Goal or Interface]"
description: "[Observable behavior and scope recovered]"
id: "[Stable behavior ID when cross-referenced]"
status: "[draft | active | reconciled]"
revision: "[Commit, tag, build, or snapshot]"
tags: [reverse-engineering, behavior]
---

# Recovered Behavior: [Goal or Interface]

## At a Glance

[Explain the external goal, observed outcome, and why this behavior matters,
with its evidence status.]

## Boundary and Actors

- System: [black-box boundary]
- Actor: [goal and exchanged events]

## Main Observed Scenario

1. [Actor intent or external event]
2. [Observable system responsibility or result]

## Extensions and Failures

- [condition]: [observable result, effects, and recovery]

## Inputs, Outputs, and Effects

- [interface data, persistent effect, external call, timing, or ordering]

## Evidence

- [claim record using the shared vocabulary]

## Anomalies and Unknowns

- [possible defect, conflict, untested branch, or missing intent]

## Candidate Forward Artifacts

- [use case, SSD, contract, quality requirement, or characterization need]
```

## Red Flags

- Naming internal functions or UI gestures as actor goals.
- Treating every passing test as a complete requirement.
- Inferring absence of behavior only because no test was found.
- Describing only successful flows around validation, security, or external
  dependencies.
- Running production-affecting probes without explicit authority.

## Verification

- [ ] The selected behavior is bounded by an external goal or interface.
- [ ] Actors, inputs, outputs, effects, and meaningful responses are black-box.
- [ ] Main, alternate, failure, and security-sensitive paths are covered in
      proportion to evidence and risk.
- [ ] Each material behavior claim names perspective, status, confidence,
      temporal status, and evidence.
- [ ] Existing behavior and intended behavior remain distinguishable.
- [ ] Anomalies, contradictions, and unobserved paths are explicit.
- [ ] The opening explains the observed behavior and evidence status before detailed interfaces or failures.
- [ ] A standalone model exposes identity, revision, summary, and lifecycle
      metadata in one frontmatter block.
