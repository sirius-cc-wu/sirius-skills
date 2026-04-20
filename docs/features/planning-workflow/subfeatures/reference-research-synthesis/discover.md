# Discover: Reference Research Synthesis

## Parent Feature

- Feature: `planning-workflow`
- Subfeature ID: `reference-research-synthesis`
- Subfeature Type: `additive`

## Problem

`sirius-skills` already supports canonical feature discovery, design, breakdown,
planning review, and a bootstrapped wiki layout, but it does not yet have a
durable planning capability dedicated to **reference research plus reusable wiki
synthesis**.

Today, reference comparison usually happens ad hoc inside `discover`,
`design`, `review-planning`, or repo-local `AGENTS.md` guidance. That can work
for a single task, but it leaves three gaps:

1. useful cross-reference conclusions are easy to lose in chat or feature-local
   docs,
2. wiki updates depend on maintainer discipline rather than an explicit
   workflow capability,
3. discovery can finish without a durable reference handoff even when upstream
   comparison should influence the feature shape.

This subfeature exists to give `planning-workflow` an explicit child capability
for researching checked-in references, recording the chosen borrowing path, and
updating the repository wiki layer when the conclusions are reusable beyond one
feature.

## Goals

- Add a repo-native planning capability for reference comparison and durable wiki
  synthesis.
- Keep reusable cross-reference conclusions in the wiki layer instead of burying
  them only inside one feature packet or one chat transcript.
- Let discovery and later planning steps explicitly consume reference-research
  conclusions when the feature shape depends on upstream patterns.
- Keep the wiki layer separate from canonical planning and execution artifacts.
- Make reference research **required when relevant**, without forcing it onto
  every trivial repo-local change.

## Non-Goals

- Replace `discover`, `design`, or `review-planning` as the main planning
  phases.
- Require cross-reference research for every small repository-local edit.
- Turn the workflow into a broad internet research agent or a generic
  search-summarization product.
- Make the wiki the source of truth for planning readiness or execution state.

## Primary Actors

- Planner or maintainer shaping a feature whose solution could be influenced by
  checked-in references.
- Reviewer wanting durable evidence for why one upstream pattern was chosen over
  another.
- Repository adopter using the wiki layer as the synthesized knowledge layer
  between raw references and feature-local planning.
- Skill maintainer extending `discover`-adjacent behavior without overloading
  `discover` itself.

## Desired Outcomes

- Teams can run an explicit research step when a feature overlaps existing
  upstream patterns.
- Reusable conclusions land in the wiki layer with index/log maintenance
  instead of staying feature-local only.
- Feature discovery can cite the resulting synthesis page and chosen borrowing
  path directly.
- The workflow stays generic-first and repository-centric rather than
  hardcoding one project's reference tree.

## Candidate Capability Areas

- **Reference discovery**
  - Inspect relevant checked-in `references/`, repo docs, and skill docs before
    or alongside feature discovery.
  - Compare multiple candidate upstream patterns instead of assuming one default
    reference path.

- **Borrowing-path synthesis**
  - Record which reference is strongest for the current problem and why.
  - Capture tensions, caveats, and later/lower-priority references explicitly.

- **Wiki maintenance**
  - Add or update focused concept/lesson pages under the derived wiki root.
  - Keep the wiki index and log aligned with the synthesis.

- **Planning handoff**
  - Feed reusable conclusions back into `discover.md`, `system-design.md`, or
    review guidance when the feature shape depends on them.
  - Keep "research required when relevant" as an explicit planning rule rather
    than an unreliable habit.

## Confirmed Signals in Repo

- `skills/bootstrap/SKILL.md` can scaffold a wiki layer, but it does not define
  an ongoing research/synthesis workflow after bootstrap.
- `skills/discover/SKILL.md` frames problem discovery, but it does not currently
  require a durable wiki update or a separate research handoff.
- `skills/design/SKILL.md`, `skills/assess/SKILL.md`, and
  `skills/review-planning/SKILL.md` already tell maintainers to read references
  when relevant, which shows the need exists but is still distributed.
- `AGENTS.md` already treats docs and skills as durable repo artifacts, so a
  reusable wiki-synthesis capability fits the repository's current workflow
  philosophy.

## Baseline Artifacts To Assess

- `skills/discover/SKILL.md`
- `skills/design/SKILL.md`
- `skills/review-planning/SKILL.md`
- `skills/bootstrap/SKILL.md`
- `AGENTS.md`
- any wiki structure expected by bootstrap and downstream guidance

## Subfeature Execution Planning

- Add or update `slice-planning.md` and `slice-traceability.md` inside this
  subfeature folder for any new execution work.
- Treat the parent feature docs as baseline context unless impact analysis
  explicitly narrows or supersedes them.

## Success Criteria

- A maintainer can invoke one explicit workflow capability for relevant
  cross-reference research instead of improvising it inside unrelated planning
  steps.
- Reusable conclusions are written into the wiki layer with index/log
  maintenance.
- Discovery or later planning artifacts can cite the research output directly.
- The workflow guidance stays clear that research is mandatory **when relevant**
  and optional otherwise.

## Risks and Open Questions

- Current design direction is one dedicated action-oriented `research` skill
  with a feature-local research artifact, rather than only a thin helper hidden
  inside `discover` and `review-planning`.
- Repositories without a bootstrapped wiki layer should still be able to record
  local research durably; reusable wiki synthesis can stay deferred until the
  wiki root exists.
- How strict should the "when relevant" trigger be so the workflow improves
  planning quality without becoming ceremony for trivial changes?
- Which planning artifacts should be required to cite the research output once it
  exists?
