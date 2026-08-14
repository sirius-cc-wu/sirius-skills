---
name: plan-up-iterations
description: Plans and sequences an explicit multi-iteration Unified Process (UP) roadmap across inception, elaboration, construction, or transition using architectural risks, phase intent, selected use-case and object-design dependencies, exit evidence, replanning triggers, and durable artifact lifecycles. Use when a team asks to plan several UP iterations, elaboration and construction candidates, or a phased requirements-to-object-design route without executing them; use run-development-iteration to execute any one selected iteration, even when that iteration has UP phase context.
---

# Plan UP Iterations

## Overview

Plan several risk-driven UP iterations without turning the method into a
mandatory artifact sequence. Preserve phase intent, selected dependencies, and
durable knowledge while giving each proposed iteration one objective and exit
evidence. This is an advisory planning specialization, not an execution
coordinator: it does not perform an iteration, validate implementation, create
an execution commit, or continue automatically from one iteration to the next.

## When to Use

- A team explicitly requests Unified Process phase framing across two or more
  proposed iterations.
- Product, requirements, architecture, and object-design risks need sequencing
  across inception, elaboration, construction, or transition.
- A multi-iteration roadmap must show when selected use cases, examples, domain
  concepts, SSDs, contracts, responsibilities, realizations, design classes, or
  patterns become useful.
- Durable artifacts and optional historical iteration records need
  lifecycle-aware ownership across an explicitly UP-framed plan.
- Do not use to execute an iteration, modify product code, validate a completed
  slice, or create its commit; use `run-development-iteration`.
- Do not use for a single iteration merely because it is called elaboration or
  construction. Carry that phase context into `run-development-iteration`.
- Do not use for an isolated specialist question, ordinary roadmap planning
  without UP framing, a bug fix, or a repository-placement decision.

## Workflow

1. **Fix the planning baseline.** Read repository governance and identify the
   source material, revisions, lifecycle and approval states, planning horizon,
   requested UP vocabulary, non-goals, and unresolved authority. Planning may
   expose candidate work but must not promote it to approved execution input.
2. **State phase intent.** Explain which inception, elaboration, construction,
   or transition concerns matter and why. Treat phases as risk context, not
   sequential gates or directory names.
3. **Inventory material risks and learning needs.** Identify product scope,
   stakeholder, behavior, architecture, integration, object-responsibility,
   language, verification, deployment, and adoption uncertainties that may
   justify separate iterations.
4. **Shape multiple iteration candidates.** Give each proposed iteration one
   risk, learning, decision, or delivery objective plus concrete exit evidence.
   Keep each candidate small enough for one coherent execution change; do not
   execute or close it here.
5. **Select methods conditionally.** Use cases may lead to examples, SSDs,
   domain concepts, or contracts when those questions matter. Add GRASP,
   realizations, patterns, or design class diagrams only when object
   responsibility or collaboration is the selected problem. Do not treat the
   dependency graph as a deliverable checklist.
6. **Budget artifact creation.** Apply the
   [Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
   Use `select-technical-artifacts` when choosing among several material owners
   or dispositions. A roadmap entry may consult or update an artifact without
   creating a separate iteration record.
7. **Choose artifact placement.** Preserve established canonical paths. When no
   convention exists, several homes compete, or migration is material, use
   [Design Repository Artifact Layout](../design-repository-artifact-layout/SKILL.md).
   Do not organize durable knowledge by UP phase.
8. **Sequence by evidence and dependency.** Order iterations so early exit
   evidence reduces the most important risk or enables a later objective.
   Record genuine dependencies and optional branches; avoid dates, estimates,
   or precision unsupported by evidence.
9. **Preserve durable ownership.** Refine selected design artifacts at their
   canonical paths across iterations. Keep a roadmap, accepted decisions,
   current design knowledge, and historical execution records distinct. Link
   rather than copy artifact bodies.
10. **Define execution boundaries.** For every iteration candidate, record
    required authority, source revision, non-goals, selected specialist
    questions, artifact dispositions, exit evidence, and conditions that would
    cause replanning.
11. **Review the whole route.** Remove iterations and artifacts that do not
    independently reduce risk, produce needed evidence, or enable a later
    objective. Verify that the plan can stop or change after every iteration.
12. **Hand off one iteration.** Identify the first candidate that is both
    authorized and ready, then route only that candidate to
    [Run Development Iteration](../run-development-iteration/SKILL.md). Do not
    execute it, commit it, or begin later candidates from this skill.

## File Output

Keep the plan conversational unless cross-session coordination, review, or
traceability gives it a durable owner. Before creating a plan file, apply the
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
When persisting standalone Markdown, follow
[Markdown Artifact Frontmatter](references/markdown-artifact-frontmatter.md)
and use STE-style.

## Multi-Iteration UP Plan

Preserve an established planning format. Without one, use this proportionate
shape and omit empty fields or sections:

```markdown
---
type: "Phase Plan"
title: "UP Roadmap: [Scope]"
description: "[Planning horizon, primary risk, and intended outcome]"
id: "[Opaque stable ID only when repository rules or cross-references require it]"
status: "[proposed | approved | superseded]"
tags: ["unified-process", "iteration-planning"]
---

# UP Roadmap: [Scope]

## Planning Boundary

- Source and revision: [authoritative or candidate input]
- Authority state: [what is approved, proposed, or unresolved]
- Horizon and phase intent: [why UP framing helps]
- Non-goals: [what this roadmap does not authorize or plan]

## Iteration Roadmap

| Candidate | Phase context | One objective | Risk or dependency | Exit evidence | Authority/readiness |
|---|---|---|---|---|---|

## [Candidate ID]: [Objective]

- Phase context: [inception | elaboration | construction | transition]
- Objective: [one learning, risk-reduction, decision, or delivery outcome]
- Entry authority and inputs: [revision-fixed sources and approval state]
- Selected specialist questions: [only methods justified for this objective]
- Exit evidence: [evidence that permits stopping, replanning, or later work]
- Non-goals: [excluded work]
- Replan when: [failed assumption, evidence, or authority change]

Artifact Budget:
- [create | update | embed | keep with implementation | omit | defer]: `[owner or subject]` - [consumer or risk] - [ownership and lifecycle reason]

Dependencies and trace:
- [prior evidence or artifact] -> [this objective] -> [possible later objective]

## Execution Handoff

- Next authorized candidate: [candidate ID or none]
- Run with: `run-development-iteration`
- Readiness gap: [approval, evidence, oracle, or specialist input still needed]
```

Approval of the roadmap does not authorize every iteration, mutation, commit,
or publication in it. `run-development-iteration` rechecks authority and the
current baseline before executing one candidate.

## Artifact Durability

- Treat the roadmap as an evolving plan, not as proof that an iteration ran.
- Treat selected use cases, domain models, SSDs, contracts, realizations, and
  design class diagrams as durable, evolving sources of truth when they pass
  the artifact budget.
- Give cross-referenced artifacts stable opaque identifiers and one canonical
  path according to repository rules.
- Let `run-development-iteration` create or close a historical iteration record
  only when coordination, audit, or durable unresolved risk gives it an
  independent lifecycle.
- Link the roadmap and execution records to canonical artifacts without copying
  their bodies.

## Execution Handoff

A selected roadmap candidate is input to `run-development-iteration`, not an
implicit command to execute. The execution skill must fix the then-current
source revision and authority, choose one objective, re-evaluate specialists
and artifact dispositions from current evidence, validate exit evidence, make
at most one authorized commit, and stop. Later roadmap entries remain proposed
until separately selected and authorized.

## Red Flags

- A single-iteration request is expanded into a multi-iteration UP roadmap.
- Phase labels are treated as approval gates, dates, or filesystem structure.
- Every UP artifact is scheduled regardless of the risks and questions present.
- The plan claims implementation, validation, results, or commits that did not
  occur.
- Roadmap approval is treated as authority to execute every candidate.
- Durable design artifacts are copied into each iteration entry.
- Object design begins from nouns alone without behavior or system events.
- A new documentation taxonomy is imposed without repository evidence or the
  artifact-layout specialist.
- The planner executes the first iteration or continues automatically after a
  handoff.

## Verification

- [ ] The source revisions, authority states, planning horizon, and non-goals
      are explicit.
- [ ] UP phase intent is justified as risk context rather than a mandatory
      lifecycle.
- [ ] The result contains at least two iteration candidates, each with one
      objective and exit evidence.
- [ ] Every selected method or artifact answers a stated question, risk, or
      dependency.
- [ ] Material documentation candidates have dispositions and every `create`
      passes the artifact budget.
- [ ] Durable artifacts, the evolving roadmap, accepted decisions, and
      historical execution records remain distinct.
- [ ] Dependencies and traceability support sequencing without inventing dates
      or certainty.
- [ ] Every candidate can stop or trigger replanning after its exit evidence.
- [ ] Exactly one ready candidate, or a precise readiness gap, is handed to
      `run-development-iteration`.
- [ ] No iteration execution, implementation validation, commit, publication,
      or later candidate occurred.
