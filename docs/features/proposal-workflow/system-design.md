# System Design: Proposal Workflow

## Overview

The proposal workflow adds a proposal-scoped staging layer ahead of canonical
feature planning.

Canonical features continue to live in:

```text
docs/features/<feature-slug>/
```

Speculative work lives separately in:

```text
docs/proposals/<proposal-slug>/
```

This preserves a clean planning boundary:

- proposal folders hold exploratory or not-yet-accepted work
- feature folders hold accepted canonical planning
- promotion is explicit instead of implicit
- existing-feature changes still route through `evolve-feature`

## Architectural Decisions

### 1. Proposal instances are not canonical features

A proposal instance represents candidate work, not accepted feature planning.
It must not appear in `docs/features/registry.json` until promoted.

### 2. Proposal storage is repository-native and configurable

Proposal folders default to `docs/proposals/` and are configured through
`.skills/planning.json` field `proposal_dir`.

### 3. Proposal lifecycle is separate from feature lifecycle

Proposal metadata lives in `.proposal-meta.json` and uses proposal-specific
states:

- `draft`
- `reviewed`
- `accepted`
- `rejected`
- `promoted`

These states are intentionally separate from canonical feature readiness states
such as `discovery_ready` or `planning_reviewed`.

### 4. Promotion is the boundary into canonical planning

Promotion creates or resolves a canonical feature folder using the existing
planning helpers and then copies applicable proposal artifacts such as
`discover.md` and `user-stories.md` when they are not already present.

Promotion must fail safely when a canonical feature already exists unless the
user is deliberately repairing state.

## Key Components

- `skills/propose/SKILL.md`
  - defines when to use `propose`
- `skills/propose/scripts/manage_proposals.py`
  - manages registry, metadata, validation, and promotion
- `docs/proposals/README.md`
  - human-readable proposal registry
- `docs/proposals/registry.json`
  - machine-readable proposal registry
- `docs/proposals/<proposal-slug>/.proposal-meta.json`
  - proposal lifecycle metadata
- `skills/guide-planning/SKILL.md`
  - routes speculative work to `propose`
- `skills/bootstrap/scripts/bootstrap.py`
  - writes default `proposal_dir`

## Validation Rules

- `discover.md` is required once a proposal reaches `reviewed` or beyond.
- `review_note` is required for `reviewed`, `accepted`, `rejected`, and `promoted` states.
- `promoted_feature` and `promoted_at` are required once a proposal reaches `promoted`.
- Promotion requires the proposal to be `accepted` unless the user explicitly forces repair.

## Routing Rules

- Use `propose` for speculative, exploratory, or umbrella-scoped work.
- Use `discover` directly when work is already accepted as canonical feature planning.
- Use `evolve-feature` when the request changes an existing canonical feature.

## Future Extension Areas

- richer proposal review checklists
- proposal-to-feature traceability backlinks in canonical feature docs
- optional proposal templates for different proposal classes
- richer rejection/closure history beyond current lifecycle metadata
