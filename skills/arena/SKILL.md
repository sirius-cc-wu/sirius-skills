---
name: arena
description: "Spawn N parallel candidates at the same design or architectural task, cross-judge against an explicit rubric, pick a base, and graft the strongest parts of the losers into it. Use for /arena, 'arena this', or when competing architectural directions should be explored before committing to an ADR or execution plan."
---

# Arena (Competitive Design & Synthesis)

Open a checklist with one entry per phase (**Frame**, **Fan out**, **Cross-judge**, **Pick a base**, **Graft**, **Verify**) before launching candidates.

## When to Use

- Between **Playbook 6 (Investigation Spike)** and **Playbook 1 (Architectural)** when 2+ genuinely distinct architectural approaches exist (e.g., upstream `[patch.crates-io]` vs. repo-local lifecycle hook) and locking in the wrong shape would be costly.
- When a non-trivial spec, API boundary, or refactor would benefit from independent zero-context ("goldfish") proposals rather than anchoring on the first idea.

## Model & Runtime Integration (`~/.config/thinker/config.yaml`)

- **Candidates & Cross-Judge**: Run via `agy` using `roles.investigation` / `roles.design_review` from `~/.config/thinker/config.yaml` (default: `gemini-4-argon-high`; fallback: `claude-opus-5-5` when Gemini is out of quota).
- **Zero-Context ("Goldfish") Isolation**: Each candidate runs in its own `agy` process and never reads another candidate's output.
- **Cross-Judge Independence**: The Phase C judge reads only the rubric and the candidate outputs (by path label), never the parent coordinator's preference. When available, prefer a judge from the opposite quota family (`claude-opus-5-5` when candidates use `gemini-4-argon-high`, or vice versa).

---

## Phase A: Frame

1. **State the target artifact** each candidate is producing (design proposal, module boundary, ADR draft, or prototype).
2. **Derive the rubric**: 3–6 concrete, gradeable criteria for what success looks like on *this* task (e.g., *failure-mode safety*, *diff/maintenance footprint*, *CI/build impact*, *testability*). Candidates see only the task and grounding—not the rubric weights—unless specific constraints are part of the problem statement.
3. **Assign isolated outputs**: Give each candidate its own output location (`scratch/arena/<slug>/candidate-<n>.md` for design arenas, or an isolated worktree via `bun scripts/worktree.ts create` for code arenas).

## Phase B: Fan Out

Launch all $N$ candidates in parallel (`agy --model <model> --dangerously-skip-permissions -p "..."`), each receiving:
- The exact problem statement and shared grounding paths (e.g., investigation report, target source files, CI config).
- Its assigned design direction (if comparing explicit options) or open prompt (if exploring divergent solutions).
- Instructions to write its proposal to its isolated output path and include a brief rationale noting alternatives considered and rejected.

If a candidate produces no output, proceed with $N-1$ and note the dropout.

## Phase C: Cross-Judge

Once all Phase B candidates complete, launch one read-only judge (`agy`) with:
- The Phase A rubric.
- The candidate output paths (labeled `Candidate A`, `Candidate B`, ...).
- Instructions to score each candidate criterion-by-criterion against the rubric, cite concrete risks/strengths from each file, and recommend a base with rationale.

The judge runs in parallel with the coordinator's own end-to-end reading of the candidates.

## Phase D: Pick a Base

Read every candidate end-to-end and compare your criterion-by-criterion scoring with the Cross-Judge's verdict:
- Agreement confirms the base.
- Disagreement means either a bias or an ambiguous rubric—read both rationales before deciding.
- Pick the base a future maintainer can extend most easily without breaking invariants. When two feel tied, prefer the smaller diff, cleaner boundary, or lower maintenance surface.

## Phase E: Graft

Walk each losing candidate once more for 1–2 concrete ideas worth porting into the chosen base (e.g., a race-condition guard, CI safety check, or companion fix).
- Fold each graft in coherently under one mental model; never paste conflicting mechanisms together.
- If candidates converge on one shape, ship the consensus shape with no graft. If they diverge because the problem was underspecified, reframe Phase A and re-run.

## Phase F: Verify & Hand Off

- Verify the synthesized design against the rubric and repo invariants (zero-warning builds, Pure Production API, CI compatibility).
- For **Playbook 1 / Playbook 2**: Record the chosen architecture in `docs/decisions/` (ADR) and `docs/execution/`, then run **Gate 1 (`scripts/goldfish-runner.ts --stage gate1 --all`)** before dispatching a Builder.

## Outputs

Present a concise synthesis summary containing:
- The rubric scores and chosen base (plus the Cross-Judge verdict).
- Each graft ported from losing candidates (and what was rejected and why).
- Recommended next Playbook step (e.g., PB-1 ADR + Gate 1).
