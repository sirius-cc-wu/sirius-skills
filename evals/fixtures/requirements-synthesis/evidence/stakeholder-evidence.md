---
type: "Stakeholder Evidence Record"
title: "Stakeholder Evidence: Regional Reconciliation"
description: "Sanitized evidence about unresolved regional-account reconciliation."
id: "DISCOVERY-RECON"
status: "completed-with-gaps"
tags: ["requirements", "elicitation"]
---

# Stakeholder Evidence: Regional Reconciliation

## Stakeholder Coverage

| Role | Decision authority | Coverage |
|---|---|---|
| Operations sponsor | Funding and priority, not workflow or compliance policy | Represented |
| Reconciliation operator | Current workflow accuracy, not funding or policy | Represented |
| Compliance policy owner | Export and disclosure controls | Represented by approved policy |
| Support lead | Support workflow and consequences | Missing |

## Evidence

### SRC-SPONSOR-ALPHA

- Method: sponsor interview
- Authority: funding and operational priority; not compliance policy
- Claim status and confidence: reported, high
- Publication: sanitized summaries allowed
- Content: The sponsor requested a dashboard showing every regional
  transaction and assumed managers mainly needed better charts.

### SRC-OPS-BETA

- Method: contextual observation and operator interview
- Authority: current workflow accuracy; not funding or compliance policy
- Claim status and confidence: observed and reported, high
- Publication: role and sanitized workflow may be published
- Content: The operator reconciled differently formatted account identifiers,
  investigated unmatched records, and asked for a saved work queue. No charts
  were used in the observed workflow.

### SRC-POLICY-GAMMA

- Method: approved policy review
- Revision: CP-17 revision 4
- Authority: data export and disclosure
- Claim status and confidence: corroborated policy fact, high
- Publication: policy ID and summarized rule only
- Content: Personal banking details and customer identity attributes may not
  leave the controlled ledger environment. Aggregated counts and opaque account
  references require compliance review before external display.

## Coverage Gaps and Conflicts

- SRC-SPONSOR-ALPHA proposes charts, while SRC-OPS-BETA describes identifier
  matching and queue management as the difficult work.
- No represented source has authority to choose a retention duration for saved
  reconciliation items.
- Support consequences remain unobserved.
