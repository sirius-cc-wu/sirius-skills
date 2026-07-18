# Applying UML and Patterns Skills

This collection distills `applying-uml-and-patterns.md` into agent skills for moving from requirements through object design to tested implementation and refactoring with UML, Unified Process practices, GRASP, and common design patterns.

## Installing Skills

Install all managed skills globally for GitHub Copilot, Codex, Antigravity, and Antigravity CLI:

```bash
just install
```

The managed set is defined by `managed_skills` in `justfile`. Keep that list in sync when adding or retiring skills.

Remove the managed skills later with:

```bash
just uninstall
```

## Validation

Validate the collection structure and skill metadata:

```bash
just validate
```

## Recommended Sequence

1. `iterative-up-analysis-design` - frame the work as an iterative, risk-driven analysis/design slice.
2. `inception` - envision product scope, feasibility, business case, and key risks to decide if the project is worth serious investigation.
3. `use-case-modeling` - identify actors, goals, and black-box system behavior.
4. `domain-modeling` - model conceptual classes, associations, and attributes.
5. `system-sequence-diagrams` - convert use-case scenarios into system events.
6. `operation-contracts` - specify non-trivial system operation effects.
7. `grasp-responsibility-design` - assign responsibilities using GRASP.
8. `use-case-realization` - realize use cases with interaction diagrams and collaborating objects.
9. `uml-class-diagram-design` - summarize the design model as software classes.
10. `design-pattern-application` - apply GoF patterns only where variation, creation, notification, or composition pressure warrants them.
11. `test-driven-implementation` - implement risk-sized behavior slices from independent executable or mechanically checked oracles.
12. `behavior-preserving-refactoring` - improve code and design through independently reviewable transformations or bounded mechanical batches protected by verification.

Use `software-design-language-adaptation` alongside steps 7-12 when the implementation language is known. Load only the reference for the selected language.

## Artifact Durability and Layouts

The iterative UP coordinator distinguishes durable design knowledge from
iteration history:

- Use cases, domain models, SSDs, contracts, realizations, and design class
  diagrams are canonical artifacts refined across iterations.
- Iteration records retain goals, risks, selected scope, exit criteria, and
  results without copying the canonical artifacts.
- Decision records preserve cross-cutting choices and explicitly supersede
  earlier decisions when needed.

The coordinator preserves an established repository layout. When no convention
exists, it selects the smallest suitable structure rather than imposing one
taxonomy:

| Layout | Best fit |
|---|---|
| Feature-iteration hybrid, flat variant | Small repositories and one-page features |
| Feature-iteration hybrid, package variant | Cohesive features with independently changing artifacts |
| Artifact-oriented | Shared models spanning many features |
| Product-area oriented | Stable subsystems with area ownership |
| Iteration-first | Audit-focused repositories with snapshots plus a canonical `current/` index |

See [Artifact Durability and Repository Layouts](skills/iterative-up-analysis-design/references/artifact-layouts.md)
for selection criteria, tradeoffs, linking rules, and migration guidance.

## Files

- `skill-inventory.md` maps source concepts to skill boundaries.
- `skills/*/SKILL.md` contains the agent-facing workflows.
- `skills/iterative-up-analysis-design/references/artifact-layouts.md` describes supported persistence layouts.
- `scripts/validate_skills.sh` performs lightweight structure validation.
- `justfile` installs, removes, and validates the managed skills.
