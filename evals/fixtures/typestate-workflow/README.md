# Synthetic Fixture: Typestate Workflow

This fixture provides an approved domain workflow that must be encoded into compile-time type boundaries.

## Domain Scenario: Order Fulfillment Workflow

### State Transitions
1. `Draft` → `Submitted` (only when valid items exist)
2. `Submitted` → `Approved` OR `Rejected`
3. `Approved` → `Fulfilled`

### Invariants
- An order in `Draft` state must NEVER be fulfilled directly.
- An order in `Rejected` state must NEVER be approved or fulfilled.
- Transitions must consume the previous state value (`self`) and return the new typestate.
