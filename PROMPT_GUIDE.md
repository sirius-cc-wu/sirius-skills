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
Use governance-update to review these repeated formatter-spillover incidents
and add the narrowest enforceable repository rule.
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
Use iterative-up-analysis-design to plan the smallest risk-driven iteration for
this feature. Preserve durable artifacts and avoid creating documents that do
not reduce uncertainty.
```

```text
Use use-case-modeling and domain-modeling to clarify the actor goals, main and
alternate scenarios, domain vocabulary, associations, and rules before object
design.
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
