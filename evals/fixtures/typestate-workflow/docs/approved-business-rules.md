# Approved Business Rules: Order Fulfillment

## Status: Approved
Authority: Architecture Governance

## Rules
1. **Rule R-1 (Linear Progression)**: An Order progresses strictly through `Draft` -> `Submitted` -> `Approved` -> `Fulfilled`.
2. **Rule R-2 (Rejection Termination)**: An Order in `Submitted` state may transition to `Rejected`. No further transitions are permitted from `Rejected`.
3. **Rule R-3 (Compile-Time Enforcement)**: It must be structurally impossible at compile time to invoke `fulfill()` on an Order that is in `Draft` or `Submitted` state.
4. **Rule R-4 (Ownership Invariant)**: Each state transition method must take ownership of `self` by value to prevent reuse of stale states.
