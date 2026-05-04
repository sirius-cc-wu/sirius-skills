---
name: governance-update
description: Tightens durable repo-level rules in AGENTS.md and adjacent governance surfaces when repeated drift reveals a policy gap.
---

# Governance Update

Use this skill when the real fix is a repository rule change, not only a one-off
artifact rewrite.

Read these references when relevant:

- `references/config-surface-governance.md` when the governance change touches
  configuration, startup, compatibility boundaries, environment injection, or
  test harness inputs

## Responsibilities

1. Read the current governance surfaces and the concrete examples that exposed a
   policy gap.
2. Decide whether the problem belongs in governance at all or should remain a
   one-off artifact/code change.
3. Update the narrowest durable surface that should own the rule, such as
   `AGENTS.md`, `.skills/conventions.json`, or closely related top-level docs.
4. Keep rules specific, minimal, and enforceable instead of adding broad
   preference lists.
5. When the gap is really about workflow ownership, say which skill or surface
   should enforce the rule and which surfaces should only document it.
6. Explain the intended future behavior change and explicit non-goals.

## Preferred Inputs

- one repeated problem pattern or source of drift
- 1-3 concrete examples that show the gap
- an optional target surface such as `AGENTS.md` or `.skills/conventions.json`
- context about whether the rule should stay generic or become repo-local

## Workflow

1. Read the current governance surfaces first:
   - nearest `AGENTS.md`
   - relevant `.skills/*.json` files when they already own conventions or
     workflow behavior
   - top-level docs that describe the same workflow, skill family, or policy
2. Read the concrete artifacts, diffs, or examples that motivated the update.
3. Decide whether a governance change is the right fix:
   - if the issue is isolated, prefer a local artifact change and stop
   - if the issue is repeated or likely to recur, continue
4. Choose the narrowest durable owner:
   - prefer extending an existing section over creating a new scattered rule
   - prefer one control surface per policy
5. Draft or revise the rule so it is:
   - concrete enough to guide future work
   - short enough to stay readable
   - generic-first unless the repository explicitly needs local policy
6. When the gap is recurring design-versus-execution drift at feature closeout,
   prefer a rule that requires canonical design reconciliation before archive
   and name the owner boundary explicitly.
7. Update any top-level docs or examples that enumerate the affected governance
   surface or promise the old behavior.
8. Summarize:
   - the governance surface updated
   - the new or changed rule
   - what future behavior it should steer
   - what remains intentionally out of scope

## Guardrails

- Do not add policy for one-off incidents that are unlikely to recur.
- Do not create duplicate rule owners for the same concern.
- Prefer editing an existing section over adding many small sections.
- Keep shared skills generic; do not hardcode company-specific trackers, naming
  rules, or workflow steps unless the repo explicitly opts into them.
- Prefer defaults, heuristics, and examples over giant checklists.
- If the policy is "reconcile before archive," keep governance focused on the
  rule and owner boundaries; do not move archive or reconciliation logic into
  `governance-update` itself.
- Treat new configuration surfaces as suspicious; if governance touches config,
  preserve existing typed ownership and document the owning boundary clearly.
- If a better fix is “update one artifact” or “create one new skill,” say so
  explicitly instead of forcing a governance rule.

## Output Checklist

1. Governance surface updated.
2. Problem pattern and examples reviewed.
3. Rule added or refined.
4. Expected future behavior change and explicit non-goals.
