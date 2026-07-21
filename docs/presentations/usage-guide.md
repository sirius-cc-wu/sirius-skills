# Sirius Skills: Focused Repository Workflows

The managed collection now contains four generic skills. The former
spec-driven development workflow has been retired from the catalog.

## The four skills

- `simplify`: make a focused cleanup pass over a branch or pull-request diff
  without intentionally changing behavior
- `commit`: verify and commit only the intended change set using repository
  conventions
- `create-pr`: validate branch state and open a well-described GitHub pull
  request
- `governance-update`: improve durable repository rules when repeated drift
  reveals a genuine policy gap

## A common flow

```text
implement and verify -> simplify -> commit -> create-pr
```

`governance-update` is not a routine gate in that sequence. Use it separately
when multiple concrete examples justify a lasting rule.

## Installation

```bash
just install
```

The install target registers only the four skills above. Remove them with:

```bash
just uninstall
```

Repository-specific commit and pull-request formats belong in
`.skills/conventions.json`, not in shared skill instructions.
