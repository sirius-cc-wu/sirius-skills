# Skill Catalog

This catalog describes each deployable skill's responsibility and boundary.
See [Source Catalog](sources.md) for intellectual provenance and
[Workflow Tracks](tracks/) for ways to compose the skills.

| Skill | Source Concepts Preserved | Primary Artifact | Boundary |
|---|---|---|---|
| `agy-second-opinion` | One isolated Antigravity CLI opinion of a bounded artifact and explicit contract, with disclosure and dangerous-permission confirmation | Attributed independent review report | Obtains one external opinion only after current user approval; does not own the primary review, reconcile findings, edit, commit, push, publish, or approve |
| `create-pr` | Base and head verification, duplicate detection, convention-aware titles, validation evidence, and draft-first publication | GitHub pull request | Publishes committed work for review; does not implement, silently commit, or resolve divergent history |
| `walkthrough-me` | Revision- or snapshot-fixed inspection of pull requests, commits, ranges, branches, and staged, unstaged, or selected untracked worktree changes; dependency-ordered tour maps; small code excerpts; evidence labels; user-controlled depth; explicit section checkpoints | Interactive code-change walkthrough and final recap | Establishes paced comprehension without approving or committing the change, conducting a formal review, combining local change sources silently, changing repository or remote state, or recovering unrelated system scope |
| `select-technical-artifacts` | Value, ownership, and lifecycle creation gate; executable-first disposition order; create/update/embed/keep/omit/defer classification; minimal artifact-set review | Artifact disposition table, minimal selected set, or authorized budget update | Decides whether knowledge needs an independent artifact without authoring specialist content, choosing canonical paths, coordinating an iteration, or creating selected artifacts |
| `design-repository-artifact-layout` | Repository-first convention discovery, missing-guide inference, artifact lifecycle separation, minimal feature/artifact/product-area/chronological layouts, canonical paths, linking, and migration | Repository artifact-layout recommendation or authorized canonical-path migration | Chooses where justified durable technical artifacts live; does not decide that an artifact must exist, require a layout document, author content, replace its owning specialist, or mutate the repository without explicit authority |
| `assess-development-input` | Session-start task discovery, content-based readiness assessment, authority and uncertainty preservation, and single-owner selection across Sirius skills, external add-ons, and repository-native processes | Initial development route or optional development input assessment | Owns entry routing without imposing a lifecycle, rewriting source material, inventing decisions, executing the handoff, or replacing in-iteration coordination |
| `define-project-vision` | Evidence-backed project identity, principles, non-goals, acceptance policy, boundary-case review, and authority-approved vision revision | Vision draft or bounded revision of the canonical vision | Defines a durable contribution-acceptance policy without treating history as approval, replacing candidate-direction refinement, or deciding business cases, investment, detailed requirements, or architecture |
| `specify-quality-constraints` | Measurable quality requirements, binding constraints, source and authority status, acceptance evidence, conflicts, and links to affected behavior | Supplementary specification or canonical requirements refinement | Specifies cross-cutting and special requirements without inventing business approval, actor-goal flow, architecture, or implementation |
| `software-design-language-adaptation` | Language-native mappings for architecture, behavior, boundaries, state, responsibilities, variation, lifecycle, errors, concurrency, and diagrams | Implementation-facing design adaptation | Adapts design intent to Rust, Python, TypeScript, C#, or C++ without forcing object structure or altering language-neutral requirements and contracts |
| `design-rust-lifecycles` | Native responsibility realization, ownership and capability transfer, staged startup, readiness, rollback, async cancellation, supervision, RAII, explicit termination, fallible cleanup, and vertical verification retention | Rust lifecycle design | Turns established system and architecture boundaries, a representative scenario, and native responsibilities into an implementation-facing Rust lifecycle; does not replace missing analysis, force typestate or traits, claim a parent outcome from a local seam, or implement the design |
| `behavior-preserving-refactoring` | Responsibility and dependency correction, configuration ownership, boundary-impact classification, bounded structural batches, verification after each reviewable step, and durable design feedback | Verified structural design improvement and optional refactoring record | Changes established responsibility, dependency, variation, or configuration structure behind passing checks; leaves routine clarity cleanup to external `code-simplification` and returns boundary-sensitive redesign to coordinated development |

## Distillation Rules

- Convert source material into agent behavior, not a chapter summary.
- Prefer checklists, decision points, and artifact templates over explanation.
- Keep each skill small enough to load independently.
- Avoid copying long source passages; preserve concepts as practical procedures.
- Put discovery and lifecycle metadata for standalone Markdown artifacts in one
  OKF-aligned YAML frontmatter block; keep narrative analysis, design,
  rationale, and evidence in the body.
