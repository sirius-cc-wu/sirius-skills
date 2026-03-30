# Discover: Workflow Capability Upgrades

## Problem

`sirius-skills` already has a strong planning and execution-slice model, but it
is thinner than `spec-kit` and `OpenSpec` in a few planning-adjacent areas that
would improve day-to-day usability without turning the repository into a CLI
product or duplicating coding-agent implementation capabilities.

The main gaps are not in execution orchestration. They are in upstream planning
quality, project guidance, customization, and artifact lifecycle support:

- no first-class project-principles or constitution artifact
- no dedicated clarification step for resolving ambiguous scope before design
- limited project-level workflow customization beyond a few config files
- limited planning-artifact verification and post-planning sync patterns

The goal is to strengthen the planning layer while preserving the repository's
skill-first, generic-first, and agent-neutral direction.

## Goals

- Add planning-layer capabilities that improve artifact quality before slice
  bootstrap.
- Preserve the current decision to stay skill-based rather than shipping a CLI.
- Preserve the decision not to add an `implement` skill because coding agents
  already cover implementation execution.
- Make project-local customization more explicit and durable without hardcoding
  company behavior into core skills.
- Improve planning artifact verification, reconciliation, and closure patterns.

## Non-Goals

- Introduce a standalone CLI comparable to `specify` or `openspec`.
- Add a new implementation-execution skill that overlaps with coding-agent
  built-ins.
- Replace the current slice-scoped execution workflow with change-folder or
  proposal-folder mechanics from another project.
- Turn `.skills/plugins/` into an automatic runtime plugin loader unless that is
  explicitly designed as a future capability.

## Primary Actors

- Repository maintainer evolving the core skill set.
- Project lead who wants stronger repo-native planning guidance.
- Planner who needs to resolve ambiguity before design and breakdown.
- Reviewer who needs clearer validation of planning artifacts before execution.
- Team adopting `sirius-skills` in a project with local rules and conventions.

## Constraints

- The solution must remain skill-first and repository-centric.
- Core workflow skills must keep working with generic defaults.
- Existing planning layout under `docs/features/<feature-slug>/` should remain
  valid unless explicitly configured otherwise.
- New capabilities should align with the current two-layer boundary:
  planning-layer artifacts stay feature-scoped, execution artifacts stay
  slice-scoped.
- Any customization model should remain opt-in and understandable from repo
  artifacts, not hidden chat state.

## Desired Outcomes

- Teams can define durable project principles that shape planning and review.
- Ambiguous requests can be clarified in a dedicated artifact before design.
- Projects can express richer planning behavior through configuration, schema,
  or rule artifacts without forking core skills unnecessarily.
- Maintainers can verify and reconcile planning artifacts more explicitly before
  slice bootstrap.

## Candidate Capability Areas

- **Project principles / constitution**
  - Add a skill that creates and maintains durable project principles.
  - Keep those principles consumable by planning and review skills.

- **Clarification workflow**
  - Add a skill that extracts and resolves high-impact ambiguities before
    design.
  - Keep clarification output in the repository rather than transient chat.

- **Richer planning customization**
  - Add a more explicit way to define project context, planning rules, and
    optional workflow variants beyond the current narrow config surface.
  - Reuse the generic-first approach: default behavior first, project overrides
    second.

- **Planning verification and reconciliation**
  - Add stronger checks for planning readiness, consistency, and artifact drift.
  - Consider explicit skills for validating planning artifacts and optionally
    reconciling approved planning output back into durable repo guidance.

## Confirmed Signals in Repo

- `guide-planning`, `discover`, `design`, `breakdown`, `review-planning`, and
  `slice` already define a coherent planning layer.
- `.skills/planning.json`, `.skills/execution.json`, and
  `.skills/conventions.json` provide an initial configuration model.
- `.skills/plugins/` is documented as a convention, but not as an automatic
  plugin system.
- `review-planning` already provides a planning-readiness checkpoint, so new
  verification behavior should complement it rather than duplicate it.
- `close-slice` already contains an example of optional publishing behavior,
  which is useful precedent for opt-in artifact rollup or sync patterns.

## Assumptions

- The next improvements should deepen planning quality rather than widen into
  full product packaging.
- Maintainers prefer additive skills and small config extensions over a large
  rewrite of the current methodology.
- Borrowed ideas should be adapted to the slice-based and feature-based model of
  `sirius-skills`, not copied literally from `spec-kit` or `OpenSpec`.

## Success Criteria

- A maintainer can point to a small set of planned capabilities that close the
  biggest planning-quality gaps without introducing a CLI or an implement skill.
- The planned capabilities fit cleanly into the current planning-layer routing
  model.
- The resulting story set is concrete enough for `design` to define artifact
  shapes, interfaces, and validation strategy.

## Risks and Open Questions

- A new constitution or clarification skill could overlap awkwardly with
  `discover` unless responsibilities are separated carefully.
- A richer customization model could become too abstract if it is not anchored
  in concrete repo files and clear ownership.
- Verification, sync, and archive concepts from `OpenSpec` need adaptation so
  they strengthen planning and closure without undermining the slice model.
