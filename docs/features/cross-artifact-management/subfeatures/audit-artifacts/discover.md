# Discover: Audit Artifacts

## Parent Feature

- Feature: `cross-artifact-management`
- Subfeature ID: `audit-artifacts`
- Subfeature Type: `additive`

## Problem

The repo already validates individual artifact types in a few narrow places, but
it lacks one cross-artifact audit capability that can answer questions like:

- which proposals or features are missing required docs
- which registries disagree with on-disk folders or metadata
- which reviewed packets are stale or never promoted to the next handoff
- which links across proposals, features, subfeatures, and slices are missing
  or inconsistent

Without a dedicated audit capability, maintainers have to inspect each layer
manually and drift is easy to miss until it blocks planning or execution work.

## Goals

- Detect missing required files across proposal, feature, subfeature, and slice
  packets.
- Surface lifecycle inconsistencies such as stale reviewed packets, missing
  promotions, or registry entries pointing at missing paths.
- Reuse existing validators where possible instead of duplicating type-specific
  rules.
- Produce actionable findings that later repair tooling can consume.
- Distinguish genuinely broken active slice state from intentionally pruned
  archived history.

## Non-Goals

- Mutate or repair artifacts automatically as part of the first audit pass.
- Re-implement every existing validator inside a second state machine.
- Replace `audit-relations` for slice relations; build on it.

## Baseline Artifacts To Assess

- `docs/proposals/README.md` and `docs/proposals/registry.json`
- `docs/features/README.md` and `docs/features/registry.json`
- feature-local `subfeatures/README.md` and `subfeatures/registry.json`
- `slices/README.md`, `slices/registry.json`, and `.slice-meta.json`
- feature/subfeature `system-design.md` archived slice summary blocks

## Success Criteria

- A maintainer can run one audit-oriented capability and get a coherent list of
  cross-artifact issues.
- Findings distinguish between missing files, stale states, and broken links.
- The audit output is structured enough for future reporting and repair flows.
- Intentionally pruned archived slices do not appear as missing active slice
  directories once the retained history has moved to planning-layer summaries.

## Risks and Open Questions

- How much of the first version should be strict validation vs advisory linting?
- Which stale-state checks should be generic defaults vs project-specific rules?
- What durable signal should prove that a missing archived slice directory was
  pruned intentionally rather than lost accidentally?
