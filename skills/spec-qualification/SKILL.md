---
name: spec-qualification
description: Qualifies an implemented task slice against its governing normative specification (SSD contracts and Example Mapping rules) and Architecture Decision Record (ADR). Audits implementation execution reports and git diffs across behavioral, architectural, and code quality dimensions to issue a Verified or Unverified verdict without executing builds directly.
---

# Spec Qualification (Acceptance Gate)

## Overview & Grounding in ISO 26262-6

`spec-qualification` is the acceptance gate that closes the **Spec–Validate Loop**. It qualifies that an implementation fulfills its governing behavioral specification and adheres strictly to architectural invariants.

### Grounding in the ISO 26262-6 V-Model
`spec-qualification` operationalizes the software verification and qualification principles of **ISO 26262-6 (Road vehicles — Functional safety, Part 6: Product development at the software level)**:

```text
               ISO 26262-6 V-Model                         Two-Gate Verification Architecture
─────────────────────────────────────────────────   ────────────────────────────────────────────────────────
Software Safety Requirements (Clause 6)             Stage 1: Requirements (Example Mapping R1, R2...)
         \                               /                   \                                 /
          \                             /                     \                               /
      Software Architecture (Clause 7)             Stage 3: Architecture & ADR Invariants
               \               /                               \                           /
                \             /                                 \                         /
            Unit Design (Clause 8)                       Stage 4: Execution Tasks (<module-id>.md)
                     \   /                                         \                     /
                   Coding                                       Implementation (TDD: Red → Green → Clean)
                     |                                                     |
            [Bottom of the V]                                     [Commits & Execution Report]
                     |                                                     |
             Unit Verification (Clause 9)                Gate 2 Pillar 3: Code Health & Anti-Phantom Paths
                     /   \                                         \                     /
                    /     \                                         \                   /
   Integration Verification (Clause 10)                 Gate 2 Pillar 2: Architectural Audit (ADRs)
                  /         \                                         \               /
                 /           \                                         \             /
    Software Qualification (Clause 11)                   Gate 2 Pillar 1: Behavioral Audit (100% Rule Matrix)
```

1. **Software Qualification (Clause 11) $\longleftrightarrow$ Pillar 1 (Behavioral Compliance)**: Black-box verification proving that the integrated software satisfies all functional and safety requirements (100% Example Mapping rules).
2. **Software Integration & Verification (Clause 10) $\longleftrightarrow$ Pillar 2 (Architectural Audit)**: Verifies that software components adhere to defined interfaces, hexagonal layers, and binding ADR invariants.
3. **Software Unit Verification & Static Analysis (Clause 9) $\longleftrightarrow$ Pillar 3 (Code Health & Quality)**: Static verification auditing anti-phantom call paths (no dead code), memory/resource safety, and simplicity.
4. **Bidirectional Traceability (Clauses 6.4.3 & 7.4.3)**: Every delivered test case must explicitly trace back to a specific requirement rule ($R_x$) and architecture contract.
5. **Evaluator Independence (ASIL C/D Mandate)**: ISO 26262 requires organizational and cognitive independence for verification. The author or agent who writes code is strictly forbidden from self-qualifying; qualification must be executed by an independent evaluator in an isolated context.

### Non-Executing Inspector Protocol
The qualification evaluator operates as a **non-executing inspector**. It **DOES NOT** execute local build commands, compile code, or run test runners directly.
* **The Implementer (Author)** owns execution: running compilers, executing test suites, capturing runtime logs, and providing an execution report with verifiable test results.
* **The Evaluator (Reviewer)** owns inspection: operating with read-only inspection capabilities in an isolated context to objectively audit delivered diffs, test assertion authenticity, and structural coverage. Specific runner harnesses and model assignments are governed by repository orchestration policy (e.g. `AGENTS.md`).
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
3. **Implementation Execution Report**:
   - Verification matrix mapping rules to test locations.
   - Exact test runner output with execution times and pass counts.
   - List of atomic commit hashes.
4. **Git Diff / Revision**:
   - The actual code changes across production and test files.

---

## The Three-Pillar Qualification Audit

Every qualification evaluates the delivered slice across three strict pillars aligned with ISO 26262-6:

### 1. Behavioral Audit (ISO 26262-6 Clause 11: Software Qualification Testing)
Verify that the delivered code fulfills 100% of the observable contract:
- **Rule Exhaustiveness**: Does every Example Mapping rule ($R_1, R_2, \dots$) have a corresponding, passing automated test?
- **Assertion Authenticity**: Inspect the test source code. Do the tests actually verify the expected state changes and postconditions, or are they vacuous/tautological assertions?
- **Error & Negative Paths**: Are negative edge cases (e.g., duplicate idempotency key, boundary overflow, invalid signals, communication timeouts) verified with expected error codes and safe state transitions?
- **Precondition & Postcondition Invariants**: Does the system reject operations when preconditions fail? Are domain events or state changes emitted as specified?

### 2. Architectural Audit (ISO 26262-6 Clause 10: Software Integration & Verification)
Verify that the implementation obeys the architectural law established in the ADR:
- **Clean Layering (Hexagonal / Ports & Adapters)**:
  - Do domain entities remain pure (free from database, ORM, framework, or HTTP transport decorators/dependencies)?
  - Are external boundaries isolated behind explicit ports and adapters?
- **Aggregate Consistency**:
  - Are invariants guarded at the Aggregate root?
  - Are there direct mutations across aggregate boundaries that violate transaction isolation?
- **No Architectural Drift / Forbidden Shortcuts**:
  - Were unauthorized dependencies introduced, defined adapters bypassed, or unapproved global state added?

### 3. Code Health & Unit Audit (ISO 26262-6 Clause 9: Software Unit Verification & Static Analysis)
Evaluate code structure using `code-review-and-quality` guidelines:
- **Anti-Phantom Call-Path Verification**: Inspect the call graph of all new methods, types, and configurations. Verify that every newly introduced function has an active, executing caller in production runtime code. Any function or method called solely by unit tests or mocks is dead code / phantom implementation and must be rejected (`UNVERIFIED`).
- **Simplicity**: Is the implementation the minimal required logic, or is there speculative generalization?
- **Dead Code Hygiene**: Are there leftover debug statements, unused shims, commented-out code, or unreferenced helpers?
- **Security & Safety**: Are user inputs validated at boundaries? Are secrets absent from code and logs?

### 4. Structural Coverage (ISO 26262-6 Table 12 & Table 15 Guidance)
For software governing real-time motion, actuators, hardware bus communication (e.g., EtherCAT, CANopen), or safety-critical state machines:
- **Requirement-Based Coverage**: 100% of Example Mapping rules ($R_1, R_2, \dots$) is mandatory across all tiers.
- **Structural Coverage Evidence**: For safety-critical modules, the execution report should supply automated structural coverage metrics (e.g. `llvm-cov`, `cargo-tarpaulin`, `istanbul`/`c8`):
  - **Statement Coverage**: Proves zero dead code branches in production modules.
  - **Branch / Decision Coverage**: Proves all conditionals evaluate both true and false.
  - **MC/DC (Modified Condition/Decision Coverage)**: Recommended for high-integrity safety logic where multiple boolean conditions govern critical actuations.

---

## Workflow

```text
Implementation Execution Report + Diff
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

1. **Ingest & Trace**: Map each rule from the spec's Example Mapping table ($R_1, R_2, \dots$) to the reported test cases. Flag any missing or skipped rule immediately.
2. **Test Integrity Audit**: Read the test files in the diff. Confirm that:
   - Tests follow RED-GREEN discipline (testing real behavior, not internal implementation details).
   - Mocking is restricted to external ports; domain logic is tested with real domain objects.
3. **ADR Invariant Audit**: Inspect production code diff against the governing ADR. Check module boundaries and package imports.
4. **Code Quality Review**: Check for code cleanliness, descriptive naming, error handling, and security boundary sanitization.
5. **Issue Verdict & Report**: Author the permanent qualification report in the target project's canonical qualification or verification documentation location.

---

## Verdicts & Return Routing (Causal V-Model Feedback)

In accordance with ISO 26262 defect management, when an issue is detected, it must be traced back to the exact abstraction level on the left side of the V that introduced the defect:

The verdict must be strictly binary: **`VERIFIED`** or **`UNVERIFIED`**.

### When `VERIFIED`
All rules have genuine passing test evidence, ADR invariants are preserved, anti-phantom call path checks pass, and code quality is approved.
* **Action**: Mark task slice as complete in task board. Unblock dependent slices or trigger merge.

### When `UNVERIFIED`
Route findings deterministically to the smallest responsible phase on the left side of the V:

| Failure Category | ISO 26262 Defect Source | Root Cause | Return Path | Action Required |
| :--- | :--- | :--- | :--- | :--- |
| **Execution Defect** | Clause 8 / 9 (Unit Design & Implementation) | Test failed, assertion flawed, missing edge case test | **Implementation / Unit Design** | Implementer re-enters RED-GREEN cycle to fix implementation or add missing test coverage. |
| **Architectural Breach** | Clause 7 / 10 (Architectural Design & Integration) | Domain leaks DB/HTTP/transport, violated ADR pattern, unauthorized dependency | **Implementation / Integration** | Implementer refactors to comply with governing ADR invariant. |
| **Specification Gap** | Clause 6 / 11 (Software Safety Requirements) | Spec has contradictory rules, missing error contract, or unrealistic precondition | **Requirements & Contracts (Stage 1/2)** | Return to `example-mapping` or `system-behavior` to revise the specification. |
| **Architectural Defect** | Clause 7 (Architectural Design) | ADR decision proves infeasible or conflicts with system constraints | **System Architecture & ADRs (Stage 3)** | Return to `architecture-decision-records` to author an amending ADR. |

---

## Durable Qualification Report Template

Save all qualification reports in the target project's canonical qualification or verification documentation location:

```markdown
---
type: Qualification Report
slice: "[target-project canonical specification path]"
governing_adr: "[target-project canonical ADR path]"
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

## 2. Behavioral Compliance Matrix (Example Mapping)
| Rule # | Rule Description | Implementation Test Case | Test Status | Audit Assessment |
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
- [ ] Anti-phantom call-path verified (zero uncalled production functions).
- [ ] No dead code, debug statements, or temporary shims.
- [ ] Inputs validated and sanitized at boundaries.

## 6. Structural & Code Coverage Audit (if safety-critical)
- [ ] Statement coverage: `[XX]%` (target: 100% of modified production code)
- [ ] Branch/Decision coverage: `[XX]%`
- [ ] Zero uninstrumented dead code or unhandled conditional branches.

## 7. Findings & Return Path (if UNVERIFIED)
- **Failure Category**: `[Execution Defect | Architectural Breach | Specification Gap]`
- **ISO 26262 Defect Source**: `[Clause 6 Requirements | Clause 7 Architecture | Clause 8/9 Unit]`
- **Return Destination**: `[Implementation | Requirements | Architecture]`
- **Action Items**:
  1. [Specific issue that must be addressed before re-qualification]

## 8. Conclusion & Next Steps
[Detailed conclusion explaining why the slice is verified or what steps are required next.]
```
