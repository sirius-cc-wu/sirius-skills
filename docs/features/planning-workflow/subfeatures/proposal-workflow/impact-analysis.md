# Impact Analysis: Proposal Workflow

## Target Subfeature

- Parent Feature: `planning-workflow`
- Subfeature ID: `proposal-workflow`
- Subfeature Type: `additive`
- Current Subfeature Status: `reviewed`

## Subfeature Summary

Track proposal staging, lifecycle, routing, and promotion as a durable child
planning workflow without treating proposal instances as canonical features.

## Parent Baseline Reviewed

- `docs/features/planning-workflow/discover.md`
- `docs/features/planning-workflow/system-design.md`
- `docs/features/planning-workflow/user-stories.md`
- `skills/propose/SKILL.md`
- `skills/guide-planning/SKILL.md`

## Candidate Affected Story IDs

- `PFW-01`
- `PFW-02`
- `PFW-03`
- `PFW-04`
- `PFW-05`

## Candidate Affected Slice IDs

- `PFW-01-proposal-registry`
- `PFW-02-guide-routing`
- `PFW-03-proposal-lifecycle`
- `PFW-04-proposal-promotion`
- `PFW-05-config-support`

## Impact Notes

- This subfeature establishes the proposal mechanism itself as a durable
  planning capability; it does not turn proposal instances into canonical
  features.
- The main boundary is between speculative proposal storage under
  `docs/proposals/` and accepted work promoted into `docs/features/`.
- The routing impact centers on `guide-planning`, which should send uncertain
  or exploratory work to `propose` before canonical feature planning starts.
- Configuration impact is limited to proposal storage semantics such as
  `proposal_dir`; later work should preserve generic defaults.
