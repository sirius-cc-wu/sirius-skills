# Discover: Repair Artifacts

## Parent Feature

- Feature: `cross-artifact-management`
- Subfeature ID: `repair-artifacts`
- Subfeature Type: `additive`

## Problem

Even with strong workflow helpers, durable repos can drift after:

- manual edits to README or registry files
- merge conflicts or partial conflict resolution
- interrupted automation that updates some metadata but not all of it
- historical repositories upgraded from older layouts

The repo needs an explicit repair capability that can resync artifact views
without forcing maintainers to patch JSON and markdown by hand.

## Goals

- Rebuild derived registry views from the durable folder structure and metadata.
- Offer conservative repair flows that prefer dry runs and explicit changes.
- Repair drift across proposal, feature, subfeature, and slice registries.
- Complement audit findings with a supported remediation path.

## Non-Goals

- Silently overwrite handwritten planning content.
- Repair semantic planning mistakes such as poor story breakdown.
- Use destructive cleanup as the default repair mechanism.

## Baseline Artifacts To Assess

- `README.md` and `registry.json` files generated for proposal, feature,
  subfeature, and slice registries
- `.proposal-meta.json`, `.planning-meta.json`, `.subfeature-meta.json`, and
  `.slice-meta.json`
- existing migration and finalization helpers that already repair narrow cases

## Success Criteria

- A maintainer can restore registry and metadata consistency after common drift
  events.
- Repair flows explain what changed and what still requires manual attention.
- The first version stays conservative and reviewable.

## Risks and Open Questions

- Some inconsistencies are structural while others reflect genuine human intent.
- Repair tooling must avoid becoming an unsafe “force sync everything” shortcut.
