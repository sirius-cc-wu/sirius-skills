# gstack Ship Reference

## Scope

This comparison focuses on `gstack` `ship` as an upstream reference and
`sirius-skills` `ship` + `ship-slice` as the local implementation target.

Reference baseline used here:

- `gstack` local clone commit `656df0e3`
- upstream URL: `https://github.com/garrytan/gstack`

## Behavior Comparison

| Dimension | `gstack /ship` | `sirius-skills ship` + `ship-slice` |
|---|---|---|
| Workflow objective | Land a feature branch safely: merge base, test, review, version/changelog, push, create PR/MR. | Resolve one reviewed planning backlog into executable slice routing and resumable one-slice acceleration. |
| Main control plane | One long skill workflow with numbered steps and release gates. | Python scripts (`ship.py`, `ship_slice.py`) plus planning/execution registries and traceability docs. |
| State model | Branch/diff/review readiness state; release checklist idempotency. | Durable artifact state (`slice-planning.md`, `slice-traceability.md`, `.slice-meta.json`, registries). |
| Stop conditions | Hard gates on conflicts, test/review failures, coverage/verification thresholds, and unresolved asks. | Hard gates on active-slice conflicts, dependency blocks, ambiguous mapping, and commit checkpoints. |
| Rerun semantics | Re-runs full verification checklist every run; action steps are idempotent. | Recomputes backlog from artifact truth every run; mutates only when `--bootstrap-next` or delegated handoff is enabled. |
| End output | Pushed branch and PR URL with refreshed PR body sections and ship metrics. | Next-owner handoff, machine-readable payload, checkpoint/event-log updates (when ship-slice is used). |

## Architectural Delta

`gstack /ship` is release-pipeline-centric; `sirius-skills ship` is
artifact-orchestration-centric. They solve adjacent but different problems.

`sirius-skills` intentionally keeps ownership split:

- backlog resolution in `ship`
- one-slice resume in `ship-slice`
- execution writes in existing execution owners

This boundary should remain intact even when borrowing ideas.

## Two-Step Question: "Does gstack already work like this?"

Short answer: **partially, but not in the same artifact model**.

- `gstack /autoplan` is an auto-review pipeline for a plan document (CEO/design/
  eng/DX review phases with auto-decisions).
- `gstack /ship` is a fully automated ship pipeline for a branch (merge base,
  tests, review gates, version/changelog, push, PR/MR).
- `gstack` does **not** use `sirius-skills` planning artifacts (`discover.md`,
  `system-design.md`, `slice-planning.md`) or execution artifacts (`brief.md`,
  `blueprint.md`) as first-class lifecycle owners.

So gstack demonstrates a strong two-command experience pattern, but not a
drop-in implementation of `sirius-skills` discover/design/breakdown/brief/
blueprint semantics.

## Adoptable Patterns From gstack

1. **Readiness dashboard pattern**
   Add a concise readiness matrix to `ship` text/JSON output so maintainers can
   see gate status quickly before any mutation. Status: implemented as
   normalized `readiness` JSON across `autoplan`, `ship`, and `ship-slice`.
2. **Explicit idempotency contract**
   Document rerun behavior in `skills/ship/SKILL.md` using "always recheck vs
   mutate once" language.
3. **Structured release handoff (optional)**
   Keep release/PR creation outside `ship`, but optionally emit a richer
   handoff artifact that downstream skills can consume.

## Patterns To Avoid Copying Directly

1. Embedding full branch-release responsibilities into `ship` itself
2. Replacing artifact truth with session/runtime truth
3. Coupling backlog routing to telemetry/personalization preambles

## Sirius-Skills Two-Step Direction

To match the requested two-step UX while preserving current ownership rules:

1. Step 1 command (`autoplan`) should orchestrate owner execution
   (`discover -> design -> breakdown -> review-planning`) instead of only
   returning the next owner.
2. After explicit user approval, Step 2 command (`ship` + delegated
   `ship-slice`) should orchestrate owner execution
   (`brief -> blueprint -> implementation -> review-execution`) until stop
   boundaries are hit.
3. Keep explicit approval and high-risk boundaries as hard stops, but remove
   manual skill-to-skill prompting for normal happy-path progression.

## Main Sources

- `gstack/ship/SKILL.md` (sibling local reference clone)
- `gstack/autoplan/SKILL.md` (sibling local reference clone)
- `skills/ship/SKILL.md`
- `sirius ship`
- `skills/ship-slice/SKILL.md`
- `sirius ship-slice`
- `skills/autoplan/SKILL.md`
- `sirius autoplan`
- `docs/features/throughput-acceleration-workflow/system-design.md`
