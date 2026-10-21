---
name: recover-specification
description: "Writes requirements, contracts, and decision records that prescribe the required behavior of code that is already implemented, instead of describing that code. Classifies observed behavior as intended, accidental, defect, or undecided; turns only approved intent into must-rules with acceptance examples; asks the decision owner about undecided points; and lists implementation gaps in a conformance record."
---

# Recover Specification

## Overview

A specification that is written after the code tends to describe the code. It
then records accidents and defects as if they were requirements, and reviewers
lose the baseline that tells them whether the code is correct.

`recover-specification` writes the specification as if it came before the
code. It uses the existing implementation as evidence, not as approval:

- Normative artifacts state required behavior with "must" rules and
  acceptance examples.
- A separate conformance record states where the implementation meets or
  misses each rule.
- The decision owner decides every point that the evidence does not decide.

Readers who want to know how the code works read the code. The specification
says what the code must do.

## When to Use

- Requirements, contracts, decision records, or architecture views must be
  written for behavior that already exists.
- Existing documents describe an implementation (for example "Current" and
  "Target" pairs, "Known limitations", or failures written as behavior) and
  must become normative.
- A review or a refactoring needs a normative baseline to judge the code
  against.

Do not use it for:

- new behavior that has no implementation yet (use the normal analysis and
  design flow);
- an investigation that only explains a subsystem or its history (use `how`
  or `why`);
- qualification of a change against an existing specification (use
  `spec-qualification`).

## Inputs and Authority

- A fixed baseline: repository revision, scope boundary, and exclusions.
- Evidence about current behavior from a responsible recovery process, such
  as `how` for runtime flows and `why` for historical intent. Each claim has a
  locator and a confidence level.
- A named decision owner for behavior that the evidence does not decide.

The implementation and its tests are evidence of what exists. They are not
evidence of what is wanted. A dependent caller is also part of the
implementation: it shows the impact of a change, not intent. Only independent
intent evidence or the decision owner can make a behavior required.

## Workflow

1. **Fix the baseline and the artifact set.** Record the revision and the
   boundary. Decide which artifacts are needed and where they live. Follow the
   [Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md)
   and the repository layout. Give each artifact the frontmatter that the
   [Markdown Artifact Frontmatter](../design-repository-artifact-layout/references/markdown-artifact-frontmatter.md)
   guide requires.
2. **Inventory observed behavior.** List each behavior at the boundary with
   its locator, its evidence kind (as-built, as-tested, as-documented, or
   historical), and its confidence. Keep this inventory in working notes. Do
   not commit it as a specification.
3. **Classify each behavior.** Use the evidence and the classification table
   in [classification.md](references/classification.md):
   - **Intended**: independent intent evidence supports it. It becomes a
     rule.
   - **Accidental**: no intent evidence and no dependent caller. Omit it.
   - **Defect**: it breaks stated intent, a standard, or an invariant (for
     example a crash, silent data loss, or a misrouted response). Record the
     gap. Write a rule for the remedy only when the cited intent, standard, or
     invariant determines the remedy. Otherwise the remedy is undecided.
   - **Undecided**: the evidence does not decide it, or only a dependent
     caller supports it. It becomes a question for the decision owner.

   Check every dependent caller before you omit or change a behavior. A
   dependent caller does not prove intent. Present it to the decision owner as
   a consequence of each option.
4. **Get decisions.** Present each undecided item, including each defect
   remedy that the evidence does not determine, to the decision owner. Give
   the options, the consequences (including dependent callers), and a
   recommendation. Record each decision.
   Do not write a rule for an undecided item, and do not write the current
   behavior as a rule because it exists.
5. **Write the normative artifacts.** Author artifacts in this exact sequence:
   **Decision records (`docs/decisions/`)** ──► **Behavioral contracts (`docs/contracts/`)** ──► **Integration architecture (`docs/architecture/`)**.
   Use the rule form in [templates.md](references/templates.md):
   - Write each rule as "must" or "must not".
   - Give each rule at least one acceptance example that fails when the rule
     is broken.
   - Write decisions as binding in `docs/decisions/`. Do not split them into current and target.
   - Define architectural blueprints in `docs/architecture/` with topologies, composition roots, and native architecture rules (`A1`, `A2`...). **The architecture document must not back-reference ADR numbers or decision IDs in its responsibilities table or text.**
   - Define each term on first use.
   - Name only the elements that are part of the contract surface. Do not
     list callers, internal types, tasks, or build switches.
6. **Write the conformance record.** Put it in the verification location of
   the repository, not in the normative artifacts. For each rule, record
   Conforms, Partial, Gap, or Not verified, with a locator at the baseline.
   Give each gap a follow-up owner. Link the normative artifacts to the
   record.
7. **Verify.** Use an independent reviewer. The reviewer checks the
   Verification list below against the artifacts and the code at the
   baseline.

## Red Flags

These signs show that an artifact describes the implementation:

- A rule states what the code does ("the runtime returns", "the adapter
  logs") instead of "must" or "must not".
- "Current" and "Target" pairs, "Known limitations", or "Behavior changes in
  change N" sections in a normative artifact.
- Lists of callers, call sites, task lifetimes, build switches, or internal
  type names that are not part of the contract surface.
- A defect written as behavior ("a late response stops the process").
- A rule whose only support is that the code does it, or that a caller
  depends on it.
- A defect remedy that no cited intent, standard, invariant, or decision
  determines.
- An acceptance example that cannot fail, or that contradicts another rule.
- A decision marked "proposed" in an artifact with status "accepted".
- Implementation status inside a normative artifact instead of in the
  conformance record.
- An architecture document citing ADR IDs or decision numbers in its responsibilities table or text, turning the living blueprint into an index of historical decision tickets.

## Output

- Normative artifacts: requirements, contracts, decision records, or
  architecture views, as selected in step 1.
- A conformance record for the baseline.
- A decision log: each decision of the decision owner, with its date. It can
  be part of a decision record.
- Open questions, if the decision owner defers a decision. An open question
  never becomes a rule.

## Boundaries

- Does not recover current-system facts by itself. It consumes evidence from
  a responsible recovery process.
- Does not change code. Each gap becomes follow-up work.
- Does not approve intent. The decision owner does.
- Does not decide whether an artifact exists or where it lives. Use
  `select-technical-artifacts` and `design-repository-artifact-layout`.
- Does not qualify a change. Use `spec-qualification` with the normative
  artifacts as input.

## Verification

- [ ] Every rule uses "must" or "must not" and is testable.
- [ ] Every rule has an acceptance example, and each example fails when its
      rule is broken.
- [ ] No rule contradicts another rule, a decision, or an invariant.
- [ ] No Red Flag appears in a normative artifact.
- [ ] Every rule traces to independent intent evidence or to a recorded
      decision.
- [ ] Every defect remedy traces to cited intent, a standard, an invariant,
      or a recorded decision.
- [ ] No undecided item became a rule.
- [ ] Every conformance entry matches the code at the baseline and has a
      locator.
- [ ] Every gap has a follow-up owner.
- [ ] Every dependent caller of a changed or omitted behavior was checked and
      presented to the decision owner as a consequence.
