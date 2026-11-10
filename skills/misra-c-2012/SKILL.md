---
name: misra-c-2012
description: "Audits, diagnoses, and guides compliance for automotive embedded C code against MISRA C:2012 (Amendments 1–4, ISO 26262-6, AUTOSAR C). Identifies rule violations across essential types, pointers, control flow, and preprocessors; prescribes compliant remediations and formal deviation rationales."
---

# MISRA C:2012 Compliance and Diagnostic

## Overview

Diagnose implementation-level safety, portability, and reliability violations in automotive embedded C codebases (AUTOSAR Classic CP, MCAL, BSW, Complex Device Drivers (CDD), and RTOS microkernels). Grounded in the **MISRA C:2012 Third Edition** standard (incorporating Amendments 1–4 and Technical Corrigenda) and automotive functional safety requirements under **ISO 26262-6:2018 (Clause 8: Software unit design and implementation)**.

Identify non-compliant patterns objectively, classify them across guideline obligation categories (*Mandatory*, *Required*, *Advisory*), and prescribe either mechanical code remedies or formal deviation records with engineering and safety justifications.

Read the [MISRA C:2012 Rule Catalog](references/misra-c-2012-rule-catalog.md) for concrete rule descriptions, essential type models, code examples, and standard deviation rationales.

## When to Use

- **Automotive C Implementation & Review**: Audit new or modified C source code and headers (`.c`, `.h`) across AUTOSAR layers, driver stacks, or ECU application components (e.g., FDC, VCU, BMS, Gateway).
- **Gate 2 Code Qualification**: Perform automated or interactive static audits of pull requests and commits before merge, ensuring no MISRA regressions or undocumented deviations are introduced.
- **Compiler Warning & Static Analysis Triage**: Interpret and resolve findings from static analysis tools (e.g., PC-lint Plus, Axivion, Polyspace Bug Finder, Coverity, Clang-Tidy MISRA) with authoritative rule references.
- **Functional Safety (ISO 26262 ASIL A–D) Auditing**: Verify enforcement of defensive coding, no dynamic memory allocation, bounded loops, and strict type safety required for ASIL qualification.
- **Do not use for**:
  - Pure Modern C++ / Rust codebases (route to language-specific linters or `code-review-and-quality`).
  - Architectural decoupling or cyclic package dependencies (route to [`design-smell`](../design-smell/SKILL.md)).
  - Executing code modifications directly without operator or builder verification (diagnose and prescribe only; hand off implementation to an autonomous builder or [`code-simplification`](../code-simplification/SKILL.md)).

## Related Owners

- Use [`code-smell`](../code-smell/SKILL.md) to diagnose intra-module structural smells (bloaters, couplers, arrow antipatterns) alongside MISRA compliance.
- Use [`code-review-and-quality`](../code-review-and-quality/SKILL.md) for multi-axis pull request reviews (correctness, performance, readability).
- Use [`spec-qualification`](../spec-qualification/SKILL.md) for Gate 2 qualification of implemented behavior against behavioral contracts and ADR invariants.
- Use [`architecture-decision-records`](../architecture-decision-records/SKILL.md) to record overarching system deviations or architectural safety mechanisms.

## MISRA Guideline Obligation Levels

Every MISRA C:2012 guideline belongs to one of three obligation classes:

1. **Mandatory**:
   - Must be followed without exception.
   - **No deviation permitted** under any circumstances (e.g., Rule 9.1: uninitialized variables, Rule 22.1: resource leaks).
2. **Required**:
   - Must be followed unless a formal, documented **Deviation Record** is approved by technical leadership and functional safety managers (e.g., Rule 10.3: essential type conversions, Rule 11.4: pointer-to-integer casts for hardware register mapping).
3. **Advisory**:
   - Good practice recommendations. Should be followed in new code. Deviations must be logged in project records but do not require formal safety deviation justification unless enforced as Required by project policy.

## Workflow

1. **Establish the Analysis Scope & Target Profile.**
   - Identify target files (`.c`, `.h`), diff ranges, or function units.
   - Determine target environment parameters:
     - Target architecture (e.g., 32-bit ARM Cortex-M7, 64-bit AArch64, S32K3).
     - Standard version (C99 vs C11).
     - Component layer (AUTOSAR BSW, MCAL hardware abstraction, CDD, or Application SWC).
     - ASIL classification (QM, ASIL-B, ASIL-D).

2. **Audit Essential Types & Type Conversions (MISRA Section 10).**
   - *Rule 10.1*: Verify operands possess appropriate essential types (Boolean, Character, Enum, Signed, Unsigned, Floating).
   - *Rule 10.3*: Check for narrowing assignments (e.g., `uint32_t` assigned or passed to `uint16_t` without explicit casting or range checks).
   - *Rule 10.4*: Ensure both operands of binary operators have identical essential type categories.
   - *Rule 10.6 / 10.7 / 10.8*: Verify composite expressions are not assigned to wider types or cast inappropriately before arithmetic evaluation.

3. **Audit Pointers, Arrays, and Memory Safety (MISRA Sections 11, 18, 21).**
   - *Rule 11.1 / 11.3 / 11.4*: Flag pointer conversions between incompatible object types or pointer/integer conversions (unless strictly mapping hardware memory-mapped I/O with deviation).
   - *Rule 11.8*: Check for casting away `const` or `volatile` qualifiers.
   - *Rule 18.1 / 18.4*: Verify array indexing stays strictly within bounds; prohibit pointer arithmetic (`+`, `-`, `++`, `--`) outside indexed array notation.
   - *Rule 21.3 (Dir 4.12)*: Verify zero dynamic memory allocation (`malloc`, `calloc`, `realloc`, `free`, `alloca`). All buffers must be statically or deterministically allocated.

4. **Audit Control Flow & Defensive Structures (MISRA Sections 14, 15, 16).**
   - *Rule 14.3*: Audit for invariant controlling expressions (e.g., conditions that statically evaluate to constant true/false).
   - *Rule 15.6*: Enforce compound statements (`{ ... }`) for all iteration and selection blocks (`if`, `for`, `while`, `do-while`), even single-line bodies.
   - *Rule 15.7*: Ensure all `if ... else if` chains conclude with an explicit terminal `else` branch (even if only containing an assertion or comment explaining why unreachable).
   - *Rule 16.1..16.7*: Audit `switch` statements: non-empty, default clause present and terminating, case statements enclosed, explicit `/* fallthrough */` annotations where permitted.

5. **Audit Functions, Declarations, and Unused Entities (MISRA Sections 2, 8, 17).**
   - *Rule 2.1*: Ensure zero unreachable code.
   - *Rule 2.2*: Eliminate dead operations whose results are unread.
   - *Rule 2.7*: Ensure no unused parameters in functions (suppress intentionally unused callback parameters with explicit `(void)param;` or project-defined unused macro).
   - *Rule 8.4*: Ensure external functions and objects have a visible prototype declaration in an included header before definition.
   - *Rule 8.7*: Restrict internal-only functions and objects to `static` file scope.
   - *Rule 17.2*: Prohibit direct or indirect recursion (mandatory for stack boundedness in safety ECUs).
   - *Rule 17.7*: Verify return values of non-void functions are used or explicitly cast to `(void)`.

6. **Audit Preprocessor and Defensive Macros (MISRA Section 20).**
   - *Rule 20.7*: Ensure macro parameters are enclosed in parentheses when used in expressions.
   - *Rule 20.10*: Prohibit `#` (stringification) and `##` (token pasting) operators unless thoroughly justified.
   - *Directive 4.6*: Require explicit-width integer types (`uint8_t`, `int16_t`, `uint32_t`, etc. from `<stdint.h>` or AUTOSAR `Platform_Types.h`) instead of raw basic types (`int`, `short`, `long`, `char`).

7. **Synthesize Findings: Prescribe Remediation or Draft Deviation Record.**
   - Pair every violation with its exact rule number, obligation level, and code citation.
   - Provide the compliant refactoring.
   - If the code interfaces directly with hardware registers or vendor MCAL drivers where a rule cannot be met, draft a structured **Formal Deviation Record**.

## Output

Emit audit findings directly in review notes or pull request qualification summaries.
When a standalone audit artifact or deviation package is required, follow the artifact layout standard:

```markdown
---
type: "MISRA C:2012 Compliance Audit"
title: "MISRA C:2012 Audit: [Module / Component Name]"
description: "Compliance diagnosis and remediation plan for MISRA C:2012 guidelines in [Component]"
status: "identified"
tags: [misra-c-2012, autosar, embedded-c, functional-safety, iso26262]
---

# MISRA C:2012 Compliance Audit: [Module / Component Name]

## Scope & Target Profile
- **Component**: [e.g., `uds_routine_handler.c`, `dkc_api`]
- **Standard**: MISRA C:2012 (Amendments 1–4) / C99 / AUTOSAR CP 4.4
- **Target Architecture**: [e.g., ARM Cortex-M7 (32-bit little-endian)]
- **Safety Integrity Level**: [e.g., ASIL-B / QM]

## Summary of Findings
| Obligation | Count | Status |
| :--- | :---: | :--- |
| **Mandatory** | 0 | Clean |
| **Required** | 2 | Action Required (Remediate or Deviate) |
| **Advisory** | 1 | Recommended Cleanup |

---

## Detailed Violations and Prescribed Remediations

### 1. Rule 10.3 (Required): Expression Assigned to Object of Narrower Essential Type
- **Location**: `source/fvt_cdd/common/uds/core/uds_routine_handler.c:1042`
- **Code Quote**:
  ```c
  if (E_OK == dkc_query_phone_key_info_start(option_record, option_record_len))
  ```
- **Violation Details**:
  `option_record_len` is of type `uint32_t`, while `dkc_query_phone_key_info_start` expects `uint16_t data_len`. Implicit narrowing conversion without range validation.
- **Prescribed Remediation**:
  Validate bounds before invoking or explicitly cast:
  ```c
  if (option_record_len > UINT16_MAX)
  {
      *error_code = requestOutOfRange;
      return E_NOT_OK;
  }
  if (E_OK != dkc_query_phone_key_info_start(option_record, (uint16_t)option_record_len))
  {
      *error_code = conditionsNotCorrect;
      return E_NOT_OK;
  }
  ```

---

## Formal Deviation Records (If Applicable)

### DEV-001: Rule 11.4 (Required) — Pointer to Integer Conversion for Hardware Register Mapping
- **Guideline**: MISRA C:2012 Rule 11.4 (Conversion between pointer and integer)
- **Scope**: `source/bsw/mcal/dio/dio_hw.c:45-52`
- **Safety Rationale**: Direct memory-mapped I/O register access requires casting fixed physical addresses (`#define DIO_PORTA_BASE 0x400FF000UL`) to volatile hardware register pointers (`(volatile uint32_t *)`).
- **Mitigation & Verification**: Addresses are bounded by memory protection unit (MPU) configurations and verified via automated register read/write unit test suites under target hardware.
- **Approval**: Required sign-off by Technical Lead and Functional Safety Manager.
```

## Red Flags

- **Silencing Warnings Without Rationale**: Suppressing static analyzer warnings with pragmas without a logged deviation record.
- **Implicit Narrowing Conversions**: Passing wide integers (`uint32_t`, `size_t`) into narrow fields (`uint16_t`, `uint8_t`) without range checks.
- **Dynamic Memory in Safety Systems**: Permitting `malloc`/`free` in ASIL-rated automotive software.
- **Unbounded Loops or Recursion**: Allowing `while (1)` without watchdog refresh or hardware timeout break conditions, or recursive calls that risk stack exhaustion.
- **Missing Final Else**: Writing `if ... else if` constructs without a mandatory terminal `else` block (violating Rule 15.7).

## Verification Checklist

- [ ] Every identified violation cites exact MISRA C:2012 rule/directive numbers and obligation class (*Mandatory*, *Required*, *Advisory*).
- [ ] Every violation provides exact file path, line numbers, and illustrative code snippets.
- [ ] Remediation proposals preserve existing system behavior and public AUTOSAR / ISO 14229 API contracts.
- [ ] Any required deviations contain the 4 essential fields: Guideline, Scope, Safety Rationale, and Mitigation/Verification.
