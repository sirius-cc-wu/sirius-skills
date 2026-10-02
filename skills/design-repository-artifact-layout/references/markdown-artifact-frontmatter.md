# Markdown Artifact Frontmatter

Use these rules when a skill persists an analysis, design, decision, iteration,
or verification artifact as a standalone Markdown file. They adapt the
[Open Knowledge Format (OKF) v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
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
status: "[Lifecycle state: draft | proposed | accepted | stable | superseded | deprecated]"
tags: ["[short-tag]"]
generated: { by: "human:sirius", at: "YYYY-MM-DDTHH:MM:SSZ" }
verified: { by: "human:sirius", at: "YYYY-MM-DDTHH:MM:SSZ" }
---
```

Only `type` is required by OKF. This collection also defaults to `title` and
`description` because they make indexes, previews, and searches useful. The
other fields in the base shape are conditional.

## Actor Attribution & Trust Tiers

Identities in `generated.by` and `verified.by` follow the OKF actor convention:
- `human:<id>`: Human engineer (e.g. `human:sirius`).
- `<producer>/<model-or-version>`: Autonomous agent (e.g. `agent/thinker`, `agent/builder`, `copilot-cli/gemini-3.8-flash`).
- `process:<id>`: Automated pipeline (e.g. `process:ci-qualification`, `process:bun-test`).

Consumers (both agents and humans) derive trust tiers from `verified`:
- **Unverified**: Concept has no `verified` metadata or is in `draft` status.
- **Machine-Confirmed**: Verified by automated test suites or compiler checks (`process:*` or agent).
- **Human-Reviewed**: Explicitly signed off by a human authority (`human:*`).

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
| Software architecture design | `Software Architecture Design` |
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

## Reserved Files & Progressive Disclosure

- **`index.md` catalogs**: Directory and stage `index.md` files provide progressive
  disclosure catalogs for knowledge bundles. Root and stage `index.md` files declare
  `okf_version: "0.2"`, `title`, and `description` in YAML frontmatter and list concept documents.
- **`log.md` files**: Keep `log.md` files free of frontmatter and use ISO 8601 `YYYY-MM-DD` date
  headings for entries.
- Do not use `index.md` or `log.md` as names for concept artifacts.

These reserved-file rules apply when producing an OKF-compatible knowledge
bundle. Preserve stricter established repository conventions when they exist.
