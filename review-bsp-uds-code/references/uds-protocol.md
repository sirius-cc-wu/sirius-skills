# UDS Service Reference (ISO 14229-1)

## Diagnostic Service IDs

| SID | Service Name | Min Length |
|-----|--------------|------------|
| 0x10 | DiagnosticSessionControl | 2 |
| 0x11 | ECUReset | 2 |
| 0x14 | ClearDiagnosticInformation | 4 |
| 0x19 | ReadDTCInformation | 2+ |
| 0x22 | ReadDataByIdentifier | 3 |
| 0x23 | ReadMemoryByAddress | 4+ |
| 0x24 | ReadScalingDataByIdentifier | 3 |
| 0x27 | SecurityAccess | 2 |
| 0x28 | CommunicationControl | 3 |
| 0x2E | WriteDataByIdentifier | 4+ |
| 0x2F | InputOutputControlByIdentifier | 4+ |
| 0x31 | RoutineControl | 4 |
| 0x34 | RequestDownload | 4+ |
| 0x35 | RequestUpload | 4+ |
| 0x36 | TransferData | 2+ |
| 0x37 | RequestTransferExit | 1 |
| 0x3E | TesterPresent | 2 |
| 0x85 | ControlDTCSetting | 2 |

## Negative Response Codes (NRC)

| NRC | Value | Description |
|-----|-------|-------------|
| positiveResponse | 0x00 | (Not an NRC, just reference) |
| serviceNotSupported | 0x11 | Service identifier not supported |
| subfunctionNotSupported | 0x12 | Subfunction not supported |
| incorrectMessageLengthOrInvalidFormat | 0x13 | Message length wrong |
| responseTooLong | 0x14 | Response exceeds buffer |
| busyRepeatRequest | 0x21 | Server busy, repeat later |
| conditionsNotCorrect | 0x22 | Conditions not met |
| requestSequenceError | 0x24 | Request received in wrong sequence |
| noResponseFromSubnetComponent | 0x25 | Subnet component not responding |
| failurePreventsExecutionOfRequestedAction | 0x26 | Action cannot be executed |
| requestOutOfRange | 0x31 | Parameter out of range |
| securityAccessDenied | 0x33 | Security access not granted |
| invalidKey | 0x35 | Security key invalid |
| exceededNumberOfAttempts | 0x36 | Too many security attempts |
| requiredTimeDelayNotExpired | 0x37 | Security delay active |
| uploadDownloadNotAccepted | 0x70 | Transfer not accepted |
| transferDataSuspended | 0x71 | Transfer suspended |
| generalProgrammingFailure | 0x72 | Programming failed |
| wrongBlockSequenceCounter | 0x73 | Block sequence error |
| responsePending | 0x78 | Response is pending |
| subfunctionNotSupportedInActiveSession | 0x7E | Not in correct session |
| serviceNotSupportedInActiveSession | 0x7F | Service not in session |

## DTC Setting Control (SID 0x85)

| Subfunction | Value | Description |
|-------------|-------|-------------|
| DTC_SETTING_ON | 0x01 | Enable DTC setting |
| DTC_SETTING_OFF | 0x02 | Disable DTC setting |

## Communication Control (SID 0x28)

| Subfunction | Value | Description |
|-------------|-------|-------------|
| enableRxAndTx | 0x00 | Enable Rx and Tx |
| enableRxAndDisableTx | 0x01 | Enable Rx, disable Tx |
| disableRxAndEnableTx | 0x02 | Disable Rx, enable Tx |
| disableRxAndTx | 0x03 | Disable Rx and Tx |

| Communication Type | Value | Description |
|--------------------|-------|-------------|
| normalCommunicationMessages | 0x01 | Normal communication |
| nmCommunicationMessages | 0x02 | NM messages |
| allCommunicationMessages | 0x03 | All messages |

## Routine Control (SID 0x31)

| Subfunction | Value | Description |
|-------------|-------|-------------|
| startRoutine | 0x01 | Start routine |
| stopRoutine | 0x02 | Stop routine |
| requestRoutineResults | 0x03 | Request results |

## P2 Timing Parameters (ISO 14229-2)

| Parameter | Default | Description |
|-----------|---------|-------------|
| P2_Server | 50ms | Server response time |
| P2*_Server | 5000ms | Extended response time |
| P3_Client | 50ms | Client min request interval |

## DoIP Protocol (ISO 13400)

| Payload Type | Value | Description |
|--------------|-------|-------------|
| DOIP_DIAGNOSTIC_MESSAGE | 0x8001 | Standard diagnostic |
| DOIP_DIAGNOSTIC_MESSAGE_RTT | 0x8002 | RTT diagnostic |
| DOIP_DIAGNOSTIC_TROUBLE_CODE | 0x8003 | DTC specific |

Header format:
```
| Version (1) | Inv Version (1) | Payload Type (2) | Payload Length (4) |
| Source Address (2) | Target Address (2) | UDS Data (n) |
```
