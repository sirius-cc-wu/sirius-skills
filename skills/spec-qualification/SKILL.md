---
name: spec-qualification
description: Qualifies an implemented task slice against its governing normative specification (SSD contracts and Example Mapping rules) and Architecture Decision Record (ADR). Audits Worker Execution Reports and git diffs across behavioral, architectural, and code quality dimensions to issue a Verified or Unverified verdict without executing builds directly.
---

# Spec Qualification (Phase 6 Acceptance Gate)

## Overview & The Thinker Boundary

`spec-qualification` is the acceptance gate that closes the **Spec–Validate Loop** in `thinker`. It qualifies that an implementation produced by a downstream Worker fulfills the behavioral specification and adheres strictly to architectural invariants.

### Non-Executing Inspector Protocol & Model Mandate
As the **Thinker Engine**, you **DO NOT** execute local build commands, compile code, or run test runners yourself.
* **The Worker** owns execution: running compilers, executing tests, capturing logs, and producing a `Worker Execution Report`. Workers are always implemented using **Gemini 3.8 Flash (High)**.
* **The Thinker / Reviewer** owns qualification: running via **Codex CLI (`codex exec -m gpt-5.6-sol -c model_reasoning_effort="xhigh" --sandbox read-only`)** and **agy CLI (`agy --model gemini-3.8-flash-high --dangerously-skip-permissions -p "..."`)** in isolated processes/context windows.
* **Mandatory Dual-Skill Pairing**: Qualification MUST always execute both `spec-qualification` and `code-review-and-quality` concurrently to combine behavioral contract validation with multi-axis static and architectural audit.

---

## Required Ingest Artifacts

Before qualifying a slice, obtain and review:

1. **Normative Behavioral Specification** (at the target project's canonical specification or use-case location):
   - Actor goal and System Behavioral Contract (SSD operations, inputs, outputs, postconditions).
   - Business Rules and Example Mapping table ($R_1, R_2, R_3, \dots$).
2. **Governing Architecture Decision Record** (at the target project's canonical decision location):
   - Architectural pattern (e.g., Hexagonal / Ports & Adapters).
   - Forbidden shortcuts, invariants, and accepted trade-offs.
3. **Worker Execution Report**:
   - Verification matrix mapping rules to test locations.
   - Exact test runner output with execution times and pass counts.
   - List of atomic commit hashes.
4. **Git Diff / Revision**:
   - The actual code changes produced by the Worker across production and test files.

---

## The Three-Pillar Qualification Audit

Every qualification evaluates the delivered slice across three strict pillars:

### 1. Behavioral Audit (Specification Compliance)
Verify that the delivered code fulfills 100% of the observable contract:
- **Rule Exhaustiveness**: Does every Example Mapping rule ($R_1, R_2, \dots$) have a corresponding, passing automated test?
- **Assertion Authenticity**: Inspect the test source code. Do the tests actually verify the expected state changes and postconditions, or are they vacuous/tautological assertions?
- **Error & Edge Paths**: Are negative edge cases (e.g., duplicate idempotency key, boundary overflow, invalid types) verified with expected error codes?
- **Precondition & Postcondition Invariants**: Does the system reject operations when preconditions fail? Are domain events or state changes emitted as specified?

### 2. Architectural Audit (ADR Compliance)
Verify that the implementation obeys the architectural law established in the ADR:
- **Clean Layering (Hexagonal / Ports & Adapters)**:
  - Do domain entities remain pure (free from database, ORM, framework, or HTTP transport decorators/dependencies)?
  - Are external boundaries isolated behind explicit ports and adapters?
- **Aggregate Consistency**:
  - Are invariants guarded at the Aggregate root?
  - Are there direct mutations across aggregate boundaries that violate transaction isolation?
- **No Architectural Drift / Forbidden Shortcuts**:
  - Did the worker introduce unauthorized dependencies, bypass defined adapters, or add unapproved global state?

### 3. Code Health & Quality Audit
Evaluate code structure using `code-review-and-quality` guidelines:
- **Anti-Phantom Call-Path Verification**: Inspect the call graph of all new methods, types, and configurations. Verify that every newly introduced function has an active, executing caller in production runtime code. Any function or method called solely by unit tests or mocks is dead code / phantom implementation and must be rejected (`UNVERIFIED`).
- **Simplicity**: Did the worker implement the minimal required logic, or is there speculative generalization?
- **Dead Code Hygiene**: Are there leftover debug statements, unused shims, commented-out code, or unreferenced helpers?
- **Security & Safety**: Are user inputs validated at boundaries? Are secrets absent from code and logs?

---

## Workflow

```text
Worker Execution Report + Diff
             │
             ▼
  [Step 1: Ingest & Trace] ──────────► Verify 100% Example Mapping rules covered
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
  [Step 5: Verdict & Routing] ──────► Issue VERIFIED or UNVERIFIED with report
```

1. **Ingest & Trace**: Map each rule from the spec's Example Mapping table ($R_1, R_2, \dots$) to the Worker's reported test cases. Flag any missing or skipped rule immediately.
2. **Test Integrity Audit**: Read the test files in the diff. Confirm that:
   - Tests follow RED-GREEN discipline (testing real behavior, not internal implementation details).
   - Mocking is restricted to external ports; domain logic is tested with real domain objects.
3. **ADR Invariant Audit**: Inspect production code diff against the governing ADR. Check module boundaries and package imports.
4. **Code Quality Review**: Check for code cleanliness, descriptive naming, error handling, and security boundary sanitization.
5. **Issue Verdict & Report**: Author the permanent qualification report in the target project's canonical qualification or verification documentation location.

---

## Verdicts & Return Routing

The verdict must be strictly binary: **`VERIFIED`** or **`UNVERIFIED`**.

### When `VERIFIED`
All rules have genuine passing test evidence, ADR invariants are preserved, and code quality is approved.
* **Action**: Mark task slice as complete in task board. Unblock dependent slices or trigger merge.

### When `UNVERIFIED`
Route findings deterministically to the smallest responsible phase:

| Failure Category | Root Cause | Return Path | Action Required |
| :--- | :--- | :--- | :--- |
| **Execution Defect** | Test failed, assertion flawed, missing edge case test | **Worker (Builder)** | Worker re-enters RED-GREEN cycle to fix implementation or add missing test coverage. |
| **Architectural Breach** | Domain leaks DB/HTTP, violated ADR pattern, unauthorized dependency | **Worker (Builder)** | Worker refactors to comply with governing ADR invariant. |
| **Specification Gap** | Spec has contradictory rules, missing error contract, or unrealistic precondition | **Thinker (Phase 1/2)** | Return to `example-mapping` or `system-behavior` to revise the specification. |
| **Architectural Defect** | ADR decision proves infeasible or conflicts with system constraints | **Thinker (Phase 3)** | Return to `architecture-decision-records` to author an amending ADR. |

---

## Durable Qualification Report Template

Save all qualification reports in the target project's canonical qualification or verification documentation location:

```markdown
---
type: Qualification Report
slice: "[target-project canonical specification path]"
governing_adr: "[target-project canonical ADR path]"
worker_revision: "[commit SHA]"
verdict: "[VERIFIED | UNVERIFIED]"
date: "YYYY-MM-DD"
---

# Qualification Report: [Slice Name]

## 1. Executive Summary
- **Governing Spec**: `[spec path]`
- **Governing ADR**: `[adr path]`
- **Worker Revision**: `[commit SHA]`
- **Final Verdict**: **[VERIFIED | UNVERIFIED]**

## 2. Behavioral Compliance Matrix (Example Mapping)
| Rule # | Rule Description | Worker Test Case | Test Status | Audit Assessment |
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
- [ ] No dead code, debug statements, or temporary shims.
- [ ] Inputs validated and sanitized at boundaries.

## 6. Findings & Return Path (if UNVERIFIED)
- **Failure Category**: `[Execution Defect | Architectural Breach | Specification Gap]`
- **Return Destination**: `[Worker | Thinker Phase 1/2/3]`
- **Action Items**:
  1. [Specific issue that must be addressed before re-qualification]

## 7. Conclusion & Next Steps
[Detailed conclusion explaining why the slice is verified or what steps are required next.]
```
