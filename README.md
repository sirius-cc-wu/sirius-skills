# sirius-skills

`sirius-skills` is a generic-first skill collection for spec-driven development, planning, implementation support, and repository workflows, including an implemented two-step accelerator path built around `autoplan` and `ship`.

## Installing skills

Install the managed skills with the packaged workflow:

This installs all skills listed in `skills/*/SKILL.md` that are part of the managed packaged set, including `governance-update` and `research`.

```bash
make install
```

This uses `npx skills add` to register the managed skills after refreshing the
shared runtime and shared references that packaged installs depend on. The
managed packaged set is sourced from `MANAGED_SKILLS` in `Makefile`, so keep
that list in sync when adding or retiring packaged skills.

To remove the managed packaged install later:

```bash
make uninstall
```

The explicit packaged aliases are still available:

```bash
make install-packaged
make uninstall-packaged
```

`make install`, `make install-packaged`, `make uninstall`, and
`make uninstall-packaged` all use the managed packaged flow through
`npx skills`.

## Migration Notes

Current command map:

- default packaged use: `make install` / `make uninstall`
- explicit packaged aliases: `make install-packaged` / `make uninstall-packaged`
- current managed packaged list also includes `governance-update` and `research`

Current parity guidance:

- default local `report-artifacts` and `audit-artifacts` runs do not inspect
  installed packaged-skill parity
- use `--check-packaged-parity` when you explicitly want packaged install
  validation

Current install stance:

- use `make install` for normal repo refreshes before reloading skills
- use `make install-packaged` only when you want the explicit packaged alias
- treat `make uninstall` / `make uninstall-packaged` as equivalent packaged removals

To rerun the curated workflow consistency validation bundle used by CI and
workflow-state maintenance work:

```bash
make validate-workflow-state
```

The intended direction is:

- keep core workflow skills reusable across personal and company projects
- express project-specific conventions through local configuration
- isolate domain or company logic in project-local extensions instead of hardcoding it into the base skills

## Generic-first workflow

The managed repo-first skill set is grouped into:

- repo utilities: `skills/bootstrap/`, `skills/commit/`, `skills/create-pr/`, `skills/governance-update/`, `skills/simplify/`
- accelerator utilities: `skills/autoplan/`, `skills/learn/`, `skills/ship-slice/`, `skills/ship-worktree/`
- artifact maintenance: `skills/audit-artifacts/`, `skills/measure-artifacts/`, `skills/trace-artifacts/`, `skills/report-artifacts/`, `skills/repair-artifacts/`, `skills/archive-artifacts/`
- planning layer: `skills/guide-scope/`, `skills/guide-planning/`, `skills/propose/`, `skills/add-subfeature/`, `skills/migrate-subfeatures/`, `skills/assess/`, `skills/research/`, `skills/discover/`, `skills/design/`, `skills/ui-flow/`, `skills/breakdown/`, `skills/review-planning/`
- execution layer: `skills/slice/`, `skills/guide-execution/`, `skills/ship/`, `skills/ship-worktree/`, `skills/brief/`, `skills/blueprint/`, `skills/review-execution/`, `skills/reconcile-execution/`, `skills/close-slice/`

If a project has no extra configuration, these skills should still work with generic conventions.

For the operational guide to using the skills together, see `SKILLS_METHODOLOGY.md`.
For developer-facing examples of how to prompt the skills, see `PROMPT_GUIDE.md`.

When accelerator config is enabled, the intended happy path is: use `autoplan`
to drive planning to review-ready state, rerun `autoplan --approve` after
explicit human approval so it can hand off the planning commit checkpoint, then
use `ship --resume` once the approved planning artifacts are committed, or use
`ship-worktree` when execution should move into a dedicated git worktree tied to
that feature or subfeature.

Shared runtime state under `.skills/runtime/` is the cross-agent transient
handoff surface. Keep durable feature/subfeature truth in repo planning docs,
but use structured runtime files such as checkpoints, event logs, and
`request-handoff.json` for resumable request-level routing that should not
depend on one agent's private scratch plan.

## Shared skill references

Some guidance is kept as a canonical shared reference under `docs/shared/` and
then copied into the individual skill folders that need to package it.

Current shared-reference workflow:

- keep the canonical source in `docs/shared/`
- `make install-packaged` refreshes shared runtime and reference copies before packaging managed skills
- `make validate-workflow-state` reruns the curated workflow consistency pytest
  bundle for parity and transition guardrail regressions
- run `make sync-shared-references` after editing a canonical shared reference
- have each consuming skill point only at its local `references/` copy so the
  packaged skill remains self-contained

## Planning layer

For repositories that use repo-first planning, the recommended short-name planning skills are:

- `skills/guide-scope/`
- `skills/guide-planning/`
- `skills/propose/`
- `skills/add-subfeature/`
- `skills/migrate-subfeatures/`
- `skills/assess/`
- `skills/research/`
- `skills/discover/`
- `skills/design/`
- `skills/ui-flow/`
- `skills/breakdown/`
- `skills/review-planning/`

These skills sit **before** the execution-slice skills:

- planning layer: `guide-scope`, `guide-planning`, `propose`, `add-subfeature`, `migrate-subfeatures`, `assess`, `research`, `discover`, `design`, `ui-flow`, `breakdown`, `review-planning`
- execution layer: `slice`, `guide-execution`, `ship`, `ship-worktree`, `brief`, `blueprint`, `review-execution`, `reconcile-execution`, `close-slice`

Canonical planning surface:

- use `guide-scope` when repository scope is ambiguous
- use `guide-planning` as the canonical planning entrypoint once scope is resolved
- when a planning packet consolidates or narrows older workflow surface, keep one user-facing route and describe superseded surfaces as historical, migration-only, or archival context instead of implied parallel paths


Recommended boundary:

- keep goals, design, stories, decomposition, and increment plans in repo documents
- keep executable slices and dependency tracking in the repository planning artifacts
- stop planning at `review-planning` until a human explicitly approves the planning artifacts
- commit approved planning artifacts before bootstrapping execution with `slice`
- bootstrap one execution slice per executable slice
- use `guide-scope` as the optional scope-aware entrypoint when multi-scope routing or explicit scope choice matters
- let `guide-planning` own feature-planning readiness and routing inside the planning layer
- when consolidation simplifies the planning surface, update docs so one path stays canonical and older surfaces are clearly historical rather than silently co-active
- let `guide-execution` own slice readiness and state transitions within the execution layer
- let `ship` orchestrate one reviewed and committed feature or subfeature backlog without absorbing the owning execution steps

Feature-local planning defaults to `docs/features/<feature-slug>/` unless
the active planning scope's `.skills/planning.json` defines a different
`planning_dir`. Planning-layer helpers first look for the nearest
`.skills/planning.json` in ancestor directories, then fall back to the
repository root when inside a Git worktree.

Proposal staging defaults to `docs/proposals/<proposal-slug>/` unless
the active planning scope's `.skills/planning.json` defines a different
`proposal_dir`.

Default operator path (when accelerators are enabled):

1. `python3 skills/autoplan/scripts/autoplan.py <target> --execute-owner-chain --json`
2. review planning artifacts, then approve explicitly
3. `python3 skills/ship/scripts/ship.py <target> --approve --approval-note "<note>" --json`
4. `python3 skills/ship/scripts/ship.py <target> --resume --json`
5. or `python3 skills/ship-worktree/scripts/ship_worktree.py <target> --resume --json`
   when the implementation should live on a dedicated worktree branch
6. repeat `ship --resume` or `ship-worktree --resume` until `readiness.blocked_by`
   or `readiness.preflight` reports a manual boundary
7. once the target is `implemented` and all planned slices are closed, run
   `python3 skills/ship/scripts/ship.py <target> --finalize --json`, or keep
   the worktree wrapper in control with
   `python3 skills/ship-worktree/scripts/ship_worktree.py <target> --finalize --create-pr --json`

`guide-scope`, `guide-planning`, and `guide-execution` remain valid but are
best treated as fallback/manual control paths for ambiguity resolution,
recovery, or fine-grained intervention.

Manual repo workflow (explicit control path):

1. In multi-scope repositories, `guide-scope` can resolve the active scope, stop on ambiguity, and hand off to `guide-planning`, `guide-execution`, or `bootstrap` without changing their ownership rules. In single-scope repositories it remains optional.
2. `guide-planning` resolves the feature planning folder, validates planning readiness, and routes to the right planning skill.
3. If the request is still speculative and should not become a canonical feature yet, `propose` creates a proposal folder under `docs/proposals/<proposal-slug>/`.
4. If the request adds or reshapes a durable child capability under an existing feature, `add-subfeature` creates a subfeature folder under `docs/features/<feature>/subfeatures/<subfeature-id>/`.
5. `assess` inspects the parent feature and writes subfeature-scoped `impact-analysis.md` before subfeature-local design starts.
6. When checked-in reference comparison materially affects planning shape, `research` writes `reference-research.md` and, when a derived wiki root already exists, can also update one focused wiki page plus wiki `index.md` and `log.md`.
7. `discover` creates problem framing and initial story candidates.
8. `design` turns that into architecture, interfaces, and risks.
9. `ui-flow` adds optional UX or screen-flow artifacts.
10. `breakdown` turns repo stories into directly executable work items and groups those slices into small demonstrable increments.
11. `review-planning` reviews planning artifacts and slice definitions, then stops for explicit human approval.
12. After approval, commit the planning artifacts so the reviewed plan is durable before execution begins. For reviewed subfeatures, also record that approval in `.subfeature-meta.json` so the approval boundary stays durable in the single source of truth.
13. `slice` validates approved, committed execution-ready input, bootstraps a slice-scoped execution slice, and hands off to `guide-execution`.
14. `guide-execution` routes slice-scoped execution through `brief` to capture a lean slice contract covering intent, expected behavior, acceptance, and assumptions, then through `blueprint` to produce the final technical execution artifact. When `.skills/execution.json` enables `auto_start_implementation`, that handoff continues directly into implementation after the blueprint is marked ready.
15. `ship` is the optional batch entrypoint when a reviewed and committed feature or subfeature backlog should be worked one planned slice at a time. It respects increment order first, then slice dependencies within the current increment, resumes or bootstraps one mapped slice, reports the next concrete execution owner for that slice, and stops at blockers or commit checkpoints. Its JSON output also includes a machine-readable `handoff_payload` for the active slice so future accelerators can consume the same routing contract without changing `ship` ownership.
16. `ship-worktree` is the optional wrapper entrypoint when that same reviewed and committed backlog should execute in a dedicated git worktree branch. It owns worktree lifecycle and PR handoff, but still delegates slice backlog execution to `ship`.
17. `review-execution` checks implementation and validation outcomes against the slice-scoped execution artifacts before closure.
18. `close-slice` closes completed execution slices, records durable closure metadata, and invokes shared owner-completion reconciliation for linked planning owners.
19. `reconcile-execution` records durable design-versus-execution alignment in `system-design.md`, and `ship --finalize` can first run the same shared owner-completion reconciliation before routing `archive-artifacts` to summarize and archive the closed slices.

For repositories that still contain legacy `changes/` packets from the old
workflow, `migrate-subfeatures` can scan and convert those legacy planning
folders into the current durable `subfeatures/` layout before normal planning
work continues.

In the repo-native flow, `guide-planning` owns feature-planning readiness and routing, `breakdown` owns repo-story decomposition, `review-planning` owns planning readiness review, `slice` owns execution bootstrap from approved committed planning artifacts, `brief` owns the slice-scoped `brief.md` as a lean contract for intent, acceptance, and assumptions, `blueprint` owns the final slice-scoped technical execution plan and validation checklist, and `review-execution` owns the final implementation-versus-brief review before closure.

Execution follows the same pattern: `guide-execution` owns routing, readiness, and registry state, while `brief`, `blueprint`, `review-execution`, `reconcile-execution`, and `close-slice` own execution-side artifacts and closure/reconciliation metadata. With `auto_start_implementation`, `guide-execution` can promote a slice from `blueprint_ready` to `execution_ready` as the signal to begin coding immediately.

`ship` sits above that single-slice flow as an optional orchestrator. It resolves one reviewed and committed feature or subfeature backlog, resumes or bootstraps one mapped execution slice at a time, and hands that slice to the next concrete owner such as `brief`, `blueprint`, repository implementation, `guide-execution`, `review-execution`, `reconcile-execution`, `close-slice`, or `commit`. It does not replace those owners. When the target is completed and `implemented`, `ship --finalize` can require reconciliation and then route the terminal archive step through `archive-artifacts`.

`ship-worktree` sits one layer above that orchestrator when the same target
should execute in a dedicated git worktree. It keeps the original branch as the
PR base, reuses a target-named worktree branch and path, runs `ship` inside that
checkout, and can hand the finished worktree branch off to PR creation without
moving backlog ownership out of `ship`.

By default, new execution slices are created under `slices/` unless `.skills/execution.json` overrides the location.

When UML diagrams are useful, use **PlantUML**:

- `design` should produce feature-scoped system-design diagrams in `system-design.md`
- `blueprint` should produce slice-scoped detailed-design diagrams in `blueprint.md`

By default, `design` embeds PlantUML directly in `system-design.md`. If `.skills/planning.json` sets `"design_diagram_mode": "linked_svg"`, `design` should instead write `.puml` and `.svg` files under `<feature_path>/figures/` and link the SVGs from `system-design.md`. In that mode, keep diagrams on an explicit white background by setting `skinparam backgroundColor white` in PlantUML and ensuring the rendered SVG includes a white canvas rect.

## Execution slice source of truth

The `guide-execution` workflow now keeps three complementary artifacts in sync:

- `<slice_dir>/README.md` for a human-readable registry
- `<slice_dir>/registry.json` for machine-readable registry/state
- `<slice_path>/.slice-meta.json` for per-slice lifecycle metadata such as `created_at`, `updated_at`, `closed_at`, and explicit relation metadata

The machine-readable metadata can also store explicit cross-slice relations such as `supersedes`, `invalidates`, `narrows`, and `replaces_partially`, with reciprocal backlinks and optional soft selectors for story titles, requirement IDs, or freeform selectors.

Closed slices are retained non-destructively. `sirius-skills` does not merge or delete the original `brief.md`/`blueprint.md` artifacts when a slice closes; instead it records closure durably in the slice registry and metadata.

Per-slice closure is non-destructive. `sirius-skills` keeps closed slices and durable subfeature planning folders in place by default; any later cleanup or archival should happen through explicit maintenance tooling instead of an automatic feature-finalization step.

To keep relation metadata healthy over time, `skills/guide-execution/scripts/manage_execution.py` also provides `audit-relations`, which checks for missing targets and missing reciprocal links.

## Example prompts

Examples of repo-native prompts that fit the current workflow:

- "Audit workflow artifacts across proposals, features, subfeatures, and slices."
- "Measure durable implementation metrics for a completed feature or subfeature."
- "Trace workflow lineage across proposals, features, subfeatures, planned slices, and execution slices."
- "Report workflow state across proposals, features, subfeatures, and slices."
- "Preview and repair workflow registry drift across proposals, features, subfeatures, and slices."
- "Report archive candidates and archive one closed execution slice safely."
- "Use `guide-planning` to decide the next step for `planning-workflow`."
- "Use `research` for `docs/features/planning-workflow/subfeatures/reference-research-synthesis/` and record the chosen borrowing path from checked-in references."
- "Create a proposal for a new review automation feature, but keep it out of canonical planning for now."
- "Add a durable subfeature `replace-legacy-flow` under `checkout` and frame its discovery docs."
- "Assess the impact of subfeature `replace-legacy-flow` under `checkout`."
- "Design the subfeature at `docs/features/checkout/subfeatures/replace-legacy-flow/`."
- "Break down `docs/features/checkout/subfeatures/replace-legacy-flow/` into execution-ready slices."
- "Review planning for the `replace-legacy-flow` subfeature before slice bootstrap."
- "Use `ship` for `docs/features/checkout/subfeatures/replace-legacy-flow/` and continue until a blocker or per-slice commit checkpoint stops the run."
- "Finalize subfeature `replace-legacy-flow` under `checkout` after its planned slices are closed."
- "Use `governance-update` to add a repo rule that completed features must be reconciled against `system-design.md` before archive."
- "Scan the repo for legacy `changes/` packets that still need migration."
- "Dry-run migration of old `changes/` packets under `checkout` into durable subfeatures."

For a broader developer prompt cookbook, including prompt-first design and reverse-engineered current-state design, see `PROMPT_GUIDE.md`.

## Optional project configuration

Use `skills/bootstrap/` when you want an agent to bootstrap the repo's
supported `.skills/planning.json`, `.skills/execution.json`, and
`.skills/conventions.json` files. The skill supports a generic `default` mode,
a Jira-oriented `jira` mode, and an `ask` mode that makes the agent stop and
ask the user which preset to apply before writing config. When wiki scaffolding
is requested, bootstrap also creates the derived wiki skeleton and patches an
existing target-repo `AGENTS.md` with a small architecture-wiki guidance block.

Use `skills/governance-update/` when the real fix is a durable repo rule rather
than another one-off artifact edit. A good example is repeated
design-versus-execution drift at feature closeout: governance should define the
`reconcile-execution` / `ship --finalize` / `archive-artifacts` owner boundary,
while `bootstrap` should stay limited to initial repo setup and should not
invent that policy by default.

Projects can add `.skills/planning.json` in the repository root to configure planning-layer layout.

Example:

```json
{
  "planning_dir": "planning/features",
  "proposal_dir": "planning/proposals",
  "design_diagram_mode": "embedded"
}
```

Accelerator example:

```json
{
  "planning_dir": "docs/features",
  "proposal_dir": "docs/proposals",
  "design_diagram_mode": "embedded",
  "accelerators": {
    "autoplan": {
      "execute_owner_chain": true,
      "stop_on_owner": ["review-planning"]
    }
  }
}
```

Projects can add `.skills/conventions.json` in the repository root to describe their local conventions.

Generic default slice naming now assumes scope-prefixed planned slice IDs:

- default format: `{scope_prefix}-{capability_slug}`
- feature-scoped planning uses a short lowercase alias derived from the feature slug
- subfeature-scoped planning uses a short lowercase alias derived from the subfeature ID
- avoid bare `slice-*` IDs unless the project explicitly overrides that convention

Projects can add `.skills/execution.json` in the repository root to configure execution-slice layout for `guide-execution` and `slice` bootstrap.

Example:

```json
{
  "slice_dir": "slices",
  "preferred_workflow": "TDD",
  "auto_start_implementation": true
}
```

Accelerator example:

```json
{
  "slice_dir": "slices",
  "preferred_workflow": "TDD",
  "auto_start_implementation": true,
  "accelerators": {
    "ship": {
      "delegate_to_ship_slice": true,
      "preflight": {
        "mode": "local_only"
      }
    },
    "ship_slice": {
      "execute_owner_chain": true,
      "stop_on_owner": ["review-execution"],
      "continuation_policy": {
        "review_boundary": "stop",
        "commit_checkpoint": "stop"
      },
      "auto_format": false,
      "auto_close": false,
      "auto_commit": false
    }
  }
}
```

Conventions example:

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

Current configuration usage:

- `skills/guide-scope/SKILL.md` documents the optional scope-aware entrypoint for routing multi-scope work into planning, execution, or bootstrap
- planning-layer skills resolve `.skills/planning.json` from the nearest scope, then fall back to the repository root when inside a Git worktree; `planning_dir` still defaults to `docs/features/<feature-slug>/`
- `skills/autoplan/SKILL.md` documents `.skills/planning.json` fields under `accelerators.autoplan`, including `execute_owner_chain` and `stop_on_owner`
- `skills/propose/scripts/manage_proposals.py` reads the active scope's `.skills/planning.json` field `proposal_dir` when present and otherwise defaults to `docs/proposals/<proposal-slug>/`
- `skills/guide-planning/scripts/manage_planning.py` reads the active scope's `.skills/planning.json` for `planning_dir`, maintains feature readiness metadata under `<feature_path>/.planning-meta.json`, and derives subfeature planning views from `<subfeature_path>/.subfeature-meta.json`, including explicit approval and ready-slice handoff for reviewed subfeatures
- `skills/design/SKILL.md` reads `.skills/planning.json` field `design_diagram_mode`; `embedded` keeps fenced PlantUML in `system-design.md`, while `linked_svg` writes `.puml` and `.svg` files under `<feature_path>/figures/`, links the SVGs from `system-design.md`, and keeps those SVGs on an explicit white canvas
- `skills/breakdown/scripts/scaffold_breakdown.py` uses `.skills/planning.json` field `planning_dir` during scaffolding when the file is present
- `skills/slice/scripts/bootstrap_slice.py` resolves the nearest execution scope, reuses inherited scoped execution config when present, and only initializes `.skills/execution.json` locally when no execution config exists in the scope chain
- `skills/guide-execution/scripts/manage_execution.py` resolves `.skills/execution.json`, `.skills/conventions.json`, and `slice_dir` from the active execution scope so nested scopes keep local slice registries and folders
- when `auto_start_implementation` is `true`, `skills/guide-execution/scripts/manage_execution.py set-status <slice> blueprint_ready` auto-advances the slice into `execution_ready`
- `skills/ship/SKILL.md` documents `.skills/execution.json` fields under `accelerators.ship`, including `delegate_to_ship_slice` and `preflight.mode`
- `skills/ship-slice/SKILL.md` documents `.skills/execution.json` fields under `accelerators.ship_slice`, including `execute_owner_chain`, `stop_on_owner`, `continuation_policy`, `auto_format`, `format_command`, `auto_close`, and `auto_commit`
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
