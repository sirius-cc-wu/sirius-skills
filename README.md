# sirius-skills

`sirius-skills` is a generic-first skill collection for spec-driven development, planning, implementation support, and repository workflows.

## Installing skills

Use the repository `Makefile` to register the managed skill set:

```bash
make install
```

To remove the same managed skill set later:

```bash
make uninstall
```

The intended direction is:

- keep core workflow skills reusable across personal and company projects
- express project-specific conventions through local configuration
- isolate domain or company logic in project-local extensions instead of hardcoding it into the base skills

## Generic-first workflow

The managed repo-first skill set is grouped into:

- repo utilities: `skills/bootstrap/`, `skills/commit/`, `skills/create-pr/`, `skills/simplify/`
- planning layer: `skills/guide-planning/`, `skills/propose/`, `skills/evolve-feature/`, `skills/assess/`, `skills/reconcile-feature/`, `skills/discover/`, `skills/design/`, `skills/ui-flow/`, `skills/breakdown/`, `skills/review-planning/`, `skills/slice/`
- execution layer: `skills/guide-execution/`, `skills/brief/`, `skills/blueprint/`, `skills/review-execution/`, `skills/close-slice/`

If a project has no extra configuration, these skills should still work with generic conventions.

For the operational guide to using the skills together, see `SKILLS_METHODOLOGY.md`.

## Planning layer

For repositories that use repo-first planning, the recommended short-name planning skills are:

- `skills/guide-planning/`
- `skills/propose/`
- `skills/evolve-feature/`
- `skills/assess/`
- `skills/reconcile-feature/`
- `skills/discover/`
- `skills/design/`
- `skills/ui-flow/`
- `skills/breakdown/`
- `skills/review-planning/`
- `skills/slice/`

These skills sit **before** the execution-slice skills:

- planning layer: `guide-planning`, `propose`, `evolve-feature`, `assess`, `reconcile-feature`, `discover`, `design`, `ui-flow`, `breakdown`, `review-planning`, `slice`
- execution layer: `guide-execution`, `brief`, `blueprint`, `review-execution`, `close-slice`


Recommended boundary:

- keep goals, design, stories, decomposition, and increment plans in repo documents
- keep executable slices and dependency tracking in the repository planning artifacts
- bootstrap one execution slice per executable slice
- let `guide-planning` own feature-planning readiness and routing inside the planning layer
- let `guide-execution` own slice readiness and state transitions within the execution layer

Feature-local planning defaults to `docs/features/<feature-slug>/` unless
`.skills/planning.json` defines a different `planning_dir`.

Proposal staging defaults to `docs/proposals/<proposal-slug>/` unless
`.skills/planning.json` defines a different `proposal_dir`.

Preferred repo workflow:

1. `guide-planning` resolves the feature planning folder, validates planning readiness, and routes to the right planning skill.
2. If the request is still speculative and should not become a canonical feature yet, `propose` creates a proposal folder under `docs/proposals/<proposal-slug>/`.
3. If the request changes an existing feature rather than starting a new one, `evolve-feature` creates a feature-local change packet under `docs/features/<feature>/changes/<change-id>/`.
4. `assess` inspects the canonical feature and writes change-scoped `impact-analysis.md` before change-local design starts.
5. `discover` creates problem framing and initial story candidates.
6. `design` turns that into architecture, interfaces, and risks.
7. `ui-flow` adds optional UX or screen-flow artifacts.
8. `breakdown` turns repo stories into directly executable work items and groups those slices into small demonstrable increments.
9. `review-planning` reviews planning artifacts and slice definitions before execution slice bootstrap.
10. `slice` validates execution-ready input, bootstraps a slice-scoped execution slice, and hands off to `guide-execution`.
11. `guide-execution` routes slice-scoped execution through `brief` to capture slice intent and acceptance, then through `blueprint` to produce the final execution artifact.
12. `review-execution` checks implementation and validation outcomes against the slice-scoped execution artifacts before closure.
13. `close-slice` closes completed execution slices and can optionally publish a project-local summary.
14. `reconcile-feature` folds an approved feature change packet back into the canonical planning docs, writes `reconciliation.md`, publishes retained change history, and closes the change packet.

In the repo-native flow, `guide-planning` owns feature-planning readiness and routing, `breakdown` owns repo-story decomposition, `review-planning` owns planning readiness review, `brief` owns the slice-scoped `brief.md`, `blueprint` owns the final slice-scoped execution plan and validation checklist, and `review-execution` owns the final implementation-versus-brief review before closure.

Execution follows the same pattern: `guide-execution` owns routing, readiness, and registry state, while `brief`, `blueprint`, `review-execution`, and `close-slice` own their artifacts and outputs.

By default, new execution slices are created under `slices/` unless `.skills/execution.json` overrides the location.

When UML diagrams are useful, use **PlantUML**:

- `design` should produce feature-scoped system-design diagrams in `system-design.md`
- `blueprint` should produce slice-scoped detailed-design diagrams in `blueprint.md`

## Execution slice source of truth

The `guide-execution` workflow now keeps three complementary artifacts in sync:

- `<slice_dir>/README.md` for a human-readable registry
- `<slice_dir>/registry.json` for machine-readable registry/state
- `<slice_path>/.slice-meta.json` for per-slice lifecycle metadata such as `created_at`, `updated_at`, and `closed_at`

The machine-readable metadata can also store explicit cross-slice relations such as `supersedes`, `invalidates`, `narrows`, and `replaces_partially`, with reciprocal backlinks and optional soft selectors for story titles, requirement IDs, or freeform selectors.

Closed slices are retained in place. `sirius-skills` does not merge or delete the original `brief.md`/`blueprint.md` artifacts when a slice closes; instead it records closure durably and leaves project-specific publishing or rollup logic to local extensions.

If a project wants a canonical rollup document, `skills/close-slice/` can optionally publish closed-slice summaries into a project-local history file such as `docs/slice-history.md`, driven by explicit command arguments or `.skills/plugins/spec-publish.json`.

The published entry can include:

- backlinks to the retained `brief.md` / `blueprint.md` artifacts, plus any legacy `slices.md`
- explicit relation summaries such as which older slice or story scope is superseded
- source issue links when `.slice-meta.json` and `.skills/conventions.json` provide them
- implementation verification highlights inferred from `blueprint.md` and any legacy `slices.md`

For a starting point, see `skills/close-slice/assets/spec-publish.example.json`.

To keep relation metadata healthy over time, `skills/guide-execution/scripts/manage_execution.py` also provides `audit-relations`, which checks for missing targets and missing reciprocal links.
## Optional project configuration

Use `skills/bootstrap/` when you want an agent to bootstrap the repo's
supported `.skills/planning.json`, `.skills/execution.json`, and
`.skills/conventions.json` files. The skill supports a generic `default` mode,
a Jira-oriented `jira` mode, and an `ask` mode that makes the agent stop and
ask the user which preset to apply before writing config.

Projects can add `.skills/planning.json` in the repository root to configure planning-layer layout.

Example:

```json
{
  "planning_dir": "planning/features",
  "proposal_dir": "planning/proposals"
}
```

Projects can add `.skills/conventions.json` in the repository root to describe their local conventions.

Projects can add `.skills/execution.json` in the repository root to configure execution-slice layout for `guide-execution` and `slice` bootstrap.

Example:

```json
{
  "slice_dir": "slices",
  "preferred_workflow": "TDD"
}
```

Example:

```json
{
  "issue_sliceer": "jira",
  "id_pattern": "^[A-Z][A-Z0-9]*-[0-9]+$",
  "branch_extract_pattern": "^([A-Z][A-Z0-9]*-[0-9]+)-(.+)$",
  "commit_format": "{ID}: {summary}",
  "pr_title_format": "{ID}: {summary}",
  "issue_url_template": "https://jira.example.com/browse/{ID}"
}
```

Current Phase 1 usage:

- planning-layer skills resolve `<feature_path>` from `.skills/planning.json` field `planning_dir` when the file is present, otherwise they default to `docs/features/<feature-slug>/`
- `skills/propose/scripts/manage_proposals.py` reads `.skills/planning.json` field `proposal_dir` when present and otherwise defaults to `docs/proposals/<proposal-slug>/`
- `skills/guide-planning/scripts/manage_planning.py` reads `.skills/planning.json` for `planning_dir` and maintains planning readiness metadata under `<feature_path>/.planning-meta.json`
- `skills/breakdown/scripts/scaffold_breakdown.py` uses `.skills/planning.json` field `planning_dir` during scaffolding when the file is present
- `skills/slice/scripts/bootstrap_slice.py` can initialize `.skills/execution.json` with the generic `slices/` default (or an explicit `--slice-dir`) before delegating to execution-layer tooling
- `skills/guide-execution/scripts/manage_execution.py` reads `.skills/execution.json` for `slice_dir` and `preferred_workflow`
- `skills/guide-execution/scripts/manage_execution.py` uses `branch_extract_pattern` during `add` when the file is present
- `skills/commit/SKILL.md` documents how `commit_format` can override the generic default
- `skills/create-pr/SKILL.md` documents how `pr_title_format`, `branch_extract_pattern`, and `id_pattern` can define stricter PR conventions

If the file is absent, the generic defaults remain in effect.

## Project-local extensions

Use `.skills/plugins/` as the project-local area for company or domain add-ons.

Important: this is currently a **convention**, not an automatically loaded plugin system. Nothing in `sirius-skills` scans or executes `.skills/plugins/` by itself today.

Current usage model:

- put project-local helper configs or scripts in `.skills/plugins/`
- have a specific skill or script read them explicitly
- document that behavior in the relevant skill

Today, the project-local files that are actually consumed automatically are `.skills/planning.json`, `.skills/conventions.json`, and `.skills/execution.json`.

Examples:

- `.skills/plugins/jira-validator.json`
- `.skills/plugins/jira-backlog-analyzer.py`
- `.skills/plugins/iso14229-reviewer.py`

Example of how to use the convention today:

- a future `create-pr` implementation could read `.skills/plugins/jira-validator.json`
- a future `review-pr` or `review-bsp-uds-code` implementation could import `.skills/plugins/iso14229-reviewer.py`
- a future planning skill could read `.skills/plugins/jira-backlog-analyzer.py`

Core skills should only rely on these extensions when a project explicitly opts in. This keeps `sirius-skills` reusable while still allowing company overlays.
