---
name: reflect
description: "Spawn three parallel Goldfish review lenses (Judgment, Tooling, Divergent) plus a Synthesizer over the active session transcript to surface durable learnings and route each to a concrete skill edit or structural backlog item. User-invoked only: use when the operator says /reflect or reflect; do not invoke automatically."
disable-model-invocation: true
---

# Reflect (Multi-Lens Session Learning)

Mine the current conversation for durable learnings, then route them into concrete skill edits or structural backlog items.

Invoke when the operator says `reflect` or `/reflect`. Skip when the conversation is trivial, off-topic, or already covered by an existing skill the orchestrator followed correctly. One-offs are not learnings.

Companion to `correct`:
- **`reflect`** improves **skills** from one session transcript (plus routes structural mechanisms to Backlog).
- **`correct`** mines **repository history** to eliminate repeating mistake classes ($\ge 2$ occurrences) at the architectural, type, lint/CI, or test level.

## 1. Locate the active transcript

Stay strictly within the active conversation (or the specific conversation ID the operator explicitly names). Do not glob across unrelated `<appDataDir>/brain/*/` conversations from other projects.

- **Primary Thinker (Elephant) transcript**: `<appDataDir>/brain/<conversation-id>/.system_generated/logs/transcript.jsonl` (and `transcript_full.jsonl` for lines with `truncated_fields`).
- **Subagent & Goldfish logs (optional scope)**: grep `invoke_subagent` in `transcript.jsonl` or include relevant Gate 1/2 Goldfish outputs from `<appDataDir>/scratch/reviews/` if the session's struggles occurred there.

If the transcript path is unavailable, build a tight factual digest of the session (user turns, key tool outcomes, failures, corrections, skills opened) and pass that instead.

## 2. Spawn three reviewers in parallel

Launch all three lenses concurrently in isolated, zero-context ("goldfish") processes using the configured Reviewer model from `~/.config/thinker/config.yaml` (`gemini-4-neon-<budget>` in `gemini` mode; `claude-opus-5-5-<min(budget, high)>` in `claude` mode). When available, you may run the Divergent lens on the opposite quota family for broader blind-spot coverage.

Write each filled prompt template (substituting the transcript path or digest where marked) to scratch files under `<appDataDir>/brain/<conversation-id>/scratch/reflect/<lens>-prompt.md`—never interpolate raw transcript text into double-quoted shell strings—and invoke read-only Goldfish runners (`agy --sandbox --dangerously-skip-permissions --model <reviewer>-<budget> --print "Read and execute <prompt-path>."`), writing each lens's report to `<scratch>/reflect/<lens>-out.md`.

| Lens | Focus | Prompt template |
|---|---|---|
| **Judgment** | Durable principles behind incidents, corrections, and workflow friction | `references/judgment-reviewer.md` |
| **Tooling** | Concrete commands, flags, quirks, and **agent self-sufficiency** gaps | `references/tooling-reviewer.md` |
| **Divergent** | Contrarian/second-order blind spots, lucky passes, missed skill triggers | `references/divergent-reviewer.md` |

Reviewers must never modify files, edit skills, or commit. Each lens sees only the transcript and its own prompt—never another lens's output.

## 3. Synthesize

Once all three lenses complete, launch one fresh Reviewer-model Goldfish process with `references/synthesizer.md` (passing the three lens output paths and the active transcript path via a scratch prompt file).

The Synthesizer:
1. Spot-verifies cited quotes, turn numbers, and target `SKILL.md` files directly from disk (ADR-005 D6 evidence discipline).
2. Applies all 8 gates (`durability`, `specificity`, `existing-skill-first`, `convergence`, `decision-changing`, `structural-mechanism check`, `skill-was-used`, `already-covered`).
3. Returns the exact `## Accepted`, `## Rejected`, and `## Backlog` report.

## 4. Structural enforcement check

Move any `Accepted` item that architecture, types, a lint rule, script, metadata flag, or runtime check would enforce more reliably to `Backlog`. *If the fix is structural, only use the structural fix—prose is the symptom.* Route target-repo structural items to **`/correct`** (or a scoped Builder task).

## 5. Apply (Human Approval & Skill Source-of-Truth Gate)

Present the Synthesizer's full `Accepted` / `Rejected` / `Backlog` output and **wait for explicit operator approval** before applying any edit or filing any backlog item. The operator picks the subset and may redirect routings. Skill changes affect every future run—never auto-apply.

**Skill Source-of-Truth Guardrail:**
- Never edit read-only built-in Antigravity skills (`~/.gemini/antigravity-cli/builtin/skills/`).
- Before editing a Thinker skill, check `package.json` (`sirius-skills.skills` vs `sirius-skills.preserveSkills`):
  - Skills in `preserveSkills` live locally at `skills/<name>/SKILL.md`.
  - Skills in `sirius-skills.skills` are synced from the upstream `sirius-skills` repo; show the upstream source path before approval so edits do not drift out of sync with `bun run sync:skills:check`.
- Never commit or push automatically without explicit operator approval.

Follow each approved row's Routing:
- **Existing skill edit (`<skill path> + <section>`)**: Apply trivial edits directly; for substantive edits (>~10 lines), keep `SKILL.md` concise and disclose bulky detail into `references/`.
- **`tune description: <skill path>`**: Tighten frontmatter `description` triggers so the skill fires reliably next time without bloating always-loaded context.
- **`new skill: <kebab-name>`**: Rare; create `skills/<kebab-name>/SKILL.md`, `.agents/skills/<kebab-name>` symlink, and register in `package.json` (`preserveSkills`) only on explicit approval.
- **Approved Backlog items**: Hand off target-repo recurring mistake classes to **`/correct`**, or file issues via `github-issue-workflow` if requested.

After approved skill edits in `thinker`, verify with `bun run sync:skills:check` (and `bun test` if scripts/tests changed).

## 6. Summarize for the operator

Short list, no preamble:
- **Edits applied**: `<skill path>` — what changed, one line each.
- **New skills created**: `<skill path>` — one line each (rare).
- **Backlog / `/correct` follow-ups**: `<item>` — one line each.
- **Dropped**: one line per rejected finding + reason from the Synthesizer.
