---
name: reflect
description: "Spawn three parallel Goldfish review lenses (Judgment, Tooling, Divergent) plus a Synthesizer over the active session transcript to surface durable learnings and route each to the right scope: Thinker/shared skills, target-repo harness and steering docs, or structural backlog (/correct). User-invoked only: use when the operator says /reflect or reflect; do not invoke automatically."
disable-model-invocation: true
---

# Reflect (Multi-Lens Session Learning)

Mine the current conversation for durable learnings, then route each finding to its proper owner: **Thinker / shared skills**, **target-repo harness & steering**, or **structural backlog (`/correct`)**.

Invoke when the operator says `reflect` or `/reflect`. Skip when the conversation is trivial, off-topic, or already covered by an existing skill or harness doc the session followed correctly. One-offs are not learnings.

Companion to `correct`:
- **`reflect`** mines **one session transcript** to improve Thinker/shared skills, target-repo runtime harnesses/steering, and queue structural backlog items.
- **`correct`** mines **target-repo history** to eliminate repeating mistake classes ($\ge 2$ occurrences) at the architectural, type, lint/CI, test, or runtime-harness level.

## 1. Locate the active transcript and target repository

Stay strictly within the active conversation (or the specific conversation ID the operator explicitly names). Do not glob across unrelated `<appDataDir>/brain/*/` conversations from other projects.

- **Primary Thinker (Elephant) transcript**: `<appDataDir>/brain/<conversation-id>/.system_generated/logs/transcript.jsonl` (and `transcript_full.jsonl` for lines with `truncated_fields`).
- **Subagent & Goldfish logs (optional scope)**: grep `invoke_subagent` in `transcript.jsonl` or include relevant Gate 1/2 Goldfish outputs from `<appDataDir>/scratch/reviews/` if the session's struggles occurred there.
- **Target repository (`<TARGET_REPO_PATH>`)**: Because `agy` runs in `thinker` while working on another repository, resolve the session's target repository absolute path from the operator's prompt or transcript paths (or set `none` if the session worked only on `thinker`). Note any target-repo harness surfaces present or touched (read-only): `<target>/AGENTS.md`, `<target>/CODING_STANDARDS.md`, `<target>/docs/ui/surface-map/`, `<target>/scripts/verify-*`, and `<target>/.agents/skills/*`.

If the transcript path is unavailable, build a tight factual digest of the session (user turns, target repo path, key tool outcomes, failures, corrections, skills and harness files opened) and pass that instead.

## 2. Spawn three reviewers in parallel

Launch all three lenses concurrently in isolated, zero-context ("goldfish") processes using the configured Reviewer model from `~/.config/thinker/config.yaml` (`gemini-4-neon-<budget>` in `gemini` mode; `claude-opus-5-5-<min(budget, high)>` in `claude` mode). When available, you may run the Divergent lens on the opposite quota family for broader blind-spot coverage.

Write each filled prompt template (substituting `<TRANSCRIPT_PATH>`, `<TRANSCRIPT_FULL_PATH>`, `<TARGET_REPO_PATH>`, or `<DIGEST_IF_PATH_UNAVAILABLE>` where marked) to scratch files under `<appDataDir>/brain/<conversation-id>/scratch/reflect/<lens>-prompt.md`—never interpolate raw transcript text into double-quoted shell strings—and invoke read-only Goldfish runners (`agy --sandbox --dangerously-skip-permissions --model <reviewer>-<budget> --print "Read and execute <prompt-path>."`), writing each lens's report to `<scratch>/reflect/<lens>-out.md`.

| Lens | Focus | Prompt template |
|---|---|---|
| **Judgment** | Durable principles behind incidents, corrections, and workflow/harness friction | `references/judgment-reviewer.md` |
| **Tooling** | Concrete commands, flags, harness/runtime quirks, and **agent self-sufficiency** gaps | `references/tooling-reviewer.md` |
| **Divergent** | Contrarian/second-order blind spots, lucky passes, missed skill triggers, scope misplacement | `references/divergent-reviewer.md` |

Reviewers must never modify files, edit skills, or commit. Each lens sees only the transcript, `<TARGET_REPO_PATH>`, and its own prompt—never another lens's output.

**Quick mode (`--quick`):** When the operator explicitly asks for a quick reflection on a small session, skip the 3-lens fan-out and run a single Reviewer-model Goldfish pass combining all three lenses directly into the Step 3 `Accepted` / `Rejected` / `Backlog` format (keeping all 9 Synthesizer gates and ADR-005 citation verification intact).

## 3. Synthesize

Once all three lenses complete, launch one fresh Reviewer-model Goldfish process with `references/synthesizer.md` (passing `<TRANSCRIPT_PATH>`, `<TARGET_REPO_PATH>`, and the three lens output paths via a scratch prompt file).

The Synthesizer:
1. Spot-verifies cited quotes, turn numbers, target `SKILL.md` files, and target-repo harness/steering files directly from disk (ADR-005 D6 evidence discipline).
2. Applies all 9 gates (`durability`, `specificity`, `existing-skill-first`, `convergence`, `decision-changing`, `structural-mechanism check`, `scope-purity`, `used-surface`, `already-covered`).
3. Returns the exact `## Accepted`, `## Rejected`, and `## Backlog` report with explicit `Thinker` vs `Target Repo` scope tags.

## 4. Structural enforcement check

Move any `Accepted` item that architecture, types, a lint rule, script, metadata flag, or runtime check would enforce more reliably to `Backlog`. *If the fix is structural, only use the structural fix—prose is the symptom.*
- Target-repo code, types, lint, CI, or behavioral tests → `Backlog` → **`/correct <TARGET_REPO_PATH>`**.
- Target-repo runtime verification harness drift (`docs/ui/surface-map/`, `scripts/verify-*`, `.agents/skills/verify-*`) → route to **`maintain-verification-harness`** (or explicit target harness task).
- Thinker tooling (`scripts/goldfish-runner.ts`, `scripts/okf.ts`, etc.) → Thinker tooling `Backlog`.

## 5. Apply (Human Approval & Cross-Repo Ownership Gate)

Present the Synthesizer's full `Accepted` / `Rejected` / `Backlog` output and **wait for explicit operator approval** before applying any edit, running a harness pass, or filing any backlog item. The operator picks the subset and may redirect routings. Changes affect every future run—never auto-apply.

**Cross-Repo Source-of-Truth Guardrails:**
- **Read-only built-ins**: Never edit built-in Antigravity skills (`~/.gemini/antigravity-cli/builtin/skills/`).
- **Thinker vs `sirius-skills`**: Check `thinker`'s `package.json` (`sirius-skills.skills` vs `sirius-skills.preserveSkills`). Local `preserveSkills` edit at `skills/<name>/SKILL.md`; synced skills show their upstream source (`../skills/sirius-skills/skills/<name>/SKILL.md`) before approval so edits do not drift out of sync with `bun run sync:skills:check`.
- **Target repo harness & Zero Repo Pollution (ADR-003)**:
  - Keep generic cross-project rules in `thinker` / `sirius-skills`, and keep repo-specific gotchas, runtime recipes, and steering in `<TARGET_REPO_PATH>`—never leak target-repo trivia into shared skills, and never create Thinker-only config files (e.g., `.thinker.yaml`) in `<TARGET_REPO_PATH>`.
  - Target-owned docs (`<target>/AGENTS.md`, `<target>/CODING_STANDARDS.md`, `<target>/docs/ui/surface-map/`, `<target>/.agents/skills/*/SKILL.md`): edit directly only after operator approval.
  - Target executable harness scripts (`<target>/scripts/verify-*`) or repo guardrails: route through **`maintain-verification-harness`** or a scoped Builder worktree (**`/correct <TARGET_REPO_PATH>`** → PB-3)—Thinker does not directly mutate target application/build code.
- Never commit or push automatically without explicit operator approval.

Follow each approved row's Routing:
- **Existing skill edit (`<skill path> + <section>`)**: Apply trivial edits directly; for substantive edits (>~10 lines), keep `SKILL.md` concise and disclose bulky detail into `references/`.
- **`tune description: <skill path>`**: Tighten frontmatter `description` triggers so the skill fires reliably next time without bloating always-loaded context.
- **`target harness: <target path> + <section>`** (or **`maintain-verification-harness`**): Apply approved doc/surface-map/local-skill updates in `<TARGET_REPO_PATH>`, or run `maintain-verification-harness` for live-verified harness drift.
- **`new skill: <kebab-name>`**: Rare; create only on explicit approval at its declared scope (Thinker/`sirius-skills` or `<TARGET_REPO_PATH>/.agents/skills/`).
- **Approved Backlog items**: Hand off target-repo recurring mistake classes to **`/correct <TARGET_REPO_PATH>`**, or file issues via `github-issue-workflow` if requested.

After approved Thinker/`sirius-skills` edits, verify with `bun run sync:skills:check` (and `bun test` if scripts/tests changed).

## 6. Summarize for the operator

Short list, no preamble:
- **Thinker / skill edits applied**: `<skill path>` — what changed, one line each.
- **Target-repo harness edits applied**: `<target path>` — what changed, one line each.
- **New skills created**: `<skill path>` — one line each (rare).
- **Backlog / `/correct` / `maintain-verification-harness` follow-ups**: `<item>` — one line each.
- **Dropped**: one line per rejected finding + reason from the Synthesizer.
