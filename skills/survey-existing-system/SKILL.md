---
name: survey-existing-system
description: Maps an unfamiliar software repository's entry points, interfaces, dependencies, verification surfaces, documentation, and risk areas. Use when beginning maintenance, onboarding, architecture recovery, migration discovery, or a bounded reverse-engineering effort.
---

# Survey Existing System

## Overview

Build a fast, evidence-backed map of an unfamiliar system so that deeper
recovery work starts at the right boundaries. Stop at orientation; do not turn
the survey into an exhaustive architecture description.

## When to Use

- Approaching an unfamiliar repository or subsystem.
- Choosing where to trace behavior or reconstruct architecture.
- Establishing build, runtime, deployment, and test surfaces before change.
- Do not use as a substitute for scenario-level behavior recovery or
  architecture reconstruction.

## Evidence Discipline

Read
[Recovery Evidence and Confidence](../reverse-engineer-software-system/references/recovery-evidence.md).
Record the revision and distinguish repository facts from responsibility or
intent hypotheses.

## Workflow

1. **Read repository governance.** Find agent instructions, contribution
   guidance, generated-file rules, security constraints, and verification
   commands before exploring or executing anything.
2. **Fix scope and revision.** Name the repository or subsystem root, current
   revision, excluded generated/vendor areas, and the decision the survey
   supports.
3. **Inventory technology and packaging.** Locate manifests, workspaces,
   modules, languages, generated sources, release scripts, deployment
   definitions, and pinned toolchains.
4. **Find execution entry points.** Identify commands, processes, services,
   scheduled jobs, handlers, consumers, plugins, browser bundles, and startup
   composition roots.
5. **Map external interfaces.** List CLI commands, APIs, routes, messages,
   files, schemas, environment variables, user interfaces, and external
   systems without yet reconstructing full scenarios.
6. **Sketch repository responsibility areas.** Group directories and modules
   by cohesive capability using declarations, imports, build boundaries, and
   neighboring tests. Mark inferred groupings as inferred.
7. **Locate state and side effects.** Note databases, files, caches, queues,
   locks, background tasks, network calls, process launch, and other authority
   boundaries.
8. **Map verification surfaces.** Identify test levels, fixtures, static
   checks, browser/system harnesses, CI commands, and obvious gaps. Do not
   assume a test passes unless its result is available.
9. **Assess documentation and history.** Locate requirements, diagrams,
   decisions, runbooks, release notes, and lifecycle markers such as active,
   retired, or superseded.
10. **Prioritize follow-up slices.** Rank interfaces, scenarios, components, or
    risks for behavior recovery or architecture reconstruction and explain why
    each is decision-relevant.

## Survey Template

Before creating a new document, apply
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
Prefer updating an existing system survey or aggregate recovery record when it
already owns the scope and evidence.

When persisting a standalone Markdown survey, follow
[Markdown Artifact Frontmatter](../plan-up-iterations/references/markdown-artifact-frontmatter.md)
and [Readable Technical Artifacts](../plan-up-iterations/references/readable-technical-artifacts.md).

```markdown
---
type: "System Survey"
title: "System Survey: [System or Subsystem]"
description: "[Scope and decision supported by the survey]"
id: "[Stable survey ID when cross-referenced]"
status: "[draft | active | completed]"
revision: "[Commit, tag, build, or snapshot]"
tags: [reverse-engineering, survey]
---

# System Survey: [System or Subsystem]

## Survey Purpose

- Decision: [why this orientation is needed]
- Reader: [who will use it and what they need to find]

## Scope and Governance

- [root, revision, exclusions, and governing instructions]

## Technology and Packaging

- [language, manifest, build, deployment, release unit]

## Entry Points and Interfaces

- [entry point or external surface]: [evidence locator]

## Responsibility Areas

- [area]: [evidenced purpose or explicitly labeled hypothesis]

## State, Effects, and External Systems

- [state or authority boundary]

## Verification and Documentation

- [checks, artifacts, lifecycle signals, and gaps]

## Priority Recovery Slices

1. [slice]: [decision, risk, or learning value]

## Unknowns

- [question and evidence needed]
```

## Red Flags

- Reading files alphabetically without following entry points or interfaces.
- Treating directory names as proven architecture.
- Emitting a dependency or symbol dump without abstraction or purpose.
- Running expensive, mutating, or externally visible commands during a
  read-only survey.
- Reporting tests as green when they were only discovered, not executed.

## Verification

- [ ] Scope, revision, exclusions, and governance are recorded.
- [ ] Build, runtime, external interface, state, and verification surfaces are
      represented.
- [ ] Facts and hypotheses use the shared evidence vocabulary.
- [ ] Generated, vendor, fixture, and historical material are not mistaken for
      current production ownership.
- [ ] The survey ends with bounded, decision-relevant follow-up slices.
- [ ] The survey purpose explains why the inventory matters before listing system surfaces.
- [ ] A standalone survey exposes identity, revision, summary, and lifecycle
      metadata in one frontmatter block.
