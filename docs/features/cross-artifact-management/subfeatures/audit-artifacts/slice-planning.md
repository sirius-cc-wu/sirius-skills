# Slice Planning

## 1. Planning Scope

- Feature: Audit artifacts
- Planning sources:
  - `discover.md`
  - `impact-analysis.md`
  - `system-design.md`
  - parent `docs/features/cross-artifact-management/user-stories.md`
- Execution system: repository-managed code changes and tests
- Execution mode: `single-agent`
- Notes: The first slice should establish a reusable artifact inventory model so
  later trace/report/repair/archive capabilities can extend it without inventing
  a second graph format.

## 2. Story Decisions

| Story ID | Story Size | Story Risk | Decision | Reason | Output Slice Count |
| --- | --- | --- | --- | --- | --- |
| CAM-01 | L | medium | keep | Delegated validation, registry drift checks, and read-only reporting form one cohesive capability with one primary validation path. | 1 |

## 3. Increment Plan

| Increment | Goal / User-Visible Value | Included Story IDs | Planned Slice IDs | Demo / Verification Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | Audit the repo's durable workflow packets in one command | CAM-01 | aat-cross-artifact-audit | A maintainer can run one audit command and see missing files, registry drift, broken links, and slice relation issues in one report. | Simplest usable path |

## 4. Execution Slice Backlog

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aat-cross-artifact-audit | CAM-01 | Build the cross-artifact audit command | Add a reusable artifact inventory helper, delegate owner-script validation, audit registry/link drift, and ship the `audit-artifacts` skill with tests and docs. | `skills/audit-artifacts/`, shared artifact inventory helper, owner-script integration points | primary | `pytest -q skills/audit-artifacts/tests/test_audit_artifacts.py` and `pytest -q` | create slice |  | yes |

## 5. Dependency Notes

- Critical path: inventory helper -> delegated validators -> cross-artifact
  checks -> skill/docs/tests.
- Explicit blockers: none.
- Parallel-safe slices: none recommended; the first audit surface depends on one
  consistent shared finding model.
- Increment ordering: I1 only.
- Lane owners and handoffs: `audit-artifacts` owns the user-facing audit
  command; existing owner scripts keep artifact-specific validation rules.
- Integration checkpoints: verify human-readable output and JSON output from the
  same findings collection.

## 6. Bootstrap Order

1. aat-cross-artifact-audit

## 7. Review Notes

- Review outcome: Ready for `slice` with `aat-cross-artifact-audit`.
- Blocking findings: none. The planning packet keeps artifact-specific
  validation in the existing owner scripts and limits new work to the shared
  inventory plus cross-artifact checks.
- Handoff note: keep the audit command read-only and reuse
  `manage_execution.py audit-relations` rather than re-implementing slice
  relation semantics.

## 8. Notes

- This breakdown stays subfeature-scoped; it does not replace the parent
  feature's broader cross-artifact roadmap.
- The shared artifact inventory model created here should remain generic enough
  for the later `trace-artifacts`, `report-artifacts`, `repair-artifacts`, and
  `archive-artifacts` subfeatures.
