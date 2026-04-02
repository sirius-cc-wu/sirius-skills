# Slice Planning

## 1. Planning Scope

- Feature: Proposal workflow
- Planning sources:
  - `discover.md`
  - `system-design.md`
  - `user-stories.md`
- Execution system: repository-managed slices
- Execution mode: `single-agent`
- Notes: The initial implementation is already present in the repo; this feature records the capability durably as a canonical feature.

## 2. Story Decisions

| Story ID | Story Size | Story Risk | Decision | Reason | Output Slice Count |
| --- | --- | --- | --- | --- | --- |
| PFW-01 | M | medium | keep | Proposal registry and storage behavior are one coherent deliverable. | 1 |
| PFW-02 | M | medium | keep | Guide-planning routing is one bounded integration surface. | 1 |
| PFW-03 | M | low | keep | Proposal lifecycle validation has one primary implementation path. | 1 |
| PFW-04 | M | medium | keep | Promotion is one bounded handoff from proposal staging into canonical planning. | 1 |
| PFW-05 | S | low | keep | Config support is a small supporting integration. | 1 |

## 3. Increment Plan

| Increment | Goal / User-Visible Value | Included Story IDs | Planned Slice IDs | Demo / Verification Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | Stage speculative ideas outside the feature registry | PFW-01, PFW-03 | PFW-01-proposal-registry, PFW-03-proposal-lifecycle | A maintainer can create and validate proposal folders under `docs/proposals/`. | Simplest usable path |
| I2 | Route planning into the proposal workflow | PFW-02, PFW-05 | PFW-02-guide-routing, PFW-05-config-support | `guide-planning` and project config support proposal staging cleanly. | Depends on I1 |
| I3 | Promote accepted proposals into canonical planning | PFW-04 | PFW-04-proposal-promotion | An accepted proposal can be promoted into `docs/features/<feature>/` with safeguards. | Depends on I2 |

## 4. Execution Slice Backlog

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PFW-01-proposal-registry | PFW-01 | Create proposal registry and storage | Add `docs/proposals/` registry files and proposal-scoped folder creation. | `skills/propose/`, `docs/proposals/` | primary | `pytest -q skills/propose/tests/test_manage_proposals.py` | completed |  | yes |
| PFW-03-proposal-lifecycle | PFW-03 | Enforce proposal lifecycle and validation | Track proposal states, review notes, and validation gates in `.proposal-meta.json`. | `skills/propose/scripts/manage_proposals.py` | primary | `pytest -q skills/propose/tests/test_manage_proposals.py` | completed | PFW-01-proposal-registry | yes |
| PFW-02-guide-routing | PFW-02 | Route speculative work through propose | Update planning docs and skill routing so early ideas use `propose`. | `README.md`, `SKILLS_METHODOLOGY.md`, `skills/guide-planning/SKILL.md` | primary | doc review + related pytest coverage | completed | PFW-01-proposal-registry | yes |
| PFW-05-config-support | PFW-05 | Support configurable proposal storage | Extend `.skills/planning.json` and bootstrap defaults with `proposal_dir`. | `.skills/planning.json`, `skills/bootstrap/` | primary | `pytest -q skills/bootstrap/tests/test_bootstrap.py` | completed | PFW-01-proposal-registry | yes |
| PFW-04-proposal-promotion | PFW-04 | Promote accepted proposals into features | Add explicit promotion from proposal staging into canonical feature planning. | `skills/guide-planning/scripts/manage_planning.py` | primary | `pytest -q skills/propose/tests/test_manage_proposals.py skills/guide-planning/tests/test_manage_planning.py` | completed | PFW-02-guide-routing, PFW-03-proposal-lifecycle, PFW-05-config-support | yes |

## 5. Dependency Notes

- Critical path: proposal registry -> lifecycle validation -> routing/config -> promotion.
- Parallel-safe work was limited because routing, config, and promotion all depended on the same proposal model.
- The implemented scope is coherent and already validated by the repository tests.

## 6. Review Notes

- Review outcome: Ready for `slice` if future enhancement work is needed.
- Blocking findings: none for the current implemented scope.
- Handoff note: keep the separation between proposal instances and canonical features explicit in future changes.
