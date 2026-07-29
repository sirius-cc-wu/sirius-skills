---
name: rewrite-technical-artifacts
description: Restructures existing requirements, analysis, design, decision, planning, verification, or recovery Markdown for progressive disclosure without changing normative meaning, identifiers, lifecycle status, evidence, or traceability. Use when a technically correct artifact is difficult to read, needs a reader-oriented opening or representative scenario, or should be reviewed for semantic-preserving documentation improvement.
---

# Rewrite Technical Artifacts

## Overview

Make an existing technical artifact easier to understand while preserving what
it asserts, requires, forbids, qualifies, and leaves uncertain. Prefer revising
the canonical artifact in place over creating a second source of truth.

## When to Use

- A generated or manually written artifact is correct but difficult to enter,
  navigate, or explain to its primary reader.
- Detailed terminology, contracts, evidence, or edge cases appear before the
  reader understands the problem and consequence.
- The same rule is repeated across artifacts and should be consolidated behind
  one canonical link.
- A review must identify readability improvements without modifying the file.
- Do not use to change requirements, resolve contradictions, approve inferred
  intent, or make one artifact serve audiences with genuinely different tasks.

## Workflow

1. **Read governance and neighboring artifacts.** Preserve repository
   conventions, canonical paths, generated-file rules, and local terminology.
2. **Identify the artifact and reader.** State its lifecycle, primary reader,
   and the question that reader brings to it.
3. **Choose the mode.**
   - Review only: report problems and a proposed reading order without editing.
   - Revise in place: default when the canonical artifact can serve the reader.
   - Companion explanation: use only when a different audience or task cannot
     safely be served by the canonical technical artifact.
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
- [ ] Repository checks and final-diff inspection pass, or remaining gaps are
      reported precisely.
