# Discover: Report Artifacts

## Parent Feature

- Feature: `cross-artifact-management`
- Subfeature ID: `report-artifacts`
- Subfeature Type: `additive`

## Problem

The repo has durable artifacts and registries, but maintainers still need to
open multiple folders or JSON files to answer simple operational questions:

- what proposals are active or accepted
- which feature packets are waiting for design, review, or execution bootstrap
- which subfeatures are stale
- which slices are open, closed, or relation-bearing

A reporting capability should turn the existing durable metadata into concise
operational views.

## Goals

- Provide summary outputs for active, stale, reviewed, and completed artifacts.
- Support reports grouped by artifact type, parent feature, or lifecycle state.
- Make it easy to surface workflow bottlenecks without mutating any source
  artifact.
- Reuse data from registries and metadata rather than duplicating it.

## Non-Goals

- Replace artifact-specific source-of-truth files with generated reports.
- Force one dashboard style or one storage target for every repository.
- Hide important details behind opaque aggregate counts.

## Baseline Artifacts To Assess

- proposal, feature, subfeature, and slice registries
- planning and slice metadata timestamps and statuses
- relation metadata that can enrich reports with dependency or supersession
  context

## Success Criteria

- A maintainer can generate useful status summaries without manual folder reads.
- Reports make stale or blocked workflow packets easy to spot.
- The outputs are reusable for future human-facing docs or automation.

## Risks and Open Questions

- Which report shapes should be first-class vs left to project-local extensions?
- How much historical detail should reports include by default?
