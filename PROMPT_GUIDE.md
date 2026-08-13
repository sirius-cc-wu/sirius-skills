# Prompt Guide

Name the skill and provide the repository outcome you want. Include constraints
such as scope, revision, validation command, intended files, or publication
state when they matter.

## Repository workflow

```text
Use simplify on the current branch diff. Preserve behavior, keep changes within
the files already touched, and run the focused test suite afterward.
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

## Optional upstream intent and idea refinement

These skills come from Addy Osmani's external `agent-skills` collection and are
not installed by Sirius profiles.

```text
Use interview-me to ask one question at a time until my intended outcome, user,
success condition, binding constraint, and non-goals are explicit. Do not plan
or implement yet.
```

```text
Use idea-refine to explore alternatives for this confirmed intent, test the key
assumptions, and converge on one candidate direction with MVP scope and a Not
Doing list. Preserve this repository's established ideas or proposals path.
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
Use plan-up-iterations to plan several risk-driven UP iterations for
this feature. Give each candidate one objective and exit evidence, preserve
only justified durable artifacts, and hand off the first ready candidate to
run-development-iteration without executing it.
```

```text
Use use-case-modeling and domain-modeling to clarify the actor goals, main and
alternate scenarios, domain vocabulary, associations, and rules before object
design.
```

```text
Use design-rust-lifecycles to turn this approved validation-run behavior into
an ownership-safe Rust lifecycle. Define preparation, resource transfer,
readiness, partial-start rollback, cancellation, and fallible cleanup without
introducing speculative traits or typestate.
```

```text
Use test-driven-implementation to add this behavior from the approved examples.
Demonstrate that the focused checks detect the missing behavior, then run the
relevant regression suite.
```

```text
Use behavior-preserving-refactoring on this module behind the current passing
tests. Keep behavior changes separate and verify each bounded transformation.
```

See [`catalog/skills.md`](catalog/skills.md) for the complete catalog and
[`catalog/tracks/`](catalog/tracks/) for common compositions.
