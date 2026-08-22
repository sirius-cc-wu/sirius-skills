# Prompt Guide

Name the skill and provide the repository outcome you want. Include constraints
such as scope, revision, validation command, intended files, or publication
state when they matter.

## Repository workflow

```text
Use walkthrough-me on PR #123. I understand the frontend but not the
persistence layer. Build a logical tour, show only the first section, and wait
for me before continuing. Focus on request flow, state changes, and tests.
```

```text
Use walkthrough-me on commit 4f9c2ab. Explain its behavior change in logical
sections and wait at each checkpoint.
```

```text
Use walkthrough-me on my unstaged changes. Keep untracked files separate, show
only the first section, and do not edit or stage anything.
```

```text
Use commit to review and commit only the retry fix. Follow this repository's
configured commit format and exclude unrelated working-tree changes.
```

```text
Use create-pr to open a draft pull request against the default branch. Include
the checks that passed and avoid creating a duplicate PR.
```

```text
Review these repeated formatter-spillover incidents and update the nearest
applicable AGENTS.md with the narrowest enforceable rule. Avoid duplicating
existing guidance or codifying a one-off incident.
```

## Optional external add-ons

These skills come from Addy Osmani's external `agent-skills` collection. The
`all` installation provides the curated add-on set; the skills remain outside
the Sirius catalog and named profiles.

```text
Use interview-me to ask one question at a time until my intended outcome, user,
success condition, binding constraint, and non-goals are explicit. Do not plan
or implement yet.
```

```text
Use idea-refine to explore alternatives for this confirmed intent, test the key
assumptions, and converge on one candidate direction with MVP scope and a Not
Doing list. Store the confirmed idea in an established ideas path or a
feature path defined by local governance. Do not create a new proposal artifact.
Preserve existing legacy proposals at their historical paths.
```

```text
Use code-review-and-quality before merging this change. Review correctness,
readability, architecture, security, and performance; label findings by
severity and report the verification evidence.
```

```text
Use code-simplification on the recently changed code after the checks pass.
Preserve exact behavior, follow local conventions, keep the pass within the
changed scope, and rerun the affected checks after each simplification.
```

## Reverse engineering

```text
Use reverse-engineer-software-system to recover the behavior and architecture
needed to plan this migration. Fix the analysis to the current revision and
separate observed facts from inferences.
```

```text
Use survey-existing-system to map this repository's entry points, interfaces,
state, side effects, verification surfaces, and highest-risk follow-up slices.
```

## Iterative design and implementation

```text
Use select-technical-artifacts to review the proposed vision, use-case,
architecture, ADR, test-plan, and iteration documents. Classify each as create,
update, embed, keep with implementation, omit, or defer; select the smallest
durable set; do not create or edit files.
```

```text
Use record-architecture-decision to capture our accepted choice of PostgreSQL
for transactional services. Preserve local ADR conventions; record authority,
forces, serious alternatives, consequences, confidence, and reconsideration
triggers; do not implement or commit anything.
```

```text
Use design-repository-artifact-layout to inspect the existing documentation
structure and recommend canonical homes for durable feature knowledge,
decisions, verification evidence, and iteration history. Preserve established
conventions and do not move files.
```

```text
Use stakeholder-requirements-elicitation to identify the affected roles and
capture interview, observation, and policy evidence without turning feature
requests into requirements or design.
```

```text
Use requirements-synthesis-validation to turn this identified evidence set into
source-linked candidate requirements and examples. Record validation and
approval only for roles with documented authority, and preserve open conflicts.
```

```text
Use implementation-slice-briefing to select the smallest ready vertical
behavior slice from these approved requirements and design inputs. Fix the brief
to the current repository revision and expose every exclusion and stop condition.
```

```text
Use iterative-risk-driven-development to select one risk-driven objective for
this feature. Use only the methods, artifacts, and Rust lifecycle design that
the objective justifies. If the work moves a system, test, responsibility,
runtime, resource, or verification boundary, retain the representative vertical
scenario and distinguish an enabling seam from the parent outcome. Implement,
validate, and commit one iteration at a time until the work is complete.
```

```text
Use use-case-modeling and domain-modeling to clarify the actor goals, main and
alternate scenarios, domain vocabulary, associations, and rules before object
design.
```

```text
Use grasp-responsibility-design to assign this approved scenario's preparation,
coordination, supervision, and cleanup to native modules, functions, tasks,
adapters, handles, types, or composition roots. Explain coupling and cohesion
without forcing class-shaped owners or deciding exact Rust resource ownership.
```

```text
Use design-rust-lifecycles to turn this approved validation-run behavior and
native responsibility map into an ownership-safe Rust lifecycle. Preserve the
system boundary and end-to-end oracle. Define preparation, resource transfer,
readiness, partial-start rollback, cancellation, joining, and fallible cleanup
without introducing speculative traits or typestate.
```

```text
Use test-driven-implementation to add this behavior from the approved examples.
Demonstrate that the focused checks detect the missing behavior, then run the
relevant regression suite.
```

```text
Use behavior-preserving-refactoring on this module behind the current passing
tests. Keep behavior changes separate and verify each bounded transformation.
If the change creates a backend, composition root, runtime owner, test seam, or
cleanup boundary, return to iterative-risk-driven-development instead of
hiding a system redesign inside local cleanup.
```

See [`catalog/skills.md`](catalog/skills.md) for the complete catalog and
[`catalog/tracks/`](catalog/tracks/) for common compositions.
