---
name: conductor
description: Hybrid orchestrator: spec-driven for protocol/interface artifacts, design-driven for architecture and implementation.
---

# Conductor Skill (Orchestrator)

This skill manages a hybrid lifecycle: treat protocol/interface artifacts as spec-driven (SDD) and treat architecture, prototyping and implementation details as design-driven (DDD). It coordinates handoffs between specification, planning, and implementation tracks and enforces guardrails for interface conformance.

## Lifecycle Coordination
- **Phase 1: Specification (SDD)**: If no `spec.md` exists and the track is interface-critical: Redirect to `specify` (SDD) to produce a formal `spec.md` including `Interface Spec` and `Acceptance Tests` sections. For non-interface-critical tracks, `design.md` (DDD) is acceptable.
- **Phase 1b: Design (DDD)**: If a `design.md` exists but no `spec.md`, redirect to `design` for iterative architecture and prototyping. A `design.md` is encouraged for all tracks.
- **Phase 2: Planning**: If `spec.md` exists but no `plan.md`: Redirect to `plan`. `plan.md` MUST map TDD steps to spec items for interface-critical tracks.
- **Phase 3: Implementation**: If required spec/design and `plan.md` exist and validation passes: Hand off to `implement` for the execution loop.

## Key Responsibilities
1. **Discovery**: Scan `specs/README.md` to identify the active track and whether it is interface-critical.
2. **Registry Management**: Update track status in `specs/README.md` using `scripts/manage_specs.py` (use `add`, `validate-spec`, `validate-design`, `status`).
3. **Guardrails**: Ensure `implement` only starts once required validations pass (for interface-critical tracks `validate-spec` must pass) and the `plan.md` is approved and contains verifiable TDD steps.

## Tooling
Always use `scripts/manage_specs.py` for registry updates and validation to ensure cross-platform compatibility. The script automatically extracts the **Track ID** from the current branch name (e.g., `123-feature` or `feature/123-name`) to use as the track ID when adding or validating tracks. If no ID is found, it will fallback to a timestamp for personal projects.

```bash
# When on a branch with an ID or simple feature name:
python3 <path-to-conductor>/scripts/manage_specs.py add "feature-name"

# To specify an ID manually:
python3 <path-to-conductor>/scripts/manage_specs.py add "ID" "feature-name"
```
