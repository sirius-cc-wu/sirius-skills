# Applying UML and Patterns Skills

This collection distills `applying-uml-and-patterns.md` into agent skills for moving from requirements to object design with UML, Unified Process practices, GRASP, and common design patterns.

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
2. `use-case-modeling` - identify actors, goals, and black-box system behavior.
3. `domain-modeling` - model conceptual classes, associations, and attributes.
4. `system-sequence-diagrams` - convert use-case scenarios into system events.
5. `operation-contracts` - specify non-trivial system operation effects.
6. `grasp-responsibility-design` - assign responsibilities using GRASP.
7. `use-case-realization` - realize use cases with interaction diagrams and collaborating objects.
8. `uml-class-diagram-design` - summarize the design model as software classes.
9. `design-pattern-application` - apply GoF patterns only where variation, creation, notification, or composition pressure warrants them.

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
