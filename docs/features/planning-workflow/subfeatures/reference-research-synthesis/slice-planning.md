# Slice Planning

Use this file to decompose repo stories into execution-ready slices before
bootstrapping execution slices.

## Slice ID Naming

- Default naming: `<scope-prefix>-<capability-slug>`
- Use a short lowercase alias derived from the owning feature slug for
  feature-scoped breakdown.
- Use a short lowercase alias derived from the owning subfeature ID for
  subfeature-scoped breakdown.
- Avoid meaningless generic prefixes such as bare `slice-*` unless a
  repository-specific convention explicitly requires them.

## 0. Subfeature Context

- Parent feature: `planning-workflow`
- Parent feature path: `docs/features/planning-workflow`
- Subfeature ID: `reference-research-synthesis`
- Subfeature type: `additive`
- Current subfeature status: `breakdown_ready`
- Impact input: `impact-analysis.md` is present and should drive the
  subfeature-local slice plan.

### Affected Story IDs

- `PW-01`
- `PW-02`
- `PW-03`
- `PW-04`

### Affected Canonical Slice IDs

- `pw-registry`
- `pw-gates`
- `pw-routing`
- `pw-templates`
- `pw-breakdown-guidance`
- `pw-review-readiness`
- `pw-slice-handoff`

### Affected Baseline Artifacts

- `docs/features/planning-workflow/discover.md`
- `docs/features/planning-workflow/system-design.md`
- `docs/features/planning-workflow/user-stories.md`
- `docs/features/planning-workflow/slice-planning.md`
- `docs/features/planning-workflow/slice-traceability.md`

## 1. Planning Scope

- Feature: reference-research-synthesis
- Planning sources:
  - `discover.md`
  - `impact-analysis.md`
  - `system-design.md`
  - `user-stories.md`
  - parent `docs/features/planning-workflow/user-stories.md`
  - parent `docs/features/planning-workflow/slice-planning.md`
  - parent `docs/features/planning-workflow/slice-traceability.md`
- Execution system: repository-managed slices
- Execution mode: `single-agent`
- Notes:
  - This is subfeature-local breakdown for `reference-research-synthesis` under
    parent feature `planning-workflow`.
  - Plan only the new or amended slices required by this subfeature.
  - Keep this subfeature's `slice-planning.md` and `slice-traceability.md` as
    the execution-planning source of truth for the child capability.
  - Use `rrs-` as the subfeature slice prefix.
  - Keep affected parent slice IDs such as `pw-routing` and
    `pw-review-readiness` in dependencies or notes only; do not reuse them as
    new subfeature-local slice IDs.

## 2. Story Decisions

| Story ID | Story Size | Story Risk | Decision | Reason | Output Slice Count |
| --- | --- | --- | --- | --- | --- |
| RRS-01 | M | medium | keep | Creating one explicit `research` skill plus the local `reference-research.md` contract is one cohesive execution packet with one primary validation path. | 1 |
| RRS-02 | M | medium | keep | Reusable wiki synthesis is a focused follow-on once the local research artifact contract is stable. | 1 |
| RRS-03 | M | medium | keep | Downstream planning-doc consumption shares one citation contract and can be validated together. | 1 |
| RRS-04 | S | low | keep | Routing thresholds and methodology guidance are a small, coherent packet once the explicit skill exists. | 1 |

Decision rules:

- `keep` means the story is already small enough to map to one executable slice.
- `split` means the story fans out into multiple execution-ready slices.
- `defer` means the story is not ready and should not be executed yet.
- split any `XL` story before slice bootstrap
- `S`/`M`/`L` stories may also split when risk, validation shape, coupling, or
  handoff complexity would make one packet brittle
- record the main reason for the decision, not just the size label

Risk rubric:

- `low`: one cohesive packet with one clear validation path
- `medium`: some coupling, multiple touchpoints, or moderate sequencing/handoff
  risk
- `high`: cross-subsystem impact, migration/reconciliation, compatibility risk,
  or materially different validation paths

## 3. Increment Plan

Use increments to group related slices into small, demonstrable outcomes.
Increment 1 should usually be the simplest end-to-end usable path.

| Increment | Goal / User-Visible Value | Included Story IDs | Planned Slice IDs | Demo / Verification Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | Explicit local research workflow exists | RRS-01, RRS-04 | rrs-research-skill, rrs-relevance-routing | A maintainer can be routed to a dedicated `research` skill when relevant and get a local `reference-research.md` artifact without adding a new planning lifecycle state. | Simplest usable path |
| I2 | Research output is reused across planning and wiki synthesis | RRS-03, RRS-02 | rrs-research-consumers, rrs-wiki-synthesis | Downstream planning skills cite the local research artifact, and reusable conclusions update the derived wiki root plus index/log. | Depends on I1 |

Rules:

- keep increments feature-scoped planning artifacts, not execution slices
- each increment should be demonstrable without requiring the full project to be
  complete
- an increment can include one or many execution-ready slices
- planned slices and execution slices remain slice-scoped even when they belong
  to the same increment

## 4. Execution Slice Backlog

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rrs-research-skill | RRS-01 | Create explicit research skill | Add `skills/research/` workflow guidance plus helper behavior that resolves feature or subfeature targets and writes `reference-research.md`. | `skills/research/` | primary | `pytest -q skills/research/tests/test_research.py` | create slice |  | yes |
| rrs-relevance-routing | RRS-04 | Route research only when relevant | Update `guide-planning` and methodology guidance so reference research is invoked only when upstream comparison materially affects planning shape. | `skills/guide-planning/`, `SKILLS_METHODOLOGY.md` | primary | `pytest -q skills/guide-planning/tests/test_manage_planning.py` | create slice | rrs-research-skill | yes |
| rrs-research-consumers | RRS-03 | Teach planning docs to cite research output | Update `discover`, `design`, and `review-planning` guidance so later planning phases read `reference-research.md` and preserve the chosen borrowing path durably. | `skills/discover/`, `skills/design/`, `skills/review-planning/`, `SKILLS_METHODOLOGY.md` | primary | `rg -n "reference-research\\.md|research" skills/discover/SKILL.md skills/design/SKILL.md skills/review-planning/SKILL.md SKILLS_METHODOLOGY.md` | create slice | rrs-relevance-routing | yes |
| rrs-wiki-synthesis | RRS-02 | Add reusable wiki synthesis flow | Extend the research workflow so reusable conclusions update the derived wiki root plus `index.md` and `log.md` without auto-bootstrapping the wiki layer. | `skills/research/`, wiki docs | primary | `pytest -q skills/research/tests/test_research.py` | create slice | rrs-research-consumers | yes |

## 5. Dependency Notes

- Critical path: `rrs-research-skill` -> `rrs-relevance-routing` ->
  `rrs-research-consumers` -> `rrs-wiki-synthesis`.
- Explicit blockers: downstream planning guidance and wiki synthesis both depend
  on the local `reference-research.md` contract being stable first.
- Parallel-safe slices: none recommended; the slices share one workflow contract
  and should stay in one lane to reduce documentation and helper drift.
- Increment ordering: `I1` -> `I2`.
- Lane owners and handoffs: single-agent planning work across `guide-planning`,
  the new `research` skill, and downstream planning docs.
- Integration checkpoints: after `I1`, confirm local artifact generation plus
  routing guidance; after `I2`, confirm planning-doc citations and derived
  wiki-root behavior stay aligned.

## 6. Bootstrap Order

1. `rrs-research-skill`
2. `rrs-relevance-routing`
3. `rrs-research-consumers`
4. `rrs-wiki-synthesis`

## 7. Open Questions / Stop-and-Ask Items

- Default wiki page selection should prefer one focused destination per run; use
  a concept page by default unless the synthesis is clearly feature-lesson
  specific.
- Use checked-in references as the default source set; broader fetched docs
  should stay opt-in when local references are insufficient.

## 8. Review Notes

- Review outcome: Ready for human approval, planning commit, and later `slice`
  bootstrap.
- Blocking findings: none. Discovery intent, design boundaries, and breakdown
  sequencing are coherent with the affected parent planning workflow.
- Handoff note: start with `rrs-research-skill`, keep `reference-research.md` as
  the local contract first, then layer routing guidance, downstream planning-doc
  consumption, and wiki synthesis on top.

## Notes

- This file is feature-scoped planning, not slice-scoped execution.
- Keep increment definitions here, not in execution-slice artifacts.
- Once planned slices are created, record the actual slice IDs in
  `slice-traceability.md`.
- Keep slice IDs stable enough that they can be cross-referenced from
  traceability notes and planning discussion.
