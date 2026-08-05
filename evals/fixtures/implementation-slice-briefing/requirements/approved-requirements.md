---
type: "Requirements Discovery Brief"
title: "Approved Requirements: Opaque Reference Reconciliation"
description: "Approved matching behavior and disclosure controls, with queue retention still candidate."
id: "REQDISC-MATCH"
revision: "RD-3"
status: "completed-with-gaps"
tags: ["requirements", "validation"]
---

# Approved Requirements: Opaque Reference Reconciliation

## Approved Requirements

### RR-MATCH-OUTCOME

- Status: approved in `RD-3`
- Authority: operations sponsor for outcome and reconciliation process owner for
  operational correctness
- Statement: An operator can determine whether two opaque regional account
  references identify the same controlled account without exposing protected
  customer attributes.
- Source evidence IDs: `SRC-SPONSOR-ALPHA`, `SRC-OPS-BETA`

### RR-MATCH-RULE

- Status: approved in `RD-3`
- Authority: reconciliation process owner for identifier-matching rules
- Statement: A valid opaque reference has a two-letter region, a `-` or `/`
  separator, and a numeric account part. Region comparison is case-insensitive
  and leading zeroes in the numeric part are insignificant. References match
  only when both normalized region and numeric account are equal.
- Source evidence IDs: `SRC-OPS-BETA`, `PLAYBACK-PB-3`

### RR-DISCLOSURE

- Status: approved in `RD-3` against policy `CP-17` revision 4
- Authority: compliance policy owner for data export and disclosure
- Statement: The matching result may contain the supplied opaque references and
  match state, but no personal banking details or customer identity attributes.
- Source evidence IDs: `SRC-POLICY-GAMMA`, `PLAYBACK-PB-3`

## Approved Examples

### EX-MATCH-A

- Status: approved in `RD-3`
- Authority: reconciliation process owner for behavior and compliance policy
  owner for disclosed result fields
- Given: opaque references `EU-0042` and `eu/42`
- Then: the result is `same-account` and contains no protected attributes
- Traces: `RR-MATCH-OUTCOME`, `RR-MATCH-RULE`, `RR-DISCLOSURE`

### EX-MATCH-B

- Status: approved in `RD-3`
- Authority: reconciliation process owner
- Given: opaque references `EU-42` and `US-42`
- Then: the result is `different-account`
- Traces: `RR-MATCH-RULE`

### EX-MATCH-C

- Status: approved in `RD-3`
- Authority: reconciliation process owner
- Given: either reference does not follow the approved opaque-reference grammar
- Then: the result is `invalid-reference` and identifies which input is invalid
- Traces: `RR-MATCH-RULE`

## Candidate Feature Work

### RR-QUEUE-RETENTION

- Status: candidate in `RD-3`
- Authority needed: records governance
- Statement: Retention and disposition for a persisted unmatched-item queue are
  undecided. No duration, trigger, or deletion rule is approved.
- Implementation consequence: queue persistence is not ready for briefing.

## Approved Non-Goals for the Matching Slice

- No dashboard or chart behavior.
- No persistence, queue management, retention, customer lookup, or identity
  disclosure.
