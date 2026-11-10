# MISRA C:2012 Rule Catalog for Automotive Embedded Systems

This catalog provides an authoritative reference for common MISRA C:2012 rules and directives applied in automotive embedded C engineering, AUTOSAR Classic, Complex Device Drivers (CDD), and ISO 26262 functional safety software development.

---

## 1. Guideline Taxonomy & Obligations

| Obligation | Definition | Deviation Permitted? |
| :--- | :--- | :---: |
| **Mandatory** | Absolute compliance required. Compilers or code violating mandatory rules cannot be claimed as MISRA compliant. | **No** |
| **Required** | Strict compliance required. Any violation must be formally justified with an approved **Deviation Record**. | **Yes** (Formal) |
| **Advisory** | Best-practice recommendations. Should be followed in all new code; project deviation log tracks exceptions. | **Yes** (Logged) |

---

## 2. Essential Types & Type Conversions (Section 10)

MISRA C:2012 replaces standard C implicit conversion rules with the **Essential Type Model**. Every expression has an essential type category:
* *Boolean* (`bool`, `boolean`)
* *Character* (`char`)
* *Signed* (`int8_t`, `int16_t`, `int32_t`, `int64_t`)
* *Unsigned* (`uint8_t`, `uint16_t`, `uint32_t`, `uint64_t`)
* *Floating* (`float32_t`, `float64_t`)
* *Enum* (Enumeration types)

### Rule 10.1 (Required)
**Operands shall not be of an inappropriate essential type.**
- *Violation*: Performing bitwise operations (`&`, `|`, `^`, `~`, `<<`, `>>`) on signed integers or boolean expressions.
- *Remedy*: Cast or declare bitwise operands as unsigned types (`uint8_t`, `uint16_t`, `uint32_t`).

### Rule 10.3 (Required)
**The value of an expression shall not be assigned to an object with a narrower essential type or of a different essential type category.**
- *Violation*: Passing a `uint32_t` variable to a function expecting `uint16_t`, or assigning an `int32_t` expression to an `int8_t` variable without an explicit cast and range check.
- *Remedy*: Ensure type matching. If narrowing is intentional, validate the value does not exceed the destination maximum before explicitly casting:
  ```c
  if (length <= UINT16_MAX)
  {
      dev_send((uint16_t)length);
  }
  ```

### Rule 10.4 (Required)
**Both operands of an operator in which the usual arithmetic conversions are performed shall have the same essential type category.**
- *Violation*: Mixing signed and unsigned operands in comparisons or arithmetic (e.g., `if (signed_val > unsigned_val)`).
- *Remedy*: Align both operands to the same type explicitly before comparison.

### Rule 10.6 (Required)
**The value of a composite expression shall not be assigned to an object with wider essential type.**
- *Violation*: `uint32_t result = u16_a * u16_b;` (arithmetic is evaluated in 16-bit or standard int promotion, risking overflow before 32-bit assignment).
- *Remedy*: Cast the first operand to the wider type before the operation:
  ```c
  uint32_t result = (uint32_t)u16_a * u16_b;
  ```

---

## 3. Pointers, Arrays, and Memory Safety (Sections 11, 18, 21)

### Rule 11.1 (Required)
**Conversions shall not be performed between a pointer to a function and any other type.**

### Rule 11.4 (Advisory / Required in Safety)
**A conversion should not be performed between a pointer to object and an integer type.**
- *Exception / Deviation*: Memory-mapped I/O registers in hardware drivers (e.g., MCAL) require casting physical addresses to pointer types:
  ```c
  /* Requires approved project deviation DEV-HW-001 */
  #define REG_CTRL (*(volatile uint32_t *)(0x40001000UL))
  ```

### Rule 11.8 (Required)
**A conversion shall not remove any const or volatile qualification from the type pointed to by a pointer.**
- *Violation*: Casting away `const` to modify read-only data, or casting away `volatile` from hardware registers or shared IPC memory buffers.

### Rule 18.1 (Required)
**A pointer resulting from arithmetic on a pointer operand shall address an element of the same array or one past the end.**

### Rule 18.4 (Advisory)
**The `+`, `-`, `+=` and `-=` operators should not be applied to an expression of pointer type.**
- *Remedy*: Use indexed array access (`buffer[i]`) instead of pointer arithmetic (`*(buffer + i)` or `p++`).

### Rule 21.3 / Directive 4.12 (Required)
**The memory allocation and deallocation functions of `<stdlib.h>` (`malloc`, `calloc`, `realloc`, and `free`) shall not be used.**
- *Rationale*: Dynamic heap allocation introduces non-deterministic execution time, fragmentation, and out-of-memory failure modes unacceptable in ISO 26262 ASIL ECUs.
- *Remedy*: Preallocate all memory statically at compile-time or use deterministic fixed-block pools.

---

## 4. Control Flow & Defensive Structures (Sections 14, 15, 16)

### Rule 14.3 (Required)
**Controlling expressions shall not be invariant.**
- *Violation*: `if (1)` or `while (x == x)` where the condition can never evaluate to another branch at runtime.

### Rule 15.6 (Required)
**The body of an iteration-statement or a selection-statement shall be a compound statement.**
- *Violation*:
  ```c
  if (ret != E_OK)
      return E_NOT_OK; /* Non-compliant: missing braces */
  ```
- *Remedy*: Always enclose bodies in curly braces:
  ```c
  if (ret != E_OK)
  {
      return E_NOT_OK;
  }
  ```

### Rule 15.7 (Required)
**All `if ... else if` constructs shall be terminated with an `else` statement.**
- *Rationale*: Defensive programming requires explicit handling or documenting of unreachable branches.
- *Remedy*:
  ```c
  if (state == STATE_INIT)
  {
      handle_init();
  }
  else if (state == STATE_RUN)
  {
      handle_run();
  }
  else
  {
      /* Defensive: Unhandled state */
      handle_error(state);
  }
  ```

### Rule 16.1 through 16.7 (Required)
**Discipline for `switch` statements:**
- Every `switch` statement shall have a terminating `default` clause (Rule 16.4).
- Every non-empty case clause shall conclude with an unconditional `break` or `return`, unless marked with an explicit fallthrough comment (Rule 16.3).
- The `switch` controlling expression shall not have essential boolean type (Rule 16.7).

---

## 5. Declarations, Functions, and Scope (Sections 2, 8, 17)

### Rule 2.1 (Required)
**A project shall not contain unreachable code.**

### Rule 2.2 (Required)
**There shall be no dead code (operations whose results are unconsumed).**

### Rule 2.7 (Advisory)
**There should be no unused parameters in functions.**
- *Remedy*: If an API callback interface mandates fixed parameters that this specific handler does not require, explicitly suppress compiler warnings:
  ```c
  (void)unused_parameter;
  ```

### Rule 8.4 (Required)
**A compatible declaration shall be visible when an object or function with external linkage is defined.**
- *Remedy*: Always declare exported functions in their companion `.h` file and include that `.h` file in the implementing `.c` file.

### Rule 8.7 (Advisory)
**Functions and objects should not be defined with external linkage if they are only referenced in one translation unit.**
- *Remedy*: Declare private intra-module functions and global variables as `static`.

### Rule 17.2 (Required)
**Functions shall not call themselves, either directly or indirectly (No recursion).**
- *Rationale*: Recursion produces unbounded stack growth, triggering stack overflows on embedded ECUs.

### Rule 17.7 (Required)
**The value returned by a function having non-void return type shall be used.**
- *Remedy*: Evaluate the return value, or if intentionally ignored, cast to `(void)`:
  ```c
  (void)memset(buffer, 0, sizeof(buffer));
  ```

---

## 6. Preprocessor and Directives (Section 20 & Directives)

### Directive 4.6 (Advisory)
**Typedefs that indicate size and signedness should be used in place of the basic numerical types.**
- *Remedy*: Use `<stdint.h>` or AUTOSAR `Platform_Types.h` (`uint8_t`, `uint16_t`, `uint32_t`, `sint8_t`, `sint16_t`, `sint32_t`, `boolean`). Do not use bare `int`, `long`, `short`, `unsigned`.

### Rule 20.7 (Required)
**Expressions resulting from the expansion of macro parameters shall be enclosed in parentheses.**
- *Violation*: `#define SQUARE(x) (x * x)`
- *Remedy*: `#define SQUARE(x) ((x) * (x))`

### Rule 20.10 (Advisory)
**The `#` and `##` preprocessor operators should not be used.**

---

## 7. Formal Deviation Record Template

When a **Required** or **Advisory** guideline cannot be adhered to due to hardware constraints, vendor MCAL interfaces, or architectural drivers, document a formal deviation:

```markdown
### Deviation Record: DEV-[YYYY]-[SEQ]
- **Guideline**: MISRA C:2012 Rule [Number] ([Obligation])
- **Affected Files & Functions**: `path/to/file.c` (`function_name`)
- **Reason & Scope**: [Precise explanation of why compliance is impossible or counter-productive]
- **Safety Impact Analysis (ISO 26262)**: [Impact on memory safety, stack bounds, or execution predictability]
- **Mitigation & Verification**: [Static assertion, MPU protection, automated test, or hardware bounding that prevents hazards]
- **Approvers**:
  - Technical Lead / Architect: [Name / Signature]
  - Functional Safety Manager: [Name / Signature]
```
