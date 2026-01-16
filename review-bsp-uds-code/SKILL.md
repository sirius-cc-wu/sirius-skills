---
name: review-bsp-uds-code
description: Reviews UDS (Unified Diagnostic Services) code in this BSP project for correctness, safety, and ISO 14229 compliance. Use when reviewing PRs or code changes in source/fvt_cdd/common/uds/, when the user asks to review UDS code in a BSP project.
---

# Review UDS Code

Reviews UDS implementation code for automotive diagnostic services per ISO 14229 and AUTOSAR standards.

## Code Location

UDS code resides in `source/fvt_cdd/common/uds/`:
- `core/` - Core UDS dispatcher and service handlers
- `app/` - Application-specific DID/routine implementations
- `test/` - Unit tests

## Review Checklist

### 1. Buffer Safety (Critical)

Check all request parsing functions for proper bounds validation:

```c
// BAD: Reads 4 bytes but only checks 2
if (len < offset + 2) { return E_NOT_OK; }
uint16_t did = request[offset] << 8 | request[offset + 1];
offset += 2;
uint16_t length = request[offset] << 8 | request[offset + 1];  // Buffer over-read!

// GOOD: Check all bytes before reading
if (len < offset + 4) { return E_NOT_OK; }
uint16_t did = request[offset] << 8 | request[offset + 1];
offset += 2;
uint16_t length = request[offset] << 8 | request[offset + 1];
offset += 2;
```

Verify `memcpy` calls have length guards:

```c
// BAD: No length check
memcpy(buffer, request, EXPECTED_LEN);

// GOOD: Validate before copy
if (len < EXPECTED_LEN) { return; }
memcpy(buffer, request, EXPECTED_LEN);
```

### 2. Static Variable State

Static variables must be reset appropriately:

```c
// BAD: Counter never resets, breaks on re-initialization
static size_t collected_count = 0;
collected_count++;
if (collected_count >= expected) {
    init_module();
    // Missing: collected_count = 0;
}

// GOOD: Reset after use
if (collected_count >= expected) {
    init_module();
    collected_count = 0;
}
```

### 3. NULL Pointer Checks

Verify pointer validation before dereference:

```c
// BAD: Missing NULL check on dsp
static int lookup_dtc_index(const t_dsp *dsp, uint32_t dtc) {
    for (int i = 0; i < dsp->dem_config.dtc_len; i++) {  // Crash if dsp is NULL

// GOOD: Check first
static int lookup_dtc_index(const t_dsp *dsp, uint32_t dtc) {
    if (dsp == NULL) { return -1; }
    for (int i = 0; i < dsp->dem_config.dtc_len; i++) {
```

### 4. UDS Response Format (ISO 14229-1)

Positive response: SID + 0x40
```c
response[0] = request[0] + 0x40;  // Correct
```

Negative response: 0x7F + SID + NRC
```c
response[0] = 0x7F;
response[1] = service_id;
response[2] = error_code;
*res_len = 3;
```

### 5. Service Length Validation

Each service has minimum request length:
| Service | Min Length |
|---------|------------|
| ReadDataByIdentifier (0x22) | 3 (SID + 2-byte DID) |
| WriteDataByIdentifier (0x2E) | 3+ (SID + 2-byte DID + data) |
| ClearDiagnosticInformation (0x14) | 4 (SID + 3-byte DTC group) |
| RoutineControl (0x31) | 4 (SID + subfunc + 2-byte RID) |
| ControlDTCSetting (0x85) | 2 (SID + subfunc) |
| CommunicationControl (0x28) | 3 (SID + subfunc + type) |

### 6. Return Value Consistency

Ensure return values match documented behavior:
- `E_OK` - Operation successful
- `E_NOT_OK` - Operation failed
- `DCM_E_PENDING` - Async operation in progress
- `DCM_E_FORCE_RCRRP` - Force ResponsePending

```c
// BAD: Returns E_NOT_OK but should return E_OK after setting NRC
if (rid_index < 0) {
    to_negative_response(response, request[0], res_len, requestOutOfRange);
    return E_NOT_OK;  // Inconsistent with other error paths
}

// GOOD: Consistent return after response is prepared
if (rid_index < 0) {
    to_negative_response(response, request[0], res_len, requestOutOfRange);
    return E_OK;  // Response is ready
}
```

### 7. P2 Server Timeout

P2 timeout per ISO 14229-2: recommended 50ms.
Task cycle is 10ms, so timeout count = 5.

```c
#define P2_SERVER_TIMEOUT 5  // 5 × 10ms = 50ms
```

## Common NRC Codes

| NRC | Value | Meaning |
|-----|-------|---------|
| serviceNotSupported | 0x11 | SID not implemented |
| subfunctionNotSupported | 0x12 | Subfunction not valid |
| incorrectMessageLengthOrInvalidFormat | 0x13 | Length mismatch |
| conditionsNotCorrect | 0x22 | Preconditions not met |
| requestOutOfRange | 0x31 | DID/RID not found |
| securityAccessDenied | 0x33 | Security level insufficient |
| requestSequenceError | 0x24 | Invalid sequence |

## Review Output Format

Provide findings as PR comments with:
1. **File and line reference**
2. **Issue severity**: Bug, Warning, or Suggestion
3. **Description** of the problem
4. **Fix** recommendation with code example
