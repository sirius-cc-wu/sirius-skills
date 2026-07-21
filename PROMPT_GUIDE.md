# Prompt Guide

Name the skill and provide the repository outcome you want. Include constraints
such as the intended file set, validation command, base branch, or required
identifier when they matter.

## `simplify`

```text
Use simplify on the current branch diff. Preserve behavior, keep changes within
the files already touched, and run the focused test suite afterward.
```

```text
Simplify this pull request after review feedback. Remove duplication and
unnecessary state, but call out any cleanup that would change the public API.
```

## `commit`

```text
Use commit to review and commit only the changes for the retry fix. Run the
relevant tests and follow this repository's configured commit format.
```

```text
Commit the documentation cleanup, excluding unrelated working-tree changes.
```

## `create-pr`

```text
Use create-pr to open a draft pull request against the repository's default
branch. Derive the title from the commits and include the tests that passed.
```

```text
Create a ready-for-review PR for the current branch with base release/2.x.
```

## `governance-update`

```text
Use governance-update to review these three repeated formatter spillover
incidents and add the narrowest enforceable rule to AGENTS.md.
```

```text
Use governance-update to decide whether repeated commit-title drift belongs in
AGENTS.md or .skills/conventions.json, then update the single best owner.
```

Avoid invoking `governance-update` for an isolated typo, defect, or stale
artifact. Fix those directly.
