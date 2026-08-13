# Markdown Artifact Frontmatter

Use these rules when a skill persists an analysis, design, decision, iteration,
or verification artifact as a standalone Markdown file. They adapt the
[Open Knowledge Format (OKF) 0.1 draft](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
to this skill collection.

## File Rules

- Start each standalone artifact file with exactly one YAML frontmatter block.
- Include a non-empty `type`, plus a human-readable `title` and a one-sentence
  `description`.
- Add producer-defined scalar or list fields such as `id`, `status`,
  `use_case`, `scenario`, or `language` only when they improve identity,
  routing, filtering, or lifecycle discovery. Keep rationale, scenarios,
  diagrams, and evidence in the Markdown body.
- Add `resource` only when the artifact describes an underlying asset with a
  canonical URI. Add `timestamp` only when an accurate ISO 8601 time for the
  last meaningful change is available. Use `tags` as a YAML list of short
  strings.
- Quote placeholder text and values that YAML could interpret as booleans,
  numbers, dates, or collection syntax. Remove unfilled optional fields rather
  than leaving placeholders in a finished artifact.
- Preserve compatible repository-defined and unknown frontmatter keys when
  updating a file. Merge these fields into existing frontmatter instead of
  creating a second block.
- Treat a file containing several closely related artifacts as one aggregate
  concept: describe the aggregate in file-level frontmatter and keep each
  artifact's local details in its body section.
- Do not add frontmatter to conversational responses, source files, generated
  diagrams that are not Markdown, or Markdown fragments embedded in another
  file.

Templates in the skills assume a standalone file. When embedding a template as
a section of an aggregate Markdown file, omit its frontmatter and adjust its
heading level to fit the containing document.

## Base Shape

```yaml
---
type: "[Descriptive artifact type]"
title: "[Human-readable display name]"
description: "[One-sentence summary]"
id: "[Stable ID when the artifact is cross-referenced]"
status: "[Lifecycle state when useful]"
tags: ["[short-tag]"]
---
```

Only `type` is required by OKF. This collection also defaults to `title` and
`description` because they make indexes, previews, and searches useful. The
other fields in the base shape are conditional.

## Artifact Types

Use a descriptive type that matches the file's primary content. Prefer these
stable values across this collection:

| Artifact | `type` value |
|---|---|
| Vision | `Vision` |
| Business case | `Business Case` |
| Supplementary specification | `Supplementary Specification` |
| Glossary | `Glossary` |
| Risk list | `Risk List` |
| Development case | `Development Case` |
| Phase plan | `Phase Plan` |
| Iteration plan and result | `Iteration Record` |
| Use case | `Use Case` |
| Domain model | `Domain Model` |
| System sequence diagram | `System Sequence Diagram` |
| Operation contract | `Operation Contract` |
| GRASP responsibility decision | `Responsibility Decision` |
| Use-case realization | `Use-Case Realization` |
| Design class diagram | `Design Class Diagram` |
| Pattern decision | `Pattern Decision` |
| Language-specific design adaptation | `Implementation Design Adaptation` |
| Behavior-slice evidence | `Behavior Slice Evidence` |
| Refactoring evidence | `Refactoring Record` |
| Cross-cutting design decision | `Architecture Decision` |
| Other mechanically checked evidence | `Verification Evidence` |

Use another self-explanatory value when none of these accurately describes the
artifact. Do not combine unrelated concepts merely to avoid introducing a new
type.

## Reserved Files

- Keep directory `index.md` files free of frontmatter. A bundle-root `index.md`
  may contain frontmatter only when declaring `okf_version: "0.1"`.
- Keep `log.md` files free of frontmatter and use ISO 8601 `YYYY-MM-DD` date
  headings for entries.
- Do not use `index.md` or `log.md` as names for concept artifacts.

These reserved-file rules apply when producing an OKF-compatible knowledge
bundle. Preserve stricter established repository conventions when they exist.
