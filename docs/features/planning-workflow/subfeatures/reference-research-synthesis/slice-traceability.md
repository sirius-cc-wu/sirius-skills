# Slice Traceability

Use this file to map repo story IDs to execution slices without moving story
ownership outside repository planning artifacts.

## Subfeature Context

- Parent feature: `planning-workflow`
- Subfeature ID: `reference-research-synthesis`
- Subfeature type: `additive`
- Use `Planned Slice IDs` for the new or amended slices defined by this
  subfeature.
- Keep subfeature-local traceability in this folder instead of folding it back
  into parent feature breakdown docs.
- Record affected canonical slice IDs such as `pw-routing` and
  `pw-review-readiness` in `Notes`, not `Execution Slice IDs`.

## Conventions

- Keep repo story IDs exactly as they appear in `user-stories.md`.
- Use planned slice IDs that begin with a feature or subfeature prefix rather
  than bare `slice-*` placeholders unless a repository-specific convention says
  otherwise.
- Use one primary row per repo story. When one story fans out into multiple
  planned slices, add additional rows for that same story so each row keeps
  exactly one planned slice ID.
- List increment IDs as a comma-separated list when a story spans multiple
  increments.
- List multiple execution slice IDs as a comma-separated list only when a
  single planned slice genuinely maps to more than one execution slice.
- Record only real execution blockers in `Blocked By`.
- Leave `Execution Slice IDs` blank until `slice` bootstraps execution slices.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RRS-01 | M | Add an explicit reference-research step | I1 | rrs-research-skill | research skill, local artifact |  | rrs-research-skill | Seeds the `reference-research.md` contract for both feature and subfeature planning packets |
| RRS-04 | S | Require research only when relevant | I1 | rrs-relevance-routing | guide-planning routing, methodology | rrs-research-skill | rrs-relevance-routing | Keeps low-relevance work on direct `discover` or `design` paths |
| RRS-03 | M | Record the chosen borrowing path durably | I2 | rrs-research-consumers | planning skill docs | rrs-relevance-routing | rrs-research-consumers | Makes downstream planning phases consume the local research artifact instead of re-deriving comparison |
| RRS-02 | M | Write reusable conclusions into the wiki layer | I2 | rrs-wiki-synthesis | research skill, wiki layer | rrs-research-consumers |  | Uses the derived wiki root and updates `index.md` and `log.md` only when conclusions are reusable |

## Notes

- `Blocked By` uses execution-slice relationships between planned slices.
- `Planned Slice IDs` records the planned identifiers before slice bootstrap.
- `Execution Slice IDs` records the actual bootstrapped slice IDs after `slice`
  runs.
- `Increments` records planning-level grouping only; do not treat it as an
  execution state.
- Affected parent slices remain baseline context only; this subfeature does not
  reuse parent slice IDs as new planned slices.
