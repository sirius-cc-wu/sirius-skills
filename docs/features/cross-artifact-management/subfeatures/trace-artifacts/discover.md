# Discover: Trace Artifacts

## Parent Feature

- Feature: `cross-artifact-management`
- Subfeature ID: `trace-artifacts`
- Subfeature Type: `additive`

## Problem

The workflow already stores durable metadata, but answering lineage questions is
still harder than it should be:

- which accepted proposal led to this feature
- which subfeature changed this parent capability
- which slices implement a planned story or requirement
- which newer slice superseded an older one

Maintainers need a trace capability that can follow these relationships across
layers without manual directory traversal.

## Goals

- Trace proposal -> feature -> subfeature -> planned slice -> execution slice
  lineage where the metadata exists.
- Present cross-artifact relations in a human-readable and machine-usable form.
- Reuse existing planning and execution registries instead of building a second
  hidden graph.
- Support both targeted lookups and broader lineage summaries.

## Non-Goals

- Infer unsupported links by guessing when the repository lacks durable signals.
- Replace the per-slice relation model already owned by execution tooling.
- Require every repository to adopt one specific visualization format.

## Baseline Artifacts To Assess

- proposal metadata including accepted and promoted state
- `.planning-meta.json` for features and subfeatures
- `slice-planning.md` and `slice-traceability.md`
- `.slice-meta.json` relation metadata and execution registry entries

## Success Criteria

- A maintainer can ask for the lineage of one artifact and get a coherent answer.
- The trace model makes ownership boundaries visible instead of hiding them.
- Future reporting can reuse the same cross-artifact lineage data.

## Risks and Open Questions

- Some lineage is explicit in metadata while other parts live only in markdown.
- The right output format may differ between CLI summaries, docs, and audits.
