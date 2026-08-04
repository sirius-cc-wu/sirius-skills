# Order Cancellation Feedback Fixture

This disposable project models a small order lifecycle. Its checked-in tests
describe the legacy behavior and pass before the evaluation starts.

The approved change requires `Order.cancel(reason)` to:

- reject an empty or whitespace-only reason without changing the order;
- retain the supplied reason as `order.cancellation_reason`; and
- reject cancellation after shipment without changing the order.

`CancellationReason` is the domain name for the captured explanation; it does
not prescribe a separate Python class. A rejection may use any ordinary
exception. The independent verifier under `verification/` checks these
observable outcomes and is not implementation-owned test code.

[`docs/domain-model.md`](docs/domain-model.md) is the project's one canonical
domain model. Update it if implementation establishes durable domain knowledge,
but do not create competing analysis, design, contract, or diagram files.
