# Multi-Skill and Progressive Disclosure Design

Use this guide when a skill supports multiple domains, frameworks, providers, or output modes.

## Goal

Keep the top-level `SKILL.md` focused on:

- what the skill does
- how to choose the right branch or variant
- the shared workflow that applies everywhere

Move variant-specific details into `references/` files so the model only reads the parts it needs.

## Why this matters

Large all-in-one skills waste context and make it harder for the model to find the relevant guidance quickly.

Progressive disclosure keeps the main skill lean while still allowing deep domain detail when needed.

## Recommended structure

```text
skill-name/
├── SKILL.md
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

Or by domain:

```text
skill-name/
├── SKILL.md
└── references/
    ├── finance.md
    ├── sales.md
    └── marketing.md
```

## What belongs in SKILL.md

Keep these in the main file:

- overall purpose
- triggering guidance
- shared workflow
- branch-selection guidance
- links to the relevant reference files

## What belongs in references

Move these out of the main file when they differ by variant:

- provider-specific commands
- framework-specific conventions
- domain schemas and terminology
- long examples
- configuration tables

## Good navigation pattern

```markdown
## Choose the deployment target

- For AWS deployments, read `references/aws.md`
- For GCP deployments, read `references/gcp.md`
- For Azure deployments, read `references/azure.md`
```

The important part is not just linking the file, but stating when to read it.

## One-level-deep rule

Prefer all reference files to be linked directly from `SKILL.md`.

Avoid chains like:

- `SKILL.md` -> `references/overview.md`
- `overview.md` -> `references/providers/aws.md`

That structure makes discovery harder and increases the chance the wrong file gets read.

## When to split content

Split content into references when:

- the skill supports more than one variant
- the main file is getting long
- most users only need one subset of the guidance
- the details are reference-heavy rather than procedural

Keep content in the main file when:

- every invocation needs it
- it is part of the shared workflow
- it helps the model choose the correct branch

## Iteration tip

If a skill started simple and later gained multiple modes, do not keep appending everything to the main `SKILL.md`.

Instead:

1. Identify the shared core.
2. Move branch-specific details into separate references.
3. Update the main file to route the model to the correct reference.

This usually improves both triggering clarity and runtime efficiency.
