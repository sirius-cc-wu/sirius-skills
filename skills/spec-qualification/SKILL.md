---
name: spec-qualification
description: Qualifies an implemented change, Worker Execution Report, and git diff against its governing behavioral specification (contracts, rules), anti-phantom call paths, and Architecture Decision Records (ADRs) to issue a binary Verified or Unverified verdict without executing builds directly.
---

# Spec Qualification

## Overview

`spec-qualification` audits an implemented change to confirm that it strictly fulfills its governing behavioral specifications and preserves architectural invariants.

It is a **contractual acceptance gate**, distinct from general code review (`code-review-and-quality`):
- `code-review-and-quality` evaluates **code craftsmanship & health** (readability, simplicity, security, maintainability).
- `spec-qualification` evaluates **contractual conformance** (rule traceability, assertion authenticity, ADR invariants, anti-phantom call paths).

### The Independent Inspector Rule
The evaluator operates as a **non-executing inspector**:
- **Cognitive & Context Isolation**: The evaluator must be independent of the author/implementer and operate with read-only inspection tools.
- **Evidence-Based Inspection**: The evaluator audits the code diff and execution receipts (test logs, pass/fail counts, coverage evidence). It does not compile or run test runners directly.
- **Dual Audit Pairing**: Run concurrently with `code-review-and-quality` so that contract qualification and code craftsmanship are evaluated together.

---

## Required Ingest Artifacts

Before qualifying a change, obtain and review:
1. **Normative Behavioral Specification**: System operations, postconditions, and Example Mapping rules ($R_1, R_2, \dots$).
2. **Governing Architecture Decision Record (ADR)**: Boundary invariants, prohibited shortcuts, and layer rules.
3. **Execution Report**: Test runner output, pass/fail counts, and commit hashes.
4. **Code Diff**: All modified production and test files.

---

## The Four Qualification Criteria

### 1. Rule Traceability (100% Coverage)
- Every specification rule ($R_1, R_2, \dots$) must map to an explicit, passing automated test.
- Negative edge cases and boundary conditions must be explicitly verified with expected error states.
- Zero unverified or skipped specification rules allowed.

### 2. Assertion Authenticity
- Inspect test source code: tests must prove observable postconditions, state transitions, or domain events.
- Reject vacuous assertions (e.g. `expect(true).toBe(true)`), tautologies, or assertions that test only mock mechanics rather than domain outcomes.

### 3. ADR Invariant Fidelity
- Inspect production code diff against governing ADRs.
- Verify that declared architectural boundaries (e.g. Hexagonal ports & adapters, domain isolation, aggregate consistency boundaries) are preserved.
- Reject unauthorized shortcuts, bypassing of defined adapters, or unapproved dependencies.

### 4. Anti-Phantom Call Paths (Live Integration)
- Trace the static and dynamic call graph of all newly introduced production functions, methods, and configurations.
- Verify that every new capability has an active caller in production runtime paths.
- Any function or method called solely by unit tests or test mocks is dead code / a phantom feature and must be rejected (`UNVERIFIED`).

---

## Workflow

```text
Execution Report + Diff
           │
           ▼
[Step 1: Rule Traceability] ──────► Map every spec rule (R1, R2...) to tests
           │
           ▼
[Step 2: Assertion Authenticity] ─► Verify tests prove real domain postconditions
           │
           ▼
[Step 3: ADR Invariant Audit] ────► Verify declared architectural constraints
           │
           ▼
[Step 4: Anti-Phantom Audit] ─────► Verify live production callers for all new code
           │
           ▼
[Step 5: Verdict & Report] ───────► Issue VERIFIED or UNVERIFIED with report
```

---

## Verdicts & Return Routing

Verdicts are strictly binary: **`VERIFIED`** or **`UNVERIFIED`**.

### When `VERIFIED`
All specification rules have authentic passing test evidence, ADR invariants are preserved, and anti-phantom call path checks pass. Mark task as complete and unblock downstream integration.

### When `UNVERIFIED`
Route findings deterministically to the responsible phase:

| Failure Category | Root Cause | Return Destination | Action Required |
| :--- | :--- | :--- | :--- |
| **Implementation Defect** | Test failed, vacuous assertion, missing edge case | **Implementation** | Fix implementation or add genuine test assertions. |
| **Phantom Code** | New production function has no caller outside unit tests | **Implementation** | Connect capability to live execution path or remove dead code. |
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

## 3. Test Integrity & Assertion Authenticity
- [ ] Every rule maps to a genuine passing automated test.
- [ ] Assertions verify observable state changes/events, not mock mechanics.
- [ ] Zero vacuous, tautological, or skipped tests.

## 4. Architectural Invariant Audit (ADR Compliance)
- [ ] Governing ADR invariants and boundaries are strictly maintained.
- [ ] Domain logic remains isolated from transport/persistence.
- [ ] Zero unauthorized dependencies or bypassed adapters.

## 5. Anti-Phantom Call-Path Audit
- [ ] Every new production function/method has an active caller in live runtime code.
- [ ] Zero functions called solely by unit tests or mocks.

## 6. Findings & Return Path (if UNVERIFIED)
- **Failure Category**: `[Implementation Defect | Phantom Code | Architectural Breach | Specification Gap | Architectural Defect]`
- **Return Destination**: `[Implementation | Requirements / Contracts | Architecture / ADR]`
- **Action Items**:
  1. [Specific issue that must be addressed before re-qualification]

## 7. Conclusion
[Clear summary explaining why the change is verified or what steps are required next.]
```
