# Impact Analysis: Split Install Modes

## Target Subfeature

- Parent Feature: `installation-and-configuration`
- Subfeature ID: `split-install-modes`
- Subfeature Type: `superseding`
- Current Subfeature Status: `draft`

## Subfeature Summary

Prefer source-linked local installs over packaged per-skill local installs while keeping packaged distribution explicit.

## Parent Baseline Reviewed

- `docs/features/installation-and-configuration/discover.md`
- `docs/features/installation-and-configuration/system-design.md`
- `docs/features/installation-and-configuration/user-stories.md`
- `docs/features/installation-and-configuration/slice-planning.md`
- `docs/features/installation-and-configuration/slice-traceability.md`
- `Makefile`
- `docs/features/workflow-state-consistency/system-design.md`
- `slices/wsc-maintenance-adoption-adopt-shared-reconciliation-across-maintenance-skills/blueprint.md`

## Candidate Affected Story IDs

- `IC-01`
- `IC-04`

## Candidate Affected Increment IDs

- `I1`
- `I3`

## Candidate Affected Slice IDs

- `iac-install`
- `iac-plugin-convention`
- `iac-doc-alignment`

## Impact Notes

- This subfeature supersedes the original assumption that one managed install
  path should serve both local development and packaged standalone skill
  distribution.
- `iac-install` remains relevant, but its scope narrows to the packaged
  install/export boundary once a local source-linked path exists.
- `iac-plugin-convention` and `iac-doc-alignment` are affected because the
  repo will now document a native-discovery local path alongside the existing
  managed packaging flow.
- The workflow-state consistency feature is affected indirectly: its packaged
  runtime sync and parity assumptions remain valid only for explicit packaged
  installs and release-style validation.
- This subfeature should avoid broadening `.skills/` configuration. The install
  split belongs in repo-level helpers and docs, not new planning/execution
  config surfaces.
