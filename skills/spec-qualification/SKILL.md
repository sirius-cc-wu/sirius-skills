---
name: spec-qualification
description: Qualifies an implemented change against its governing behavioral specification (contracts, rules) and Architecture Decision Records (ADRs) to issue a binary Verified or Unverified verdict without executing builds directly.
---

# Spec Qualification

## Overview

`spec-qualification` audits an implemented change to confirm that it fulfills its governing behavioral specifications and preserves architectural invariants.

### The Independent Inspector Rule
The evaluator operates as a **non-executing inspector**:
- **Cognitive & Context Isolation**: The evaluator must be independent of the author/implementer and operate with read-only inspection tools.
- **Evidence-Based Inspection**: The evaluator audits the code diff and execution receipts (test logs, pass/fail counts, coverage evidence). It does not compile or run test runners directly.
- **Dual Audit Mandate**: Pair with `code-review-and-quality` to concurrently evaluate behavioral compliance, architectural boundaries, and code health.

---

## Required Ingest Artifacts

Before qualifying a change, obtain and review:
1. **Normative Behavioral Specification**: System operations, postconditions, and Example Mapping rules ($R_1, R_2, \dots$).
2. **Governing Architecture Decision Record (ADR)**: Boundary invariants, prohibited shortcuts, and layer rules.
3. **Execution Report**: Test runner output, pass/fail counts, and commit hashes.
4. **Code Diff**: All modified production and test files.

---

## The Three-Pillar Audit

### 1. Behavioral Compliance
- **100% Rule Coverage**: Every specification rule ($R_1, R_2, \dots$) must have an explicit passing automated test.
- **Assertion Authenticity**: Tests must verify real state changes, side-effects, or emitted events—reject vacuous, tautological, or mock-only assertions.
- **Negative & Boundary Paths**: Failure modes (timeouts, bad inputs, invariant violations) must be verified with expected error states.

### 2. Architectural Invariants
- **Layer Boundaries**: Domain logic must remain decoupled from transport, persistence, and external frameworks.
- **Aggregate Integrity**: Mutations must be guarded by aggregate roots without cross-boundary leaks.
- **Zero Architectural Drift**: No unauthorized dependencies, bypassed ports, or unapproved global state.

### 3. Code Health & Anti-Phantom Call Paths
- **Anti-Phantom Call Paths**: Every new production function, method, or configuration must have an active caller in production runtime code. Functions tested solely by unit mocks with no live production caller are dead code (`UNVERIFIED`).
- **Simplicity**: Minimal logic to satisfy the specification—reject speculative generalization.
- **Cleanliness & Security**: Zero debug residue or orphaned shims; boundary inputs must be validated and sanitized.

---

## Workflow

```text
Execution Report + Diff
           │
           ▼
[Step 1: Ingest & Trace] ──────────► Verify 100% specification rules covered
           │
           ▼
[Step 2: Test Integrity Audit] ───► Verify test assertions actually prove behavior
           │
           ▼
[Step 3: ADR Invariant Audit] ────► Verify layering, aggregate boundaries, no drift
           │
           ▼
[Step 4: Code Quality Review] ────► Verify simplicity, security, dead code hygiene
           │
           ▼
[Step 5: Verdict & Report] ───────► Issue VERIFIED or UNVERIFIED with report
```

---

## Verdicts & Return Routing

Verdicts are strictly binary: **`VERIFIED`** or **`UNVERIFIED`**.

### When `VERIFIED`
All rules have genuine passing test evidence, ADR invariants are preserved, anti-phantom checks pass, and code quality is approved. Mark task as complete and unblock downstream integration.

### When `UNVERIFIED`
Route findings deterministically to the responsible phase:

| Failure Category | Root Cause | Return Destination | Action Required |
| :--- | :--- | :--- | :--- |
| **Implementation Defect** | Test failed, vacuous assertion, missing edge case | **Implementation** | Fix implementation or add genuine test assertions. |
| **Architectural Breach** | Violated ADR pattern, unauthorized dependency | **Implementation** | Refactor code to conform to the governing ADR. |
| **Specification Gap** | Contradictory rules, missing error contracts | **Requirements / Contracts** | Clarify or amend the specification rules. |
| **Architectural Defect** | ADR invariant proves infeasible or contradictory | **Architecture / ADR** | Author an amending ADR. |

---

## Qualification Report Template

Save the qualification report in the target project's canonical verification directory (e.g. `docs/verification/qualification-<module-id>.md`):

```markdown
---
type: Qualification Report
slice: "[spec path]"
governing_adr: "[adr path]"
implementation_revision: "[commit SHA]"
verdict: "[VERIFIED | UNVERIFIED]"
date: "YYYY-MM-DD"
---

# Qualification Report: [Slice Name]

## 1. Executive Summary
- **Governing Spec**: `[spec path]`
- **Governing ADR**: `[adr path]`
- **Implementation Revision**: `[commit SHA]`
- **Final Verdict**: **[VERIFIED | UNVERIFIED]**

## 2. Behavioral Compliance Matrix
| Rule # | Rule Description | Test Location | Test Status | Audit Assessment |
| :--- | :--- | :--- | :--- | :--- |
| **R1** | [Happy path description] | `tests/...::test_...` | PASS | Valid assertion of postcondition |
| **R2** | [Edge case description] | `tests/...::test_...` | PASS | Valid rejection handling |
| **R3** | [Boundary description] | `tests/...::test_...` | PASS | Valid boundary check |

## 3. Test Integrity & Assertion Audit
- [ ] Test cases verify observable state/events, not mock mechanics.
- [ ] Test runner evidence is complete and reproducible.
- [ ] Zero unexecuted or skipped tests without explicit sign-off.

## 4. Architectural Invariant Audit (ADR Compliance)
- [ ] Layer boundaries respected (domain is pure, ports & adapters decoupled).
- [ ] Aggregate transaction invariants enforced.
- [ ] No unauthorized dependencies or forbidden shortcuts.

## 5. Code Quality & Security Gate
- [ ] Clean, readable code without speculative complexity.
- [ ] Anti-phantom call paths verified (zero uncalled production functions).
- [ ] No dead code, debug statements, or temporary shims.
- [ ] Inputs validated and sanitized at boundaries.

## 6. Findings & Return Path (if UNVERIFIED)
- **Failure Category**: `[Implementation Defect | Architectural Breach | Specification Gap | Architectural Defect]`
- **Return Destination**: `[Implementation | Requirements / Contracts | Architecture / ADR]`
- **Action Items**:
  1. [Specific issue that must be addressed before re-qualification]

## 7. Conclusion
[Clear summary explaining why the change is verified or what steps are required next.]
```
