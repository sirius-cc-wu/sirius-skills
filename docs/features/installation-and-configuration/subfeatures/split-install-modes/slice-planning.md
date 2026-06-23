# Slice Planning

## 1. Planning Scope

- Feature: Split install modes
- Planning sources:
  - `discover.md`
  - `impact-analysis.md`
  - `system-design.md`
  - `user-stories.md`
  - parent feature `installation-and-configuration`
  - workflow-state precedent from `workflow-state-consistency`
- Execution system: repository-managed slices
- Execution mode: `single-agent`
- Notes: The rollout must preserve the current packaged path long enough for a
  compatibility migration while making source-linked local install the preferred
  development path.

## 2. Story Decisions

| Story ID | Story Size | Story Risk | Decision | Reason | Output Slice Count |
| --- | --- | --- | --- | --- | --- |
| SIM-01 | M | medium | split | Local install helper behavior and repo-facing adoption/docs need separate validation paths. | 2 |
| SIM-02 | L | medium | split | Make target split and packaged compatibility policy affect different operator surfaces. | 2 |
| SIM-03 | L | high | split | Runtime sync scoping and parity/reporting scoping touch different maintenance layers and failure modes. | 2 |
| SIM-04 | M | medium | keep | Migration guidance is one coherent documentation and compatibility packet. | 1 |

## 3. Increment Plan

| Increment | Goal / User-Visible Value | Included Story IDs | Planned Slice IDs | Demo / Verification Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | Local users can install the repo skills without packaging them | SIM-01 | sim-local-helper, sim-local-docs | A contributor can run a source-linked local install helper and see repo skills discovered through symlinks in the target skill home. | Simplest end-to-end path |
| I2 | Packaged install remains available but becomes explicit | SIM-02 | sim-packaged-targets, sim-packaged-compat | The repo exposes separate local and packaged install commands without silently dropping the old path. | Depends on I1 |
| I3 | Packaging-only runtime sync and parity are clear | SIM-03, SIM-04 | sim-runtime-scope, sim-parity-scope, sim-migration-guidance | Local maintenance flows stop assuming copied installs, while packaged/release validation still works. | Depends on I2 |

## 4. Execution Slice Backlog

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sim-local-helper | SIM-01 | Add source-linked local install helper | Create deterministic `install-local` and `uninstall-local` helpers that manage per-skill symlinks under the target skill home without touching unrelated skills. | `Makefile`, new install helper under `scripts/` | primary | Helper-focused tests plus a dry-run or fixture-based symlink refresh check | create slice |  | yes |
| sim-local-docs | SIM-01 | Document the source-linked local install path | Update README and install guidance so local CLI usage clearly points at the source-linked workflow. | `README.md`, `AGENTS.md`, install docs | primary | Review docs against helper behavior and one local install example | create slice | sim-local-helper | yes |
| sim-packaged-targets | SIM-02 | Split local and packaged install targets | Rename or alias Make targets so packaged install/uninstall becomes an explicit mode distinct from source-linked local install. | `Makefile` | primary | Review target behavior plus fixture or smoke coverage for target selection | create slice | sim-local-helper | yes |
| sim-packaged-compat | SIM-02 | Preserve packaged install compatibility during migration | Keep the existing packaged path working while documenting the compatibility phase and future default flip. | `Makefile`, packaging docs, helper scripts | primary | Validate packaged install helpers still call the required sync steps and managed packaging flow | create slice | sim-packaged-targets | yes |
| sim-runtime-scope | SIM-03 | Scope centralized packaged runtime to packaged installs | Remove centralized packaged runtime from the local install path and keep it only in packaged/export flows that still rely on copied runtime files. | `Makefile`, the centralized packaged runtime, maintenance-skill packaging assumptions | primary | Packaged regression tests for self-contained runtime imports plus local helper smoke checks | create slice | sim-packaged-compat | yes |
| sim-parity-scope | SIM-03 | Re-scope installed parity to packaged validation | Narrow parity and related maintenance output so repo-local usage no longer treats copied installs as the default runtime contract. | `lib/workflow_state/`, maintenance skill entrypoints, tests | primary | `pytest -q skills/audit-artifacts/tests/test_audit_artifacts.py skills/report-artifacts/tests/test_report_artifacts.py` plus explicit packaged-parity fixture coverage | create slice | sim-runtime-scope | yes |
| sim-migration-guidance | SIM-04 | Publish the migration path and operator guidance | Add durable guidance for moving from the current `make install` behavior to the split local-versus-packaged model. | `README.md`, feature docs, migration notes | primary | Cross-check docs against final Make targets and helper behavior | create slice | sim-parity-scope | yes |

## 5. Dependency Notes

- Critical path: local helper -> local docs -> install target split -> packaged compatibility -> runtime sync scoping -> parity scoping -> migration guidance.
- Explicit blockers: parity should not narrow until the repo has an explicit packaged boundary, and migration docs should not freeze before the final target names are chosen.
- Parallel-safe slices: none recommended in the first rollout because install naming, runtime sync, and parity semantics share the same boundary definition.
- Increment ordering: I1 -> I2 -> I3.
- Lane owners and handoffs: repo install helpers define the boundary first; maintenance/reporting skills then narrow their assumptions to that boundary; documentation closes the migration loop.
- Integration checkpoints:
  - confirm local install helper behavior after I1
  - confirm packaged compatibility after I2
  - confirm parity/reporting semantics and migration docs after I3

## 6. Bootstrap Order

1. sim-local-helper
2. sim-local-docs
3. sim-packaged-targets
4. sim-packaged-compat
5. sim-runtime-scope
6. sim-parity-scope
7. sim-migration-guidance

## 7. Open Questions / Stop-and-Ask Items

- Should `install` remain a compatibility alias to the packaged path for one release, or flip immediately to the source-linked local path once the helper lands?
- Do packaged parity findings remain in the default report output with a clearer label, or should they move behind an explicit packaged-validation mode?

## Notes

- This subfeature is planning-scoped. It defines the rollout for install-mode boundaries; execution slices still carry the implementation work.
- The parent `installation-and-configuration` feature remains the baseline. This subfeature narrows and supersedes only the install-path assumptions, not the broader configuration-surface model.

## Review Notes

- Planning reviewed: the packet uses generic `install-local` versus
  `install-packaged` naming, keeps `install` as a compatibility alias in the
  first rollout, and scopes the local install root to a helper or Makefile
  override instead of a new durable config surface.
