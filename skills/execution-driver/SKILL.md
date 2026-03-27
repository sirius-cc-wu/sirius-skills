---
name: execution-driver
description: Deprecated alias for guide-execution.
---

# Execution Driver

`execution-driver` remains available as a backward-compatible alias for `guide-execution`.

## Status

- Deprecated for new workflows
- Supported for existing prompts, automation, and repositories

## What to use now

Use `guide-execution` as the canonical execution-layer entrypoint.

Recommended migration:

- prefer the `guide-execution` skill name in prompts and workflow docs
- prefer `skills/guide-execution/scripts/manage_execution.py` in examples and automation
- keep `execution-driver` only when you need compatibility with older instructions

## Scope

This alias still represents the same execution-layer responsibility:

- resolve the active slice
- verify registry state, slice files, and metadata
- route work to `brief`, `blueprint`, `review-execution`, or `close-slice`
- maintain execution readiness state in the slice registry

For the canonical guidance, use `skills/guide-execution/SKILL.md`.
