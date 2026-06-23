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
- Subfeature ID: `feature-consolidation-and-reduction`
- Subfeature type: `superseding`
- Current subfeature status: `breakdown_ready`
- Impact input: no subfeature-local `impact-analysis.md` exists yet; this
  breakdown uses the parent planning packet plus the subfeature discovery and
  design artifacts as the current impact baseline.

### Affected Story IDs

- `PW-01`
- `PW-02`
- `PW-03`
- `PW-04`

### Affected Canonical Slice IDs

- `pw-registry`
- `pw-gates`
- `pw-routing`
- `pw-breakdown-guidance`
- `pw-review-readiness`

### Affected Baseline Artifacts

- `docs/features/planning-workflow/discover.md`
- `docs/features/planning-workflow/system-design.md`
- `docs/features/planning-workflow/user-stories.md`
- `docs/features/planning-workflow/slice-planning.md`
- `docs/features/planning-workflow/slice-traceability.md`

## 1. Planning Scope

- Feature: `feature-consolidation-and-reduction`
- Planning sources:
  - `discover.md`
  - `system-design.md`
  - `user-stories.md`
  - parent `docs/features/planning-workflow/user-stories.md`
  - parent `docs/features/planning-workflow/slice-planning.md`
  - parent `docs/features/planning-workflow/slice-traceability.md`
- Execution system: repository-managed slices
- Execution mode: `single-agent`
- Notes:
  - This is subfeature-local breakdown for
    `feature-consolidation-and-reduction` under parent feature
    `planning-workflow`.
  - Plan only the new or amended slices required by the consolidation policy;
    do not restate the entire parent planning backlog.
  - Use `fcr-` as the subfeature slice prefix.
  - Keep affected parent slice IDs such as `pw-routing` and
    `pw-review-readiness` in notes or dependencies only; do not reuse them as
    new subfeature-local slice IDs.
  - The current packet is reviewable without a dedicated `impact-analysis.md`
    because the affected parent stories, slices, and baseline artifacts are
    already named explicitly in this breakdown and the design packet.

## 2. Story Decisions

| Story ID | Story Size | Story Risk | Decision | Reason | Output Slice Count |
| --- | --- | --- | --- | --- | --- |
| FCR-01 | M | medium | keep | Consolidation declaration requirements across planning authoring guidance are one coherent execution packet with one primary validation path. | 1 |
| FCR-02 | M | medium | keep | Planning-review enforcement is one bounded packet once the declaration and metadata contract are defined. | 1 |
| FCR-03 | M | high | split | The story crosses metadata carriers plus multiple maintenance consumers, so it should separate contract introduction from downstream consumption. | 2 |
| FCR-04 | S | low | keep | Canonical user-facing surface guidance is a small, documentation-centered packet once review enforcement is defined. | 1 |

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
| I1 | Consolidation intent is declared and stored durably | FCR-01, FCR-03 | fcr-declaration-contract, fcr-metadata-summary | A maintainer can author consolidation intent in planning docs and persist one compact summary in the existing metadata carriers. | Simplest usable path |
| I2 | Planning review can block additive-only workflow growth | FCR-02, FCR-04 | fcr-review-gate, fcr-canonical-surface | Review guidance flags missing reduction stories as blocking when overlap exists, and maintainers can see which planning path stays canonical. | Depends on I1 |
| I3 | Maintenance workflows can trace and report consolidation outcomes | FCR-03 | fcr-history-consumers | Trace/report/archive surfaces can read consolidation summaries without inventing a second workflow-state model. | Depends on I1 and should land after the core review contract stabilizes |

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
| fcr-declaration-contract | FCR-01 | Require consolidation declarations in planning authoring | Update planning authoring guidance and scaffolding so workflow-shaping changes declare disposition, targets, artifact movement, and user-facing simplification. | `skills/discover/`, `skills/add-subfeature/`, `skills/assess/` | primary | `rg -n "consolidation|historical|simplification" /home/ccwu/.agents/skills/discover/SKILL.md /home/ccwu/.agents/skills/add-subfeature/SKILL.md /home/ccwu/.agents/skills/assess/SKILL.md /home/ccwu/.agents/sirius manage-subfeatures` | create slice |  | yes |
| fcr-metadata-summary | FCR-03 | Add compact consolidation summary carriers | Extend planning and subfeature metadata helpers so `.planning-meta.json` or `.subfeature-meta.json` can store one normalized consolidation summary without introducing a new sidecar file. | `skills/guide-planning/`, `skills/add-subfeature/` | primary | `pytest -q /home/ccwu/.agents/skills/guide-planning/tests/test_manage_planning.py /home/ccwu/.agents/skills/add-subfeature/tests/test_manage_subfeatures.py` | create slice | fcr-declaration-contract | yes |
| fcr-review-gate | FCR-02 | Enforce consolidation during planning review | Update `review-planning` guidance and any supporting planning validation behavior so overlapping planning capabilities without a reduction story become blocking findings. | `skills/review-planning/`, `skills/guide-planning/` | primary | `rg -n "consolidation|active-versus-historical|no valid consolidation target" /home/ccwu/.agents/skills/review-planning/SKILL.md && pytest -q /home/ccwu/.agents/skills/guide-planning/tests/test_manage_planning.py` | create slice | fcr-metadata-summary | yes |
| fcr-canonical-surface | FCR-04 | Document the canonical planning surface | Update planning entrypoint and methodology docs so maintainers can tell which planning path remains canonical after consolidation and which surfaces are now historical. | `/home/ccwu/.agents/skills/guide-planning/SKILL.md`, `/home/ccwu/skills/sirius-skills/README.md`, `/home/ccwu/skills/sirius-skills/SKILLS_METHODOLOGY.md` | primary | `rg -n "canonical|consolidation|simplif" /home/ccwu/.agents/skills/guide-planning/SKILL.md /home/ccwu/skills/sirius-skills/README.md /home/ccwu/skills/sirius-skills/SKILLS_METHODOLOGY.md` | create slice | fcr-review-gate | yes |
| fcr-history-consumers | FCR-03 | Teach maintenance skills to consume consolidation summaries | Extend trace, report, and archive inventory/output layers so they surface consolidation disposition, targets, and historical-artifact context from the shared metadata carriers. | `skills/trace-artifacts/`, `skills/report-artifacts/`, `skills/archive-artifacts/` | primary | `pytest -q /home/ccwu/.agents/skills/trace-artifacts/tests/test_trace_artifacts.py /home/ccwu/.agents/skills/report-artifacts/tests/test_report_artifacts.py /home/ccwu/.agents/skills/archive-artifacts/tests/test_archive_artifacts.py` | create slice | fcr-metadata-summary, fcr-review-gate | yes |

## 5. Dependency Notes

- Critical path: `fcr-declaration-contract` -> `fcr-metadata-summary` ->
  `fcr-review-gate` -> `fcr-canonical-surface` -> `fcr-history-consumers`.
- Explicit blockers: downstream maintenance consumers should wait until the
  metadata summary shape and review wording are stable enough to avoid contract
  churn.
- Parallel-safe slices: none recommended; these slices share one metadata and
  review contract and should stay in one lane to reduce drift.
- Increment ordering: `I1` -> `I2` -> `I3`.
- Lane owners and handoffs: single-agent planning work across planning authoring
  skills, planning metadata helpers, review guidance, and maintenance skills.
- Integration checkpoints: after `I1`, confirm authoring plus metadata
  persistence align; after `I2`, confirm review enforcement and canonical-path
  guidance use the same language; after `I3`, confirm maintenance reporting
  reads the same fields without inventing a second state model.

## 6. Bootstrap Order

1. `fcr-declaration-contract`
2. `fcr-metadata-summary`
3. `fcr-review-gate`
4. `fcr-canonical-surface`
5. `fcr-history-consumers`

## 7. Open Questions / Stop-and-Ask Items

- Should first-rollout enforcement apply only to planning-workflow capabilities,
  or to any feature whose change materially alters the planning surface?

## 8. Review Notes

- Review outcome: Ready for human approval, planning commit, and later `slice`
  bootstrap.
- Blocking findings: none. Discovery intent, design boundaries, and breakdown
  sequencing are coherent, and the planned slices stay scoped to the new
  consolidation contract rather than reusing the parent planning backlog.
- Handoff note: start with `fcr-declaration-contract`, then stabilize
  `fcr-metadata-summary` before implementing `fcr-review-gate`; keep
  `fcr-history-consumers` last so maintenance outputs inherit the settled
  metadata contract and review language.

## Notes

- This file is feature-scoped planning, not slice-scoped execution.
- Keep increment definitions here, not in execution-slice artifacts.
- Once planned slices are created, record the actual slice IDs in
  `slice-traceability.md`.
- Keep slice IDs stable enough that they can be cross-referenced from
  traceability notes and planning discussion.
