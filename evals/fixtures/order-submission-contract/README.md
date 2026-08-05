# Order Submission Contract Fixture

This disposable project contains approved effects for the non-trivial
`submitOrder(orderId)` system operation. The existing
[`docs/order-submission.md`](docs/order-submission.md) file is the feature's one
canonical analysis artifact: it already owns the use case, domain vocabulary,
and system sequence diagram.

Refine that aggregate with one declarative operation contract. Do not create a
standalone contract, implementation code, database design, or another analysis
artifact. The approved effects under `requirements/` are authoritative. The
independent verifier under `verification/` checks the minimum contract boundary
without prescribing prose outside those effects.
