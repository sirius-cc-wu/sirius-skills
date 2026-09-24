---
name: audit-vestigial-contracts
description: Audits code changes and diffs for removed features, configs, or tokens to identify residual passthroughs, orphaned parameters, and vestigial test scaffolding for human-approved pruning.
---

# Audit Vestigial Contracts

Audits codebases and diffs for dead contracts, wrappers, and test residue left behind after a feature, configuration, or environment variable is removed.

> **Safety Invariant:** Never modify or delete tests autonomously. Pruning requires explicit human approval and belongs in a dedicated cleanup PR.

## When to Use

- When reviewing a PR or commit range where a configuration, token, or feature was removed or deprecated.
- When evaluating if an interface parameter or wrapper is still necessary.
- Do not use for routine refactoring without feature deprecation or removal.

## Workflow

1. **Extract Deleted Tokens:** Scan diffs (and commit messages) for removed environment variables (`os.environ`), config keys, CLI flags, or API arguments.
2. **Inspect Enclosing Helpers:** Check if functions touching those deletions degraded into trivial passthroughs, redundant wrappers around static constants, or private helpers with no external callers.
3. **Trace Parameter Propagation:** Check all call sites of the degraded helper and its arguments across the codebase. If an argument (e.g., `candidate_ips`) is never varied by production callers, flag it as an **orphaned parameter**.
4. **Audit Test & Mock Coupling:** Inspect existing AND newly added/modified tests for:
   - *Ignored-Token Tests:* Assertions verifying that a removed token is ignored (e.g., `setenv("LEGACY_VAR")`). Flag even when bundled inside compound tests.
   - *Private Helper Coupling:* Unit tests targeting private resolution helpers rather than public entrypoint contracts.
   - *Tautological Tests:* Asserting standard library behavior on hardcoded constants.
   - *Plumbing Mocks:* Mocking internal parameter forwarding instead of domain behavior.
5. **Present Proposal for Human Approval:** Report deleted tokens, degraded helpers, orphaned parameters, affected tests/assertions, and blast radius.
6. **Execute in Dedicated PR:** Upon human approval, create a separate cleanup branch/PR to prune dead wrappers, parameters, and obsolete assertions, verifying the suite passes cleanly.

## Report Format

Present findings succinctly:
- **Removed Token:** `<token>` (`<commit/PR>`)
- **Degraded Helpers:** `function()` in `file:line` (trivial wrapper / private coupling)
- **Orphaned Parameters:** `param` across call chain (never varied)
- **Vestigial Tests:** `test_name` in `file:line` (ignored-token assertion / private helper coupling / plumbing mock)
- **Blast Radius & Plan:** Proposed files to edit and tests/assertions to prune
