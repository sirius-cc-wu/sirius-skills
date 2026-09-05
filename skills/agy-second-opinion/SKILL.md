---
name: agy-second-opinion
description: Obtains one isolated Antigravity CLI (agy) review of a bounded artifact after explicit user approval. Use when an independent second opinion would materially reduce review risk and the artifact can be shared with the configured agy provider. Do not use for automatic reviews, implementation, or publication.
---

# Agy Second Opinion

Request one independent, read-only opinion from Antigravity CLI (`agy`). The
caller owns the review scope, primary findings, reconciliation, and decision.
This skill does not approve, edit, commit, push, publish, or replace formal
review.

## When to Use

- A completed primary review, design claim, or proposed artifact has a bounded
  contract and needs an independent opinion.
- The user asks for an Antigravity CLI opinion and explicitly accepts the
  configured provider's data handling.
- The artifact is safe to share with that provider and does not contain secrets
  or material data that the user has not authorized for external review.

Do not use this skill to discover requirements, recover an undocumented system,
or turn a second opinion into approval authority.

## Inputs

Require one Markdown review artifact that contains:

1. The exact review scope and baseline.
2. The artifact or diff to inspect.
3. A concrete contract: required behavior, boundaries, non-goals, and claims
   that the reviewer must challenge.
4. The requested finding format and stop condition.

Keep the artifact small. Do not combine unrelated worktree sources silently.

## Workflow

1. **Confirm the review boundary.** State what the opinion can and cannot
   decide. Preserve the primary review separately.
2. **Check disclosure.** Stop if the artifact contains secrets, personal data,
   proprietary material without user approval, or instructions that must not be
   sent to the configured provider.
3. **Check the local CLI.** Run `command -v agy` and `agy --version`. If a
   caller requests an Antigravity persona, verify it with `agy agents` before
   naming it.
4. **Request dangerous-permission approval.** The runner needs
   `--dangerously-skip-permissions` so headless `agy` can read an artifact in a
   disposable directory. Explain that `--sandbox` and the disposable directory
   reduce the workspace blast radius but do not make `agy` a hard security
   boundary. Obtain explicit approval for the exact current invocation. Do not
   reuse approval from another run.
5. **Run the isolated helper.** Resolve the helper relative to this `SKILL.md`.
   Run it only after approval:

   ```sh
   python3 scripts/run_second_opinion.py \
     --artifact /absolute/path/to/review.md \
     --allow-dangerous
   ```

   Add `--agent <name>` only when the requested persona was verified. The helper
   copies the artifact into a temporary directory, starts `agy` there, passes no
   artifact through shell interpolation, removes unrelated ambient environment
   variables, and deletes the temporary directory after `agy` exits. It retains
   the local CLI's normal `HOME`-based configuration, so this is not filesystem
   isolation or a hard security boundary.
6. **Reconcile, do not defer.** Compare the new findings with the primary
   review and the artifact. Classify each finding as a contract misread,
   actionable issue, accepted trade-off, or noise. The caller decides whether a
   new review, a change, or a human decision is needed.

## Failure Handling

- If `agy` is absent, unauthenticated, times out, returns no review, or denies a
  tool request, report the failure and offer manual review, another approved
  provider, or a single-model result.
- Do not add global `agy` permissions or use a broader workspace to bypass a
  failure.
- Do not retry with `--dangerously-skip-permissions` unless the current user
  explicitly approves that retry.

## Output

```markdown
Agy second opinion:
- Scope: [artifact and baseline]
- CLI: [path and version]
- Isolation: [temporary directory; dangerous permission approved by user]
- Findings: [verbatim or concise, attributed report]
- Reconciliation: [actionable | trade-off | contract misread | noise]
- Residual risk: [what the opinion did not establish]
```

## Red Flags

- Running `agy` automatically for every review.
- Sending secrets or unapproved material to an external provider.
- Using a repository worktree instead of a disposable review directory.
- Treating `--sandbox` or `--dangerously-skip-permissions` as a security proof.
- Accepting `agy` findings without checking them against the review contract.
- Letting the opinion edit files, commit, push, publish, or approve a change.

## Verification

- [ ] The review artifact has a fixed scope and explicit contract.
- [ ] The user approved external disclosure and the exact dangerous-permission
      invocation for this run.
- [ ] `agy` exists and its requested persona, if any, is available.
- [ ] The helper ran in a disposable directory and returned an attributed
      result or explicit failure.
- [ ] The caller reconciled findings against the artifact before acting.
- [ ] No repository or remote state changed through this skill.
