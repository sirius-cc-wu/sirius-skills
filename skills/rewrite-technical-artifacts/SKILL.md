---
name: rewrite-technical-artifacts
description: Reviews and restructures requirements, analysis, design, architecture decision records (ADRs), planning, verification, or recovery Markdown for cognitive simplicity and progressive disclosure without changing normative meaning, identifiers, lifecycle status, evidence, or traceability. Use when an artifact or proposed ADR is difficult to read, contains avoidable repetition or ceremony, needs a reader-oriented opening or representative scenario, an accepted ADR needs read-only editorial review, or a branch or pull-request diff needs a semantic-preserving final pass.
---

# Rewrite Technical Artifacts

## Overview

Make an existing technical artifact easier to understand while preserving what
it asserts, requires, forbids, qualifies, and leaves uncertain. Prefer revising
the canonical artifact in place over creating a second source of truth.
Simplification means reducing reader effort; it may remove or consolidate text,
but it may instead add a small amount of orientation before exact specification.

## When to Use

- A generated or manually written artifact is correct but difficult to enter,
  navigate, or explain to its primary reader.
- A branch or pull request contains substantial changed artifacts that need a
  focused editorial pass before review or commit.
- Detailed terminology, contracts, evidence, or edge cases appear before the
  reader understands the problem and consequence.
- The same rule is repeated across artifacts and should be consolidated behind
  one canonical link.
- A review must identify readability improvements without modifying the file.
- Do not require a pass for a narrow index, registry, traceability ledger, or
  checklist when it is already proportionate to its task.
- Do not use to change requirements, resolve contradictions, approve inferred
  intent, or make one artifact serve audiences with genuinely different tasks.

## Workflow

1. **Read governance and neighboring artifacts.** Preserve repository
   conventions, canonical paths, generated-file rules, and local terminology.
2. **Identify the artifact and reader.** State its lifecycle, primary reader,
   and the question that reader brings to it.
3. **Choose the mode.**
   - Review only: report problems and a proposed reading order without editing.
     Use this for an accepted ADR whose lifecycle forbids substantive revision.
   - Revise in place: default when the canonical artifact can serve the reader.
   - Diff-focused review: inspect only the changed reader-facing artifacts and
     their necessary canonical context before commit or review.
   - Companion explanation: first apply
     [Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md),
     then use only when a different audience or task cannot safely be served by
     the canonical technical artifact.
4. **Inventory meaning before editing.** Record frontmatter, lifecycle status,
   stable IDs, requirements, guarantees, prohibitions, states, operations,
   evidence qualifications, uncertainties, and traceability links.
5. **Map the current reading path.** Find missing orientation, terminology
   introduced before context, mixed audiences, repeated rules, and detail that
   obscures the main decision or behavior.
6. **Restructure with progressive disclosure.** Follow
   [Readable Technical Artifacts](../iterative-up-analysis-design/references/readable-technical-artifacts.md).
   Explain the problem, behavior or decision, and consequence first. Use a
   representative scenario when the behavior is unfamiliar, stateful, or
   concurrent. Keep exact rules and reference detail afterward.
7. **Preserve the artifact's technical shape.** Retain artifact-specific
   sections required by its owning skill. Move or consolidate material instead
   of merely prepending a summary to unchanged repetition.
8. **Compare meaning after editing.** Check the revision against the inventory.
   Do not silently strengthen, weaken, infer, delete, or reconcile any claim.
9. **Validate the result.** Run repository checks, verify links and identifiers,
   inspect the final diff, and report any meaning that remains ambiguous.

## Diff-Focused Review Mode

Use this mode as a final cleanup pass over a branch or pull-request diff:

1. **Scope.** Start from the diff, select the changed reader-facing artifacts,
   and lock their requirements, identifiers, evidence qualifications,
   lifecycle, and traceability. Read neighboring artifacts only as needed to
   preserve canonical ownership and context.
2. **Review.** Look for four kinds of reader cost:
   - reading flow: missing orientation, unexplained terms, or reference detail
     before the reader understands the problem and consequence;
   - proportion: repeated summaries, redundant headings, dead ceremony, or
     low-value detail obscuring the main behavior or decision;
   - ownership and lifecycle: duplicated rules, competing sources of truth, or
     current knowledge placed in a historical artifact; and
   - semantic safety: explanatory prose that overstates rules, hides
     uncertainty, or weakens evidence qualifications.
3. **Fix and verify.** Apply only high-confidence changes within the selected
   artifact scope. It is valid to conclude that the diff is already
   proportionate. Compare the final diff with the semantic inventory and run
   relevant frontmatter, identifier, link, and repository checks.

## File Output

When revising a standalone Markdown artifact, preserve its existing
frontmatter and follow
[Markdown Artifact Frontmatter](../iterative-up-analysis-design/references/markdown-artifact-frontmatter.md).
Do not add nested frontmatter or change identity and lifecycle metadata as a
writing side effect.

## Red Flags

- A friendly summary claims behavior that the exact rules do not guarantee.
- A scenario omits the failure or concurrency condition that makes the design
  significant.
- Normative words, identifiers, evidence confidence, or uncertainty disappear
  during simplification.
- A companion document is created only because revising the canonical artifact
  requires care.
- The artifact becomes longer because all previous repetition remains below a
  new explanation layer.
- A diff-focused pass expands into unrelated documentation cleanup.
- Readability scores or sentence-length limits replace judgment about the
  reader's task.

## Verification

- [ ] The artifact lifecycle, primary reader, and reading question are explicit.
- [ ] The pre-edit inventory covers normative facts, uncertainty, identifiers,
      evidence, and traceability.
- [ ] The opening explains the problem, behavior or decision, and consequence
      before exhaustive specification.
- [ ] A representative scenario is present when it materially improves
      understanding and agrees with the exact rules.
- [ ] No requirement, guarantee, prohibition, state, operation, lifecycle
      marker, evidence qualification, or stable identifier changed accidentally.
- [ ] Repetition was consolidated without creating another source of truth.
- [ ] A diff-focused pass stayed within the selected changed-artifact scope and
      skipped low-value stylistic churn.
- [ ] Repository checks and final-diff inspection pass, or remaining gaps are
      reported precisely.
