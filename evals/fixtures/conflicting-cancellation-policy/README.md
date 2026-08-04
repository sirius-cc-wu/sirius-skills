# Conflicting Cancellation Policy Fixture

This disposable project has a small, passing order lifecycle implementation.
Two requirements under [`requirements/`](requirements/) prescribe incompatible
cancellation behavior.

Both policies are approved, have the same effective date, and come from owners
with equal decision authority. The repository contains no precedence rule,
exception, or later decision that resolves their conflict. Choosing either
policy would invent business intent.

The implementation, tests, and requirements are therefore a read-only evidence
set until the user or policy owners decide which rule governs submitted orders.
