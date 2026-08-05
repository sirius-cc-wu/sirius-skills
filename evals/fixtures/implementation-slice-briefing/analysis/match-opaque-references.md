---
type: "Use Case"
title: "Match Opaque References"
description: "An operator determines whether two opaque references identify the same controlled account."
id: "UC-MATCH-OPAQUE"
revision: "UC-2"
status: "active"
primary_actor: "Reconciliation operator"
scope: "Regional reconciliation service"
level: "user goal"
tags: ["requirements", "use-case"]
---

# Use Case: Match Opaque References

## Goal

Determine whether two opaque regional account references identify the same
controlled account without retrieving or disclosing protected customer data.
This use case realizes approved requirements in `REQDISC-MATCH` revision `RD-3`.

## Main Success Scenario

1. The operator supplies two opaque regional account references.
2. The system validates both references against the approved grammar.
3. The system compares their normalized region and numeric account parts.
4. The system returns `same-account` or `different-account` with the supplied
   opaque references and no protected attributes.

## Extensions

2a. Either reference is invalid: the system returns `invalid-reference` and
identifies which input is invalid without attempting customer lookup.

## Special Requirements

- Apply `RR-DISCLOSURE` from `REQDISC-MATCH` revision `RD-3` and `CP-17`
  revision 4.

## Excluded Related Behavior

- Persisting unmatched items, queue management, and retention.
