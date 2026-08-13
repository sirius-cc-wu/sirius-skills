---
name: design-repository-artifact-layout
description: Designs or revises the smallest repository-specific layout for durable proposals, requirements, analysis, design, recovery, decision, iteration, and verification artifacts. Use when asked where technical artifacts should live, how canonical paths and indexes should be organized, whether a documentation structure should be split or consolidated, or how to migrate competing artifact homes while preserving links and history; use the artifact's owning skill when its content rather than its repository placement is the primary task.
---

# Design Repository Artifact Layout

## Overview

Give durable technical knowledge one obvious canonical home without imposing a
speculative documentation taxonomy. Start from repository governance and the
way readers already navigate, separate artifacts with different lifecycles,
and recommend the smallest compatible structure. A request for advice remains
read-only; create directories or move files only when the user explicitly
authorizes those repository changes.

## When to Use

- A proposal, requirement, analysis, design, recovery, decision, iteration, or
  verification artifact needs a canonical repository location.
- A repository has partial or competing documentation structures and needs a
  lifecycle-aware placement decision.
- A flat artifact must be evaluated for promotion into independently maintained
  files, or small files may need consolidation.
- Current artifacts need a migration plan that preserves stable identifiers,
  inbound links, indexes, and historical records.
- Do not use merely to decide whether any standalone document should exist;
  use `select-technical-artifacts` when that is the material question, or apply
  its artifact-selection budget locally when the disposition is clear.
- Do not author or semantically rewrite the artifact body, plan a multi-iteration
  UP roadmap, or choose implementation design on behalf of the corresponding
  specialist.

## Workflow

1. **Read local authority.** Inspect the nearest `AGENTS.md`, documentation
   guidance, naming and identifier rules, indexes, templates, validators, and
   neighboring artifacts. Preserve explicit repository conventions.
2. **Bound the placement decision.** Name the artifact kinds and repository
   area in scope, the readers whose navigation matters, the concrete ownership
   or navigation problem, and whether the user authorized recommendations,
   file creation, or migration.
3. **Inventory actual homes.** Locate current proposals, decisions, feature or
   product knowledge, architecture and recovery views, verification evidence,
   and iteration history. Distinguish an established layout from an incidental
   directory or one-off file.
4. **Confirm selection.** Require every artifact in scope to pass the
   [Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md)
   before assigning a new file or directory. If several candidate artifacts or
   dispositions remain material, route that decision to
   `select-technical-artifacts`. Prefer executable evidence, an existing
   canonical owner, or an aggregate section when it is sufficient.
5. **Separate lifecycles.** Classify current evolving knowledge, historical
   iteration records, decision-seeking proposals, accepted decisions, and
   executable or retained verification evidence. Do not co-locate them merely
   because one activity produced them together.
6. **Identify the navigation axis.** Determine whether readers primarily find
   knowledge by feature, artifact type, product area, or chronology. Resolve
   conflicts from repository evidence rather than personal preference.
7. **Choose the smallest layout.** Follow
   [Artifact Durability and Repository Layouts](references/artifact-layouts.md).
   Preserve a coherent established structure. Without one, begin with the flat
   feature-iteration hybrid and promote a feature to a package only when its
   artifacts are independently maintained.
8. **Define canonical ownership.** Assign one current path per artifact, stable
   IDs only where cross-references need them, any necessary index ownership,
   and links among requirements, decisions, design, verification, and history.
9. **Plan migration proportionately.** List source and destination paths,
   affected indexes and inbound links, compatibility redirects or migration
   notes when needed, and validation. Keep closed historical records stable
   unless moving them solves a concrete problem.
10. **Recommend or apply within authority.** Explain preserved conventions,
    the minimal addition or migration, alternatives, and uncertainty. If moves
    were explicitly authorized, perform only the approved changes, update
    links and indexes, run repository checks, and inspect the final diff.

## Output

A placement recommendation should include only useful parts of this shape:

```markdown
Scope:
- [artifact kinds, repository area, and mutation authority]

Observed conventions:
- `[path]` - [what it establishes and confidence]

Recommended canonical homes:
- `[artifact or lifecycle]` -> `[path or pattern]` - [reader, owner, and reason]

Preserve:
- [existing paths, names, IDs, indexes, and historical records]

Migration:
- `[old path]` -> `[new path]` - [links, index, and validation]

Alternatives and uncertainty:
- [credible alternative or unresolved local rule]
```

Do not create a layout proposal file unless it independently passes the
artifact-selection budget. If a standalone Markdown recommendation is
justified, follow
[Markdown Artifact Frontmatter](../plan-up-iterations/references/markdown-artifact-frontmatter.md)
and
[Readable Technical Artifacts](../plan-up-iterations/references/readable-technical-artifacts.md).
Do not add placeholder indexes or empty directory trees merely to make a
recommendation visible.

## Red Flags

- A generic preferred taxonomy replaces a coherent repository convention.
- Directories are created for artifact kinds that have no current durable
  owner or independently changing content.
- Current design knowledge is copied into iteration records or organized by UP
  phase, obscuring its canonical source.
- One pending idea or proposal is treated as accepted intent or an accepted
  decision.
- The same candidate direction is copied into both an idea and a proposal even
  though their audience, owner, and lifecycle do not differ.
- A file is split because it is long rather than because its parts have
  independent ownership or lifecycles.
- Stable identifiers, inbound links, indexes, or historical records are lost
  during migration.
- A recommendation silently becomes repository mutation.
- The layout skill starts authoring requirements, design, recovery findings, or
  proposal content that belongs to another skill.

## Verification

- [ ] Applicable governance, indexes, validators, and neighboring artifacts were inspected.
- [ ] The scope, navigation problem, primary readers, and mutation authority are explicit.
- [ ] Every proposed standalone artifact passes the value, ownership, and lifecycle gate.
- [ ] Current knowledge, proposals, decisions, iteration history, and verification evidence have appropriate lifecycle boundaries.
- [ ] The recommendation preserves a coherent established layout or cites a concrete reason to change it.
- [ ] The selected structure is the smallest one with obvious canonical homes and no speculative directories.
- [ ] Cross-referenced artifacts retain stable IDs, one canonical path, and valid inbound and outbound links.
- [ ] Migration preserves historical records and updates affected indexes and links.
- [ ] No artifact content, lifecycle status, implementation, commit, or publication changed without separate authority.
- [ ] Repository checks and final-diff inspection pass after any authorized mutation, or remaining gaps are reported precisely.
