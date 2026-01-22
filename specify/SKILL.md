---
name: specify
description: Create formal `spec.md` artifacts (Spec-Driven Development).
---

# Specification Authoring (SDD)

Use this skill to produce formal `spec.md` documents for interface- or protocol-critical tracks. Output must be machine- and review-friendly and include required sections so `scripts/manage_specs.py validate-spec` can verify conformance.

## Required Sections
- `Interface Spec` (describe message formats, fields, semantics)
- `Acceptance Tests` (GIVEN/WHEN/THEN items mapped to spec entries)
- `Traceability` (Track ID and related plan references)

## Workflow
1. Clarify scope and constraints.
2. Produce a draft `spec.md` containing the required sections.
3. Iterate with reviewers until `validate-spec` passes and the conductor approves the plan handoff.

## Handoff
- On approval, `conductor` will trigger `plan` for TDD mapping and then `implement` once validations pass.
