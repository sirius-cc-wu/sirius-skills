# Slice Planning

## 1. Planning Scope

- Feature: Installation and configuration
- Planning sources:
  - `Makefile`
  - `README.md`
  - `AGENTS.md`
  - `skills/guide-planning/scripts/manage_planning.py`
  - `skills/guide-execution/scripts/manage_execution.py`
  - `skills/commit/SKILL.md`
  - `skills/create-pr/SKILL.md`
  - `skills/close-slice/SKILL.md`
- Execution system: repository-managed slices (reverse-engineered repo planning only)
- Execution mode: `single-agent`
- Notes: This feature captures how the repo is adopted and configured rather than how a single execution slice runs.

## 2. Story Decisions

| Story ID | Story Size | Decision | Reason | Output Slice Count |
| --- | --- | --- | --- | --- |
| IC-01 | M | keep | Managed install/uninstall is a coherent repository integration slice. | 1 |
| IC-02 | M | split | Planning and execution config readers are separate concerns. | 2 |
| IC-03 | M | keep | Conventions config is a distinct cross-cutting config surface. | 1 |
| IC-04 | L | split | Plugin conventions and documentation alignment require separate slices. | 2 |

## 3. Increment Plan

| Increment | Goal / User-Visible Value | Included Story IDs | Planned Slice IDs | Demo / Verification Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | Managed repo setup works out of the box | IC-01, IC-02 | IC-01-install, IC-02-planning-config, IC-02-execution-config | A project can install the shared skills and resolve planning/execution layout from config. | Simplest repository adoption path |
| I2 | Project conventions stay generic-first | IC-03 | IC-03-conventions-config | Commit, PR, and execution naming behavior can be configured without hardcoding project-specific workflow logic. | Depends on I1 |
| I3 | Project-local extension boundaries are explicit | IC-04 | IC-04-plugin-convention, IC-04-doc-alignment | A maintainer understands where optional extension scripts/configs live and that core skills read them explicitly. | Depends on I2 |

## 4. Execution Slice Backlog

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IC-01-install | IC-01 | Manage installed skill set | Keep `make install` / `make uninstall` aligned with the managed skills list. | `Makefile` | primary | Review install/uninstall targets and managed skill list | create slice |  | yes |
| IC-02-planning-config | IC-02 | Resolve planning layout from config | Keep `planning.json` semantics explicit and stable. | `skills/guide-planning/scripts/manage_planning.py`, docs | primary | `pytest -q skills/guide-planning/tests/test_manage_planning.py` | create slice | IC-01-install | yes |
| IC-02-execution-config | IC-02 | Resolve execution layout from config | Keep `execution.json` semantics explicit and stable. | `skills/guide-execution/scripts/manage_execution.py`, docs | primary | `pytest -q skills/guide-execution/tests/test_manage_execution.py` | create slice | IC-02-planning-config | yes |
| IC-03-conventions-config | IC-03 | Apply repo naming and ID conventions | Keep `conventions.json` as the cross-cutting conventions surface. | `skills/guide-execution/scripts/manage_execution.py`, `skills/commit/SKILL.md`, `skills/create-pr/SKILL.md` | primary | Review config consumers and tests | create slice | IC-02-execution-config | yes |
| IC-04-plugin-convention | IC-04 | Document project-local plugin behavior | Keep `.skills/plugins/` explicit and opt-in rather than auto-loaded. | `README.md`, `AGENTS.md`, consumer skills | primary | Review docs for explicit plugin loading language | create slice | IC-03-conventions-config | yes |
| IC-04-doc-alignment | IC-04 | Keep docs aligned with config behavior | Update docs and examples whenever config semantics shift. | `README.md`, `AGENTS.md`, skill docs | primary | Cross-check docs with code readers | create slice | IC-04-plugin-convention | yes |

## 5. Dependency Notes

- Critical path: managed install -> planning config -> execution config -> conventions config -> plugin/documentation alignment.
- Explicit blockers: downstream config docs must reflect actual code readers.
- Parallel-safe slices: none recommended because config naming and docs are cross-cutting.
- Increment ordering: I1 -> I2 -> I3.
- Lane owners and handoffs: repo maintainer updates Makefile and configs; consuming skills enforce the behavior.
- Integration checkpoints: repo tests after config-reader changes and doc review after naming changes.

## 6. Bootstrap Order

1. IC-01-install
2. IC-02-planning-config, IC-02-execution-config
3. IC-03-conventions-config
4. IC-04-plugin-convention, IC-04-doc-alignment

## 7. Open Questions / Stop-and-Ask Items

- Should the repo eventually offer a single documented bootstrap command for initializing all three config files?
- Should plugin config discovery remain manual forever, or should some limited explicit loader be introduced later?
## 8. Review Notes

- Review outcome: Ready for `slice` after selecting the first configuration or installation slice to execute.
- Blocking findings: none. The install path, config-surface split, and plugin-boundary guidance are coherent across the planning artifacts.
- Handoff note: begin with `IC-01-install` and keep later config/documentation slices aligned with the documented ownership boundaries.
- Follow-up improvements: if plugin conventions expand, add a more explicit repository example showing how a consumer skill opts into project-local extensions.
